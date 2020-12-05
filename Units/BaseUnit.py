class BaseUnit:
    def __init__(self):
        self.attack = 1
        self.health = 1
        self.moves_per_round = 1
        self.moved = self.moves_per_round

    def move(self, move):
        if self.moved - move >= 0:
            self.moved -= move

    def update(self):
        self.moved = 0
