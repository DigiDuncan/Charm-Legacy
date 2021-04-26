from __future__ import annotations

from typing import Dict, List

from pygame import joystick
from pygame.constants import JOYAXISMOTION, JOYBUTTONDOWN, JOYBUTTONUP, JOYHATMOTION, KEYDOWN, KEYUP

KBID = -1

joystick.init()


# TODO: Detect instrument type
# TODO: Inject instrument events
# TODO: Auto-connect instruments
# TODO: Gracefully handle disconnected instruments
# TODO: Detect player number
class Instrument:
    instruments = {}

    def __init__(self):
        self._events: List[InstrumentEvent] = []

    @classmethod
    def connect(cls, joynum: int):
        if joynum == KBID:
            instid = KBID
        else:
            instid = joystick.Joystick(joynum).get_instance_id()

        if instid not in cls.instruments:
            cls.instruments[instid] = cls()

        return cls.instruments[instid]

    def add_event(self, event: InstrumentEvent):
        self._events.append(event)

    def get_events(self) -> List[InstrumentEvent]:
        events = self._events.copy()
        self._events.clear()
        return events

    @property
    def state(self) -> Dict[str, bool]:
        raise NotImplementedError

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
