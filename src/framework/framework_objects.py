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
