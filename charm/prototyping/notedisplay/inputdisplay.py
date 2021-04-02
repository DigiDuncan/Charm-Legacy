from charm.lib.instruments.instrument import Instrument
import importlib.resources as pkg_resources
from typing import Union

import pygame
from pygame import Rect, Surface, image
from pygame.constants import SRCALPHA

import charm.data.images.spritesheets as image_folder
from charm.lib.instruments.guitar import Guitar
from charm.lib.pgutils import gradientRect

HIT_WINDOW = 0.140  # 140ms

fretnums = {
    "green": 0,
    "red": 1,
    "yellow": 2,
    "blue": 3,
    "orange": 4,
    "open": 7
}

fretnums_rev = {v: k for k, v in fretnums.items()}

fretmap = {
    "green": 0,
    "red": 1,
    "yellow": 2,
    "blue": 3,
    "orange": 4,
    "greensp": 5,
    "redsp": 6,
    "yellowsp": 7,
    "bluesp": 8,
    "orangesp": 9,
    "open": (10, 5),
    "opensp": (15, 5)
}

flagmap = {
    "note": 0,
    "hopo": 1,
    "tap": 2,
    "strike": 6
}

gh_sheet: Surface = None

fret_images = {}


def get_sprite(flag: str, fret: Union[str, int]) -> Surface:
    return fret_images[flag][fret]


def set_sprite(flag: str, fretname: str, sprite: Surface):
    fret_images[flag][fretname] = sprite
    if fretname in fretnums:
        fretnum = fretnums[fretname]
        fret_images[flag][fretnum] = sprite


def init():
    global gh_sheet

    SPRITE_SIZE = 64

    with pkg_resources.path(image_folder, "gh.png") as p:
        gh_sheet = image.load(p)
        gh_sheet.convert_alpha()

    if gh_sheet.get_size()[1] == 1280:
        gh_sheet = pygame.transform.scale(gh_sheet, (1280, 640))  # TODO: This is hacky and needs to be flexible.

    for flag, sy in flagmap.items():
        fret_images[flag] = {}
        for fret, sxw in fretmap.items():
            sw = 1
            try:
                sx, sw = sxw
            except TypeError:
                sx = sxw
            x = sx * SPRITE_SIZE
            y = sy * SPRITE_SIZE
            w = sw * SPRITE_SIZE
            h = SPRITE_SIZE
            img = gh_sheet.subsurface(Rect(x, y, w, h))
            set_sprite(flag, fret, img)


class InputDisplay:
    def __init__(self, guitar: Instrument, *, size: tuple = (400, 100)):
        self.guitar = guitar  # VERY game unagnostic
        self.size = size
        self.opacity = 128
        self.pressed = None
        self.last_drawn = None
        self._image = Surface(size, SRCALPHA)
        self.strum_image = gradientRect((255, 255, 255, 127), (255, 255, 255, 0), Rect(0, 0, self.size[0] / 2, 64))

    def get_fret_pos(self, f):
        w, h = self.size
        fw, fh = 64, 64
        fcnt = 5

        wspace = w / fcnt
        x = (wspace * f) + (wspace / 2) - (fw / 2)

        y = h - fh

        if f == 7:
            x = 0
            y += 16

        return x, y

    def update(self):
        self.pressed = self.guitar.shape, self.guitar.strumup, self.guitar.strumdown

    def draw(self):
        self._image.fill("clear")

        if self.pressed is None:
            return

        if self.guitar.strumup:
            strum_image = self.strum_image
            rect = strum_image.get_rect()
            rect.bottomleft = self._image.get_rect().bottomleft
            self._image.blit(strum_image, rect)

        if self.guitar.strumdown:
            strum_image = pygame.transform.flip(self.strum_image, True, False)
            rect = strum_image.get_rect()
            rect.bottomright = self._image.get_rect().bottomright
            self._image.blit(strum_image, rect)

        for n, f in enumerate(self.guitar.shape):
            if f:
                self._image.blit(get_sprite("note", n), self.get_fret_pos(n))

        self._image.set_alpha(self.opacity)

    @property
    def image(self) -> Surface:
        # Don't rerender what we just rendered
        to_draw = self.pressed, self.guitar.strumup, self.guitar.strumdown
        if to_draw != self.last_drawn:
            self.draw()
            self.last_drawn = to_draw
        return self._image
