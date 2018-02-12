import pyautogui
import subprocess
import os
import time
import config
import random


class Color(object):
    def to_rgb(self, hex):
        return tuple(int(hex[i:i + 2], 16) for i in (0, 2, 4))


class Emulator(object):
    def __init__(self):
        random.seed(42)

    # mouse
    def click(self, x, y):
        pyautogui.moveTo(x, y, random.random(), pyautogui.easeOutQuad)
        pyautogui.click()

    def fast_click(self, x, y):
        pyautogui.click(x, y)

    def right_click(self, x, y):
        pyautogui.moveTo(x, y, random.random(), pyautogui.easeOutQuad)
        pyautogui.rightClick()

    def fast_right_click(self, x, y):
        pyautogui.rightClick(x, y)

    def mouse_move(self, x, y):
        pyautogui.moveTo(x, y, random.random(), pyautogui.easeOutQuad)

    # keyboard
    def write(self, word):
        pyautogui.typewrite(word, random.random())

    def press_key(self, keys):
        pyautogui.press(keys, interval=random.random())

    def paste(self):
        pyautogui.hotkey('ctrl', 'v')

    def hotkey(self, key):
        pyautogui.hotkey(key)

    def select_talent(self, talent_number):
        pyautogui.keyDown('ctrl')
        time.sleep(0.2)
        pyautogui.press(talent_number.__str__())
        pyautogui.keyUp('ctrl')

    def use_ability(self, ability_key):
        pyautogui.keyDown(ability_key)
        time.sleep(0.2)
        pyautogui.keyUp(ability_key)

    # random
    def wait_random_delay(self):
        delay = 1.0 + random.random() * 4.0
        time.sleep(delay)





class Pixel(object):
    def search(self, x, y, width, height, rgb_color, tolerance=0):
        for i in range(x, x + width):
            for k in range(y, y + height):
                if pyautogui.pixelMatchesColor(i, k, rgb_color, tolerance):
                    return i, k
        return None

    def matches(self, x, y, rgb_color, tolerance=0):
        return pyautogui.pixelMatchesColor(x, y, rgb_color, tolerance)

    def color(self, x, y):
        return pyautogui.pixel(x, y)

    def screen(self):
        return pyautogui.grab()


def get_resource_path(filename):
    return os.path.join('resources', 'img', filename)


def run_hots():
    # Start Battle.Net client
    subprocess.call([config.BATTLE_NET_EXE_PATH])
    time.sleep(5)

    # Maximize Battle.Net client
    battle_net_window = pyautogui.getWindow('Blizzard Battle.net')
    battle_net_window.set_position(0, 0, 800, 600)
    battle_net_window.maximize()

    # Button fragments to find
    default_btn = get_resource_path('play_btn_default.png')
    highlighted_btn = get_resource_path('play_btn_highlighted.png')

    # Search for button on the screen
    btn_location = pyautogui.locateOnScreen(default_btn)
    if btn_location is None:  # if button not found then search for highlighted button
        btn_location = pyautogui.locateOnScreen(highlighted_btn)
    if btn_location is None:  # button not found (smth goes terribly wrong)
        raise Exception('Could not find game on screen. Is the game visible?')
    Emulator().click(btn_location[0], btn_location[1])
