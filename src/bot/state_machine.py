import random
import threading
import time
from datetime import datetime

from transitions import Machine, State

import config
import framework_objects
import hots
import match_result_helpers
import windows_helpers
from logger import logger


class Application(object):
    def __init__(self):
        random.seed(39)
        states = [
            State(name='not_running'),
            State(name='running', on_enter=['state_running_on_enter'])
        ]
        transitions = [
            {'trigger': 'run', 'source': 'not_running', 'dest': 'running'}
        ]

        self.machine = Machine(model=self, states=states, transitions=transitions,
                               initial='not_running', queued=True)

    def state_running_on_enter(self):
        logger.debug('Запускаю HOTS')
        windows_helpers.run_hots()

        game = Game()
        game.switch_game_state()


class Game(object):
    def __init__(self):
        states = [
            State(name='idle'),
            State(name='main_menu', on_enter=['state_main_menu_on_enter']),
            State(name='selecting_game_mode', on_enter=['state_selecting_game_mode_on_enter']),
            State(name='selecting_hero', on_enter=['state_selecting_hero_on_enter']),
            State(name='waiting_match', on_enter=['state_waiting_match_on_enter']),
            State(name='loading', on_enter=['state_loading_on_enter']),
            State(name='initiating_game', on_enter=['state_initiating_game_on_enter']),
            State(name='playing', on_enter=['state_playing_on_enter']),
            State(name='finishing', on_enter=['state_finishing_on_enter'])
        ]
        transitions = [
            {'trigger': 'switch_game_state', 'source': 'idle', 'dest': 'main_menu'},
            {'trigger': 'select_game_mode', 'source': 'main_menu', 'dest': 'selecting_game_mode'},
            {'trigger': 'select_hero', 'source': 'selecting_game_mode', 'dest': 'selecting_hero'},
            {'trigger': 'start_game', 'source': 'selecting_hero', 'dest': 'waiting_match'},
            {'trigger': 'wait_for_match', 'source': 'waiting_match', 'dest': 'loading'},
            {'trigger': 'initiate', 'source': 'loading', 'dest': 'initiating_game'},
            {'trigger': 'play', 'source': 'initiating_game', 'dest': 'playing'},
            {'trigger': 'finish', 'source': 'playing', 'dest': 'finishing'},
            {'trigger': 'start_new', 'source': 'finishing', 'dest': 'waiting_match'},

        ]

        self.hots_menu = hots.MainMenu()
        self.hots_loading_screen = hots.LoadingScreen()
        self.hots_game_screen = hots.GameScreen()
        self.emulator = windows_helpers.Emulator()

        self.game_side = 'none'
        self.game_map = None
        self.checking_afk_screen = False

        self.machine = Machine(model=self, states=states, transitions=transitions, initial='idle', queued=True)

    def state_main_menu_on_enter(self):
        self.hots_menu.open_play_panel()
        self.emulator.wait_random_delay()
        self.hots_menu.open_vs_ai_panel()
        self.emulator.wait_random_delay()
        self.select_game_mode()

    def state_selecting_game_mode_on_enter(self):
        self.hots_menu.select_alies_ai_mode()
        self.emulator.wait_random_delay()
        self.hots_menu.select_ai_level(config.Configuration.AI_LEVEL)
        self.emulator.wait_random_delay()
        self.select_hero()

    def state_selecting_hero_on_enter(self):
        self.hots_menu.select_hero(config.Configuration.HERO_TO_LEVEL)
        self.emulator.wait_random_delay()
        self.start_game()

    def state_waiting_match_on_enter(self):
        self.hots_menu.start_game()
        self.hots_menu.wait_for_match()
        time.sleep(2)
        self.wait_for_match()

    def state_loading_on_enter(self):
        logger.debug('Грузимся в игру')
        self.game_map = self.hots_loading_screen.detect_map()
        self.game_side = self.hots_loading_screen.detect_side()
        self.hots_loading_screen.wait_for_loading()
        self.initiate()

    def state_initiating_game_on_enter(self):
        logger.debug('Матч начался!')
        self.play()

    def state_playing_on_enter(self):
        player = Player(self.game_side, self.game_map)
        player_thread = threading.Thread(target=player.wait_for_game_start)
        player_thread.start()

        # поток проверки, не выбросило ли нас в окно АФК
        afk_thread = threading.Thread(target=self.return_to_game_if_afk)
        afk_thread.start()

        # проверка не закончился ли матч
        while not self.hots_menu.check_if_game_finished():
            time.sleep(5)

        logger.debug('Игра завершена')

        player.finish()  # finish playing
        self.finish()

    def state_finishing_on_enter(self):
        self.checking_afk_screen = False
        time.sleep(5)
        #  skip mvp screen
        logger.debug('Пропускаю окно mvp')
        self.hots_menu.press_skip_button()
        time.sleep(5)

        # skip stats screen
        logger.debug('Пропускаю окно статистики')
        self.hots_menu.press_skip_button()
        time.sleep(5)

        # wait for loading
        logger.debug('Жду загрузки')
        self.hots_loading_screen.wait_for_loading()
        time.sleep(5)

        # сохраняем результат игры
        screenshot = windows_helpers.Pixel().screen()
        screenshot_path = match_result_helpers.save_match_result(screenshot)

        # отправляем отчет на email
        if screenshot_path is not None and config.Configuration.SEND_EMAIL_ON_MATCH_END:
            match_result_helpers.send_match_result(screenshot_path)

        # skip experience screen
        logger.debug('Пропускаю окно начисления опыта')
        self.hots_menu.press_skip_button()
        time.sleep(5)

        logger.debug('Начинаю новую игру')
        self.start_new()


    def return_to_game_if_afk(self):
        self.checking_afk_screen = True
        while self.checking_afk_screen:
            if self.hots_menu.check_if_afk_screen():
                self.hots_menu.press_return_button()

            time.sleep(5)



