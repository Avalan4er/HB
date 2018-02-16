import logging
import state_machine
import random
import sys
import config


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

    #main()

    # import state_machine
    # from objects import Map, MapStop

    # map = Map('WarheadJunction',
    #    [MapStop(1591, 865), MapStop(1619, 877), MapStop(1671, 867), MapStop(1763, 868), MapStop(1813, 878), MapStop(1841, 865)],
    #    'warhead_junction')
    # player = state_machine.Player('right_side', map)
    # player.wait_for_game_start()

    # from PIL import Image
    # import hots
    # from objects import Map, MapStop
    # import vision_helpers

    # current_map =  Map('GardenOfTerror',
    #    [MapStop(1552, 909), MapStop(1584, 904), MapStop(1641, 909), MapStop(1751, 899), MapStop(1807, 905), MapStop(1839, 896)],
    #   'garden_of_terror')


    import vision_helpers
    from PIL import Image

    screenshot = Image.open('creeps1.png')
    coords = list(vision_helpers.find_all_enemy_creeps(screenshot))
    print('t')
