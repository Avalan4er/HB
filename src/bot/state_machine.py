from transitions import Machine, State
import windows_helpers
import time
import logging
import hots
import config
import constants
import random
import threading
from datetime import datetime


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
        logging.debug('Запускаю HOTS')
        windows_helpers.run_hots()

        logging.debug('HOTS запускается, жду ' + constants.WAIT_BEFORE_GAME_STARTS.__str__() + ' секунд')
        time.sleep(constants.WAIT_BEFORE_GAME_STARTS)

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
        self.hots_menu.select_ai_level(config.AI_LEVEL)
        self.emulator.wait_random_delay()
        self.select_hero()

    def state_selecting_hero_on_enter(self):
        self.hots_menu.select_hero(config.HERO_TO_LEVEL)
        self.emulator.wait_random_delay()
        self.start_game()

    def state_waiting_match_on_enter(self):
        self.hots_menu.start_game()
        self.hots_menu.wait_for_match()
        time.sleep(2)
        self.wait_for_match()

    def state_loading_on_enter(self):
        logging.debug('Грузимся в игру')
        self.game_map = self.hots_loading_screen.detect_map()
        self.game_side = self.hots_loading_screen.detect_side()
        self.hots_loading_screen.wait_for_loading()
        self.initiate()

    def state_initiating_game_on_enter(self):
        logging.debug('Матч начался!')
        self.play()

    def state_playing_on_enter(self):
        player = Player(self.game_side, self.game_map)
        thread = threading.Thread(target=player.wait_for_game_start)
        thread.start()

        while not self.hots_menu.check_if_game_finished():
            time.sleep(5)

        logging.debug('Игра завершена')

        player.finish()  # finish playing
        self.finish()

    def state_finishing_on_enter(self):
        #  skip mvp screen
        logging.debug('Пропускаю окно mvp')
        self.hots_menu.press_skip_button()
        self.emulator.wait_random_delay()

        # skip stats screen
        logging.debug('Пропускаю окно статистики')
        self.hots_menu.press_skip_button()
        time.sleep(5)

        # wait for loading
        logging.debug('Жду загрузки')
        self.hots_loading_screen.wait_for_loading()
        time.sleep(5)

        # skip experience screen
        logging.debug('Пропускаю окно начисления опыта')
        self.hots_menu.press_skip_button()
        time.sleep(5)

        logging.debug('Начинаю новую игру')
        self.start_new()


class Player(object):
    def __init__(self, game_side, game_map):
        states = [
            State(name='idle'),
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
        logging.debug('Ожидаю начала отсчета времени')

        # wait until match timer starts
        self.game_screen.wait_match_timer_start()

        logging.debug('Иду ко второй башне')
        # move to second tower
        second_tower = self.map_screen.towers[1]
        self.game_screen.move_to(second_tower.x, second_tower.y)
        self.current_tower = 1

        logging.debug('Жду начала матча')
        # wait until match begins
        time.sleep(config.MATCH_COUNTDOWN)

        logging.debug('Иду воевать!')
        self.move()

    def state_moving_on_enter(self):
        if self.game_screen.detect_death():
            self.die()
            return None

        if self.game_screen.get_health() < 30:
            self.rest()
            return None

        movement_length = config.MOVEMENT_LONG
        screenshot = self.game_screen.pixel.screen()
        current_tower_index = self.current_tower
        frontline_tower_index = self.map_screen.get_frontline_tower_index(screenshot)


        if current_tower_index < frontline_tower_index:  # если мы еще не на фронте
            destination_tower_index = frontline_tower_index
            logging.debug('Движение к фронтовой башне')
        elif self.game_screen.get_health() < self.current_hp:  # нас бьют
            destination_tower_index = frontline_tower_index
            self.current_hp = self.game_screen.get_health()
            logging.debug('Нас бьют, значит мы идем к своей башне')
        else:  # если уже на фронте или дальше
            next_tower_index = current_tower_index + 1
            if self.map_screen.check_enemy_tower_alive(screenshot, next_tower_index):  # если следующий вражеский тавер жив
                movement_length = config.MOVEMENT_SHORT # будем двигаться не доходя до башни
                destination_tower_index = next_tower_index
                logging.debug('Двигаемся на пару шагов вперед к живой башне врага')
            else:  # в противном случае делаем полный переход
                destination_tower_index = next_tower_index
                logging.debug('Двигаемся к мертвой башне врага')

        #  определяем к какой башне движемся
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
        logging.debug('Двигаюсь к башне №' + destination_tower_index.__str__())

        if random.randint(0, 4) == 3:
            logging.debug('Кости сложились удачно')
            self.game_screen.learn_random_talent()

        # пока движемся - ищем крипов
        movement_start_time = datetime.now().timestamp()
        while datetime.now().timestamp() - movement_start_time < movement_length:
            creep = self.game_screen.detect_enemy_creep()

            if creep is not None:
                logging.debug('Цель обнаружена. Перехожу к атаке')
                self.game_screen.stop()
                self.attack(creep)
                return None

            time.sleep(1)

        logging.debug('Движение закончено, целей не обнаружено')
        if movement_length == config.MOVEMENT_LONG:  # если дошли до следущей башни
            self.current_tower = destination_tower_index  # то повышаем индекс

        self.game_screen.stop()
        time.sleep(3)
        self.move()  # движемся дальше


    def state_attacking_on_enter(self, creep):
        if self.game_screen.detect_death():
            self.die()
            return None

        if self.game_screen.get_health() < 30:
            self.rest()
            return None

        self.current_hp = self.game_screen.get_health()
        logging.debug('Атакую противника')
        self.game_screen.attack(creep)

        if random.randint(0, 5) == 3:
            logging.debug('Кости сложились удачно')
            self.game_screen.use_random_ability()
            time.sleep(0.5)


        for i in range(1, random.randint(2, 6)):
            time.sleep(0.5)
            health = self.game_screen.get_health()
            if health - self.current_hp > 10:
                logging.debug('Нас больно бьют, ретируемся')
                self.current_hp = health
                self.game_screen.run_away(self.map_screen.towers[0])
                break
            elif health - self.current_hp > 3:
                logging.debug('Нас бьют, но не сильно. Бэкпедалим')
                self.current_hp = health
                self.game_screen.backpedal(self.side)

        next_creep = self.game_screen.detect_enemy_creep()
        if next_creep is not None:
            self.attack(next_creep)
        else:
            logging.debug('Целей больше нет. Двигаюсь дальше')
            self.move()

    def state_dead_on_enter(self):
        logging.debug('Персонаж умер')
        self.current_tower = 0

        while self.game_screen.detect_death():
             time.sleep(1)

        time.sleep(2)
        logging.debug('Персонаж воскрес')
        self.current_hp = self.game_screen.get_health()
        self.move()

    def state_resting_on_enter(self):
        logging.debug('Мало здоровья, возвращаюсь на базу')
        self.game_screen.backpedal(self.side)
        self.game_screen.backpedal(self.side)

        self.game_screen.teleport()
        self.current_tower = 0

        time.sleep(15)
        self.current_hp - self.game_screen.get_health()
        self.move()
