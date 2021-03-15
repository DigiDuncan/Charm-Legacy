from __future__ import annotations

from itertools import groupby
from functools import total_ordering
from typing import List


@total_ordering
class TimeStamp:
    def __init__(self, song, ticks):
        self.song = song
        self.ticks = ticks

    @property
    def secs(self):
        return self.song.ticks_to_secs(self.ticks)

    def __lt__(self, other):
        return self.ticks < other.ticks

    def __repr__(self):
        return f"<TimeStamp(ticks = {self.ticks}, secs = {self.secs})>"


@total_ordering
class TimeDelta:
    def __init__(self, start: TimeStamp, tick_length):
        self._start = start
        self.tick_length = tick_length

    @property
    def start_ticks(self):
        return self._start.ticks

    @property
    def end_ticks(self):
        return self._start.ticks + self.tick_length

    @property
    def start(self):
        return self._start.secs

    @property
    def end(self):
        return self._start.song.ticks_to_secs(self.end_ticks)

    @property
    def length(self):
        return self.end - self.start

    def __lt__(self, other):
        self.length < other.length

    def __repr__(self):
        return f"TimeDelta<start_ticks = {self.start_ticks}, end_ticks = {self.end_ticks})>"


class TimedEvent:
    def __init__(self, song, chart, time):
        self.song = song
        self.chart = chart
        self.time = time

    def __lt__(self, other):
        return self.time < other.time


class Note(TimedEvent):
    def __init__(self, song, chart, time, kind, length):
        super().__init__(song, chart, time)
        self.kind = kind
        self.length = length

    def __repr__(self):
        return f"<Note(time = {self.time}, kind = {self.kind}), length = {self.length})>"


class SPEvent(TimedEvent):
    def __init__(self, song, chart, time, kind, length):
        super().__init__(song, chart, time)
        self.kind = kind  # Unused? Seems to always be 2...
        self.length = length

    def __repr__(self):
        return f"<SPEvent(time = {self.time}, kind = {self.kind}), length = {self.length})>"


class Event(TimedEvent):
    def __init__(self, song, chart, time, data):
        super().__init__(song, chart, time)
        self.data = data

    def __repr__(self):
        return f"<Event(time = {self.time}, data = {self.data})>"


class Chord:
    def __init__(self, song, chart, notes: List[Note]):
        self.song = song
        self.chart = chart
        if notes is None:
            notes = []
        self.notes = sorted(notes)

    @property
    def time(self):
        return min([n.time for n in self.notes])

    @property
    def length(self):
        return None if self.notes is None else max([n.length for n in self.notes])

    @property
    def shape(self):
        return sorted([n.kind for n in self.notes])

    def __repr__(self):
        return f"<Chord(time = {self.time}, shape = {self.shape}, length = {self.length})>"

    def __str__(self):
        return repr(self)


class Chart:
    def __init__(self, song, instrument, difficulty):
        self.song = song
        self.instrument = instrument
        self.difficulty = difficulty
        self.notes = None
        self.star_powers = None
        self.events = None
        self.chords = None

    def setup(self, notes, star_powers, events):
        self.notes = sorted(notes)
        self.star_powers = sorted(star_powers)
        self.events = sorted(events)
        chordnotes = (notes for ticks, notes in groupby(self.notes, key=lambda n: n.time.ticks))
        self.chords = [Chord(self.song, self, notes) for notes in chordnotes]

    def __hash__(self):
        return hash((
            tuple(self.notes),
            tuple(self.star_powers),
            tuple(self.events)
        ))

    def __repr__(self):
        return f"<Chart(difficulty = {self.difficulty}, instrument = {self.instrument}, chords = {len(self.chords)}, notes = {len(self.notes)}, star_powers = {len(self.star_powers)}, events = {len(self.events)})>"


class Song:
    def __init__(self):
        self.events = []
        self.charts = {}
        self.tempos = []
        self.timesigs = []
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

    def setup(self, events, charts, tempos, timesigs):
        self.events = sorted(events)
        self.charts = charts
        self.tempos = sorted(tempos)
        self.timesigs = sorted(timesigs)

    def ticks_to_secs(self, ticks):
        return ticks  # TODO: Placeholder

    def __hash__(self):
        return hash(
            (tuple(self.tempos),
             tuple(self.events),
             tuple(self.charts.values()))
        )

    def __repr__(self):
        return f"<Song(name = {self.full_name!r}, tempos = {len(self.tempos)}, events = {len(self.events)}, charts = {self.charts})>"
