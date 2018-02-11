import logging
import time
import windows_helpers
import pyperclip
import constants
import vision_helpers
import os
import math


class MainMenu(object):
    def __init__(self):
        self.emulator = windows_helpers.Emulator()
        self.pixel = windows_helpers.Pixel()

    def open_play_panel(self):
        logging.debug('Открываю вкладку ИГРАТЬ')
        self.emulator.click(125, 33)

    def open_vs_ai_panel(self):
        logging.debug('Открываю панель Против ИИ')
        self.emulator.click(61, 97)

    def open_heroes_selection(self):
        logging.debug('Открываю панель выбора героя')
        self.emulator.click(950, 200)

    def select_hero(self, hero_name):
        logging.debug('Выбираю героя ' + hero_name)
        self.emulator.click(950, 500)  # клик по герою для открытия меню выбора героя
        self.emulator.click(1420, 165)  # клик по полю ввода поиска героя

        time.sleep(0.5)
        pyperclip.copy(hero_name)  # копируем в буффер обмена имя героя
        time.sleep(0.5)
        self.emulator.paste()  # вставляем в поле поиска

        self.emulator.click(337, 267)  # кликаем по первому из найденных героев

    def select_ai_level(self, level):
        logging.debug('Устанавливаю сложность ботов' + level)
        levels = {'Easy': [81, 719],
                  'Medium': [245, 719],
                  'Hard': [435, 719]}

        level_coordinates = levels[level]
        self.emulator.click(level_coordinates[0], level_coordinates[1])

    def select_alies_ai_mode(self):
        logging.debug('Устанавливаю режим игры - Союзники-ИИ')
        self.emulator.click(185, 817)

    def start_game(self):
        logging.debug('Начинаем игру')
        self.emulator.click(1000, 1030)

    def wait_for_match(self):
        logging.debug('Ожидаю начала матча')
        loading_started = False
        loading_finished = False

        while not loading_started:
            time.sleep(0.5)
            loading_started = self.pixel.matches(900, 500, (10, 10, 10), 10)
            logging.debug('Проверка начала игры: ' + loading_started.__str__())

            while loading_started and not loading_finished:
                time.sleep(0.5)
                loading_finished = not self.pixel.matches(900, 500, (10, 10, 10), 10)
                logging.debug('Проверка начала игры: ' + loading_finished.__str__())

        time.sleep(1)
        logging.debug('Матч начался')


class LoadingScreen(object):
    def __init__(self):
        self.pixel = windows_helpers.Pixel()

    def detect_map(self):
        logging.debug('Определяю карту')

        screenshot = self.pixel.screen()
        width = screenshot.width

        for hots_map in constants.MAPS:
            if vision_helpers.screenshot_contains_template(
                    screenshot.crop((0, 0, width, 300)),
                    os.path.join(constants.LOADING_SCREEN_TEMPLATES_PATH,
                                 hots_map.loading_screen_template_name + '.png')):
                logging.debug('Карта обнаружена: ' + hots_map.name)
                return hots_map

        logging.debug('Карта не определена')

    def wait_for_loading(self):
        logging.debug('Ждем окончания загрузки')
        initial_pixel_color = self.pixel.color(900, 500)
        while initial_pixel_color == self.pixel.color(900, 500):
            time.sleep(1)
        logging.debug('Загрузка окончена')

    def detect_side(self):
        logging.debug('Определяю сторону')

        side = 'right_side'
        if self.pixel.matches(3, 285, (8, 88, 229), 10):
            side = 'left_side'

        logging.debug('Сторона определена: ' + side)
        return side


class GameScreen(object):
    def __init__(self):
        self.pixel = windows_helpers.Pixel()
        self.emulator = windows_helpers.Emulator()

    def wait_match_timer_start(self):
        while not self.pixel.matches(395, 1000, (62, 172, 23), 1):
            time.sleep(0.5)

    def detect_enemy_creep(self):
        screenshot = self.pixel.screen()
        creep_coords = None

        enemy_creeps = list(vision_helpers.find_all_enemy_creeps(screenshot))
        if enemy_creeps is not None and len(enemy_creeps) > 0:
            player_coords = (1920 / 2, 500)
            creeps = sorted(
                enemy_creeps,
                key=lambda creep: math.hypot(creep[0] - player_coords[0], creep[1] - player_coords[1]))
            creep_coords = creeps[0]

        if creep_coords is not None:
            return EnemyCreep(creep_coords[0], creep_coords[1])

        logging.debug('Крип не найден')

    def detect_death(self):
        logging.debug('Определяю умер ли персонаж')

        screenshot = self.pixel.screen().crop((920, 770, 1000, 840))
        if vision_helpers.screenshot_contains_template(
                screenshot,
                os.path.join(constants.IMAGES_PATH, 'template_death.png')):
            logging.debug('Персонаж мертв')
            return True

        return False

    def move_to(self, x, y):
        logging.debug('Двигаюсь')
        self.emulator.click(x, y)
        self.emulator.right_click(1920 / 2, 1080 / 2)
        self.emulator.hotkey('space')

    def attack(self, creep):
        logging.debug('Атакую крипа')
        self.emulator.mouse_move(creep.x + 30, creep.y + 50)
        self.emulator.press_key('a')

    def stop(self):
        logging.debug('Останавливаемся')
        self.emulator.press_key('s')

    def backpedal(self, game_side):
        if game_side == 'left_side':
            self.emulator.right_click(600, 500)
        else:
            self.emulator.right_click(1300, 500)

        time.sleep(1)
        self.emulator.wait_random_delay()

    def get_health(self):
        screenshot = self.pixel.screen().crop((200, 980, 430, 1030))
        health = vision_helpers.get_health(screenshot)
        logging.debug('Текущее здоровье - ' + health.__str__())
        return health

    def teleport(self):
        self.emulator.press_key('b')


class MapScreen(object):
    def __init__(self, game_map, game_side):
        self.pixel = windows_helpers.Pixel()
        self.map = game_map
        self.towers = game_map.stops
        if game_side == 'right_side':
            logging.debug('Играем за правых, реверсим башни')
            self.towers = list(reversed(game_map.stops))

    def get_frontline_tower(self):
        for i, tower in enumerate(list(self.towers)):
            if self.pixel.matches(tower.x, tower.y, (49, 132, 255), 1):
                return i, tower

        return 0, self.towers[0]

    def check_enemy_tower_alive(self, tower):
        # it is ours tower
        if self.pixel.matches(tower.x, tower.y, (49, 132, 255), 2):
            return False

        # tower dead, pixel matches map background
        if self.pixel.matches(tower.x, tower.y, (27, 16, 34), 5):
            return False

        return True


class EnemyCreep(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
