from transitions import Machine, State
import windows_helpers
import time
import logging
import hots
import config
import constants


class BotController(object):
    states = [
        State(name='not_running'),
        State(name='starting', on_enter=['state_starting_on_enter']),
        State(name='main_menu', on_enter=['state_main_menu_on_enter']),
        State(name='selecting_game_mode', on_enter=['state_selecting_game_mode_on_enter']),
        State(name='selecting_hero', on_enter=['state_selecting_hero_on_enter']),
        State(name='waiting_match', on_enter=['state_waiting_match_on_enter']),
        State(name='loading', on_enter=['state_loading_on_enter']),
        State(name='initiating_game', on_enter=['state_initiating_game_on_enter']),
        State(name='playing', on_enter=['state_playing_on_enter'])
    ]
    transitions = [
        {'trigger': 'start_game', 'source': 'not_running', 'dest': 'starting'},
        {'trigger': 'switch_game_state', 'source': 'starting', 'dest': 'main_menu'},
        {'trigger': 'select_game_mode', 'source': 'main_menu', 'dest': 'selecting_game_mode'},
        {'trigger': 'select_hero', 'source': 'selecting_game_mode', 'dest': 'selecting_hero'},
        {'trigger': 'start_game', 'source': 'selecting_hero', 'dest': 'waiting_match'},
        {'trigger': 'wait_for_match', 'source': 'waiting_match', 'dest': 'loading'},
        {'trigger': 'initiate_game', 'source': 'loading', 'dest': 'initiating_game'},
        {'trigger': 'play_game', 'source': 'initiating_game', 'dest': 'playing'},
    ]

    def __init__(self):
        self.hots_menu = hots.MainMenu()
        self.hots_loading_screen = hots.LoadingScreen()
        self.hots_game_screen = hots.GameScreen()

        self.game_map = 'none'
        self.game_side = 'none'

        self.machine = Machine(model=self, states=BotController.states, transitions=BotController.transitions,
                               initial='not_running', queued=True)

    def state_starting_on_enter(self):
        logging.debug('Запускаю HOTS')
        windows_helpers.run_hots()

        logging.debug('HOTS запускается, жду ' + constants.WAIT_BEFORE_GAME_STARTS.__str__() + ' секунд')
        time.sleep(constants.WAIT_BEFORE_GAME_STARTS)

        logging.debug('минута прошла')

    def state_main_menu_on_enter(self):
        self.hots_menu.open_play_panel()
        time.sleep(1)
        self.hots_menu.open_vs_ai_panel()
        time.sleep(1)

    def state_selecting_game_mode_on_enter(self):
        self.hots_menu.select_alies_ai_mode()
        time.sleep(1)
        self.hots_menu.select_ai_level(config.AI_LEVEL)
        time.sleep(1)

    def state_selecting_hero_on_enter(self):
        self.hots_menu.select_hero(config.HERO_TO_LEVEL)
        self.hots_menu.start_game()

    def state_waiting_match_on_enter(self):
        self.hots_menu.wait_for_match()
        time.sleep(1)

    def state_loading_on_enter(self):
        logging.debug('Грузимся в игру')
        self.game_map = self.hots_loading_screen.detect_map()
        self.hots_loading_screen.wait_for_loading()
        self.game_side = self.hots_game_screen.detect_side()

    def state_initiating_game_on_enter(self):
        logging.debug('Инициализируем игру')

    def state_playing_on_enter(self):
        logging.debug('Играем')