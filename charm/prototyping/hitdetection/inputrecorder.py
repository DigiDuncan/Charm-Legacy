from collections import defaultdict, deque
from typing import Dict, List, Literal

from charm.lib.instruments.instrument import Instrument

Seconds = float
StateName = Literal[
    "green",
    "red",
    "yellow",
    "blue",
    "orange",
    "start",
    "select",
    "strum",
    "tilt",
    "whammy"
]
EventName = Literal[
    "green_on",
    "red_on",
    "yellow_on",
    "blue_on",
    "orange_on",
    "start_on",
    "select_on",
    "strum_on",
    "tilt_on",
    "whammy_on",
    "green_off",
    "red_off",
    "yellow_off",
    "blue_off",
    "orange_off",
    "start_off",
    "select_off",
    "strum_off",
    "tilt_off",
    "whammy_off"
]


class Input:
    def __init__(self, start: Seconds, events: List[EventName], state: Dict[StateName, bool]) -> None:
        self.start = start
        self.events = events
        self.state = state

    def toJSON(self):
        return {
            "start": self.start,
            "events": self.events,
            "state": self.state
        }

    @classmethod
    def fromJSON(self, data):
        inp = Input()
        inp.start = data["start"]
        inp.events = data.get("events", [])
        inp.state = data.get("state", {})


def make_event(key: str, state: bool) -> str:
    ON_OFF = {True: "on", False: "off"}
    return f"{key}_{ON_OFF[state]}"


class InputRecorder:
    def __init__(self, instrument: Instrument):
        self.instrument = instrument
        self._tilt_threshold = 0.5
        self._whammy_threshold = 0.05
        self._whammy_delay = 0.5

        self._whammy_data = deque([0] * 5, 5) # TODO: This is average last 5 frames. Should be average [?] ms.
        self._whammy_last_messed_with = 0 # TODO: This should probably default to None

        # People probably shouldn't touch this.
        self._inputs: List[Input] = []
        self._last_state: Dict[StateName, bool] = defaultdict(bool)

    def is_whammy_messed_with(self) -> bool:
        return sum(abs(b - a) for a, b in zip(list(self._whammy_data)[:-1], list(self._whammy_data)[1:])) > self._whammy_threshold

    def update(self, tracktime: Seconds):
        raw_state = defaultdict(bool)
        for e in self.instrument.get_events():
            print(e)

        self._whammy_data.append(raw_state["whammy"])
        if self.is_whammy_messed_with():
            self._whammy_last_messed_with = tracktime

        state: Dict[StateName, bool] = {
            "green": raw_state["green"],
            "red": raw_state["red"],
            "yellow": raw_state["yellow"],
            "blue": raw_state["blue"],
            "orange": raw_state["orange"],
            "start": raw_state["start"],
            "select": raw_state["select"],
            "strum": raw_state["strumup"] or raw_state["strumdown"],
            "tilt": raw_state["tilt"] >= self._tilt_threshold,
            "whammy": tracktime <= self._whammy_last_messed_with + self._whammy_delay
        }
        last_state = self._last_state

        # Process events.
        # TODO: Agnosticism.

        if state == last_state:
            return

        self._last_state = state

        curr_events: List[EventName] = []
        for evt, val in state.items():
            if last_state[evt] == val:
                continue
            suffix = "on" if val else "off"
            curr_events.append(f"{evt}_{suffix}")

        self._inputs.append(Input(tracktime, curr_events, state))

        # if curr_events:
        #    print(f"{round(tracktime, 3):>9} {curr_events}")

    @property
    def inputs(self):
        return self._inputs

    def __len__(self):
        return len(self._inputs)

    def inputstoJSON(self):
        return [i.toJSON() for i in self._inputs]

    def inputsfromJSON(self, data):
        self._inputs = [Input.fromJSON(d) for d in data]
