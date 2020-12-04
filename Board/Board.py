from Cell.Hexagon import *
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

    def draw_hex_map(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                pygame.draw.polygon(self.screen, pygame.Color("white"), self.board[i][j].pos, 1)
                pygame.draw.circle(self.screen, pygame.Color("red"), self.board[i][j].center, 2)

    def chose_hexagon(self, pos):
        obj = min(self.one_d_board, key=lambda x: ((x.center[0] - pos[0]) ** 2 + (x.center[1] - pos[1]) ** 2) ** 0.5)
        if ((obj.center[0] - pos[0]) ** 2 + (obj.center[1] - pos[1]) ** 2) ** 0.5 > self.diagonal // 2:
            print(None)
        else:
            print(obj.index)

    def render(self):
        flag = True
        while flag:
            self.screen.fill((0, 0, 0))
            self.draw_hex_map()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    flag = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.chose_hexagon(event.pos)
            pygame.display.flip()


test = Board(400, 400, 50)
test.render()
