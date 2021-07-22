from charm.prototyping.hitdetection.accuracyviewer import AccuracyViewer
from charm.lib.instruments.instrument import Instrument, InstrumentEvent
from typing import List, Tuple

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


class ChordTape(BufferedTape):
    def __init__(self, items: List, tapeattr: str, scanner_width: float) -> None:
        super().__init__(items, tapeattr, scanner_width)
        self.missed_events = []

    def set_position(self, position: float):
        if position < self.current_position:
            self.jump_to(position - self.scanner_width)
        self.current_position = position
        self.current_items.extend(self.tape.get_items(position + self.scanner_width))
        while self.current_items and self.current_position - self.scanner_width > getattr(self.current_items[0], "start"):
            self.missed_events.append(self.current_items.pop(0))


class ScoreCalculator:
    def __init__(self, chart: Chart, guitar: Guitar):
        self.chart = chart
        self.song = self.chart.song
        self.guitar = guitar
        self._hitwindow = 0.07

        self.chord_tape = ChordTape(self.chart.chords, "start", self._hitwindow)
        self.input_tape = InputTape(self.guitar, self._hitwindow)

        self._events = []

        self.streak_end = None
        self.streak_bucket = []

        self.score = 0
        self.streak = 0
        self.accuracies = []
        self.multiplier = 1

        self.accuracyviewer = AccuracyViewer()

    def update(self, time):
        self.chord_tape.set_position(time)
        self.input_tape.set_position(time)

        bad_indexes = [i for i, n in enumerate(self.input_tape.current_events) if n.name != "STRUM_ON"]
        for index in reversed(bad_indexes):
            self.input_tape.current_events.pop(index)

        remove_chords = []

        for c, chord in enumerate(self.chord_tape.current_items):
            for i, inp in enumerate(self.input_tape.current_events):
                strum_shape = inp.shape
                if self.is_hit(chord, strum_shape):
                    remove_chords.append(c)
                    self.input_tape.current_events.pop(i)
                    event = ChordHit(inp.tracktime, chord.start)
                    self._events.append(event)
                    self.accuracies.append(event.offset)
                    self.accuracyviewer.hit(event.offset)
                    self.score += 1
                    self.streak_bucket.append(chord.id)
                    break

        for chordindex in reversed(remove_chords):
            self.chord_tape.current_items.pop(chordindex)

    def is_hit(self, chord, input_shape):
        if chord.flag == "note":
            if len(chord.notes) > 1:
                return input_shape == tuple(chord.shape)
            else:
                return chord.notes[0].fret == anchored_shape(input_shape)


def anchored_shape(shape: Tuple[bool]):
    for i, k in enumerate(reversed(shape)):
        if k:
            return (len(shape) - 1) - i
    return None


# --- EVENTS ---


class ScoreEvent:
    def __init__(self, seconds):
        self.seconds = seconds

    def __lt__(self, other):
        self.seconds < other.seconds

    def __eq__(self, other):
        self.seconds == other.seconds

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self.seconds}>"


class AccurateScoreEvent(ScoreEvent):
    def __init__(self, seconds, target: float):
        super().__init__(seconds)
        self.target = target

    @property
    def offset(self):
        return self.seconds - self.target


class ChordMissed(ScoreEvent):
    def __init__(self, seconds):
        super().__init__(seconds)


class ChordHit(AccurateScoreEvent):
    def __init__(self, seconds, target: int):
        super().__init__(seconds, target)


class SustainBreak(ScoreEvent):
    def __init__(self, seconds):
        super().__init__(seconds)


class StarPowerActivate(ScoreEvent):
    def __init__(self, seconds):
        super().__init__(seconds)


class ExtraneousInput(ScoreEvent):
    def __init__(self, seconds):
        super().__init__(seconds)
