from __future__ import annotations

from typing import List

from pygame import joystick
from pygame.constants import JOYAXISMOTION, JOYBUTTONDOWN, JOYBUTTONUP, JOYHATMOTION, KEYDOWN, KEYUP

KBID = -1


# TODO: Detect instrument type
# TODO: Inject instrument events
# TODO: Auto-connect instruments
# TODO: Gracefully handle disconnected instruments
# TODO: Detect player number
class Instrument:
    instruments = {}

    def __init__(self, joydev):
        self._joydev = joydev  # Required to prevent pygame from deleting the joystick
        self._events: List[InstrumentEvent] = []

    @classmethod
    def connect(cls, joynum: int):
        if joynum == KBID:
            joydev = None
            instid = KBID
        else:
            joydev = joystick.Joystick(joynum)
            instid = joydev.get_instance_id()

        if instid not in cls.instruments:
            cls.instruments[instid] = cls(joydev)

        return cls.instruments[instid]

    def add_event(self, event: InstrumentEvent):
        self._events.append(event)

    def get_events(self) -> List[InstrumentEvent]:
        events = self._events.copy()
        self._events.clear()
        return events

    @property
    def debug(self) -> str:
        raise NotImplementedError()

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @classmethod
    def get_count(cls):
        return joystick.get_count()

    @classmethod
    def update(cls, tracktime, events):
        if not events:
            return

        instruments = {instid: [] for instid in cls.instruments.keys()}

        for e in events:
            if e.type in (JOYBUTTONDOWN, JOYBUTTONUP, JOYAXISMOTION, JOYHATMOTION):
                instid = e.instance_id
            elif e.type in (KEYDOWN, KEYUP):
                instid = KBID
            else:
                continue
            if instid in instruments:
                instruments[instid].append(e)

        for instid, inst_events in instruments.items():
            if not inst_events:
                continue
            cls.instruments[instid].update(tracktime, inst_events)


class InstrumentEvent:
    def __init__(self, ticks, name):
        self.ticks = ticks
        self.name = name

    def __str__(self):
        return self.name
