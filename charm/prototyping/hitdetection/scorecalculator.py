from collections import deque
from math import ceil
from charm.lib.utils import clamp
from charm.prototyping.hitdetection.accuracyviewer import AccuracyViewer
from charm.lib.instruments.instrument import Instrument, InstrumentEvent
from typing import List, Tuple

from charm.song import Chart
from charm.lib.instruments.guitar import Guitar, StrumEvent
from charm.lib.tape import BufferedTape


# --- FUNCTIONS ---
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


class SPChordHit(ChordHit):
    def __init__(self, seconds, target, phrase_num: int, start: bool, end: bool):
        super().__init__(seconds, target)
        self.phrase_num = phrase_num
        self.start = start
        self.end = end


class SPChordMissed(ChordMissed):
    def __init__(self, seconds, phrase_num: int):
        super().__init__(seconds)
        self.phrase_num = phrase_num


class WhammyStart(ScoreEvent):
    def __init__(self, seconds):
        super().__init__(seconds)


class WhammyEnd(ScoreEvent):
    def __init__(self, seconds):
        super().__init__(seconds)


# --- OBJECTS ---
class InputTape:
    def __init__(self, instrument: Instrument, scanner_width: float) -> None:
        self.instrument = instrument
        self.scanner_width = scanner_width * 2
        self.current_events: List[InstrumentEvent] = []
        self.current_position = 0
        self.missed_events = []

    def set_position(self, position: float):
        self.current_position = position
        self.current_events.extend(self.instrument.get_events())
        while self.current_events and self.current_position - self.scanner_width > getattr(self.current_events[0], "tracktime"):
            self.missed_events.append(self.current_events.pop(0))

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
        while self.current_items and self.current_position > getattr(self.current_items[0], "start") + self.scanner_width:
            self.missed_events.append(self.current_items.pop(0))


class HitManager:
    def __init__(self, chart: Chart, guitar: Guitar):
        self.chart = chart
        self.guitar = guitar
        self._hitwindow = 0.07

        self.chord_tape = ChordTape(self.chart.chords, "start", self._hitwindow)
        self.input_tape = InputTape(self.guitar, self._hitwindow)

        self._queued_events = []
        self._events = []

        self.accuracyviewer = AccuracyViewer()

    def update(self, time):
        self.chord_tape.set_position(time)
        self.input_tape.set_position(time)

        # TODO: This is super temporary and assumes strums are like finalizers
        bad_indexes = [i for i, n in enumerate(self.input_tape.current_events) if n.name != "STRUM_ON"]
        for index in reversed(bad_indexes):
            self.input_tape.current_events.pop(index)

        remove_chords = []

        # Match chords to inputs
        for c, chord in enumerate(self.chord_tape.current_items):
            for i, inp in enumerate(self.input_tape.current_events):
                if self.is_hit(chord, inp):
                    remove_chords.append(c)
                    self.input_tape.current_events.pop(i)
                    event = ChordHit(inp.tracktime, chord.start)
                    self._queued_events.append(event)
                    self.accuracyviewer.hit(event.offset)
                    break

        # Remove hit chords
        for chordindex in reversed(remove_chords):
            self.chord_tape.current_items.pop(chordindex)

        # Process missed notes
        for missed_chord in reversed(self.chord_tape.missed_events):
            self._queued_events.append(ChordMissed(time))
            self.chord_tape.missed_events.remove(missed_chord)
            self.accuracyviewer.miss()

        # Process overstrums
        for missed_strum in reversed(self.input_tape.missed_events):
            if isinstance(missed_strum, StrumEvent):
                self._queued_events.append(ExtraneousInput(time))
            self.input_tape.missed_events.remove(missed_strum)

        # Process queued events
        self.process_queue()

    def process_queue(self):
        self._events = self._queued_events.copy()
        self._queued_events.clear()

    def is_hit(self, chord, inp):
        # if chord.flag == "note":  TODO: all notes are strum rn
        if abs(chord.start - inp.tracktime) > self._hitwindow:
            return False
        if len(chord.notes) > 1:
            return inp.shape == tuple(chord.shape)
        else:
            return chord.notes[0].fret == anchored_shape(inp.shape)

    def get_events(self) -> List[ScoreEvent]:
        events = self._events.copy()
        self._events.clear()
        return events


class ScoreCalculator:
    def __init__(self, hitmanager: HitManager) -> None:
        self.hitmanager = hitmanager
        self.last_time = 0

        self.base_score = 50

        self.score = 0
        self.streak = 0
        self.current_sp_phrase = None
        self.star_power = 0.0
        self.star_power_active = False

        self.states: deque[tuple] = deque([(0, 0, 0)])

    @property
    def multiplier(self):
        m = clamp(1, ceil(self.streak / 10), 4)
        return m * 2 if self.star_power_active else m

    def update(self, tracktime):
        events = self.hitmanager.get_events()

        # rewinding
        if tracktime < self.last_time:
            events = []
            while self.states[-1][0] > tracktime:
                self.states.pop()
            _, self.score, self.streak = self.states[-1]

        # score new events in order
        for event in events:
            if isinstance(event, ChordHit):
                self.streak += 1
                self.score += self.base_score * self.multiplier
                if isinstance(event, SPChordHit):
                    if self.current_sp_phrase is None and event.start:
                        self.current_sp_phrase = event.phrase_num
                    if self.current_sp_phrase == event.phrase_num and event.end:
                        self.current_sp_phrase = None
                        self.star_power = max(self.star_power + 0.25, 1)
            elif isinstance(event, ChordMissed) or isinstance(event, ExtraneousInput):
                self.streak = 0
                self.current_sp_phrase = None
            elif isinstance(event, StarPowerActivate):
                if self.star_power >= 0.5:
                    self.star_power_active = True

        # save novel states
        _, oldscore, oldstreak = self.states[-1]
        if oldscore != self.score or oldstreak != self.streak:
            self.states.append((tracktime, self.score, self.streak))

        self.last_time = tracktime
