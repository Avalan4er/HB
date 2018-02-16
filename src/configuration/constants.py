import os
import sys
import logging
from objects import Map, MapStop

WAIT_BEFORE_GAME_STARTS = 30

ABILITY_KEYS = ['q', 'w', 'e']

try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
    base_path = sys._MEIPASS
except Exception:
    base_path = os.path.abspath(".")

IMAGES_PATH = os.path.join(base_path, 'resources', 'img')
LOADING_SCREEN_TEMPLATES_PATH = os.path.join(IMAGES_PATH, 'loading_screen')
MAPS = [
    Map('Hanamura',
        [MapStop(1562, 900), MapStop(1580, 848), MapStop(1637, 829), MapStop(1744, 826), MapStop(1798, 850), MapStop(1818, 900)],
        'hanamura'),

    Map('TowersOfDoom', [MapStop(1641, 912), MapStop(1751, 912)], 'towers_of_doom'),

    Map('BraxisHoldout',
        [MapStop(1555, 844), MapStop(1577, 810), MapStop(1639, 778), MapStop(1736, 766), MapStop(1802, 802), MapStop(1823, 828)],
        'braxis_holdout'),

    Map('BlackheartsBay',
        [MapStop(1561, 935), MapStop(1587, 919), MapStop(1647, 872), MapStop(1746, 870), MapStop(1803, 916), MapStop(1831, 933)],
        'blackhearts_bay'),

    Map('BattlefieldOfEternity',
        [MapStop(1568, 946), MapStop(1589, 918), MapStop(1642, 879), MapStop(1740, 875), MapStop(1796, 906), MapStop(1823, 933)],
        'battlefield_of_eternity'),

    Map('SpiderQueen',
        [MapStop(1574, 849), MapStop(1589, 817), MapStop(1646, 816), MapStop(1735, 817), MapStop(1791, 817), MapStop(1806, 849)],
        'spider_queen'),

    Map('DragonShire',
        [MapStop(1563, 923), MapStop(1594, 927), MapStop(1645, 933), MapStop(1745, 933), MapStop(1797, 927), MapStop(1828, 923)],
        'dragon_shire'),

    Map('SkyTemple',
        [MapStop(1584, 801), MapStop(1615, 804), MapStop(1666, 831), MapStop(1761, 831), MapStop(1811, 804), MapStop(1842, 801)],
        'sky_temple'),

    Map('InfernalShrines',
        [MapStop(1556, 888), MapStop(1589, 888), MapStop(1643, 894), MapStop(1749, 893), MapStop(1804, 888), MapStop(1835, 888)],
        'infernal_shrines'),

    Map('HauntedMines',
        [MapStop(1575, 802), MapStop(1593, 779), MapStop(1641, 752), MapStop(1731, 752), MapStop(1780, 777), MapStop(1797, 802)],
        'haunted_mines'),

    Map('CursedHollow',
        [MapStop(1549, 909), MapStop(1581, 902), MapStop(1634, 904), MapStop(1739, 898), MapStop(1790, 902), MapStop(1822, 891)],
        'cursed_hollow'),

    Map('GardenOfTerror',
        [MapStop(1552, 909), MapStop(1584, 904), MapStop(1641, 909), MapStop(1751, 899), MapStop(1807, 905), MapStop(1839, 896)],
        'garden_of_terror'),

    Map('WarheadJunction',
        [MapStop(1591, 865), MapStop(1619, 877), MapStop(1671, 867), MapStop(1763, 868), MapStop(1813, 878), MapStop(1841, 865)],
        'warhead_junction'),

    Map('VolskayaFoundry',
        [MapStop(1561, 911), MapStop(1599, 913), MapStop(1651, 902), MapStop(1740, 902), MapStop(1792, 912), MapStop(1831, 911)],
        'volskaya_foundry'),
]
