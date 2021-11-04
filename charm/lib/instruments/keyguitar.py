from typing import Literal
from charm.lib.instruments.guitar import Guitar
from nygame import Coord
from pygame.constants import KEYDOWN, KEYUP, K_DOWN, K_LEFT, K_LEFTBRACKET, K_LSHIFT, K_RETURN, K_RIGHT, K_RIGHTBRACKET, K_RSHIFT, K_SPACE, K_UP, K_i, K_o, K_p, K_x, K_z
from .instrument import KBID


def tristate(a: bool, b: bool) -> Literal[-1, 0, 1]:
    if a == b:
        return 0
    elif a:
        return -1
    elif b:
        return 1


class Keyguitar(Guitar):
    def __init__(self, joydev):
        super().__init__(joydev)
        self._Z = False
        self._UP = False
        self._X = False
        self._DOWN = False
        self._LEFT = False
        self._RIGHT = False
        self._LSHIFT = False
        self._RSHIFT = False

    @classmethod
    def connect(self):
        return super().connect(KBID)

    def update(self, tracktime, events):
        for e in events:
            if e.type in (KEYDOWN, KEYUP):
                val = e.type == KEYDOWN
                if e.key == K_i:
                    self._frets[0] = val
                    # FRET_ON/FRET_OFF
                elif e.key == K_o:
                    self._frets[1] = val
                    # FRET_ON/FRET_OFF
                elif e.key == K_p:
                    self._frets[2] = val
                    # FRET_ON/FRET_OFF
                elif e.key == K_LEFTBRACKET:
                    self._frets[3] = val
                    # FRET_ON/FRET_OFF
                elif e.key == K_RIGHTBRACKET:
                    self._frets[4] = val
                    # FRET_ON/FRET_OFF
                elif e.key == K_SPACE:
                    self._select = val
                    # STAR_ON/STAR_OFF
                elif e.key == K_RETURN:
                    self._start = val
                    # START_ON/START_OFF
                elif e.key == K_z:
                    self._Z = val
                elif e.key == K_UP:
                    self._UP = val
                elif e.key == K_x:
                    self._X = val
                elif e.key == K_DOWN:
                    self._DOWN = val
                elif e.key == K_LEFT:
                    self._LEFT = val
                elif e.key == K_RIGHT:
                    self._RIGHT = val
                elif e.key == K_LSHIFT:
                    self._LSHIFT = val
                elif e.key == K_RSHIFT:
                    self._RSHIFT = val

        up = self._Z or self._UP
        down = self._X or self._DOWN
        left = self._LEFT
        right = self._RIGHT
        x = tristate(left, right)
        y = tristate(down, up)
        # STRUM_ON/STRUM_OFF
        # JOY_ON/JOY_OFF

        joy = Coord(x, y)
        whammy = int(self._LSHIFT or self._RSHIFT)
        # WHAMMY_ON/WHAMMY_OFF

        self._joy = joy
        self._whammy = whammy
