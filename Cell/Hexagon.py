class Hexagon:
    def __init__(self, index, center, pos):
        self.index = index
        self.center = center
        self.pos = pos
        self.unit = None

    def set_unit(self, unit):
        self.unit = unit

    def get_param(self):
        return self.index, self.center, self.pos