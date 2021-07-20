from typing import List

from nindex.index import Index
from charm.song import Chart, Chord
from charm.lib.instruments.guitar import Guitar


class Tape:
    def __init__(self, items: List, tapeattr: str) -> None:
        self.items = items
        self.tapeattr = tapeattr

        self._index = Index(items, self.tapeattr)

        self.current_index = 0
        self.current_position = 0

    def get_items(self, position: float):
        if position < self.current_position:
            self.jump_to(position)
        new_items = []
        self.current_position = position
        try:
            while getattr(self.items[self.current_index], self.tapeattr) <= position:
                new_items.append(self.items[self.current_index])
                self.current_index += 1
        except IndexError:
            pass
        return new_items

    def jump_to(self, position: float):
        self.current_index = self._index.lteq_index(position)


class BufferedTape:
    def __init__(self, items: List, tapeattr: str, scanner_width: float) -> None:
        self.items = items
        self.tapeattr = tapeattr
        self.scanner_width = scanner_width

        self.tape = Tape(self.items, self.tapeattr)

        self.current_items = []
        self.current_position = 0
        self.set_position(self.current_position)

    def set_position(self, position: float):
        if position < self.current_position:
            self.jump_to(position - self.scanner_width)
        self.current_position = position
        self.current_items.extend(self.tape.get_items(position + self.scanner_width))
        while self.current_items and self.current_position - self.scanner_width > getattr(self.current_items[0], "start"):
            self.current_items.pop(0)

    def jump_to(self, position: float):
        self.current_position = position
        self.current_items = []
        self.tape.jump_to(position)


class ScoreCalculator:
    def __init__(self, chart: Chart, guitar: Guitar):
        self.chart = chart
        self.song = self.chart.song
        self.guitar = guitar
        self._hitwindow = 0.07

        self.chord_tape = BufferedTape(self.chart.chords, "start", self._hitwindow)

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
