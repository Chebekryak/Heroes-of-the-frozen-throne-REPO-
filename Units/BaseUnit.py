class BaseUnit:
    def __init__(self):
        self.attack = 1
        self.health = 1
        self.moves_per_round = 4
        self.moved = self.moves_per_round

    def move(self, move):
        self.moved -= move

    def update(self):
        self.moved = 0
