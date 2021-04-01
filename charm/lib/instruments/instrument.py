from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import nygame

from pygame import joystick


def init(game: nygame.Game):
    joystick.init()
    game.register_eventhandler(Instrument.handle_event)


def get_count():
    return joystick.get_count()


# TODO: Detect instrument type
# TODO: Inject instrument events
# TODO: Auto-connect instruments
# TODO: Gracefully handle disconnected instruments
# TODO: Detect player number
class Instrument:
    instruments = {}

    @classmethod
    def connect(cls, joynum):
        joy = joystick.Joystick(joynum)
        joyid = joy.get_instance_id()

        if joyid not in cls.instruments:
            cls.instruments[joyid] = cls(joy)

        return cls.instruments[joyid]

    @property
    def state(self):
        raise NotImplementedError

    def __init__(self, rawjoy):
        self._rawjoy = rawjoy

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @classmethod
    def handle_event(cls, e):
        joyid = getattr(e, "instance_id", None)
        if joyid not in cls.instruments:
            return
        cls.instruments[joyid].handle_event(e)
