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

        logging.debug('минута прошла')


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

    def state_selecting_game_mode_on_enter(self):
        self.hots_menu.select_alies_ai_mode()
        self.emulator.wait_random_delay()
        self.hots_menu.select_ai_level(config.AI_LEVEL)
        self.emulator.wait_random_delay()

    def state_selecting_hero_on_enter(self):
        self.hots_menu.select_hero(config.HERO_TO_LEVEL)
        self.emulator.wait_random_delay()
        self.hots_menu.start_game()

    def state_waiting_match_on_enter(self):
        self.hots_menu.wait_for_match()
        time.sleep(2)

    def state_loading_on_enter(self):
        logging.debug('Грузимся в игру')
        self.game_map = self.hots_loading_screen.detect_map()
        self.game_side = self.hots_loading_screen.detect_side()
        self.hots_loading_screen.wait_for_loading()

    def state_initiating_game_on_enter(self):
        logging.debug('Матч начался!')

    def state_playing_on_enter(self):
        game_finished = False
        current_tower_idx = 0
        is_moving = False
        current_time = datetime.now().timestamp()

        towers = self.game_map.stops
        if self.game_side == 'right_side':
            logging.debug('Играем за правых, реверсим башни')
            towers = list(reversed(self.game_map.stops))

        while not game_finished:
            # detecting death
            if self.hots_game_screen.detect_death():
                time.sleep(1)
                current_tower_idx = 0
                continue

            # searching for target to attack
            creep = self.hots_game_screen.detect_enemy_creep()

            # moving or attacking creep
            if creep is not None:  # found creep - attack
                logging.debug('Атакуем крипа')
                self.hots_game_screen.attack(creep)
                time.sleep(3)
            else:
                logging.debug('Двигаемся - ' + is_moving.__str__())
                logging.debug('Длительность движения - ' + (datetime.now().timestamp() - current_time).__str__())

                if not is_moving or (is_moving and datetime.now().timestamp() - current_time > 10):
                    current_tower_idx += 1
                    if current_tower_idx == len(towers):
                        current_tower_idx = 0
                    next_tower = towers[current_tower_idx]
                    self.hots_game_screen.move_to(next_tower.x, next_tower.y)

                    is_moving = True
                    current_time = datetime.now().timestamp()
                    logging.debug('Начинаем движение к башне № ' + current_tower_idx.__str__())
                else:
                    logging.debug('Продолжаем ранее начатое движение')
                    time.sleep(1)

