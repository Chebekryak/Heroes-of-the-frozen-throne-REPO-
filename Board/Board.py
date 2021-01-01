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
        self.fps = 60
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
        self.throne_menu_enable = False
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

    def draw_throne_window(self):
        if self.throne_menu_enable:
            pygame.draw.rect(self.screen, Color("black"),
                             (20 if self.turn else self.width - self.width // 3 - 20, 20,
                              self.width // 3, self.height - 40))
            pygame.draw.rect(self.screen, Color("white"),
                             (20 if self.turn else self.width - self.width // 3 - 20, 20,
                              self.width // 3, self.height - 40), 3)

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
                        if not (elm.unit and elm.unit != self.chosen_unit.unit):
                            new += add_to_hexagons_to_move(elm, num + 1)
                    to_do = new[:]
            for elm in self.hexagons_to_move.keys():
                if elm.unit is None:
                    pygame.draw.circle(self.screen, pygame.Color("white"),
                                       self.board[elm.index[1]][elm.index[0]].center, 2, 5)
                elif elm.unit.player != self.turn:
                    pygame.draw.circle(self.screen, pygame.Color("red"),
                                       self.board[elm.index[1]][elm.index[0]].center, 2, 5)
                    pygame.draw.polygon(self.screen, pygame.Color("red"), elm.points, 3)
                else:
                    pygame.draw.polygon(self.screen, pygame.Color("green"), elm.points, 3)

    def draw_double_bar(self, colors: tuple, pos: tuple, shift: int):
        pygame.draw.rect(self.screen, pygame.Color(colors[0]), pos)
        pygame.draw.rect(self.screen, pygame.Color(colors[1]), (*map(lambda x: x - shift, pos[:2]),
                                                                *map(lambda x: x + shift, pos[2:])), shift)

    def chose_hexagon(self, pos):
        obj = min(self.one_d_board, key=lambda x: ((x.center[0] - pos[0]) ** 2 + (x.center[1] - pos[1]) ** 2) ** 0.5)
        if ((obj.center[0] - pos[0]) ** 2 + (obj.center[1] - pos[1]) ** 2) ** 0.5 > self.diagonal // 2:
            return None
        else:
            return obj

    def chose_unit(self, hexagon):
        if self.hexagons_to_move:
            self.hexagons_to_move = {}
        if not hexagon or hexagon.unit is None or hexagon.unit.player != self.turn:
            self.chosen_unit = None
        else:
            self.chosen_unit = hexagon
            hexagon.unit.update()

    def chose_tile(self, pos):
        hexagon = self.chose_hexagon(pos)
        if not hexagon or hexagon.tile.__class__ == BaseTile or hexagon.tile.player != self.turn:
            return None
        return hexagon

    def move_unit(self, to_hexagon):
        if to_hexagon in self.hexagons_to_move:
            if not self.chosen_unit == to_hexagon:
                self.chosen_unit.unit.hexagon = to_hexagon
                self.chosen_unit.unit.move(self.hexagons_to_move[to_hexagon])
                self.board[to_hexagon.index[1]][to_hexagon.index[0]].unit = self.chosen_unit.unit
                self.chosen_unit.unit.update()
                self.chosen_unit.unit = None
                self.chosen_unit = self.board[to_hexagon.index[1]][to_hexagon.index[0]]
                self.hexagons_to_move = {}
        else:
            self.chosen_unit = None
            self.hexagons_to_move = {}

    def click_in_throne_menu(self, pos):
        x = 20 if self.turn else self.width - self.width // 3 - 20
        return x <= pos[0] <= x + self.width // 3 and 20 <= pos[1] <= self.height - 20

    def click_in_hud(self, pos):
        start_pos = (0, 4 * (self.height / 5))
        hud_width = 6 * (self.width / 12)
        return start_pos[0] <= pos[0] <= hud_width and start_pos[1] <= pos[1] <= self.height

    def use_throne_menu(self, pos):
        # TODO Арсений
        pass

    def use_hud(self, pos):
        # TODO Артём
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
        if self.chosen_unit:
            start_pos = (0, 4 * (self.height / 5))
            hud_width = 6 * (self.width / 12)
            hud_height = self.height - 4 * (self.height / 5)
            indent = hud_height // 15
            text_x = hud_height
            bar_width = hud_width - indent - text_x
            pygame.draw.rect(self.screen, pygame.Color("black"),
                             (*start_pos, hud_width, hud_height))
            pygame.draw.rect(self.screen, pygame.Color("white"),
                             (*start_pos, hud_width, hud_height), 3)
            pygame.draw.circle(self.screen, pygame.Color("white"),
                               (start_pos[0] + hud_height // 2, start_pos[1] + hud_height // 2),
                               hud_height // 2 - hud_height // 15, 2)
            char_class = pygame.font.Font(None, 30).render(str(self.chosen_unit.unit), True, (255, 255, 255))
            self.screen.blit(char_class, ((text_x + (bar_width - char_class.get_width()) // 2),
                                          start_pos[1] + indent))
            attack = pygame.font.Font(None, 26).render(f"АТК: {self.chosen_unit.unit.damage}", True, (255, 255, 255))
            self.screen.blit(attack, ((text_x + (bar_width - attack.get_width()) // 2),
                                      start_pos[1] + (2 * indent) // 2 + char_class.get_height()))
            self.draw_double_bar(("red", "white"), (text_x, start_pos[1] + 2 * indent + attack.get_height()
                                                    + char_class.get_height(), bar_width, indent), 1)
            self.draw_double_bar(("blue", "white"), (text_x, start_pos[1] + 4 * indent + attack.get_height()
                                                     + char_class.get_height(), bar_width, indent), 1)
            spell_box_side = self.height - (start_pos[1] + 6 * indent + 2 * attack.get_height()) - indent
            tab = (bar_width - 4 * spell_box_side) / 4
            align_center = (bar_width - (4 * spell_box_side + 3 * tab)) / 2
            for num in range(4):
                pygame.draw.rect(self.screen, pygame.Color("white"),
                                 (align_center + text_x + (spell_box_side + tab) * num,
                                  start_pos[1] + 6 * indent + 2 * attack.get_height(),
                                  spell_box_side, spell_box_side), 1)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rendering = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    chosen_hexagon = self.chose_hexagon(event.pos)
                    if chosen_hexagon:
                        if not self.hexagons_to_move:
                            if ((not self.turn and self.chose_tile(event.pos) in self.throne_0)
                                    or (self.turn and self.chose_tile(event.pos) in self.throne_1)):
                                self.chosen_unit = None
                                self.throne_menu_enable = not self.throne_menu_enable
                            elif self.throne_menu_enable and self.click_in_throne_menu(event.pos):
                                self.use_throne_menu(event.pos)
                            elif self.chosen_unit and self.click_in_hud(event.pos):
                                self.use_hud(event.pos)
                            elif self.chosen_unit:
                                if chosen_hexagon.unit:
                                    if chosen_hexagon.unit.player == self.turn:
                                        if chosen_hexagon == self.chosen_unit:
                                            self.chosen_unit = None
                                        else:
                                            self.chose_unit(chosen_hexagon)
                                    else:
                                        self.chose_unit(chosen_hexagon)
                                else:
                                    self.chose_unit(chosen_hexagon)
                            elif chosen_hexagon.unit:
                                self.chose_unit(chosen_hexagon)
                            else:
                                self.chosen_unit = None
                        else:
                            if self.throne_menu_enable and self.click_in_throne_menu(event.pos):
                                self.use_throne_menu(event.pos)
                            elif self.chosen_unit:
                                if chosen_hexagon.unit is None:
                                    if not self.click_in_hud(event.pos):
                                        self.move_unit(chosen_hexagon)
                                    else:
                                        self.use_hud(event.pos)
                                elif chosen_hexagon.unit.player == self.turn:
                                    if chosen_hexagon == self.chosen_unit:
                                        self.chosen_unit = None
                                        self.hexagons_to_move = {}
                                    else:
                                        if not self.click_in_hud(event.pos):
                                            self.chose_unit(chosen_hexagon)
                                elif chosen_hexagon in self.hexagons_to_move:
                                    attack = self.chosen_unit.unit.attack(
                                             self.hexagons_to_move[chosen_hexagon],
                                             chosen_hexagon.unit)
                                    if attack[0]:
                                        if self.chosen_unit not in self.health_bars:
                                            self.health_bars += [self.chosen_unit]
                                        if chosen_hexagon not in self.health_bars:
                                            self.health_bars += [chosen_hexagon]
                                        if attack[1]:
                                            self.health_bars.remove(self.chosen_unit)
                                            chosen_hexagon.unit = self.chosen_unit.unit
                                            self.chosen_unit.unit = None
                                        self.chosen_unit = None
                                        self.hexagons_to_move = {}
                                else:
                                    if not self.click_in_hud(event.pos):
                                        self.chosen_unit = None
                                        self.hexagons_to_move = {}
                                    else:
                                        self.use_hud(event.pos)
                    elif not self.click_in_throne_menu(event.pos):
                        if not self.click_in_hud(event.pos):
                            self.chosen_unit = None
                            self.hexagons_to_move = {}
                        else:
                            self.use_hud(event.pos)
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
        self.board[0][0].set_unit(BaseUnit(0, self.board[0][0]))
        self.board[0][4].set_unit(Worker(0, self.board[0][4]))
        self.board[0][5].set_unit(Warrior(0, self.board[0][5]))
        self.board[1][5].set_unit(Warrior(0, self.board[1][5]))
        self.board[1][4].set_unit(Warrior(1, self.board[1][4]))
        self.board[3][3].set_tile(Mount())
        pygame.init()
        clock = pygame.time.Clock()
        while self.rendering:
            self.screen.fill((0, 0, 0))
            self.draw_hex_map()
            self.draw_units()
            self.draw_chosen_unit()
            self.draw_resources()
            self.health_bar()
            self.draw_throne_window()
            self.hud()
            self.update()
            pygame.display.flip()
            clock.tick(self.fps)


test = Board(1080, 900, 20)
test.render()
