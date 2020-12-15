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
                               tuple(map(lambda x: (x[0] + cell_size * 1.5 * j,
                                                    x[1] + self.diagonal * i + (
                                                        self.diagonal // 2 if not bool(j % 2) else 0)),
                                         (
                                             (cell_size // 2, 0),
                                             (cell_size // 2 + cell_size, 0),
                                             (cell_size * 2, self.diagonal // 2),
                                             (cell_size // 2 + cell_size, self.diagonal),
                                             (cell_size // 2, self.diagonal),
                                             (0, self.diagonal // 2)
                                         ))))
                       for j in range(int(self.width // (cell_size * 3)) * 2)]
                      for i in range(int(self.height // (cell_size * (3 ** 0.5))))]
        self.one_d_board = [i for j in self.board for i in j]
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.chosen_unit = None
        self.hexagons_to_move = {}
        self.changing_camera_pos = False
        self.camera_zooming = 0
        self.camera_pos = [0, 0]
        self.camera_data = [self.cell_size, self.diagonal]
        self.change_hexagons_pos(((self.width - (self.board[-1][-1].center[0] + self.cell_size)) // 2,
                                 ((self.height - (self.board[-1][-1].center[1] + self.diagonal)) // 2)))
        self.board[3][3] = Tail(*self.board[3][3].get_param())

    def change_hexagons_size(self, cell_size, m_p):
        diagonal = cell_size * (3 ** 0.5)
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                self.board[i][j].change_points(
                    tuple(map(lambda x: (x[0] + cell_size * 1.5 * j,
                                         x[1] + diagonal * i + (
                                             diagonal // 2 if not bool(j % 2) else 0)),
                              (
                                  (cell_size // 2, 0),
                                  (cell_size // 2 + cell_size, 0),
                                  (cell_size * 2, diagonal // 2),
                                  (cell_size // 2 + cell_size, diagonal),
                                  (cell_size // 2, diagonal),
                                  (0, diagonal // 2)
                              )))
                )
                self.board[i][j].change_center(
                    (round(cell_size + cell_size * 1.5 * j),
                     round(diagonal // 2 + diagonal * i + (
                         diagonal // 2 if not j % 2 else 0)))
                )
        new_x = ((m_p[0] + self.camera_pos[0]) / self.camera_data[0]) * cell_size
        new_y = ((m_p[1] + self.camera_pos[1]) / self.camera_data[1]) * diagonal
        self.change_hexagons_pos((-(round(new_x) - m_p[0]), -(round(new_y) - m_p[1])))
        self.cell_size = cell_size
        self.diagonal = cell_size * (3 ** 0.5)

    def change_hexagons_pos(self, pos):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                self.board[i][j].change_points(tuple(map(lambda x: (x[0] + pos[0], x[1] + pos[1]),
                                                         self.board[i][j].points)))
                self.board[i][j].change_center((self.board[i][j].center[0] + pos[0],
                                                self.board[i][j].center[1] + pos[1]))

    def draw_hex_map(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if type(self.board[i][j]) == Hexagon:
                    pygame.draw.polygon(self.screen, pygame.Color("white"), self.board[i][j].points, 1)
                else:
                    pygame.draw.polygon(self.screen, pygame.Color("grey"), self.board[i][j].points)

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
        def add_to_hexagons_to_move(hexagon, num_):
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
                    try:
                        if i < 0 or i >= len(self.board) or j < 0 or j >= len(self.board[0]) \
                                or pos == (j, i) or type(self.board[i][j]) != Hexagon:
                            raise IndexError
                        if self.board[i][j] not in self.hexagons_to_move:
                            self.hexagons_to_move[self.board[i][j]] = num_
                            if self.board[i][j] not in next_:
                                next_ += [self.board[i][j]]
                    except IndexError:
                        pass
            return next_

        if self.chosen_unit:
            to_do = [self.chosen_unit]
            for num in range(self.chosen_unit.unit.moved):
                new = []
                for elm in to_do:
                    new += add_to_hexagons_to_move(elm, num + 1)
                to_do = new[:]
            for elm in self.hexagons_to_move.keys():
                pygame.draw.circle(self.screen, pygame.Color("red"),
                                   self.board[elm.index[1]][elm.index[0]].center, 2, 5)

    def move_unit(self, to_hexagon):
        if to_hexagon in self.hexagons_to_move and not self.chosen_unit == to_hexagon:
            self.chosen_unit.unit.move(self.hexagons_to_move[to_hexagon])
            self.board[to_hexagon.index[1]][to_hexagon.index[0]].unit = self.chosen_unit.unit
            self.chosen_unit.unit = None
            self.chosen_unit = None
            self.hexagons_to_move = {}

    def render(self):
        self.board[0][0].set_unit(BaseUnit())
        flag = True
        while flag:
            self.screen.fill((0, 0, 0))
            self.draw_hex_map()
            self.draw_units()
            self.draw_chosen_unit()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    flag = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not self.hexagons_to_move:
                            self.chosen_unit = self.chose_unit(event.pos)
                        else:
                            self.move_unit(self.chose_hexagon(event.pos))
                    elif event.button == 2:
                        self.changing_camera_pos = True
                    elif event.button == 4:
                        if self.camera_zooming + 1 <= 3:
                            self.change_hexagons_size(self.cell_size + 5, event.pos)
                            self.camera_zooming += 1
                    elif event.button == 5:
                        if self.camera_zooming - 1 >= -1:
                            self.change_hexagons_size(self.cell_size - 5, event.pos)
                            self.camera_zooming -= 1
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 2:
                        self.changing_camera_pos = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.changing_camera_pos:
                        e = event.rel
                        if e[0] > 0:
                            if self.board[0][0].center[0] - 5 * self.cell_size < 0:
                                self.camera_pos[0] -= event.rel[0]
                                self.change_hexagons_pos((event.rel[0], 0))
                        elif e[0] < 0:
                            if self.board[0][-1].center[0] + 5 * self.cell_size > self.width:
                                self.camera_pos[0] -= event.rel[0]
                                self.change_hexagons_pos((event.rel[0], 0))
                        if e[1] > 0:
                            if self.board[0][0].center[1] - self.diagonal - 4 * self.cell_size < 0:
                                self.camera_pos[1] -= event.rel[1]
                                self.change_hexagons_pos((0, event.rel[1]))
                        elif e[1] < 0:
                            if self.board[-1][-1].center[1] + self.diagonal + 4 * self.cell_size > self.height:
                                self.camera_pos[1] -= event.rel[1]
                                self.change_hexagons_pos((0, event.rel[1]))
            pygame.display.flip()


test = Board(400, 400, 20)
test.render()
