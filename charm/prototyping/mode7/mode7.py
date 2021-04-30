from pathlib import Path

import cv2
import numpy as np

import nygame
import pygame.image
import pygame.surfarray
from nygame import DigiText as T


def warp(surfarray):
    rows, cols = surfarray.shape[:2]
    size = (cols, rows)

    x = cols - 1
    y = rows - 1

    src_points = np.float32([[0, 0], [100, 0], [0, 100], [100, 100]])
    dst_points = np.float32([[100, 0], [0, 100], [100, 100], [0, 0]])
    projective_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    img_output = cv2.warpPerspective(surfarray, projective_matrix, size)

    return pygame.surfarray.make_surface(img_output)


class Game(nygame.Game):
    def __init__(self):
        super().__init__(size = (1280, 720), fps = 120, showfps = True)
        self.highway = Path("./charm/data/images/highway.png")
        self.himg = pygame.image.load(self.highway)
        self.wimg = self.warp_highway(self.highway)

        self.himg = pygame.transform.scale2x(self.himg)
        self.wimg = pygame.transform.scale2x(self.wimg)

    def warp_highway(self, highway):
        pimg = pygame.image.load(highway)
        sarr = pygame.surfarray.array3d(pimg)
        return warp(sarr)

    def render_labels(self):
        original = T("Original", font="Lato Medium", size=48, color="green")
        warped = T("Warped", font="Lato Medium", size=48, color="green")
        warped.render_to(self.surface, (5, self.wimg.get_height() + warped.render().get_height() + 5))
        original.render_to(self.surface, (self.surface.get_width() - original.render().get_width() - 5, self.himg.get_height() + original.render().get_height() + 5))

    def render_images(self):
        self.surface.blit(self.wimg, (0, 0))
        self.surface.blit(self.himg, (self.surface.get_width() - self.himg.get_width(), 0))

    def loop(self, events):
        self.render_images()
        self.render_labels()


Game().run()
