from __future__ import annotations

from itertools import groupby
from functools import cache, total_ordering
from typing import List


# Abstract class
@total_ordering
class SongEvent():
    def __init__(self, song, tick_start, tick_length=None):
        self.song = song
        self.tick_start = tick_start
        self.tick_length = tick_length or 0

    @property
    def start(self):
        return self.song.tempo_calc.ticks_to_secs(self.tick_start)

    @property
    def tick_end(self):
        return self.tick_start + self.tick_length

    @property
    def end(self):
        return self.song.tempo_calc.ticks_to_secs(self.tick_end)

    @property
    def length(self):
        return self.end - self.start

    def __eq__(self, other):
        return (self.tick_start, self.tick_length) == (other.tick_start, other.tick_length)

    def __lt__(self, other):
        return (self.tick_start, self.tick_length) < (other.tick_start, other.tick_length)


# Abstract class
class ChartEvent(SongEvent):
    def __init__(self, song, chart, tick_start, tick_length=None):
        super().__init__(song, tick_start, tick_length)
        self.chart = chart


class Note(ChartEvent):
    def __init__(self, song, chart, tick_start, kind, tick_length):
        super().__init__(song, chart, tick_start, tick_length)
        self.kind = kind

    def __eq__(self, other):
        return (self.tick_start, self.kind, self.tick_length) == (other.tick_start, other.kind, other.tick_length)

    def __lt__(self, other):
        return (self.tick_start, self.kind, self.tick_length) < (other.tick_start, other.kind, other.tick_length)

    def __repr__(self):
        return f"<{self.__class__.__name__}(start = {self.start}, kind = {self.kind}), length = {self.length})>"


class SPEvent(ChartEvent):
    def __init__(self, song, chart, tick_start, kind, tick_length):
        super().__init__(song, chart, tick_start, tick_length)
        self.kind = kind  # Unused? Seems to always be 2...

    def __eq__(self, other):
        return (self.tick_start, self.kind, self.tick_length) == (other.tick_start, other.kind, other.tick_length)

    def __lt__(self, other):
        return (self.tick_start, self.kind, self.tick_length) < (other.tick_start, other.kind, other.tick_length)

    def __repr__(self):
        return f"<{self.__class__.__name__}(start = {self.start}, kind = {self.kind}), length = {self.length})>"


class Event(ChartEvent):
    def __init__(self, song, chart, tick_start, data):
        super().__init__(song, chart, tick_start)
        self.data = data

    def __repr__(self):
        return f"<{self.__class__.__name__}(start = {self.start}, data = {self.data})>"


class Chord(ChartEvent):
    def __init__(self, song, chart, mode, notes: List[Note]):
        tick_start = notes[0].tick_start
        tick_length = max(n.tick_length for n in notes)
        super().__init__(song, chart, tick_start, tick_length)
        self.mode = mode
        self.notes = notes
        self.shape = tuple(n.kind for n in notes)

    def __repr__(self):
        return f"<{self.__class__.__name__}(start = {self.start}, shape = {self.shape}, length = {self.length})>"


class Chart:
    def __init__(self, song, instrument, difficulty):
        self.song = song
        self.instrument = instrument
        self.difficulty = difficulty
        self.notes = []
        self.star_powers = []
        self.events = []
        self.chords = []

    def finalize(self):
        self.notes.sort()
        self.star_powers.sort()
        self.events.sort()
        self.chords.sort()

    def __hash__(self):
        return hash((
            tuple(self.notes),
            tuple(self.star_powers),
            tuple(self.events)
        ))

    def __repr__(self):
        return f"<{self.__class__.__name__}(difficulty = {self.difficulty}, instrument = {self.instrument}, chords = {len(self.chords)}, notes = {len(self.notes)}, star_powers = {len(self.star_powers)}, events = {len(self.events)})>"


class Song:
    def __init__(self):
        self.events = []
        self.charts = {}
        self.timesigs = []
        self.tempo_calc = None
        self.full_name = None
        self.title = None
        self.subtitle = None
        self.alt_title = None
        self.artists = None
        self.album = None
        self.year = None
        self.charter = None
        self.offset = None
        self.resolution = None
        self.difficulty = None
        self.previewstart = None
        self.previewend = None
        self.genre = None
        self.mediastream = None
        self.musicstream = None

    def finalize(self):
        self.events.sort()
        self.timesigs.sort()
        self.tempo_calc.finalize()

    def __hash__(self):
        return hash((
            tuple(self.tempo_calc),
            tuple(self.events),
            tuple(self.charts.values())
        ))

    def __repr__(self):
        return f"<{self.__class__.__name__}(name = {self.full_name!r}, tempos = {len(self.tempo_calc.tempos)}, events = {len(self.events)}, charts = {self.charts})>"


class TempoEvent(SongEvent):
    def __init__(self, song, tick_start, ticks_per_sec):
        super().__init__(song, tick_start)
        self.ticks_per_sec = ticks_per_sec


class TempoCalculator:
    def __init__(self, tempos):
        self.ticks_to_secs = cache(self.ticks_to_secs)
        self.tempos = sorted(tempos)

    def finalize(self):
        for tempo in self.tempos:
            self.ticks_to_secs(tempo.tick_start)

    def ticks_to_secs(self, ticks):
        if ticks == 0:
            return 0
        curr_tempo = next(tempo for tempo in self.tempos if tempo.tick_start <= ticks)
        diff_ticks = ticks - curr_tempo.tick_start
        diff_seconds = diff_ticks / curr_tempo.ticks_per_sec
        seconds = curr_tempo.start + diff_seconds
        return seconds

    def __hash__(self):
        return hash(tuple(self.tempos))
