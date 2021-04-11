from collections import defaultdict, deque
from typing import Dict, Iterable, List

from charm.lib.instruments.instrument import Instrument


class Input:
    def __init__(self, time, events: Iterable = [], states: Dict = {}) -> None:
        self.time = time
        self.events = events
        self.states = states

    def toJSON(self):
        return {"time": self.time,
                "events": self.events,
                "states": self.states}

    @classmethod
    def fromJSON(self, data):
        inp = Input()
        inp.time = data["time"]
        inp.events = data.get("events", [])
        inp.states = data.get("states", {})


class InputRecorder:
    def __init__(self, instrument: Instrument):
        self.instrument = instrument

        self._previous_state = defaultdict(bool)
        self._previous_tilt = 0
        self.previous_whammy = 0
        self._whammy_data = deque([0] * 4, 4)
        self._whammy_last_messed_with = 0
        self._previous_whammying = None
        self._whammying = False

        self.threshold = 0.01

        # People probably shouldn't touch this.
        self._inputs: List[Input] = []
        self._states: Dict[Dict] = {}

    def update(self, tracktime):
        self._states[tracktime] = self.instrument.state
        if self.instrument.state == self._previous_state:
            return
        else:
            # Process events.
            # TODO: Agnosticism.
            events = []
            for eventtype in ("green", "red", "yellow", "blue", "orange", "start", "select"):
                if self._previous_state[eventtype] is False and self.instrument.state[eventtype] is True:
                    events.append(eventtype + "_on")
                if self._previous_state[eventtype] is True and self.instrument.state[eventtype] is False:
                    events.append(eventtype + "_off")
            if ((self._previous_state["strumup"] is False and self.instrument.state["strumup"] is True)
               or (self._previous_state["strumdown"] is False and self.instrument.state["strumdown"] is True)):
                events.append("strum")

            if self._previous_tilt < 0.5 and self.instrument.state["tilt"] >= 0.5:
                events.append("tilt_on")
            if self._previous_tilt >= 0.5 and self.instrument.state["tilt"] < 0.5:
                events.append("tilt_off")
            self._previous_tilt = self.instrument.state["tilt"]

            self._whammy_data.append(abs(self.previous_whammy - self.instrument.state["whammy"]))
            if sum(self._whammy_data) >= self.threshold:
                self._whammy_last_messed_with = tracktime
            self.previous_whammy = self.instrument.state["whammy"]

            self._previous_whammying = self._whammying
            if tracktime - self._whammy_last_messed_with <= 0.5:
                self._whammying = True
            if tracktime - self._whammy_last_messed_with > 0.5:
                self._whammying = False

            if self._previous_whammying is False and self._whammying is True:
                events.append("whammy_on")
            if self._previous_whammying is True and self._whammying is False:
                events.append("whammy_off")

            self.add(tracktime, events, self.instrument.state)
        self._previous_state = self.instrument.state

        if events != []:
            print(f"{round(tracktime, 3):>9} {events}")
        if self.instrument.state != self._previous_state:
            print(self.instrument.state)

    @property
    def inputs(self):
        return self._inputs

    @property
    def states(self):
        return self._states

    def add(self, time, events: Iterable, states: Dict):
        i = Input(time, events, states)
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
            start, stop, step = value.start, value.stop, value.step  # Always a 3-tuple.
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
