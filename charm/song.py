from __future__ import annotations

from functools import cache, total_ordering
from typing import Dict, List, Optional

from nindex import Index


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

    def contains(self, other: SongEvent) -> bool:
        return self.tick_start <= other.tick_start and self.tick_end >= other.tick_end

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
                          # UPDATE: Nope! Sometimes 0/1 for co-op battles, 64 for drum fills.

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


class Section(SongEvent):
    def __init__(self, song: Song, tick_start: int, text: str):
        super().__init__(song, tick_start)
        self.text: str = text

    def __lt__(self, other: Section):
        return self.tick_start < other.tick_start


class LyricPhrase(SongEvent):
    def __init__(self, song: Song, tick_start: int, tick_length: int):
        super().__init__(song, tick_start, tick_length)
        self.words: List[LyricWord] = []
        self.word_by_ticks: Index[int, LyricWord] = None

    def finalize(self):
        self.word_by_ticks = Index(self.words, "tick_start")

    def get_on_text(self, track_ticks: int) -> str:
        return "".join(w.text for w in self.word_by_ticks[:track_ticks + 1])
        # return "".join(w.text for w in self.words[:self.word_by_ticks.gt_index(track_ticks)])

    def get_off_text(self, track_ticks: int) -> str:
        return "".join(w.text for w in self.word_by_ticks[track_ticks + 1:])

    def get_text(self) -> str:
        return "".join(w.text for w in self.words)

    def __lt__(self, other: SongEvent):
        return self.tick_start < other.tick_start


class LyricWord(SongEvent):
    def __init__(self, song: Song, tick_start: int, text: str):
        super().__init__(song, tick_start)
        self.text = text

    def is_on(self, track_ticks: int):
        return self.tick_start <= track_ticks

    def __lt__(self, other: SongEvent):
        return self.tick_start < other.tick_start


class Chord(ChartEvent):
    def __init__(self, song: Song, chart: Chart, flag: str, notes: List[Note]):
        tick_start = notes[0].tick_start
        tick_length = max(n.tick_length for n in notes)
        super().__init__(song, chart, tick_start, tick_length)
        self.flag = flag
        self.notes = notes
        self.frets = tuple(n.fret for n in notes)
        self.sp_phrase = None

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
        self.countdowns = {}  # {tickstart: ticklength}

    def calculate_countdowns(self):
        fakechord = Chord(self.song, self, "note", [Note(self.song, self, 0, 0, 0)])
        if self.chords == []:
            return
        for chord, nextchord in zip([fakechord] + self.chords, self.chords + [self.chords[-1]]):
            chord_end = chord.tick_start + chord.tick_length
            gap = nextchord.tick_start - chord_end
            if gap >= self.song.tempo_calc.secs_to_ticks(5):  # god this is hardcoded
                self.countdowns[chord_end] = gap

    def finalize(self):
        self.notes.sort()
        self.star_powers.sort()
        self.events.sort()
        self.chords.sort()

    def hopo_calc(self, song: Song):
        for chord, prev_chord in zip(self.chords[1:], self.chords[:-1]):
            tempo = song.tempo_calc.tempo_by_ticks.lteq(prev_chord.tick_start)
            tempo.ticks_per_sec
            timesig = song.timesig_by_ticks.lteq(prev_chord.tick_start)
            if timesig is None:
                pass

            ticks_per_quarternote = song.resolution
            ticks_per_wholenote = ticks_per_quarternote * 4
            beats_per_wholenote = timesig.denominator
            ticks_per_beat = ticks_per_wholenote / beats_per_wholenote

            chord_distance = chord.tick_start - prev_chord.tick_start

            hopo_cutoff = ticks_per_beat / (192 / 66)

            if chord.frets == prev_chord.frets:
                # You can't have two HOPO chords of the same fretting.
                if chord.flag == "forced":
                    chord.flag = "note"
            elif chord_distance <= hopo_cutoff:
                if chord.flag == "forced":
                    chord.flag = "note"
                elif chord.flag == "note":
                    chord.flag = "hopo"
            else:
                if chord.flag == "forced":
                    chord.flag = "hopo"

        self.chord_by_ticks = Index(self.chords, "tick_start")

    def sp_phrase_calc(self):
        for i, sp_phrase in enumerate(self.star_powers):
            for chord in self.chord_by_ticks[sp_phrase.tick_start:sp_phrase.tick_end]:
                chord.sp_phrase = i

    def add_chord_ids(self):
        id_ = -1
        for chord in self.chords:
            id_ += 1
            chord.id = id_

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
        self.lyrics: List[LyricPhrase] = []
        self.lyric_by_ticks: Index[int, LyricPhrase] = None
        self.sections: List[Section] = []
        self.section_by_ticks: Index[int, Section] = None
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
        self.resolution: int = None
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

        self.timesig_by_ticks = Index(self.timesigs, "tick_start")
        self.lyric_by_ticks = Index(self.lyrics, "tick_start")
        self.section_by_ticks = Index(self.sections, "tick_start")

        for chart in self.charts.values():
            chart.hopo_calc(self)
            chart.calculate_countdowns()
            chart.sp_phrase_calc()
            chart.add_chord_ids()

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
    def __init__(self, song: Song, tick_start: int, ticks_per_sec: int, mbpm: float):
        super().__init__(song, tick_start)
        self.ticks_per_sec = ticks_per_sec
        self.mbpm = mbpm


class TempoCalculator:
    def __init__(self, tempos: List[TempoEvent]):
        self.ticks_to_secs = cache(self.ticks_to_secs)
        self.secs_to_ticks = cache(self.secs_to_ticks)
        self.tempos = sorted(tempos)
        self.tempo_by_ticks: Index[int, TempoEvent] = None
        self.tempo_by_secs: Index[float, TempoEvent] = None

    def finalize(self):
        self.tempo_by_ticks = Index(self.tempos, "tick_start")
        self.tempo_by_secs = Index(self.tempos, "start")

    def ticks_to_secs(self, ticks: int) -> float:
        if ticks is None:
            return None
        if ticks == 0:
            return 0
        if ticks < 0:
            curr_tempo = self.tempos[0]
        else:
            curr_tempo = self.tempo_by_ticks.lteq(ticks - 1)

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
            curr_tempo = self.tempo_by_secs.lteq(secs)

        diff_seconds = secs - curr_tempo.start
        diff_ticks = int(diff_seconds * curr_tempo.ticks_per_sec)
        ticks = curr_tempo.tick_start + diff_ticks
        return int(ticks)

    def __hash__(self):
        return hash(tuple(self.tempos))
