from nygame import Coord
from pygame.constants import KEYDOWN, KEYUP, K_DOWN, K_LEFT, K_LEFTBRACKET, K_LSHIFT, K_RETURN, K_RIGHT, K_RIGHTBRACKET, K_RSHIFT, K_SPACE, K_UP, K_i, K_o, K_p, K_x, K_z
from .instrument import Instrument, KBID

arrows = " ←→↑↓↖↗↘↙"
dir2arrow = {
    (-1, 1): arrows[5],
    (0, 1): arrows[3],
    (1, 1): arrows[6],
    (-1, 0): arrows[1],
    (0, 0): arrows[0],
    (1, 0): arrows[2],
    (-1, -1): arrows[8],
    (0, -1): arrows[4],
    (1, -1): arrows[7]
}


def num2bar(num, token, w=20):
    hardnum = int(num * (w - 1))
    left = hardnum + 1
    right = w - left
    return format(token, f">{left}") + (right * " ")


def from_raw_tilt(value):
    return value * -1


def from_raw_whammy(value):
    return (value + 1) / 2


class Keyboard(Instrument):
    def __init__(self):
        self._frets = [False] * 5
        self._select = False
        self._start = False
        self._tilt = 0

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
                elif e.key == K_o:
                    self._frets[1] = val
                elif e.key == K_p:
                    self._frets[2] = val
                elif e.key == K_LEFTBRACKET:
                    self._frets[3] = val
                elif e.key == K_RIGHTBRACKET:
                    self._frets[4] = val
                elif e.key == K_SPACE:
                    self._select = val
                elif e.key == K_RETURN:
                    self._start = val
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

    @property
    def _joy(self):
        up = self._Z or self._UP
        down = self._X or self._DOWN
        left = self._LEFT
        right = self._RIGHT

        x = 0
        if left and not right:
            x = -1
        elif right and not left:
            x = 1

        y = 0
        if down and not up:
            y = -1
        elif up and not down:
            y = 1

        return Coord(x, y)

    @property
    def _whammy(self):
        return 1 if self._LSHIFT or self._RSHIFT else 0

    @property
    def fret1(self):
        return self._frets[0]

    green = fret1

    @property
    def fret2(self):
        return self._frets[1]

    red = fret2

    @property
    def fret3(self):
        return self._frets[2]

    blue = fret3

    @property
    def fret4(self):
        return self._frets[3]

    yellow = fret4

    @property
    def fret5(self):
        return self._frets[4]

    orange = fret5

    @property
    def shape(self):
        return (self.fret1, self.fret2, self.fret3, self.fret4, self.fret5)

    @property
    def select(self):
        return self._select

    minus = starpower = select

    @property
    def start(self):
        return self._start

    plus = start

    @property
    def strumbar(self):
        return self._joy[1]

    @property
    def strumup(self):
        return self.strumbar == 1

    @property
    def strumdown(self):
        return self.strumbar == -1

    @property
    def joy(self):
        return self._joy

    @property
    def tilt(self):
        return self._tilt

    @property
    def whammy(self):
        return self._whammy

    @property
    def state(self):
        return {
            "green": self.green,
            "red": self.red,
            "yellow": self.yellow,
            "blue": self.blue,
            "orange": self.orange,
            "strumup": self.strumup,
            "strumdown": self.strumdown,
            "joy": self.joy,
            "tilt": self.tilt,
            "whammy": self.whammy,
            "start": self.start,
            "select": self.select
        }

    @property
    def debug(self):
        fretstr = ''.join(str(int(f)) for f in self._frets)
        btnstr = f"{int(self._select)}{int(self._start)}"
        joystr = dir2arrow[tuple(self._joy)]
        tiltstr = num2bar(self._tilt, "o")
        whamstr = num2bar(self._whammy, "/")
        return f"[ {fretstr} {btnstr} ]   [ {joystr} ]   [{tiltstr}]   [{whamstr}]"
