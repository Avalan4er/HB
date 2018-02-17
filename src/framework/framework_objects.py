from enum import Enum

from PIL import Image

import config_objects
import vision_helpers


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class UnitType(object):
    def __init__(self):
        self.height = 0
        self.name = ''

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class CreepUnitType(UnitType):
    def __init__(self):
        super().__init__()

        self.height = 100
        self.name = 'Крип'


class HeroUnitType(UnitType):
    def __init__(self):
        super().__init__()

        self.height = 140
        self.name = 'Герой'


class TowerUnitType(UnitType):
    def __init__(self):
        super().__init__()

        self.height = 150
        self.name = 'Башня'


class GatesUnitType(UnitType):
    def __init__(self):
        super().__init__()

        self.height = 90
        self.name = 'Ворота'


class Unit(object):
    def __init__(self, position: Point):
        self.position = position
        self.type = CreepUnitType()
        self.is_enemy = False

    def __str__(self) -> str:
        return str(self.__dict__)

    def __eq__(self, other) -> bool:
        return self.__dict__ == other.__dict__


class Player(object):
    def __init__(self):
        self.position = Point(0, 0)
        self.health = 0

    def update_position(self, screenshot: Image):
        coords = vision_helpers.map_get_player_coords(screenshot)

        if coords is not None:
            self.position = coords

        return coords

    def update_health(self, screenshot: Image):
        health = vision_helpers.get_health(screenshot)
        delta = abs(health - self.health)
        self.health = health
        return delta


class Fort(object):
    def __init__(self, position: Point, is_enemy: bool):
        self.is_alive = True
        self.position = position
        self.is_enemy = is_enemy


class MapSides(Enum):
    LEFT = 0,
    RIGHT = 1


class Map(object):
    def __init__(self, side: MapSides, map_config: config_objects.Map):
        self.side = side

        stops = list(map_config.stops) if side == MapSides.LEFT else list(reversed(map_config.stops))
        stops_count = len(stops)

        line = []
        for i, stop in enumerate(stops):
            is_enemy_fort = i >= (stops_count / 2).__int__()
            line.append(Fort(Point(stop.x, stop.y), is_enemy_fort))

        self.lines = [line]

    def fetch_dead_forts(self, screenshot: Image):
        map_background_color = (27, 16, 34)

        for line in self.lines:
            for fort in line:
                if not fort.is_alive: continue

                pixel = screenshot.getpixel((fort.position.x, fort.position.y))

                if vision_helpers.is_color_in_range(pixel, map_background_color, 10):
                    fort.is_alive = False
