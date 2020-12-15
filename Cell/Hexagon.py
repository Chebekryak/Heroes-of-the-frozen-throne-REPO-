from Cell.Tiles import BaseTile


class Hexagon:
    def __init__(self, index, center, points):
        self.index = index
        self.center = center
        self.points = points
        self.tile = BaseTile()
        self.unit = None

    def change_points(self, points):
        self.points = points

    def change_center(self, center):
        self.center = center

    def set_unit(self, unit):
        self.unit = unit

    def set_tile(self, tile):
        self.tile = tile

    def get_param(self):
        return self.index, self.center, self.points
