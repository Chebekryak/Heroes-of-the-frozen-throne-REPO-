class Hexagon:
    def __init__(self, index, center, points):
        self.index = index
        self.center = center
        self.points = points
        self.unit = None

    def change_points(self, points):
        self.points = points

    def change_center(self, center):
        self.center = center

    def set_unit(self, unit):
        self.unit = unit

    def get_param(self):
        return self.index, self.center, self.points