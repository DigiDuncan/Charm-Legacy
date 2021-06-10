from typing import Iterable, Tuple, Union

import cv2
import numpy as np
from numpy import ndarray

import pygame
from pygame import Color, Vector2
from pygame.surface import Surface


def gradientRect(left_color, right_color, target_rect):
    """Draw a horizontal-gradient filled rectangle covering <target_rect>"""
    color_rect = pygame.Surface((2, 2), pygame.SRCALPHA)  # tiny! 2x2 bitmap
    pygame.draw.line(color_rect, left_color,  (0, 0), (0, 1))  # left color line
    pygame.draw.line(color_rect, right_color, (1, 0), (1, 1))  # right color line
    color_rect = pygame.transform.smoothscale(color_rect, (target_rect.width, target_rect.height))  # stretch!
    return color_rect


def stacksurfs(surfs: Iterable[Union[Surface, None]], gap = 0) -> Surface:
    surfs = list(filter(None, surfs))
    width = max(s.get_width() for s in surfs)
    height = sum(s.get_height() for s in surfs) + (gap * (len(surfs) - 1))
    newsurf = Surface((width, height))
    current_gap = 0

    for surf in surfs:
        newsurf.blit(surf, (0, current_gap))
        current_gap += surf.get_height() + gap

    return newsurf


TFMatrix = Tuple[
    Tuple[np.float64, np.float64, np.float64],
    Tuple[np.float64, np.float64, np.float64],
    Tuple[np.float64, np.float64, np.float64]
]


def calcdist(point1, point2):
    a = Vector2(point1)
    b = Vector2(point2)
    dist = a.distance_to(b)
    return dist


def addCoord(coord: Tuple[float, float], offset: Tuple[float, float]):
    return coord[0] + offset[0], coord[1] + offset[1]


def subCoord(coord: Tuple[float, float], offset: Tuple[float, float]):
    return coord[0] - offset[0], coord[1] - offset[1]


def coordToStr(coord: Tuple[float, float]):
    return f'[{coord[0]:0.2f}, {coord[1]:0.2f}]'


class Quad:
    def __init__(self, tl=None, tr=None, br=None, bl=None):
        self.tl = list(tl or (0, 0))
        self.tr = list(tr or (0, 0))
        self.br = list(br or (0, 0))
        self.bl = list(bl or (0, 0))

    def render_to(self, surf: Surface, colors: Tuple[Color, Color, Color, Color]):
        pygame.draw.line(surf, colors[0], self.tl, self.tr)
        pygame.draw.line(surf, colors[1], self.tr, self.br)
        pygame.draw.line(surf, colors[2], self.br, self.bl)
        pygame.draw.line(surf, colors[3], self.bl, self.tl)

    def shift(self, offset: Tuple[float, float]) -> "Quad":
        return Quad(*(addCoord(p, offset) for p in self.points))

    def __getitem__(self, key):
        return self.points[key]

    @property
    def points(self):
        return (self.tl, self.tr, self.br, self.bl)

    @property
    def coords(self):
        # The transformation library uses YX coordinates, because why not?
        return tuple(tuple(p) for p in self.points)

    def copy(self):
        return Quad(*self.points)

    def __str__(self):
        return "[" + (", ".join(coordToStr(p) for p in self.points)) + "]"


def getTF(src: Quad, dst: Quad) -> TFMatrix:
    src_points = np.float32(src.coords)
    dst_points = np.float32(dst.coords)
    pm: TFMatrix = cv2.getPerspectiveTransform(src_points, dst_points)
    return pm


def warp_surface(surf: Surface, src: Quad, dst: Quad) -> Surface:
    surfarray = pygame.surfarray.array3d(surf).swapaxes(0, 1)
    alphaarray = pygame.surfarray.array_alpha(surf).swapaxes(0, 1)
    merged = np.dstack((surfarray, alphaarray))
    w, h = surf.get_size()
    pm = getTF(src, dst)
    img_output: ndarray = cv2.warpPerspective(merged, pm, (w, h))
    flat = img_output.flatten()
    surfout = pygame.image.frombuffer(flat, (w, h), "RGBA")

    return surfout
