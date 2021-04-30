from copy import copy
from pathlib import Path

import cv2
import numpy as np

import nygame
import pygame
import pygame.image
import pygame.key
import pygame.surfarray
from nygame import DigiText as T
from pygame import K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_q, K_w, K_e, K_r, K_t, K_y, K_u, K_i, K_a, K_s, K_d, K_f, K_g, K_h, K_j, K_k, K_LSHIFT


def warp(surfarray, data):
    rows, cols = surfarray.shape[:2]
    size = (cols, rows)

    x = cols - 1
    y = rows - 1

    src_points = np.float32([data["a"], data["b"], data["c"], data["d"]])
    dst_points = np.float32([data["w"], data["x"], data["y"], data["z"]])
    pm = cv2.getPerspectiveTransform(src_points, dst_points)
    print(f"[{pm[0][0]:.5}, {pm[0][1]:.5}, {pm[0][2]:.5}, {pm[1][0]:.5}, {pm[1][1]:.5}, {pm[1][2]:.5}, {pm[2][0]:.5}, {pm[2][1]:.5}]")
    img_output = cv2.warpPerspective(surfarray, pm, size)

    return pygame.surfarray.make_surface(img_output)


class Game(nygame.Game):
    def __init__(self):
        super().__init__(size = (1280, 720), fps = 120, showfps = True)
        self.highway = Path("./charm/data/images/highway.png")
        self._himg = pygame.image.load(self.highway)
        self.speed = 100
        self.data = {
            "a": [0, 0],
            "b": [150, 0],
            "c": [0, 300],
            "d": [150, 300],
            "w": [0, 0],
            "x": [150, 0],
            "y": [0, 300],
            "z": [150, 300]
        }
        self.default_data = copy(self.data)
        self._wimg = self.warp_highway(self.highway, self.data)

    @property
    def himg(self):
        return pygame.transform.scale2x(self._himg)

    @property
    def wimg(self):
        return pygame.transform.scale2x(self._wimg)

    def pxpf(self, pxps):
        return pxps / self.fps

    def warp_highway(self, highway, data):
        pimg = pygame.image.load(highway)
        sarr = pygame.surfarray.array3d(pimg)
        return warp(sarr, data)

    def render_labels(self):
        original = T("Original", font="Lato Medium", size=48, color="green")
        warped = T("Warped", font="Lato Medium", size=48, color="green")
        warped.render_to(self.surface, (5, self.wimg.get_height() + warped.render().get_height() + 5))
        original.render_to(self.surface, (self.surface.get_width() - original.render().get_width() - 5, self.himg.get_height() + original.render().get_height() + 5))

    def render_images(self):
        self.surface.blit(self.wimg, (0, 0))
        self.surface.blit(self.himg, (self.surface.get_width() - self.himg.get_width(), 0))

    def render_coords(self):
        data = self.data
        src = T(f"SRC: [{data['a']}, {data['b']}, {data['c']}, {data['d']}]", font="Lato Medium", size=24, color="green")
        dst = T(f"DST: [{data['w']}, {data['x']}, {data['y']}, {data['z']}]", font="Lato Medium", size=24, color="green")

        src_text = src.render()
        dst_text = dst.render()

        screen = self.surface.get_rect()
        src_dest = src_text.get_rect()
        dst_dest = dst_text.get_rect()

        src_dest.midtop = screen.midtop
        dst_dest.midtop = src_dest.midbottom

        self.surface.blit(src_text, src_dest)
        self.surface.blit(dst_text, dst_dest)

    def loop(self, events):
        keys = pygame.key.get_pressed()

        if not keys[K_LSHIFT]:
            if keys[K_1]: self.data["a"][0] += self.pxpf(self.speed)  # noqa: E701
            if keys[K_2]: self.data["b"][0] += self.pxpf(self.speed)  # noqa: E701
            if keys[K_3]: self.data["c"][0] += self.pxpf(self.speed)  # noqa: E701
            if keys[K_4]: self.data["d"][0] += self.pxpf(self.speed)  # noqa: E701
            if keys[K_5]: self.data["w"][0] += self.pxpf(self.speed)  # noqa: E701
            if keys[K_6]: self.data["x"][0] += self.pxpf(self.speed)  # noqa: E701
            if keys[K_7]: self.data["y"][0] += self.pxpf(self.speed)  # noqa: E701
            if keys[K_8]: self.data["z"][0] += self.pxpf(self.speed)  # noqa: E701
            if keys[K_q]: self.data["a"][0] -= self.pxpf(self.speed)  # noqa: E701
            if keys[K_w]: self.data["b"][0] -= self.pxpf(self.speed)  # noqa: E701
            if keys[K_e]: self.data["c"][0] -= self.pxpf(self.speed)  # noqa: E701
            if keys[K_r]: self.data["d"][0] -= self.pxpf(self.speed)  # noqa: E701
            if keys[K_t]: self.data["w"][0] -= self.pxpf(self.speed)  # noqa: E701
            if keys[K_y]: self.data["x"][0] -= self.pxpf(self.speed)  # noqa: E701
            if keys[K_u]: self.data["y"][0] -= self.pxpf(self.speed)  # noqa: E701
            if keys[K_i]: self.data["z"][0] -= self.pxpf(self.speed)  # noqa: E701
            if keys[K_a]: self.data["a"][0] = self.default_data["a"][0]  # noqa: E701
            if keys[K_s]: self.data["b"][0] = self.default_data["b"][0]  # noqa: E701
            if keys[K_d]: self.data["c"][0] = self.default_data["c"][0]  # noqa: E701
            if keys[K_f]: self.data["d"][0] = self.default_data["d"][0]  # noqa: E701
            if keys[K_g]: self.data["w"][0] = self.default_data["w"][0]  # noqa: E701
            if keys[K_h]: self.data["x"][0] = self.default_data["x"][0]  # noqa: E701
            if keys[K_j]: self.data["y"][0] = self.default_data["y"][0]  # noqa: E701
            if keys[K_k]: self.data["z"][0] = self.default_data["z"][0]  # noqa: E701
        else:
            if keys[K_1]: self.data["a"][1] += self.pxpf(self.speed)  # noqa: E701
            if keys[K_2]: self.data["b"][1] += self.pxpf(self.speed)  # noqa: E701
            if keys[K_3]: self.data["c"][1] += self.pxpf(self.speed)  # noqa: E701
            if keys[K_4]: self.data["d"][1] += self.pxpf(self.speed)  # noqa: E701
            if keys[K_5]: self.data["w"][1] += self.pxpf(self.speed)  # noqa: E701
            if keys[K_6]: self.data["x"][1] += self.pxpf(self.speed)  # noqa: E701
            if keys[K_7]: self.data["y"][1] += self.pxpf(self.speed)  # noqa: E701
            if keys[K_8]: self.data["z"][1] += self.pxpf(self.speed)  # noqa: E701
            if keys[K_q]: self.data["a"][1] -= self.pxpf(self.speed)  # noqa: E701
            if keys[K_w]: self.data["b"][1] -= self.pxpf(self.speed)  # noqa: E701
            if keys[K_e]: self.data["c"][1] -= self.pxpf(self.speed)  # noqa: E701
            if keys[K_r]: self.data["d"][1] -= self.pxpf(self.speed)  # noqa: E701
            if keys[K_t]: self.data["w"][1] -= self.pxpf(self.speed)  # noqa: E701
            if keys[K_y]: self.data["x"][1] -= self.pxpf(self.speed)  # noqa: E701
            if keys[K_u]: self.data["y"][1] -= self.pxpf(self.speed)  # noqa: E701
            if keys[K_i]: self.data["z"][1] -= self.pxpf(self.speed)  # noqa: E701
            if keys[K_a]: self.data["a"][1] = self.default_data["a"][1]  # noqa: E701
            if keys[K_s]: self.data["b"][1] = self.default_data["b"][1]  # noqa: E701
            if keys[K_d]: self.data["c"][1] = self.default_data["c"][1]  # noqa: E701
            if keys[K_f]: self.data["d"][1] = self.default_data["d"][1]  # noqa: E701
            if keys[K_g]: self.data["w"][1] = self.default_data["w"][1]  # noqa: E701
            if keys[K_h]: self.data["x"][1] = self.default_data["x"][1]  # noqa: E701
            if keys[K_j]: self.data["y"][1] = self.default_data["y"][1]  # noqa: E701
            if keys[K_k]: self.data["z"][1] = self.default_data["z"][1]  # noqa: E701

        for k in "abcdwxyz":
            self.data[k] = [round(self.data[k][0], 2), round(self.data[k][1], 2)]

        self._wimg = self.warp_highway(self.highway, self.data)
        # print(self.data)

        self.render_images()
        self.render_labels()
        self.render_coords()


Game().run()
