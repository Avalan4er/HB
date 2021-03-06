import os
import random
import time
from typing import Union

import pyperclip

import constants
import framework_objects
import vision_helpers
import windows_helpers
from config import Configuration
from logger import logger


class MainMenu(object):
    def __init__(self):
        self.emulator = windows_helpers.Emulator()
        self.pixel = windows_helpers.Pixel()

    def open_play_panel(self):
        logger.debug('Открываю вкладку ИГРАТЬ')
        self.emulator.click(125, 33)

    def open_vs_ai_panel(self):
        logger.debug('Открываю панель Против ИИ')
        self.emulator.click(61, 97)

    def open_heroes_selection(self):
        logger.debug('Открываю панель выбора героя')
        self.emulator.click(950, 200)

    def select_hero(self, hero_name):
        logger.debug('Выбираю героя ' + hero_name)
        self.emulator.click(950, 500)  # клик по герою для открытия меню выбора героя
        self.emulator.click(1420, 165)  # клик по полю ввода поиска героя

        time.sleep(0.5)
        pyperclip.copy(hero_name)  # копируем в буффер обмена имя героя
        time.sleep(0.5)
        self.emulator.paste()  # вставляем в поле поиска

        self.emulator.click(337, 267)  # кликаем по первому из найденных героев

    def select_ai_level(self, level):
        logger.debug('Устанавливаю сложность ботов' + level)
        levels = {'Easy': [81, 719],
                  'Medium': [245, 719],
                  'Hard': [435, 719]}

        level_coordinates = levels[level]
        self.emulator.click(level_coordinates[0], level_coordinates[1])

    def select_alies_ai_mode(self):
        logger.debug('Устанавливаю режим игры - Союзники-ИИ')
        self.emulator.click(185, 817)

    def start_game(self):
        logger.debug('Начинаем игру')
        self.emulator.click(1000, 1030)

    def wait_for_match(self):
        blue_color = (8, 88, 229)
        logger.debug('Ожидаю начала матча')

        while True:
            screenshot = self.pixel.screen()
            left_pixel = screenshot.getpixel((3, 285))
            right_pixel = screenshot.getpixel((1917, 285))

            if vision_helpers.is_color_in_range(left_pixel, blue_color, 10) or vision_helpers.is_color_in_range(
                    right_pixel, blue_color, 10):
                break

        logger.debug('Матч начался')

    def check_if_game_finished(self):
        screenshot = self.pixel.screen().crop((230, 145, 562, 232))
        return vision_helpers.screenshot_contains_template(screenshot, os.path.join(constants.IMAGES_PATH, 'mvp.png'))

    def check_if_afk_screen(self):
        screenshot = self.pixel.screen().crop((750, 590, 960, 660))
        return vision_helpers.screenshot_contains_template(screenshot,
                                                           os.path.join(constants.IMAGES_PATH, 'btn_return.png'))

    def press_return_button(self):
        self.emulator.click(855, 622)

    def press_skip_button(self):
        self.emulator.click(100, 1030)


class LoadingScreen(object):
    def __init__(self):
        self.pixel = windows_helpers.Pixel()

    def detect_map(self):
        logger.debug('Определяю карту')

        screenshot = self.pixel.screen()
        width = screenshot.width

        for hots_map in constants.MAPS:
            if vision_helpers.screenshot_contains_template(
                    screenshot.crop((0, 0, width, 300)),
                    os.path.join(constants.LOADING_SCREEN_TEMPLATES_PATH,
                                 hots_map.loading_screen_template_name + '.png')):
                logger.debug('Карта обнаружена: ' + hots_map.name)
                return hots_map

            logger.debug('Это не ' + hots_map.name)

        logger.debug('Карта не определена')

    def wait_for_loading(self):
        logger.debug('Ждем окончания загрузки')
        initial_pixel_color = self.pixel.color(900, 500)
        while initial_pixel_color == self.pixel.color(900, 500):
            time.sleep(1)
        logger.debug('Загрузка окончена')

    def detect_side(self):
        logger.debug('Определяю сторону')

        side = 'right_side'
        if self.pixel.matches(3, 285, (8, 88, 229), 10):
            side = 'left_side'

        logger.debug('Сторона определена: ' + side)
        return side


