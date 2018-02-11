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

    map = Map('DragonShire',
       [MapStop(1563, 923), MapStop(1594, 927), MapStop(1645, 933), MapStop(1745, 933), MapStop(1797, 927), MapStop(1828, 923)],
       'dragon_shire')
    player = state_machine.Player('left_side', map)
    player.wait_for_game_start()



    #from PIL import Image
    #import vision_helpers
    #screenshot = Image.open('testimage.png')
    #vision_helpers.get_health(screenshot)