from typing import Iterable

from charm.lib.instruments.instrument import Instrument


class Input:
    def __init__(self, time, events: Iterable) -> None:
        self.time = time
        self.events = set(events)


class InputRecorder:
    def __init__(self, instrument: Instrument):
        self.instrument = instrument

        # People probably shouldn't touch this.
        self._inputs = []

    def update(self, tracktime):
        ...

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

            return [i for i in self._inputs if start <= i.time < stop][::step]

        return self._inputs[value]

    def __setitem__(self, key, value):
        raise PermissionError("Don't use this like that, please. (__setitem__ on a InputRecorder).")
