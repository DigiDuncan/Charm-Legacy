from charm.lib.instruments.instrument import Instrument, InstrumentEvent
from typing import List

from charm.song import Chart
from charm.lib.instruments.guitar import Guitar
from charm.lib.tape import BufferedTape


class InputTape:
    def __init__(self, instrument: Instrument, scanner_width: float) -> None:
        self.instrument = instrument
        self.scanner_width = scanner_width
        self.current_events: List[InstrumentEvent] = []
        self.current_position = 0

    def set_position(self, position: float):
        self.current_position = position
        self.current_events.extend(self.instrument.get_events())
        while self.current_events and self.current_position - self.scanner_width > getattr(self.current_events[0], "tracktime"):
            self.current_events.pop(0)

    def jump_to(self, position: float):
        self.current_position = position
        self.current_events = []
        self.instrument.get_events()  # dump


class ScoreCalculator:
    def __init__(self, chart: Chart, guitar: Guitar):
        self.chart = chart
        self.song = self.chart.song
        self.guitar = guitar
        self._hitwindow = 0.07

        self.chord_tape = BufferedTape(self.chart.chords, "start", self._hitwindow)
        self.input_tape = InputTape(self.guitar, self._hitwindow)

        self._events = []

        self.score = 0
        self.streak = 0
        self.accuracies = []
        self.multiplier = 1

    def update(self, time):
        pass

# --- EVENTS ---


class ScoreEvent:
    def __init__(self, ticks: int):
        self.ticks = ticks

    def __lt__(self, other):
        self.ticks < other.ticks

    def __eq__(self, other):
        self.ticks == other.ticks

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self.ticks}>"


class AccurateScoreEvent(ScoreEvent):
    def __init__(self, ticks: int, target: int):
        super().__init__(ticks)
        self.target = target

    @property
    def offset(self):
        return self.ticks - self.target


class ChordMissed(ScoreEvent):
    def __init__(self, ticks: int):
        super().__init__(ticks)


class ChordHit(AccurateScoreEvent):
    def __init__(self, ticks: int, target: int):
        super().__init__(ticks, target)


class SustainBreak(ScoreEvent):
    def __init__(self, ticks: int):
        super().__init__(ticks)


class StarPowerActivate(ScoreEvent):
    def __init__(self, ticks: int):
        super().__init__(ticks)


class ExtraneousInput(ScoreEvent):
    def __init__(self, ticks: int):
        super().__init__(ticks)
