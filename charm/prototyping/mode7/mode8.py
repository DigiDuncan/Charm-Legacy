import nygame
import pygame
import pygame.draw
from pygame.color import Color

import cv2
import numpy as np


class Game(nygame.Game):
    def __init__(self):
        super().__init__(size=(1280, 800))
        self.src = [(580, 475), (740, 475), (300, 650), (1050, 650)]
        self.dst = [(575, 0), (720, 0), (310, 720), (1000, 720)]
        print(type(cv2.getPerspectiveTransform(np.float32(self.src), np.float32(self.dst))[0][0]))

    def loop(self, events):
        self.draw_data(self.src)
        self.draw_data(self.dst)

    def draw_data(self, data):
        tl, tr, br, bl = data
        pygame.draw.line(self.surface, Color("red"), tl, tr)
        pygame.draw.line(self.surface, Color("green"), tr, bl)
        pygame.draw.line(self.surface, Color("yellow"), bl, br)
        pygame.draw.line(self.surface, Color("blue"), br, tl)


if __name__ == "__main__":
    Game().run()
