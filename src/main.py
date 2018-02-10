import logging
import state_machine


def main():
    application = state_machine.Application()
    application.run()

    game = state_machine.Game()
    game.switch_game_state()
    game.select_game_mode()
    game.select_hero()
    game.start_game()
    game.wait_for_match()
    game.initiate()
    game.play()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%H:%M:%S')
    # logging.disable(logging.DEBUG) # uncomment to block debug log messages
    main()

    import vision_helpers
    from PIL import Image
    import os

    screenshot_path = 'testimage.png'
    template_path = os.path.join('resources', 'img', 'loading_screen', 'dragon_shire.png')
    img = Image.open(screenshot_path)
    vision_helpers.screenshot_contains_template(img, template_path)
