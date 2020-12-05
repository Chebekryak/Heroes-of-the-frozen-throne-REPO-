from Cell.Tail import *
from Units.BaseUnit import *
import pygame


class Board:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.diagonal = cell_size * (3 ** 0.5)
        self.board = [[Hexagon((j, i), (round(cell_size + cell_size * 1.5 * j),
                                        round(self.diagonal // 2 + self.diagonal * i + (
                                            self.diagonal // 2 if not j % 2 else 0))),
                               tuple(map(lambda x: (x[0] + self.cell_size * 1.5 * j,
                                                    x[1] + self.diagonal * i + (
                                                        self.diagonal // 2 if not bool(j % 2) else 0)),
                                         (
                                             (self.cell_size // 2, 0),
                                             (self.cell_size // 2 + self.cell_size, 0),
                                             (self.cell_size * 2, self.diagonal // 2),
                                             (self.cell_size // 2 + self.cell_size, self.diagonal),
                                             (self.cell_size // 2, self.diagonal),
                                             (0, self.diagonal // 2)
                                         ))))
                       for j in range(int(self.width // (cell_size * 3)) * 2)]
                      for i in range(int(self.height // (cell_size * (3 ** 0.5))))]
        self.one_d_board = [i for j in self.board for i in j]
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.chosen_unit = None
        self.hexagons_to_move = []
        self.board[3][3] = Tail(*self.board[3][3].get_param())

    def draw_hex_map(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if type(self.board[i][j]) == Hexagon:
                    pygame.draw.polygon(self.screen, pygame.Color("white"), self.board[i][j].pos, 1)
                else:
                    pygame.draw.polygon(self.screen, pygame.Color("grey"), self.board[i][j].pos)

    def draw_units(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if self.board[i][j]:
                    if not self.board[i][j].unit is None:
                        pygame.draw.rect(self.screen, pygame.Color("red"), (
                            self.board[i][j].center[0] - self.cell_size // 2,
                            self.board[i][j].center[1] - self.diagonal // 2,
                            self.cell_size,
                            self.diagonal
                        ))

    def chose_hexagon(self, pos):
        obj = min(self.one_d_board, key=lambda x: ((x.center[0] - pos[0]) ** 2 + (x.center[1] - pos[1]) ** 2) ** 0.5)
        if ((obj.center[0] - pos[0]) ** 2 + (obj.center[1] - pos[1]) ** 2) ** 0.5 > self.diagonal // 2:
            return None
        else:
            return obj

    def chose_unit(self, pos):
        hexagon = self.chose_hexagon(pos)
        if not hexagon or hexagon.unit is None:
            return None
        return hexagon

    def draw_chosen_unit(self):
        def add_to_hexagons_to_move(hexagon):
            next_ = []
            move = 1
            pos = hexagon.index
            if pos[0] % 2:
                helper_1, helper_2 = 0, -1
            else:
                helper_1, helper_2 = 1, 0
            for j in range(pos[0] - move, pos[0] + move + 1):
                for i in range(pos[1] - move + helper_1 - (1 if j == pos[0] and helper_1 else 0),
                               pos[1] + move + 1 + helper_2 + (1 if j == pos[0] and helper_2 else 0)):
                    if pos != (j, i) and type(self.board[i][j]) == Hexagon:
                        try:
                            if i < 0 or j < 0:
                                raise IndexError
                            self.hexagons_to_move += [self.board[i][j]]
                            next_ += [self.board[i][j]]
                        except IndexError:
                            pass
            return next_

        if self.chosen_unit:
            to_do = [self.chosen_unit]
            for _ in range(self.chosen_unit.unit.moved):
                new = []
                for elm in to_do:
                    new += add_to_hexagons_to_move(elm)
                to_do = new[:]
            for elm in self.hexagons_to_move:
                pygame.draw.rect(
                    self.screen, pygame.Color("red"), (
                        *self.board[elm.index[1]][elm.index[0]].center,
                        5, 5))

    def move_unit(self, to_hexagon):
        # TODO Функция косячит
        def dist(p1, p2):
            y1, x1 = p1[::-1]
            y2, x2 = p2[::-1]
            du = x2 - x1
            dv = (y2 + x2 // 2) - (y1 + x1 // 2)
            return max(abs(du), abs(dv)) if ((du >= 0 and dv >= 0) or (du < 0 and dv < 0)) else abs(du) + abs(dv)

        if to_hexagon in self.hexagons_to_move:
            self.chosen_unit.unit.move(dist(to_hexagon.index[::-1], self.chosen_unit.index[::-1]))
            self.board[to_hexagon.index[1]][to_hexagon.index[0]].unit = self.chosen_unit.unit
            self.chosen_unit.unit = None
            self.chosen_unit = None
            self.hexagons_to_move = []

    def render(self):
        self.board[5][5].set_unit(BaseUnit())
        flag = True
        while flag:
            self.screen.fill((0, 0, 0))
            self.draw_hex_map()
            self.draw_units()
            self.draw_chosen_unit()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    flag = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.hexagons_to_move:
                        self.chosen_unit = self.chose_unit(event.pos)
                    else:
                        self.move_unit(self.chose_hexagon(event.pos))
            pygame.display.flip()


test = Board(400, 400, 20)
test.render()
