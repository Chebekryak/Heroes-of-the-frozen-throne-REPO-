from Cell.Tiles import *
from Cell.Hexagon import Hexagon
from Units.Units import *
from random import choice, randint
import pygame


class Board:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.start_cell_size = cell_size
        self.cell_size = cell_size
        self.diagonal = cell_size * (3 ** 0.5)
        self.rendering = True
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
                       for j in range(int(self.width // (cell_size * 3)) * 2 - 1)]
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
                                  ((self.height - (self.board[-1][-1].center[1] + self.diagonal // 2)) // 2)))
        self.health_bars = []
        self.turn = 0
        self.throne_0 = []
        self.throne_1 = []
        self.throne_menu = False
        self.generate()

    def generate(self):
        # Создание тронов
        self.throne_0 += [
            self.board[len(self.board) // 2 - 1][0],
            self.board[len(self.board) // 2][0],
            self.board[len(self.board) // 2 + 1][0],
            self.board[len(self.board) // 2][1],
            self.board[len(self.board) // 2 + 1][1]
        ]
        self.throne_1 += [
            self.board[len(self.board) // 2 - 1][-1],
            self.board[len(self.board) // 2][-1],
            self.board[len(self.board) // 2 + 1][-1],
            self.board[len(self.board) // 2][-2],
            self.board[len(self.board) // 2 + 1][-2]
        ]
        for elm in self.throne_0:
            elm.set_tile(Throne(0))
        for elm in self.throne_1:
            elm.set_tile(Throne(1))
        # Добавление ресурсов
        for _ in range(20):
            tile = choice(self.board[randint(0, len(self.board)) - 1]).tile
            if tile.useful and not any(tile.resources):
                tile.resources[randint(0, 2)] += randint(1, 3)

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
                if self.board[i][j].tile.can_move:
                    pygame.draw.polygon(self.screen, self.board[i][j].tile.color, self.board[i][j].points,
                                        round(2 * (self.cell_size / self.start_cell_size))
                                        if self.board[i][j] == self.chosen_unit else 1)
                else:
                    pygame.draw.polygon(self.screen, self.board[i][j].tile.color, self.board[i][j].points)

    def draw_units(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if self.board[i][j]:
                    if not self.board[i][j].unit is None:
                        self.board[i][j].unit.draw(self.screen, self.board[i][j],
                                                   self.cell_size, self.diagonal)

    def chose_hexagon(self, pos):
        obj = min(self.one_d_board, key=lambda x: ((x.center[0] - pos[0]) ** 2 + (x.center[1] - pos[1]) ** 2) ** 0.5)
        if ((obj.center[0] - pos[0]) ** 2 + (obj.center[1] - pos[1]) ** 2) ** 0.5 > self.diagonal // 2:
            return None
        else:
            return obj

    def chose_unit(self, pos):
        hexagon = self.chose_hexagon(pos)
        if not hexagon or hexagon.unit is None or hexagon.unit.player != self.turn:
            self.chosen_unit = None
        self.chosen_unit = hexagon

    def chose_tile(self, pos):
        hexagon = self.chose_hexagon(pos)
        if not hexagon or hexagon.tile.__class__ == BaseTile or hexagon.tile.player != self.turn:
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
                                or pos == (j, i) or not self.board[i][j].tile.can_move \
                                or self.board[i][j] == self.chosen_unit:
                            raise IndexError
                        if self.board[i][j] not in self.hexagons_to_move:
                            self.hexagons_to_move[self.board[i][j]] = num_
                            if self.board[i][j] not in next_:
                                next_ += [self.board[i][j]]
                    except IndexError:
                        pass
            return next_

        if self.chosen_unit and self.chosen_unit.unit:
            if not self.hexagons_to_move:
                to_do = [self.chosen_unit]
                for num in range(self.chosen_unit.unit.moved):
                    new = []
                    for elm in to_do:
                        if not (elm.unit and elm.unit.player != self.turn):
                            new += add_to_hexagons_to_move(elm, num + 1)
                    to_do = new[:]
            for elm in self.hexagons_to_move.keys():
                if elm.unit is None:
                    pygame.draw.circle(self.screen, pygame.Color("white"),
                                       self.board[elm.index[1]][elm.index[0]].center, 2, 5)
                else:
                    pygame.draw.circle(self.screen, pygame.Color("red"),
                                       self.board[elm.index[1]][elm.index[0]].center, 2, 5)
                    pygame.draw.polygon(self.screen, pygame.Color("red"), elm.points, 3)

    def move_unit(self, to_hexagon):
        if to_hexagon in self.hexagons_to_move:
            if not self.chosen_unit == to_hexagon:
                self.chosen_unit.unit.move(self.hexagons_to_move[to_hexagon])
                self.board[to_hexagon.index[1]][to_hexagon.index[0]].unit = self.chosen_unit.unit
                self.chosen_unit.unit = None
                self.chosen_unit = self.board[to_hexagon.index[1]][to_hexagon.index[0]]
                self.hexagons_to_move = {}
        else:
            self.chosen_unit = None
            self.hexagons_to_move = {}

    def draw_throne_window(self):
        if self.throne_menu:
            pygame.draw.rect(self.screen, Color("black"),
                             (20 if self.turn else self.width - self.width // 3 - 20, 20,
                              self.width // 3, self.height - 40))
            pygame.draw.rect(self.screen, Color("white"),
                             (20 if self.turn else self.width - self.width // 3 - 20, 20,
                              self.width // 3, self.height - 40), 3)

    def click_in_throne_menu(self, pos):
        x = 20 if self.turn else self.width - self.width // 3 - 20
        return x <= pos[0] <= x + self.width // 3 and 20 <= pos[1] <= self.height - 20

    def use_throne_menu(self, pos):
        # TODO Арсений
        pass

    def health_bar(self):
        for hexagon in self.health_bars:
            pygame.draw.rect(self.screen, Color("black"),
                             (hexagon.center[0] - self.cell_size,
                              hexagon.center[1] - self.diagonal // 2 - self.diagonal / 6,
                              self.cell_size * 2, self.diagonal / 6))
            health_per_cent = (hexagon.unit.health / hexagon.unit.full_health) * 100
            if 0 <= health_per_cent <= 25:
                color = Color("red")
            elif 25 <= health_per_cent <= 50:
                color = Color("orange")
            elif 50 <= health_per_cent <= 75:
                color = Color("yellow")
            else:
                color = Color("green")
            pygame.draw.rect(self.screen, Color("black"),
                             (hexagon.center[0] - self.cell_size,
                              hexagon.center[1] - self.diagonal // 2 - self.diagonal / 6,
                              self.cell_size * 2, self.diagonal / 6))
            pygame.draw.rect(self.screen, color,
                             (hexagon.center[0] - self.cell_size,
                              hexagon.center[1] - self.diagonal // 2 - self.diagonal / 6,
                              self.cell_size * 2 * (health_per_cent / 100), self.diagonal / 6))
            pygame.draw.rect(self.screen, Color("white"),
                             (hexagon.center[0] - self.cell_size, hexagon.center[1] - self.diagonal // 2 - self.diagonal / 6,
                              self.cell_size * 2, self.diagonal / 6), 1)

    def hud(self):
        # TODO
        if self.chosen_unit:
            pygame.draw.rect(self.screen, pygame.Color("black"),
                             (0, 4 * (self.height / 5), 6 * (self.width / 12), self.height))
            pygame.draw.rect(self.screen, pygame.Color("white"),
                             (0, 4 * (self.height / 5), 6 * (self.width / 12), self.height), 3)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rendering = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.chose_hexagon(event.pos):
                        if not self.hexagons_to_move:
                            if ((not self.turn and self.chose_tile(event.pos) in self.throne_0)
                                    or (self.turn and self.chose_tile(event.pos) in self.throne_1)):
                                self.throne_menu = not self.throne_menu
                            elif self.throne_menu and self.click_in_throne_menu(event.pos):
                                print(self.click_in_throne_menu(event.pos))
                                self.use_throne_menu(event.pos)
                            elif self.chosen_unit:
                                self.chosen_unit = None
                                self.hexagons_to_move = {}
                            elif self.chose_hexagon(event.pos).unit:
                                self.chose_unit(event.pos)
                        else:
                            if self.throne_menu and self.click_in_throne_menu(event.pos):
                                self.use_throne_menu(event.pos)
                            elif self.chosen_unit:
                                if self.chose_hexagon(event.pos).unit is None:
                                    self.move_unit(self.chose_hexagon(event.pos))
                                elif self.chose_hexagon(event.pos) in self.hexagons_to_move:
                                    if self.chosen_unit.unit.attack(
                                            self.hexagons_to_move[self.chose_hexagon(event.pos)],
                                            self.chose_hexagon(event.pos).unit):
                                        self.health_bars += [self.chosen_unit, self.chose_hexagon(event.pos)]
                                        self.chosen_unit = None
                                        self.hexagons_to_move = {}
                                else:
                                    self.chosen_unit = None
                                    self.hexagons_to_move = {}
                    elif not self.click_in_throne_menu(event.pos):
                        self.chosen_unit = None
                        self.hexagons_to_move = {}
                    else:
                        self.use_throne_menu(event.pos)
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

    def draw_resources(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                if any(self.board[i][j].tile.resources):
                    index = self.board[i][j].tile.resources.index(list(filter(lambda x: x,
                                                                              self.board[i][j].tile.resources))[0])
                    pygame.draw.circle(self.screen, {0: Color("yellow"),
                                                     1: Color("brown"),
                                                     2: Color("grey")}[index],
                                       (self.board[i][j].center[0],
                                        self.board[i][j].center[1] + self.diagonal / 3 + self.diagonal / 24),
                                       self.diagonal / 7)

    def render(self):
        self.board[0][4].set_unit(Warrior(0))
        self.board[1][4].set_unit(Warrior(1))
        self.board[3][3].set_tile(Mount())
        pygame.init()
        while self.rendering:
            self.screen.fill((0, 0, 0))
            self.draw_hex_map()
            self.draw_units()
            self.draw_chosen_unit()
            self.draw_resources()
            self.draw_throne_window()
            self.health_bar()
            self.hud()
            self.update()
            pygame.display.flip()


test = Board(1080, 900, 20)
test.render()
