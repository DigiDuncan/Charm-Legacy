from nygame import Coord
from pygame.constants import JOYAXISMOTION, JOYBUTTONDOWN, JOYBUTTONUP, JOYHATMOTION
from .instrument import Instrument


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


class Guitar(Instrument):
    def __init__(self, rawjoy):
        super().__init__(rawjoy)
        self._frets = [False] * 5
        self._select = False
        self._start = False
        self._joy = Coord(0, 0)
        self._tilt = 0
        self._whammy = 0

    def handle_event(self, e):
        if e.type == JOYHATMOTION:
            # Strum bar / Joystick
            self._joy = Coord(*e.value)
        elif e.type == JOYBUTTONDOWN or e.type == JOYBUTTONUP:
            state = e.type == JOYBUTTONDOWN
            btn = e.button
            if btn in (0, 1, 2, 3, 4):
                btn = [0, 1, 3, 2, 4][btn]
                self._frets[btn] = state
            elif btn == 6:
                self._select = state
            elif btn == 7:
                self._start = state
        elif e.type == JOYAXISMOTION:
            if e.axis == 3:
                self._tilt = from_raw_tilt(e.value)
            elif e.axis == 2:
                self._whammy = from_raw_whammy(e.value)

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
    def debug(self):
        fretstr = ''.join(str(int(f)) for f in self._frets)
        btnstr = f"{int(self._select)}{int(self._start)}"
        joystr = dir2arrow[self._joy.xy]
        tiltstr = num2bar(self._tilt, "o")
        whamstr = num2bar(self._whammy, "/")
        return f"[ {fretstr} {btnstr} ]   [ {joystr} ]   [{tiltstr}]   [{whamstr}]"
