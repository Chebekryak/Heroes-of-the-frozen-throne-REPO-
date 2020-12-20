from pygame import draw, Color


class BaseUnit:
    def __init__(self, player, move_per_round=20, spells=0):
        self.attack = 0
        self.health = 0
        self.player = player
        self.spells = spells
        self.moves_per_round = move_per_round
        self.moved = move_per_round
        self.color = Color("red")

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__str__()

    def move(self, move):
        self.moved -= move

    def draw(self, screen, tile, cell_size, diagonal):
        draw.rect(screen, self.color, (
                            tile.center[0] - cell_size // 2,
                            tile.center[1] - diagonal // 2,
                            cell_size,
                            diagonal))

    def update(self):
        self.moved = 0


class Worker(BaseUnit):
    def __init__(self):
        super().__init__(2, 1)
        self.health = 50
        self.color = Color("white")