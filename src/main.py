import logging
import state_machine


def main():
    application = state_machine.Application()
    application.run()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%H:%M:%S')
    # logging.disable(logging.DEBUG) # uncomment to block debug log messages
    # main()



    import state_machine
    from objects import Map, MapStop

    map = Map('GardenOfTerror',
        [MapStop(1552, 909), MapStop(1584, 904), MapStop(1641, 909), MapStop(1751, 899), MapStop(1807, 905), MapStop(1839, 896)],
        'garden_of_terror')
    player = state_machine.Player('left_side', map)
    player.wait_for_game_start()



    #from PIL import Image
    #import hots
    #from objects import Map, MapStop

    #current_map =  Map('GardenOfTerror',
    #    [MapStop(1552, 909), MapStop(1584, 904), MapStop(1641, 909), MapStop(1751, 899), MapStop(1807, 905), MapStop(1839, 896)],
    #    'garden_of_terror')

    #screenshot = Image.open('all_towers_alive.png')
    #map_screen = hots.MapScreen(current_map, 'left_side')
    #is_alive = map_screen.check_enemy_tower_alive(screenshot, 3)
    #rontline_idx = map_screen.get_frontline_tower_index(screenshot)
    #print('t')