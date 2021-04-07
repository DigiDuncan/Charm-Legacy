from collections import defaultdict
from typing import Iterable, List

from charm.lib.instruments.instrument import Instrument


class Input:
    def __init__(self, time, events: Iterable) -> None:
        self.time = time
        self.events = events

    def toJSON(self):
        return {"time": self.time,
                "events": self.events}

    @classmethod
    def fromJSON(self, data):
        inp = Input()
        inp.time = data["time"]
        inp.events = data.get("events", [])


class InputRecorder:
    def __init__(self, instrument: Instrument):
        self.instrument = instrument

        self._previous_state = defaultdict(bool)

        # People probably shouldn't touch this.
        self._inputs: List[Input] = []

    def update(self, tracktime):
        if self.instrument.state == self._previous_state:
            return
        else:
            # Process events.
            # TODO: Agnosticism.
            events = []
            for eventtype in ("green", "red", "yellow", "blue", "orange", "strumup", "strumdown", "start", "select"):
                if self._previous_state[eventtype] is False and self.instrument.state[eventtype] is True:
                    events.append(eventtype + "_on")
                if self._previous_state[eventtype] is True and self.instrument.state[eventtype] is False:
                    events.append(eventtype + "_off")
            for eventtype in ("joy", "tilt", "whammy"):
                if self._previous_state[eventtype] != self.instrument.state[eventtype]:
                    events.append({eventtype: self.instrument.state[eventtype]})
            self.add(tracktime, events)
            self._previous_state = self.instrument.state

    def add(self, time, events: Iterable):
        i = Input(time, events)
        self._inputs.append(i)

    def remove(self, time, end_time = None):
        if end_time:
            del self[time:end_time]
        else:
            del self[time]

    def __len__(self):
        return len(self._inputs)

    def __getitem__(self, value):
        if isinstance(value, slice):
            start, stop, step = value  # Always a 3-tuple.
            if start is None:
                start = 0
            if stop is None:
                stop = float('inf')

            ir = InputRecorder(self.instrument)
            ir._inputs = [i for i in self._inputs if start <= i.time < stop][::step]
            return ir

        return self._inputs[value]

    def __setitem__(self, key, value):
        raise PermissionError("Don't use this like that, please. (__setitem__ on a InputRecorder).")

    def inputstoJSON(self):
        return [i.toJSON() for i in self._inputs]

    def inputsfromJSON(self, data):
        self._inputs = [Input.fromJSON(d) for d in data]
