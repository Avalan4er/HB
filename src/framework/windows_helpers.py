import math
import os
import random
import subprocess
import time

import psutil
import pyautogui
from PIL import Image

import config
import constants
import framework_objects
import vision_helpers
from logger import logger


class Color(object):
    def to_rgb(self, hex_color: int) -> (float, float, float):
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


class Emulator(object):
    def __init__(self):
        random.seed(42142151)

    # mouse
    def click(self, x: int, y: int):
        pyautogui.moveTo(x, y, random.random(), pyautogui.easeOutQuad)
        pyautogui.click()

    def fast_click(self, x: int, y: int):
        pyautogui.click(x, y)

    def right_click(self, x: int, y: int):
        pyautogui.moveTo(x, y, random.random(), pyautogui.easeOutQuad)
        pyautogui.rightClick()

    def fast_right_click(self, x: int, y: int):
        pyautogui.rightClick(x, y)

    def mouse_move(self, x: int, y: int):
        pyautogui.moveTo(x, y, random.random(), pyautogui.easeOutQuad)

    # keyboard
    def write(self, word: str):
        pyautogui.typewrite(word, random.random())

    def press_key(self, keys):
        pyautogui.press(keys, interval=random.random())

    def paste(self):
        pyautogui.hotkey('ctrl', 'v')

    def hotkey(self, key: str):
        pyautogui.hotkey(key)

    def select_talent(self, talent_number: int):
        pyautogui.keyDown('ctrl')
        time.sleep(0.2)
        pyautogui.press(talent_number.__str__())
        pyautogui.keyUp('ctrl')

    def use_ability(self, ability_key: str):
        pyautogui.keyDown(ability_key)
        time.sleep(0.2)
        pyautogui.keyUp(ability_key)

    # random
    def wait_random_delay(self):
        delay = 1.0 + random.random() * 4.0
        time.sleep(delay)


class Pixel(object):
    def search(self, x: int, y: int, width: int, height: int, rgb_color: (float, float, float), tolerance=0) -> (int, int):
        for i in range(x, x + width):
            for k in range(y, y + height):
                if pyautogui.pixelMatchesColor(i, k, rgb_color, tolerance):
                    return i, k
        return None

    def matches(self, x: int, y: int, rgb_color: (float, float, float), tolerance=0) -> bool:
        return pyautogui.pixelMatchesColor(x, y, rgb_color, tolerance)

    def color(self, x: int, y: int) -> (float, float, float):
        return pyautogui.pixel(x, y)

    def screen(self) -> Image:
        return pyautogui.grab()


def is_hots_running():
    """
    Проверяет, запущен ли HOTS
    :return: True если HOTS запущен
    """
    for pid in psutil.pids():
        process = psutil.Process(pid)
        if 'Heroes' in process.name():
            return True

    return False


def distance(p1: framework_objects.Point, p2: framework_objects.Point) -> float:
    return math.sqrt(((p1.x - p2.x) ** 2) + ((p1.y - p2.y) ** 2))


def run_hots():
    """
    Запускает Heroes of the storm
    """
    if is_hots_running():
        logger.debug('HOTS уже запущен. Переключаюсь на него')
        hots_window = pyautogui.getWindow('Heroes of the Storm')
        hots_window.minimize()
        hots_window.restore()
        time.sleep(1)

    else:
        logger.debug('Запускаем HOTS')
        # Start Battle.Net client
        subprocess.call([config.Configuration.BATTLE_NET_EXE_PATH])
        time.sleep(5)

        # Maximize Battle.Net client
        battle_net_window = pyautogui.getWindow('Blizzard Battle.net')
        battle_net_window.set_position(0, 0, 800, 600)
        time.sleep(1)

        battle_net_window.maximize()
        time.sleep(1)

        # Button fragments to find
        default_btn = os.path.join(constants.IMAGES_PATH, 'play_btn_default.png')

        # Search for button on the screen
        screenshot = Pixel().screen()
        btn_locations = vision_helpers.screenshot_find_templates(screenshot, default_btn)
        if len(btn_locations) > 0:  # button not found (smth goes terribly wrong)
            raise Exception('Could not find game on screen. Is the game visible?')
        Emulator().click(btn_locations[0].x, btn_locations[0].y)

        logger.debug('HOTS запускается, жду ' + constants.WAIT_BEFORE_GAME_STARTS.__str__() + ' секунд')
        time.sleep(constants.WAIT_BEFORE_GAME_STARTS)
