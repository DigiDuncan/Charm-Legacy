from __future__ import annotations

import bisect
from functools import cache, total_ordering
from typing import Dict, Generic, List, Optional, TypeVar, Union


# Abstract class
@total_ordering
class SongEvent():
    def __init__(self, song: Song, tick_start: int, tick_length: Optional[int] = None):
        self.song = song
        self.tick_start = tick_start
        self.tick_length = tick_length or 0

    @property
    def start(self) -> float:
        return self.song.tempo_calc.ticks_to_secs(self.tick_start)

    @property
    def tick_end(self) -> int:
        return self.tick_start + self.tick_length

    @property
    def end(self) -> float:
        return self.song.tempo_calc.ticks_to_secs(self.tick_end)

    @property
    def length(self) -> float:
        return self.end - self.start

    def __eq__(self, other):
        return (self.tick_start, self.tick_length) == (other.tick_start, other.tick_length)

    def __lt__(self, other):
        return (self.tick_start, self.tick_length) < (other.tick_start, other.tick_length)


# Abstract class
class ChartEvent(SongEvent):
    def __init__(self, song: Song, chart: Chart, tick_start: int, tick_length: int = None):
        super().__init__(song, tick_start, tick_length)
        self.chart = chart


class Note(ChartEvent):
    def __init__(self, song: Song, chart: Chart, tick_start: int, fret: int, tick_length: int):
        super().__init__(song, chart, tick_start, tick_length)
        self.fret = fret

    def __eq__(self, other):
        return (self.tick_start, self.fret, self.tick_length) == (other.tick_start, other.fret, other.tick_length)

    def __lt__(self, other):
        return (self.tick_start, self.fret, self.tick_length) < (other.tick_start, other.fret, other.tick_length)

    def __repr__(self):
        return f"<{self.__class__.__name__}(start = {self.start}, fret = {self.fret}), length = {self.length})>"


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
    def __init__(self, song: Song, chart: Chart, flag: str, notes: List[Note]):
        tick_start = notes[0].tick_start
        tick_length = max(n.tick_length for n in notes)
        super().__init__(song, chart, tick_start, tick_length)
        self.flag = flag
        self.notes = notes
        self.frets = tuple(n.fret for n in notes)

    def __repr__(self):
        return f"<{self.__class__.__name__}(start = {self.start}, frets = {self.frets}, length = {self.length})>"


class Chart:
    def __init__(self, song: Song, instrument: str, difficulty: str):
        self.song = song
        self.instrument = instrument
        self.difficulty = difficulty
        self.notes: List[Note] = []
        self.star_powers: List[SPEvent] = []
        self.events: List[Event] = []
        self.chords: List[Chord] = []
        self.chord_by_ticks: Index[int, Chord] = None

    def finalize(self):
        self.notes.sort()
        self.star_powers.sort()
        self.events.sort()
        self.chords.sort()
        self.chord_by_ticks = Index(self.chords, "tick_start")

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
        self.events: List[Event] = []
        self.charts: Dict[str, Chart] = {}
        self.timesigs: List[TSEvent] = []
        self.timesig_by_ticks: Index[int, TSEvent] = None
        self.tempo_calc: TempoCalculator = None
        self.full_name: str = None
        self.title: str = None
        self.subtitle: str = None
        self.alt_title: str = None
        self.artists: str = None
        self.album: str = None
        self.year: str = None
        self.charter: str = None
        self.offset: str = None
        self.resolution: str = None
        self.difficulty: str = None
        self.previewstart: str = None
        self.previewend: str = None
        self.genre: str = None
        self.mediastream: str = None
        self.musicstream: str = None

    def finalize(self):
        self.events.sort()
        self.timesigs.sort()
        self.tempo_calc.finalize()
        self.timesig_by_ticks = Index(self.timesigs, "tick_start", minzero=True)

    def __hash__(self):
        return hash((
            tuple(self.tempo_calc),
            tuple(self.events),
            tuple(self.charts.values())
        ))

    def __repr__(self):
        return f"<{self.__class__.__name__}(name = {self.full_name!r}, tempos = {len(self.tempo_calc.tempos)}, events = {len(self.events)}, charts = {self.charts})>"


class TSEvent(SongEvent):
    def __init__(self, song: Song, tick_start: int, numerator: int, denominator: int):
        super().__init__(song, tick_start)
        self.numerator = numerator
        self.denominator = denominator


class TempoEvent(SongEvent):
    def __init__(self, song: Song, tick_start: int, ticks_per_sec: int):
        super().__init__(song, tick_start)
        self.ticks_per_sec = ticks_per_sec


class TempoCalculator:
    def __init__(self, tempos: List[TempoEvent]):
        self.ticks_to_secs = cache(self.ticks_to_secs)
        self.secs_to_ticks = cache(self.secs_to_ticks)
        self.tempos = sorted(tempos)
        self.tempo_by_ticks: Index[int, TempoEvent] = Index(self.tempos, "tick_start", minzero=True)
        self.tempo_by_secs: Index[float, TempoEvent] = None

    def finalize(self):
        for tempo in self.tempos:
            self.ticks_to_secs(tempo.tick_start)
        self.tempo_by_secs = Index(self.tempos, "start", minzero=True)

    def ticks_to_secs(self, ticks: int) -> float:
        if ticks is None:
            return None
        if ticks == 0:
            return 0
        if ticks < 0:
            curr_tempo = self.tempos[0]
        else:
            curr_tempo = self.tempo_by_ticks[ticks]

        diff_ticks = ticks - curr_tempo.tick_start
        diff_seconds = diff_ticks / curr_tempo.ticks_per_sec
        seconds = curr_tempo.start + diff_seconds
        return seconds

    def secs_to_ticks(self, secs: float) -> int:
        if secs is None:
            return None
        if secs == 0:
            return 0
        if secs < 0:
            curr_tempo = self.tempos[0]
        else:
            curr_tempo = self.tempo_by_secs[secs]

        diff_seconds = secs - curr_tempo.start
        diff_ticks = int(diff_seconds * curr_tempo.ticks_per_sec)
        ticks = curr_tempo.tick_start + diff_ticks
        return ticks

    def __hash__(self):
        return hash(tuple(self.tempos))


T = TypeVar("T")
K = TypeVar("K")


class Index(Generic[K, T]):
    def __init__(self, items: List[T], keyattr: str, minzero: bool = False):
        self.items = items
        self.keys: List[K] = [getattr(i, keyattr) for i in items]
        self.minzero = minzero

    def __getitem__(self, key: Union[slice, K]) -> Union[None, T]:
        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
            if self.minzero:
                if start is not None and start < 0:
                    start = 0
                if stop is not None and stop < 0:
                    stop = 0

            start_index = None if start is None else find_index(self.keys, start)
            stop_index = None if stop is None else find_index(self.keys, stop, start_index)
            if stop_index is None:
                stop_index = 0
            return self.items[start_index:stop_index:step]
        else:
            if self.minzero and key < 0:
                key = 0
            index = find_index(self.keys, key)
            if index is None:
                return None
            return self.items[index]


def find_index(keys: List[T], value: T, start=None) -> Union[None, int]:
    """
    Finds the index of the first key that is equal to or greater than the given value
    Accepts a sorted list, and a value to search for
    Returns None if there are no matching keys
    """
    if start is None:
        start = 0
    index = bisect.bisect_right(keys, value, start) - 1
    if index < 0:
        index = None
    return index
