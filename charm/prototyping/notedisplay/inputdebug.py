from random import randint, shuffle

from charm.lib.instruments.instrument import Instrument

from nygame import DigiText as T
from pygame import Surface
from pygame.constants import SRCALPHA
from pygame.color import Color
import pygame.draw

HIT_WINDOW = 0.140  # 140ms

GREEN = Color(0x17f533ff)
RED = Color(0xf51717ff)
YELLOW = Color(0xf4d125ff)
BLUE = Color(0x2846f0ff)
ORANGE = Color(0xf37622ff)
PURPLE = Color(0xb913f8ff)
CYAN = Color(0x00CCFFFF)
CHARM = Color(0x55d790ff)
BLACK = Color(0x000000ff)
WHITE = Color(0xffffffff)
DARK_GRAY = Color(0x333333ff)

frets = [GREEN, RED, YELLOW, BLUE, ORANGE]


class InputDebug:
    def __init__(self, guitar: Instrument, *, size: tuple = (400, 150)):
        self.guitar = guitar  # VERY game unagnostic
        self.size = size
        self.opacity = 128
        self.state = None
        self.last_whammy = 0
        self.whammy = 0
        self.secs = 0
        self.last_secs = -1
        self.last_drawn = None
        self._image = Surface(size, SRCALPHA)
        self._image.fill(BLACK)
        self.noises = [Surface((1, 100)), Surface((1, 100)), Surface((1, 100)),
                       Surface((1, 100)), Surface((1, 100)), Surface((1, 100)),
                       Surface((1, 100)), Surface((1, 100)), Surface((1, 100)),
                       Surface((1, 100))]
        pixels = [(randint(0, 255), randint(0, 255), randint(0, 255), 255) for _ in range(100)]
        for n in self.noises:
            shuffle(pixels)
            for i in range(100):
                n.set_at((0, i), pixels[i])
        self.last_noise = 0

    def update(self, secs):
        self.last_secs = self.secs
        self.secs = secs
        self.state = self.guitar.shape, self.guitar.strumup, self.guitar.strumdown, self.guitar.star
        self.last_whammy = self.whammy
        self.whammy = self.guitar._whammy_pos
        self.draw()

    def draw(self):
        edge = self.size[0] - 1
        height = self.size[1]
        self._image.scroll(-1, 0)

        pygame.draw.line(self._image, BLACK, (edge, 0), (edge, height))

        if int(self.last_secs) < int(self.secs):
            pygame.draw.line(self._image, WHITE, (edge, 0), (edge, height))
            seconds = str(int(self.secs))
            st = T(seconds, font = "Lato Medium", size = 12, color = "white").render()
            dest = st.get_rect()
            dest.bottomright = self._image.get_rect().bottomright
            dest.left -= 2
            self._image.blit(st, dest)

        if self.last_secs >= self.secs:
            self._image.blit(self.noises[self.last_noise % 10], (edge, 0))
            self.last_noise += randint(0, 9)
            return

        if self.state is None:
            return

        for n, f in enumerate(self.guitar.shape):
            if f:
                linestart = (n * 20) + 10
                lineend = linestart + 19
                color = frets[n]
                pygame.draw.line(self._image, color, (edge, linestart), (edge, lineend))

        if self.guitar.strumup:
            pygame.draw.line(self._image, PURPLE, (edge, 0), (edge, 9))

        if self.guitar.strumdown:
            pygame.draw.line(self._image, PURPLE, (edge, 110), (edge, 119))

        if self.guitar.star:
            pygame.draw.line(self._image, CYAN, (edge, 0), (edge, 4))

        lwpos = 100 - int(self.last_whammy * 100) + 10
        wpos = 100 - int(self.whammy * 100) + 10
        pygame.draw.line(self._image, CHARM, (edge - 1, lwpos), (edge, wpos))

        # self._image.set_alpha(self.opacity)

    @property
    def image(self) -> Surface:
        return self._image
