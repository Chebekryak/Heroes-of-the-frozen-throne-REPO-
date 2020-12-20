from pygame import Color


class BaseTile:
    def __init__(self, move=True, useful=True):
        self.can_move = move
        self.color = Color("white")
        self.useful = useful
        self.resources = [0, 0, 0]

    def __str__(self):
        return self.__class__.__name__


class Mount(BaseTile):
    def __init__(self):
        super().__init__(False, False)


class Throne(BaseTile):
    def __init__(self, player):
        super().__init__(False, False)
        self.color = Color("yellow")
        self.player = player
