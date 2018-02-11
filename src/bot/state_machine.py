from transitions import Machine, State
import windows_helpers
import time
import logging
import hots
import config
import constants
import random
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
            State(name='playing', on_enter=['state_playing_on_enter'])
        ]
        transitions = [
            {'trigger': 'switch_game_state', 'source': 'idle', 'dest': 'main_menu'},
            {'trigger': 'select_game_mode', 'source': 'main_menu', 'dest': 'selecting_game_mode'},
            {'trigger': 'select_hero', 'source': 'selecting_game_mode', 'dest': 'selecting_hero'},
            {'trigger': 'start_game', 'source': 'selecting_hero', 'dest': 'waiting_match'},
            {'trigger': 'wait_for_match', 'source': 'waiting_match', 'dest': 'loading'},
            {'trigger': 'initiate', 'source': 'loading', 'dest': 'initiating_game'},
            {'trigger': 'play', 'source': 'initiating_game', 'dest': 'playing'},
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
        self.hots_menu.start_game()
        self.start_game()

    def state_waiting_match_on_enter(self):
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
        player.wait_for_game_start()



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

            {'trigger': 'die', 'source': 'attacking', 'dest': 'dead'},
            {'trigger': 'die', 'source': 'moving', 'dest': 'dead'},

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
        time.sleep(35)

        logging.debug('Иду воевать!')
        self.current_tower, frontline_tower = self.map_screen.get_frontline_tower()
        self.move(frontline_tower.x, frontline_tower.y)

    def state_moving_on_enter(self, x=0.0, y=0.0):
        if x == 0.0 or y == 0.0:
            logging.debug('Что то пошло не так. Аргументы для движения - нулевые')
            return None

        if self.game_screen.detect_death():
            self.die()
            return None

        if self.game_screen.get_health() < 30:
            self.rest()
            return None

        movement_start_time = datetime.now().timestamp()

        logging.debug('Выдвигаюсь к башне №' + self.current_tower.__str__())
        h_offset = 50 if self.side == 'left_side' else -50
        self.game_screen.move_to(x + h_offset, y + 10)

        while True:
            if datetime.now().timestamp() - movement_start_time > 10:  # move complete, gonna move to next tower
                self.move_to_next_tower()
                break
            else:  # still moving and searching for enemies
                time.sleep(1)

                creep = self.game_screen.detect_enemy_creep()

                if creep is not None:
                    logging.debug('Нашел дичь')
                    self.attack(creep)
                    break

    def state_attacking_on_enter(self, creep):
        if self.game_screen.detect_death():
            self.die()
            return None

        if self.game_screen.get_health() < 30:
            self.rest()
            return None

        logging.debug('Атакую противника')
        self.game_screen.stop()
        self.game_screen.attack(creep)
        time.sleep(2)

        health = self.game_screen.get_health()
        if health < self.current_hp:
            logging.debug('Нас бьют. отступаем')
            self.current_hp = health
            self.game_screen.backpedal(self.side)

        next_creep = self.game_screen.detect_enemy_creep()
        if next_creep is not None:
            self.attack(next_creep)
        else:
            logging.debug('Целей больше нет. Двигаюсь дальше')
            self.move_to_next_tower()

    def state_dead_on_enter(self):
        logging.debug('Поездочка...')
        self.current_tower = 0

        while self.game_screen.detect_death():
            time.sleep(1)

        time.sleep(2)
        logging.debug('Воскрес')
        self.move_to_next_tower()

    def state_resting_on_enter(self):
        logging.debug('Поплохело, иду отдыхать')
        self.current_tower, frontline_tower = self.map_screen.get_frontline_tower()
        self.game_screen.move_to(frontline_tower.x, frontline_tower.y)

        self.game_screen.teleport()
        time.sleep(15)
        self.move_to_next_tower()

    def move_to_next_tower(self):
        self.current_tower += 1

        logging.debug('Выдвигаюсь к следующей башне №' + self.current_tower.__str__())
        if self.current_tower == len(self.map_screen.towers):
            idx, t = self.map_screen.get_frontline_tower()
            self.current_tower = idx

        tower = self.map_screen.towers[self.current_tower]
        if not self.map_screen.check_enemy_tower_alive(tower):
            logging.debug('Это либо наша башня либо уничтоженная башня врага')
            self.move(
                tower.x,
                tower.y)
        else:
            logging.debug('Это живая башня врага. Не пойду туда')

            h_offset = 50 if self.side == 'left_side' else -50
            idx, tower = self.map_screen.get_frontline_tower()
            logging.debug('Фронтлайновая башня это башня №' + idx.__str__())

            self.current_tower = idx
            self.move(
                tower.x + h_offset,
                tower.y)

