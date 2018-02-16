import os
import json
import codecs


class Configuration(object):
    BATTLE_NET_EXE_PATH = 'C:\Games\Heroes of the Storm\Heroes of the Storm.exe'  # Путь к Battle.net exe
    HERO_TO_LEVEL = "Гэндзи"  # Имя героя на русском
    AI_LEVEL = 'Easy'  # Сложность ботов ( Easy, Medium, Hard )

    MATCH_COUNTDOWN = 35  # 35

    MOVEMENT_LONG = 10  # длительность движения между башнями
    MOVEMENT_SHORT = 2  # длительность движения не доходя до следующей башни

    CONFIG_FILE_NAME = 'config.json'

    SEND_EMAIL_ON_MATCH_END = False
    EMAIL = 'test@test.com'
    SMTP_SERVER_ADDRESS = 'test.com'
    SMTP_SERVER_PORT = '3956'
    SMTP_LOGIN = 'test'
    SMTP_PASSWORD = 'test'


def read():
    if os.path.isfile(Configuration.CONFIG_FILE_NAME):
        config_file = codecs.open(Configuration.CONFIG_FILE_NAME, 'r', 'utf_8_sig')
        config_text = config_file.read()
        config_parser = json.loads(config_text)

        if 'BATTLE_NET_EXE_PATH' in config_parser:
            Configuration.BATTLE_NET_EXE_PATH = config_parser['BATTLE_NET_EXE_PATH']
        if 'HERO_TO_LEVEL' in config_parser:
            Configuration.HERO_TO_LEVEL = config_parser['HERO_TO_LEVEL']
        if 'AI_LEVEL' in config_parser:
            Configuration.AI_LEVEL = config_parser['AI_LEVEL']
        if 'SEND_EMAIL_ON_MATCH_END' in config_parser:
            Configuration.SEND_EMAIL_ON_MATCH_END = config_parser['SEND_EMAIL_ON_MATCH_END']
        if 'EMAIL' in config_parser:
            Configuration.EMAIL = config_parser['EMAIL']
        if 'SMTP_SERVER_ADDRESS' in config_parser:
            Configuration.SMTP_SERVER_ADDRESS = config_parser['SMTP_SERVER_ADDRESS']
        if 'SMTP_SERVER_PORT' in config_parser:
            Configuration.SMTP_SERVER_PORT = config_parser['SMTP_SERVER_PORT']
        if 'SMTP_LOGIN' in config_parser:
            Configuration.SMTP_LOGIN = config_parser['SMTP_LOGIN']
        if 'SMTP_PASSWORD' in config_parser:
            Configuration.SMTP_PASSWORD = config_parser['SMTP_PASSWORD']

