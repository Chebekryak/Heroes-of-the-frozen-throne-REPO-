from Cell.Hexagon import *
import pygame


class Board:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.board = [[Hexagon() for _ in range(int(self.width // (cell_size * 3)) * 2)]
                      for _ in range(int(self.height // (cell_size * (3 ** 0.5))))]
        self.screen = pygame.display.set_mode((self.width, self.height))
        print(len(self.board))
        print(len(self.board[0]))

    def draw_hex_map(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[0])):
                second_one = not bool(j % 2)
                diagonal = self.cell_size * (3 ** 0.5)
                pygame.draw.polygon(self.screen, pygame.Color("white"),
                                    tuple(map(lambda x: (x[0] + self.cell_size * 1.5 * j,
                                                         x[1] + diagonal * i + (diagonal // 2 if second_one else 0)),
                                              (
                                                  (self.cell_size // 2, 0),
                                                  (self.cell_size // 2 + self.cell_size, 0),
                                                  (self.cell_size * 2, diagonal // 2),
                                                  (self.cell_size // 2 + self.cell_size, diagonal),
                                                  (self.cell_size // 2, diagonal),
                                                  (0, diagonal // 2)
                                              ))), 1)
                pygame.draw.circle(self.screen, pygame.Color("red"),
                                 (round(self.cell_size + self.cell_size * 1.5 * j),
                                  round(diagonal // 2 + diagonal * i + (diagonal // 2 if second_one else 0))),
                                 round(diagonal // 2), 1)

    def chose_hexagon(self):
        pass

    def render(self):
        flag = True
        while flag:
            self.screen.fill((0, 0, 0))
            self.draw_hex_map()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    flag = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    print(event.pos)
            pygame.display.flip()


test = Board(400, 400, 20)
test.render()
