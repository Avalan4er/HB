import logging
import time
import constants
import windows_helpers
import pyperclip

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
            time.sleep(1)
            loading_started = self.pixel.matches(900, 500, (10, 10, 10), 10)
            logging.debug('Проверка начала игры: ' + loading_started.__str__())

        time.sleep(2)
        logging.debug('Матч начался')


class LoadingScreen(object):
    def __init__(self):
        self.pixel = windows_helpers.Pixel()

    def detect_map(self):
        color_converter = windows_helpers.Color()
        logging.debug('Определяю карту')
        for map_name, color in constants.MAP_COLORS.items():
            if self.pixel.search(380, 380, 10, 10, color_converter.to_rgb(color), 1):
                logging.debug('Ката определена: ' + map_name)
                return map_name
            else:
                logging.debug('Это не ' + map_name)
        logging.debug('Карта не определена')

    def wait_for_loading(self):
        logging.debug('Ждем окончания загрузки')
        initial_pixel_color = self.pixel.color(900, 500)
        while initial_pixel_color == self.pixel.color(900, 500):
            time.sleep(1)
        logging.debug('Загрузка окончена')


class GameScreen(object):
    def __init__(self):
        self.pixel = windows_helpers.Pixel()

    def detect_side(self):
        logging.debug('Определяю сторону')

        side = 'right_side'
        if self.pixel.search(7, 161, 11, 217, (79, 191, 251), 10):
            side = 'left_side'

        logging.debug('Сторона определена: ' + side)
        return side