class GameScreen(object):
    def __init__(self):
        self.pixel = windows_helpers.Pixel()
        self.emulator = windows_helpers.Emulator()
        self.current_talent_idx = 0

    def wait_match_timer_start(self):
        while not self.pixel.matches(395, 1000, (62, 172, 23), 20):
            time.sleep(0.5)

    def get_units(self) -> [framework_objects.Unit]:
        screenshot = self.pixel.screen()
        return list(vision_helpers.detect_units(screenshot))

    def find_nearest_enemy(self, units: [framework_objects.Unit]) -> Union[None, framework_objects.Unit]:
        if units is not list:
            units = list(units)

        enemy_units = list(filter(lambda unit: unit.is_enemy, units))
        enemy_heroes = list(filter(lambda unit: unit.type.name == 'Герой', enemy_units))
        logger.debug(
            'Найдено ' + len(enemy_units).__str__() + ' противников. Из них героев: ' + len(enemy_heroes).__str__())
        if len(enemy_heroes) > 0:
            units_to_pick = enemy_heroes
        else:
            units_to_pick = enemy_units

        if len(units_to_pick) <= 0:
            return None

        player_position = framework_objects.Point(1920 / 2, 500)
        sorted_enemy_units = sorted(
            units_to_pick,
            key=lambda unit: windows_helpers.distance(player_position, unit.position))
        return sorted_enemy_units[0]

    def detect_death(self) -> bool:
        logger.debug('Определяю умер ли персонаж')

        screenshot = self.pixel.screen().crop((920, 770, 1000, 840))
        if vision_helpers.screenshot_contains_template(
                screenshot,
                os.path.join(constants.IMAGES_PATH, 'template_death.png')):
            logger.debug('Персонаж мертв')
            return True

        return False

    def move_to(self, x, y):
        self.emulator.click(x, y)
        self.emulator.right_click(int(1920 / 2) + random.randint(-10, 10), int(1080 / 2) + random.randint(-10, 10))
        self.emulator.hotkey('space')

    def attack(self, unit: framework_objects.Unit):
        self.emulator.mouse_move(unit.position.x + random.randint(-5, 5),
                                 unit.position.y + unit.type.height + random.randint(-5, 5))
        self.emulator.press_key('a')

    def stop(self):
        logger.debug('Останавливаемся')
        self.emulator.press_key('s')

    def use_random_ability(self):
        abilies_count = len(list(Configuration.ABILITIES_TO_SPAM)) - 1
        abiltity = Configuration.ABILITIES_TO_SPAM[random.randint(0, abilies_count)]
        logger.debug('Использую суперспособность ' + abiltity)
        self.emulator.use_ability(abiltity)

    def check_talents_avalible(self, screenshot):
        pixel_color = screenshot.getpixel((27, 692))
        match_color = (255, 246, 231)  # (231, 246, 255)
        if vision_helpers.is_color_in_range(pixel_color, match_color, 5):
            return True

        return False

    def learn_talent(self):
        talent_number = Configuration.TALENT_BUILD[self.current_talent_idx]
        self.current_talent_idx = self.current_talent_idx + 1

        logger.info('Учу талант № ' + talent_number.__str__())
        self.emulator.select_talent(talent_number)

    def backpedal(self, game_side):
        if game_side == 'left_side':
            self.emulator.fast_right_click(600, 500)
        else:
            self.emulator.fast_right_click(1300, 500)

        time.sleep(1)
        self.emulator.wait_random_delay()

    def run_away(self, home_tower):
        self.emulator.fast_click(home_tower.x, home_tower.y)

        for i in range(0, 5):
            self.emulator.fast_right_click(1920 / 2 + random.randint(-100, 100), 500 + random.randint(-100, 100))
            time.sleep(0.2)

        self.emulator.hotkey('space')

    def get_health(self):
        screenshot = self.pixel.screen().crop((200, 980, 430, 1030))
        health = vision_helpers.get_health(screenshot)
        return health

    def teleport(self):
        self.emulator.press_key('b')
        time.sleep(2)


class MapScreen(object):
    def __init__(self, game_map, game_side):
        self.pixel = windows_helpers.Pixel()
        self.map = game_map
        self.towers = game_map.stops
        if game_side == 'right_side':
            logger.debug('Играем за правых, реверсим башни')
            self.towers = list(reversed(game_map.stops))

        towers_count = len(self.towers)
        half_towers = (towers_count / 2).__int__()
        self.our_towers = self.towers[0:half_towers]
        self.enemy_towers = self.towers[half_towers:towers_count]

    def get_frontline_tower_index(self, screenshot):
        alive_tower_color = (49, 132, 255)

        for idx, tower in enumerate(reversed(self.our_towers)):
            pixel = screenshot.getpixel((tower.x, tower.y))
            if (alive_tower_color[0] - 5 < pixel[0] < alive_tower_color[0] + 5 and
                    alive_tower_color[1] - 5 < pixel[1] < alive_tower_color[1] + 5 and
                    alive_tower_color[2] - 5 < pixel[2] < alive_tower_color[2] + 5):
                return len(self.our_towers) - idx - 1

        return len(self.our_towers) - 1

    def check_enemy_tower_alive(self, screenshot, tower_index):
        map_background_color = (27, 16, 34)

        # it is ours tower
        if tower_index < len(self.our_towers):
            return False

        if tower_index >= len(self.towers):
            tower_index = len(self.towers) - 1

        # tower dead, pixel matches map background
        tower = self.towers[tower_index]
        pixel = screenshot.getpixel((tower.x, tower.y))
        if (map_background_color[0] - 10 < pixel[0] < map_background_color[0] + 10 and
                map_background_color[1] - 10 < pixel[1] < map_background_color[1] + 10 and
                map_background_color[2] - 10 < pixel[2] < map_background_color[2] + 10):
            return False

        return True


class EnemyCreep(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
