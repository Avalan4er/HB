import logging
import time
import windows_helpers
import pyperclip
import constants
import vision_helpers
import os


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
        while not loading_started:
            time.sleep(0.5)
            loading_started = self.pixel.matches(900, 500, (10, 10, 10), 10)
            logging.debug('Проверка начала игры: ' + loading_started.__str__())

        time.sleep(2)
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
                    os.path.join(constants.LOADING_SCREEN_TEMPLATES_PATH, hots_map.loading_screen_template_name + '.png')):
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

    def detect_enemy_creep(self):
        logging.debug('Ищу крипа')
        screenshot = self.pixel.screen()

        creep_coords = vision_helpers.find_closest_enemy_creep(screenshot)

        if creep_coords is not None:
            logging.debug('Крип найден')
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
        self.emulator.right_click(creep.x + 30, creep.y + 50)

class EnemyCreep(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
