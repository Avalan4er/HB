import logging
import state_machine

def main():
    bot = state_machine.BotController()
    bot.start_game()
    bot.switch_game_state()
    bot.select_game_mode()
    bot.select_hero()
    bot.start_game()
    bot.wait_for_match()
    bot.initiate_game()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s.%(msecs)03d: %(message)s', datefmt='%H:%M:%S')
    # logging.disable(logging.DEBUG) # uncomment to block debug log messages
    main()