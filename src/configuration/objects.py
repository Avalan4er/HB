class Map(object):
    def __init__(self, name, stops, loading_screen_template_name):
        self.name = name
        self.stops = stops
        self.loading_screen_template_name = loading_screen_template_name


class MapStop(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y