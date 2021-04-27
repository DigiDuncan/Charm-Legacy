from charm.lib.instruments.guitar import FretEvent, Guitar, JoyEvent, StarEvent, StartEvent, StrumEvent, WhammyMotion
from nygame import Coord
from pygame.constants import JOYAXISMOTION, JOYBUTTONDOWN, JOYBUTTONUP, JOYHATMOTION


def from_raw_tilt(value):
    return value * -1


def from_raw_whammy(value):
    return (value + 1) / 2


class Wiitar(Guitar):
    def __init__(self, joydev):
        super().__init__(joydev)
        self._tilted = False

    def update(self, tracktime, events):
        old_star = self.star

        for e in events:
            if e.type == JOYHATMOTION:
                # Strum bar / Joystick
                old_joy = self._joy
                self._joy = Coord(e.value)
                if self._joy.x != old_joy.x:
                    state = self._joy.x != 0
                    dirnum = self._joy.x if state else old_joy.x
                    dirname = {-1: "LEFT", 1: "RIGHT"}[dirnum]
                    self.add_event(JoyEvent(tracktime, state, dirname))
                if self._joy.y != old_joy.y:
                    state = self._joy.y != 0
                    dirnum = self._joy.y if state else old_joy.y
                    dirname = {-1: "DOWN", 1: "UP"}[dirnum]
                    self.add_event(JoyEvent(tracktime, state, dirname))
                    self.add_event(StrumEvent(tracktime, state))
                # STRUM_ON EVENT {direction=up/down}
                # STRUM_OFF EVENT
                # JOY_ON {direction=up/down/left/right}
                # JOY_OFF {direction=up/down/left/right}
            elif e.type == JOYBUTTONDOWN or e.type == JOYBUTTONUP:
                state = e.type == JOYBUTTONDOWN
                btn = e.button
                if btn in (0, 1, 2, 3, 4):
                    btn = [0, 1, 3, 2, 4][btn]
                    self._frets[btn] = state
                    self.add_event(FretEvent(tracktime, state, btn + 1))
                elif btn == 6:
                    self._star = state
                elif btn == 7:
                    self._start = state
                    self.add_event(StartEvent(tracktime, state))
                # FRET_ON EVENT {fretnumber, fretcolor}
                # FRET_OFF EVENT {fretnumber, fretcolor}
                # STAR_ON EVENT
                # STAR_OFF EVENT
            elif e.type == JOYAXISMOTION:
                if e.axis == 3:
                    print(e)
                    tilt_pos = from_raw_tilt(e.value)
                    tilted = tilt_pos > 0.75
                    self._tilted = tilted
                elif e.axis == 2:
                    self._whammy_pos = from_raw_whammy(e.value)
                    self.add_event(WhammyMotion(tracktime, self._whammy_pos))
                    # WHAMMY_MOTION EVENT {value}
                # WHAMMY_ON EVENT
                # WHAMMY_OFF EVENT
        if old_star != self.star:
            self.add_event(StarEvent(tracktime, self.star))

    @property
    def star(self):
        return self._star or self._tilted
