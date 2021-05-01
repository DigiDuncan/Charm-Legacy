from pathlib import Path
from typing import Literal, Tuple

import cv2
import numpy as np
from numpy import ndarray

import nygame
import pygame
from pygame.constants import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from pygame.surface import Surface
import pygame.image
import pygame.key
import pygame.surfarray
import pygame.draw
import pygame.transform
from pygame.color import Color
from nygame import DigiText as T
from pygame import K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_q, K_w, K_e, K_r, K_t, K_y, K_u, K_i, K_a, K_s, K_d, K_f, K_g, K_h, K_j, K_k, K_LSHIFT, Vector2


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
    w, h = surf.get_size()
    pm = getTF(src, dst)
    img_output: ndarray = cv2.warpPerspective(surfarray, pm, (w, h))
    return pygame.surfarray.make_surface(img_output.swapaxes(0, 1))


class Game(nygame.Game):
    def __init__(self):
        super().__init__(size = (1280, 720), fps = 120, showfps = True)
        highway_path = Path("./charm/data/images/highway.png")
        self.highway_img = pygame.image.load(highway_path)
        self.speed = 100
        self.default_quad = Quad((0, 0), (150, 0), (150, 300), (0, 300))
        self.src = self.default_quad.copy()
        self.dst = self.default_quad.copy()
        self.original = self.highway_img.copy()
        self.warped = self.highway_img.copy()
        self.grabbed = None
        self.line_offset = (500, 100)

    def pxpf(self, pxps):
        return pxps / self.fps

    def warp_highway(self):
        img = self.highway_img.copy()
        self.warped = warp_surface(img, self.src, self.dst)

    def render_labels(self):
        original = T("Original", font="Lato Medium", size=48, color="green")
        warped = T("Warped", font="Lato Medium", size=48, color="green")
        warped_dst = (
            5,
            self.surface.get_height() - warped.get_rect().h
        )
        original_dst = (
            self.surface.get_width() - original.get_rect().w - 5,
            self.surface.get_height() - original.get_rect().h
        )
        warped.render_to(self.surface, warped_dst)
        original.render_to(self.surface, original_dst)

    def render_images(self):
        self.surface.blit(pygame.transform.scale2x(self.warped), (10, 10))
        self.surface.blit(pygame.transform.scale2x(self.original), (self.surface.get_width() - (self.original.get_width() * 2) - 10, 10))

    def render_outlines(self):
        self.default_quad.shift(self.line_offset).render_to(self.surface, (Color("#994400"), Color("#994400"), Color("#994400"), Color("#994400")))
        self.src.shift(self.line_offset).render_to(self.surface, (Color("#FF0000"), Color("#00FF00"), Color("#FFFF00"), Color("#0000FF")))
        self.dst.shift(self.line_offset).render_to(self.surface, (Color("#FF7788"), Color("#77FF77"), Color("#FFFF99"), Color("#0066FF")))

    def render_coords(self):
        tf = getTF(self.src, self.dst)
        tf_str1 = ", ".join(f"{cell:.2f}" for cell in tf[0])
        tf_str2 = ", ".join(f"{cell:.2f}" for cell in tf[1])
        tf_str3 = ", ".join(f"{cell:.2f}" for cell in tf[2])

        src = T(f"SRC: {self.src}", font="Lato Medium", size=24, color="green")
        dst = T(f"DST: {self.dst}", font="Lato Medium", size=24, color="green")
        matrix1 = T(tf_str1, font="Lato Medium", size=24, color="green")
        matrix2 = T(tf_str2, font="Lato Medium", size=24, color="green")
        matrix3 = T(tf_str3, font="Lato Medium", size=24, color="green")

        src_text = src.render()
        dst_text = dst.render()
        mdt_text1 = matrix1.render()
        mdt_text2 = matrix2.render()
        mdt_text3 = matrix3.render()

        screen = self.surface.get_rect()
        src_dest = src_text.get_rect()
        dst_dest = dst_text.get_rect()
        mdt_dest1 = mdt_text1.get_rect()
        mdt_dest2 = mdt_text2.get_rect()
        mdt_dest3 = mdt_text3.get_rect()

        src_dest.midtop = screen.midtop
        dst_dest.midtop = src_dest.midbottom
        mdt_dest3.midbottom = screen.midbottom
        mdt_dest2.bottomleft = mdt_dest3.topleft
        mdt_dest1.bottomleft = mdt_dest2.topleft

        self.surface.blit(src_text, src_dest)
        self.surface.blit(dst_text, dst_dest)
        self.surface.blit(mdt_text1, mdt_dest3)
        self.surface.blit(mdt_text2, mdt_dest2)
        self.surface.blit(mdt_text3, mdt_dest1)

    def handle_keys(self):
        if self.grabbed is not None:
            return
        keys = pygame.key.get_pressed()

        xy = 1 if keys[K_LSHIFT] else 0
        diff = self.pxpf(self.speed)

        if keys[K_1]:
            self.src.tl[xy] += diff  # noqa: E701
        if keys[K_2]:
            self.src.tr[xy] += diff  # noqa: E701
        if keys[K_3]:
            self.src.bl[xy] += diff  # noqa: E701
        if keys[K_4]:
            self.src.br[xy] += diff  # noqa: E701
        if keys[K_5]:
            self.dst.tl[xy] += diff  # noqa: E701
        if keys[K_6]:
            self.dst.tr[xy] += diff  # noqa: E701
        if keys[K_7]:
            self.dst.bl[xy] += diff  # noqa: E701
        if keys[K_8]:
            self.dst.br[xy] += diff  # noqa: E701

        if keys[K_q]:
            self.src.tl[xy] -= diff  # noqa: E701
        if keys[K_w]:
            self.src.tr[xy] -= diff  # noqa: E701
        if keys[K_e]:
            self.src.bl[xy] -= diff  # noqa: E701
        if keys[K_r]:
            self.src.br[xy] -= diff  # noqa: E701
        if keys[K_t]:
            self.dst.tl[xy] -= diff  # noqa: E701
        if keys[K_y]:
            self.dst.tr[xy] -= diff  # noqa: E701
        if keys[K_u]:
            self.dst.bl[xy] -= diff  # noqa: E701
        if keys[K_i]:
            self.dst.br[xy] -= diff  # noqa: E701

        if keys[K_a]:
            self.src.tl[xy] = self.default_quad.tl[xy]  # noqa: E701
        if keys[K_s]:
            self.src.tr[xy] = self.default_quad.tr[xy]  # noqa: E701
        if keys[K_d]:
            self.src.bl[xy] = self.default_quad.bl[xy]  # noqa: E701
        if keys[K_f]:
            self.src.br[xy] = self.default_quad.br[xy]  # noqa: E701
        if keys[K_g]:
            self.dst.tl[xy] = self.default_quad.tl[xy]  # noqa: E701
        if keys[K_h]:
            self.dst.tr[xy] = self.default_quad.tr[xy]  # noqa: E701
        if keys[K_j]:
            self.dst.bl[xy] = self.default_quad.bl[xy]  # noqa: E701
        if keys[K_k]:
            self.dst.br[xy] = self.default_quad.br[xy]  # noqa: E701

    def handle_mouse(self, events):
        keys = pygame.key.get_pressed()
        for e in events:
            if e.type == MOUSEBUTTONDOWN and e.button == 1:
                self.grab(e.pos, keys[K_LSHIFT])
                print("grab")
            elif e.type == MOUSEBUTTONUP and e.button == 1:
                self.ungrab()
                print("ungrab")
            elif e.type == MOUSEMOTION:
                self.movegrab(e.pos)
            elif e.type == MOUSEBUTTONDOWN and e.button == 3:
                print("resetgrab")
                self.resetgrab(e.pos, keys[K_LSHIFT])

    def grab(self, xy, target_src):
        xy = subCoord(xy, self.line_offset)
        if target_src:
            quad = self.src
        else:
            quad = self.dst

        grab_range = 20
        dist, corner_idx = min((calcdist(xy, corner), i) for i, corner in enumerate(quad))
        if dist > grab_range:
            return

        self.grabbed = (quad, corner_idx)

    def resetgrab(self, xy, target_src):
        xy = subCoord(xy, self.line_offset)
        if target_src:
            quad = self.src
        else:
            quad = self.dst

        grab_range = 20
        dist, corner_idx = min((calcdist(xy, corner), i) for i, corner in enumerate(quad))
        if dist > grab_range:
            return

        quad[corner_idx][0] = self.default_quad[corner_idx][0]
        quad[corner_idx][1] = self.default_quad[corner_idx][1]

    def ungrab(self):
        self.grabbed = None

    def movegrab(self, xy):
        if self.grabbed is None:
            return

        xy = subCoord(xy, self.line_offset)

        quad, corner_idx = self.grabbed
        quad[corner_idx][0] = xy[0]
        quad[corner_idx][1] = xy[1]

    def loop(self, events):
        self.handle_mouse(events)

        self.handle_keys()
        self.warp_highway()

        self.render_outlines()
        self.render_images()
        self.render_labels()
        self.render_coords()


Game().run()
