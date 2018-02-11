import logging
import state_machine


def main():
    application = state_machine.Application()
    application.run()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%H:%M:%S')
    # logging.disable(logging.DEBUG) # uncomment to block debug log messages
    main()



    #import state_machine
    #from objects import Map, MapStop

    #map = Map('InfernalShrines',
    #    [MapStop(1556, 888), MapStop(1589, 888), MapStop(1643, 894), MapStop(1749, 893), MapStop(1804, 888), MapStop(1835, 888)],
    #    'infernal_shrines')
    #player = state_machine.Player('left_side', map)
    #player.wait_for_game_start()



    #from PIL import Image
    #import hots
    #from objects import Map, MapStop
    #import vision_helpers

    #current_map =  Map('GardenOfTerror',
    #    [MapStop(1552, 909), MapStop(1584, 904), MapStop(1641, 909), MapStop(1751, 899), MapStop(1807, 905), MapStop(1839, 896)],
    #   'garden_of_terror')

    #screenshot = Image.open('creeps.png')
    #coords = list(vision_helpers.find_all_enemy_creeps(screenshot))
    #print('t')