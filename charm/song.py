from __future__ import annotations

from itertools import groupby
from functools import cache, total_ordering
from typing import List


@total_ordering
class TimeStamp:
    def __init__(self, song, ticks):
        self.song = song
        self.ticks = ticks

    @property
    def secs(self):
        return self.song.tempo_calc.ticks_to_secs(self.ticks)

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


# Abstract class
class SongEvent():
    def __init__(self, song, time):
        self.song = song
        self.time = TimeStamp(song, time)

    def __lt__(self, other):
        return self.time < other.time


# Abstract class
class ChartEvent(SongEvent):
    def __init__(self, song, chart, time):
        super().__init__(song, time)
        self.chart = chart


class Note(ChartEvent):
    def __init__(self, song, chart, time, kind, length):
        super().__init__(song, chart, time)
        self.kind = kind
        self.length = length

    def __lt__(self, other):
        if self.time != other.time:
            return self.time < other.time
        else:
            return self.kind < other.kind

    def __repr__(self):
        return f"<Note(time = {self.time}, kind = {self.kind}), length = {self.length})>"


class SPEvent(ChartEvent):
    def __init__(self, song, chart, time, kind, length):
        super().__init__(song, chart, time)
        self.kind = kind  # Unused? Seems to always be 2...
        self.length = length

    def __repr__(self):
        return f"<SPEvent(time = {self.time}, kind = {self.kind}), length = {self.length})>"


class Event(ChartEvent):
    def __init__(self, song, chart, time, data):
        super().__init__(song, chart, time)
        self.data = data

    def __repr__(self):
        return f"<Event(time = {self.time}, data = {self.data})>"


class Chord:
    def __init__(self, song, chart, notes: List[Note]):
        self.song = song
        self.chart = chart
        self.notes = notes
        self.time = self.notes[0].time
        self.length = max(n.length for n in self.notes)
        self.shape = tuple(n.kind for n in notes)

    def __repr__(self):
        return f"<Chord(time = {self.time}, shape = {self.shape}, length = {self.length})>"

    def __str__(self):
        return repr(self)


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
        chordnotes = (notes for ticks, notes in groupby(self.notes, key=lambda n: n.time.ticks))
        self.chords = [Chord(self.song, self, list(notes)) for notes in chordnotes]

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

    def finalize(self):
        self.events.sort()
        self.timesigs.sort()
        self.tempo_calc.finalize()

    def __hash__(self):
        return hash(
            (tuple(self.tempo_calc),
             tuple(self.events),
             tuple(self.charts.values()))
        )

    def __repr__(self):
        return f"<Song(name = {self.full_name!r}, tempos = {len(self.tempo_calc.tempos)}, events = {len(self.events)}, charts = {self.charts})>"


class TempoEvent(SongEvent):
    def __init__(self, song, time, ticks_per_sec):
        super().__init__(song, time)
        self.ticks_per_sec = ticks_per_sec


class TempoCalculator:
    def __init__(self, tempos):
        self.ticks_to_secs = cache(self.ticks_to_secs)
        self.tempos = sorted(tempos)

    def finalize(self):
        for tempo in self.tempos:
            self.ticks_to_secs(tempo.time.ticks)

    def ticks_to_secs(self, ticks):
        if ticks == 0:
            return 0
        curr_tempo = next(tempo for tempo in self.tempos if tempo.time.secs <= ticks)
        curr_ticks = ticks - curr_tempo.time.ticks
        curr_seconds = curr_ticks / curr_tempo.ticks_per_sec
        seconds = curr_tempo.time.secs + curr_seconds
        return seconds

    def __hash__(self):
        return hash(tuple(self.tempos))
