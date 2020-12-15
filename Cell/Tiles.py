class BaseTile:
    def __init__(self, move=True):
        self.can_move = move

    def __str__(self):
        return self.__class__.__name__


class Mount(BaseTile):
    def __init__(self):
        super().__init__(False)