class Player(object):
    def __init__(self, game_side, game_map):
        states = [
            State(name='idle', on_enter=['state_idle_on_enter']),
            State(name='dead', on_enter=['state_dead_on_enter']),
            State(name='thinking', on_enter=['state_thinking_on_enter']),
            State(name='attacking', on_enter=['state_attacking_on_enter']),
            State(name='moving', on_enter=['state_moving_on_enter']),
            State(name='resting', on_enter=['state_resting_on_enter'])
        ]
        transitions = [
            {'trigger': 'wait_for_game_start', 'source': 'idle', 'dest': 'thinking'},

            {'trigger': 'attack', 'source': 'moving', 'dest': 'attacking'},
            {'trigger': 'attack', 'source': 'attacking', 'dest': 'attacking'},

            {'trigger': 'move', 'source': 'attacking', 'dest': 'moving'},
            {'trigger': 'move', 'source': 'resting', 'dest': 'moving'},
            {'trigger': 'move', 'source': 'dead', 'dest': 'moving'},
            {'trigger': 'move', 'source': 'thinking', 'dest': 'moving'},
            {'trigger': 'move', 'source': 'moving', 'dest': 'moving'},

            {'trigger': 'rest', 'source': 'attacking', 'dest': 'resting'},
            {'trigger': 'rest', 'source': 'moving', 'dest': 'resting'},

            {'trigger': 'die', 'source': 'attacking', 'dest': 'dead'},
            {'trigger': 'die', 'source': 'moving', 'dest': 'dead'},
            {'trigger': 'die', 'source': 'resting', 'dest': 'dead'},

            {'trigger': 'finish', 'source': 'dead', 'dest': 'idle'},
            {'trigger': 'finish', 'source': 'attacking', 'dest': 'idle'},
            {'trigger': 'finish', 'source': 'moving', 'dest': 'idle'},
            {'trigger': 'finish', 'source': 'resting', 'dest': 'idle'},

        ]

        self.side = game_side
        self.map = game_map
        self.current_tower = 0
        self.current_hp = 100

        self.game_screen = hots.GameScreen()
        self.map_screen = hots.MapScreen(game_map, game_side)

        self.machine = Machine(model=self, states=states, transitions=transitions, initial='idle', queued=True)

    def state_thinking_on_enter(self):
        logger.info('Ожидаю начала отсчета времени')
        self.idle = False

        # wait until match timer starts
        self.game_screen.wait_match_timer_start()

        logger.info('Иду ко второй башне')
        # move to second tower
        second_tower = self.map_screen.towers[1]
        self.game_screen.move_to(second_tower.x, second_tower.y)
        self.current_tower = 1

        # learn initial talent
        self.game_screen.learn_talent()

        logger.info('Жду начала матча')
        # wait until match begins
        time.sleep(config.Configuration.MATCH_COUNTDOWN)

        logger.info('Иду воевать!')
        self.move()

    def state_moving_on_enter(self):
        if self.game_screen.detect_death():
            self.die()
            return None

        if self.game_screen.get_health() < 30:
            self.rest()
            return None

        movement_length = config.Configuration.MOVEMENT_LONG
        screenshot = self.game_screen.pixel.screen()
        current_tower_index = self.current_tower
        frontline_tower_index = self.map_screen.get_frontline_tower_index(screenshot)

        # определение цели движения
        if current_tower_index < frontline_tower_index:  # если мы еще не на фронте
            destination_tower_index = frontline_tower_index
            logger.debug('Движение к фронтовой башне')
        elif self.game_screen.get_health() < self.current_hp:  # нас бьют
            destination_tower_index = frontline_tower_index
            self.current_hp = self.game_screen.get_health()
            logger.debug('Нас бьют, значит мы идем к своей башне')
        else:  # если уже на фронте или дальше
            next_tower_index = current_tower_index + 1
            if self.map_screen.check_enemy_tower_alive(screenshot, next_tower_index):  # если следующий вражеский тавер жив
                movement_length = config.Configuration.MOVEMENT_SHORT # будем двигаться не доходя до башни
                destination_tower_index = next_tower_index
                logger.debug('Двигаемся на пару шагов вперед к живой башне врага')
            else:  # в противном случае делаем полный переход
                destination_tower_index = next_tower_index
                logger.debug('Двигаемся к мертвой башне врага')

        if destination_tower_index >= len(self.map_screen.towers):
            destination_tower_index = len(self.map_screen.towers) - 1

        destination_tower = self.map_screen.towers[destination_tower_index]

        # определяем сдвиг камеры для точки движения
        h_offset = 20
        if self.side == 'right_side':  # если мы за правых
            h_offset *= -1

        if destination_tower_index > frontline_tower_index:  # если идем к врагу
            h_offset *= -1.4  # не подходим на пушечный выстрел

        # начинаем движение
        self.game_screen.move_to(destination_tower.x + h_offset, destination_tower.y)
        logger.debug('Двигаюсь к башне №' + destination_tower_index.__str__())

        if self.game_screen.check_talents_avalible(screenshot):
            logger.info('Доступны новые таланты')
            self.game_screen.learn_talent()

        # пока движемся - ищем крипов
        movement_start_time = datetime.now().timestamp()
        while datetime.now().timestamp() - movement_start_time < movement_length:
            units = self.game_screen.get_units()
            enemy_unit = self.game_screen.find_nearest_enemy(units)

            if enemy_unit is not None:
                logger.debug('Цель обнаружена. Перехожу к атаке')
                self.game_screen.stop()
                self.attack(enemy_unit)
                return None

            time.sleep(1)

        logger.debug('Движение закончено, целей не обнаружено')
        if movement_length == config.Configuration.MOVEMENT_LONG:  # если дошли до следущей башни
            self.current_tower = destination_tower_index  # то повышаем индекс

        self.game_screen.stop()
        time.sleep(3)
        self.move()  # движемся дальше

    def state_attacking_on_enter(self, creep: framework_objects.Unit):
        if self.game_screen.detect_death():
            self.die()
            return None

        if self.game_screen.get_health() < 30:
            self.rest()
            return None

        self.current_hp = self.game_screen.get_health()
        logger.debug('Атакую противника')
        self.game_screen.attack(creep)

        self.game_screen.use_random_ability()
        time.sleep(0.2)

        for i in range(1, random.randint(2, 3)):
            time.sleep(0.5)
            health = self.game_screen.get_health()
            delta_health = self.current_hp - health
            if delta_health > 10:
                logger.debug('Нас больно бьют, ретируемся')
                self.current_hp = health
                self.game_screen.run_away(self.map_screen.towers[0])
                break
            elif delta_health > 3:
                logger.debug('Нас бьют, но не сильно. Бэкпедалим')
                self.current_hp = health
                self.game_screen.backpedal(self.side)

        units = self.game_screen.get_units()
        next_unit = self.game_screen.find_nearest_enemy(units)

        if next_unit is not None:
            self.attack(next_unit)
        else:
            logger.debug('Целей больше нет. Двигаюсь дальше')
            self.move()

    def state_dead_on_enter(self):
        logger.debug('Персонаж умер')
        self.current_tower = 0

        while self.game_screen.detect_death():
             time.sleep(1)

        time.sleep(2)
        logger.debug('Персонаж воскрес')
        self.current_hp = self.game_screen.get_health()
        self.move()

    def state_resting_on_enter(self):
        logger.debug('Мало здоровья, возвращаюсь на базу')
        self.game_screen.backpedal(self.side)
        self.game_screen.backpedal(self.side)

        self.game_screen.teleport()
        self.current_tower = 0

        if self.game_screen.detect_death():
            self.die()
            return None

        time.sleep(15)
        self.current_hp - self.game_screen.get_health()

        if not self.idle:
            self.move()

    def state_idle_on_enter(self):
        self.idle = True