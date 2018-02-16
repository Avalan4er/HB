import logging
import random
import sys

import config
import constants
import state_machine


def setup_environment():
    sys.path.insert(0, '/bot')
    sys.path.insert(0, '/configuration')
    sys.path.insert(0, '/framework')


def main():
    application = state_machine.Application()
    application.run()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%H:%M:%S')
    # logging.disable(logging.DEBUG) # uncomment to block debug log messages
    random.seed(12331551)
    setup_environment()
    config.read()

    logging.debug('Базовая директория ресурсов: ' + constants.base_path)
    logging.debug('Путь до HOTS: ' + config.Configuration.BATTLE_NET_EXE_PATH)
    logging.debug('Уровень ИИ: ' + config.Configuration.AI_LEVEL)
    logging.debug('Прокачиваемый герой: ' + config.Configuration.HERO_TO_LEVEL)

    main()



    # test match exp save and send email

    # import match_result_helpers
    # import pyautogui

    # screenshot = pyautogui.grab()
    # path = match_result_helpers.save_match_result(screenshot)
    # match_result_helpers.send_match_result(path)



    # test playing

    # import state_machine
    # from objects import Map, MapStop

    # map = Map('WarheadJunction',
    #    [MapStop(1591, 865), MapStop(1619, 877), MapStop(1671, 867), MapStop(1763, 868), MapStop(1813, 878), MapStop(1841, 865)],
    #    'warhead_junction')
    # player = state_machine.Player('right_side', map)
    # player.wait_for_game_start()



    # test CV

    # import vision_helpers
    # from PIL import Image

    # screenshot = Image.open('')
    # coords = list(vision_helpers.find_all_enemy_creeps(screenshot))
    # print('t')
