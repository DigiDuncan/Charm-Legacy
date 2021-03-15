from __future__ import annotations

import re
from dataclasses import dataclass
from functools import total_ordering
from typing import DefaultDict, List, Union

RE_PARENTHETICAL = r"(.*)(\(.*\).*)"


@total_ordering
class TimeStamp:
    def __init__(self, ticks, song: Song = None):
        self.ticks = ticks
        self.song = song

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


@dataclass(order = True)
class RawNote:
    time: int
    kind: int
    length: int

    def __str__(self):
        return f"<{repr(self)}>"


@dataclass(order = True)
class RawSPEvent:
    time: int
    kind: int
    length: int

    def __str__(self):
        return f"<{repr(self)}>"


@dataclass(order = True)
class RawEvent:
    time: int
    data: str

    def __str__(self):
        return f"<{repr(self)}>"


@dataclass(order = True)
class RawBPMEvent:
    time: int
    mpbm: int

    def __str__(self):
        return f"<{repr(self)}>"


@dataclass(order = True)
class RawAnchorEvent:
    time: int
    mpbm: int

    def __str__(self):
        return f"<{repr(self)}>"


@dataclass(order = True)
class RawTSEvent:
    time: int
    numerator: int
    denominator: Union[int, None]

    def __str__(self):
        return f"<{repr(self)}>"


@dataclass
class RawMetadata:
    key: str
    value: str

    def __str__(self):
        return f"<{repr(self)}>"


@dataclass
class RawDataBlock:
    name: str
    events: List[Union[RawEvent, RawAnchorEvent, RawBPMEvent, RawNote, RawSPEvent, RawTSEvent]]

    def __str__(self):
        return f"<{repr(self)}>"


@dataclass
class RawSong:
    metadata: List[RawMetadata]
    datablocks: List[RawDataBlock]

    def __str__(self):
        return f"<{repr(self)}>"


class Note:
    def __init__(self, song, chart, rawnote: RawNote = None):
        self.song = song
        self.chart = chart
        self.kind = None
        self.time = None
        self.length = None

        if rawnote is not None:
            self.load_raw(rawnote)

    def load_raw(self, rawnote: RawNote):
        self.kind = int(rawnote.kind)
        self.time = TimeStamp(rawnote.time, self.song)
        self.length = TimeDelta(self.time, rawnote.length)

    def __repr__(self):
        return f"<Note(time = {self.time}, kind = {self.kind}), length = {self.length})>"

    def __str__(self):
        return repr(self)


class SPEvent:
    def __init__(self, song, chart, rawspevent: RawSPEvent = None):
        self.song = song
        self.chart = chart
        self.time = None
        self.kind = None  # Unused? Seems to always be 2...
        self.length = None

        if rawspevent is not None:
            self.load_raw(rawspevent)

    def load_raw(self, rawspevent: RawSPEvent):
        self.time = TimeStamp(rawspevent.time, self.song)
        self.kind = int(rawspevent.kind)
        self.length = TimeDelta(self.time, rawspevent.length)

    def __repr__(self):
        return f"<SPEvent(time = {self.time}, kind = {self.kind}), length = {self.length})>"

    def __str__(self):
        return repr(self)


class Event:
    def __init__(self, song, chart, rawevent: RawEvent = None):
        self.song = song
        self.chart = chart
        self.time = None
        self.data = None

        if rawevent is not None:
            self.load_raw(rawevent)

    def load_raw(self, rawevent: RawEvent):
        self.time = TimeStamp(rawevent.time, self.song)
        self.data = rawevent.data

    def __repr__(self):
        return f"<Event(time = {self.time}, data = {self.data})>"

    def __str__(self):
        return repr(self)


class Chord:
    def __init__(self, song, chart, notes: List[Note] = None):
        self.song = song
        self.chart = chart
        self._notes = notes

    @property
    def notes(self):
        return None if self._notes is None else sorted(self._notes)

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
    def __init__(self, song, rawdatablock: RawDataBlock = None):
        self.song = song
        self.instrument = None
        self._notes = []
        self._star_powers = []
        self._events = []
        if rawdatablock is not None:
            self.load_block(rawdatablock)

    @property
    def notes(self):
        return sorted(self._notes)

    @property
    def chords(self):
        d = DefaultDict(list)
        for note in self.notes:
            d[note.time.ticks].append(note)
        return [Chord(self.song, self, ns) for ns in d.values()]

    @property
    def star_powers(self):
        return sorted(self._star_powers)

    @property
    def events(self):
        return sorted(self._events)

    def load_block(self, block: RawDataBlock):
        self.instrument = block.name
        for event in block.events:
            if isinstance(event, RawNote):
                self._notes.append(Note(self.song, self, event))
            elif isinstance(event, RawSPEvent):
                self._star_powers.append(SPEvent(self.song, self, event))
            elif isinstance(event, RawEvent):
                self._event.append(Event(self.song, self, event))

    def __hash__(self):
        return hash(
            (tuple(self.notes),
             tuple(self.star_powers),
             tuple(self.events))
        )

    def __repr__(self):
        return f"<Chart(instrument = {self.instrument}, chords = {self.chords}, star_powers = {self.star_powers}, events = {self.events})>"

    def __str__(self):
        return repr(self)


class Song:
    def __init__(self, rawsong = None):
        self.metadata = {}
        self._sync_track = []
        self._events = []
        self.charts = {}

        if rawsong is not None:
            self.load_raw(rawsong)

    @property
    def sync_track(self):
        return sorted(self.sync_track)

    @property
    def events(self):
        return sorted(self._events)

    @property
    def full_name(self):
        return self.metadata.get("name")

    @property
    def title(self):
        if self.full_name is not None:
            if m := (re.match(RE_PARENTHETICAL, self.full_name)):
                return m.group(1)
        return self.full_name

    @property
    def subtitle(self):
        if self.full_name is not None:
            if m := (re.match(RE_PARENTHETICAL, self.full_name)):
                return m.group(2)
        return None

    @property
    def alt_title(self):
        return "UNUSED"

    @property
    def artist(self):
        return self.metadata.get("artist")

    @property
    def album(self):
        return self.metadata.get("album")

    @property
    def year(self):
        return self.metadata.get("year")

    @property
    def charter(self):
        return self.metadata.get("charter")

    @property
    def offset(self):
        o = self.metadata.get("offset")
        return None if o is None else int(o)

    @property
    def resolution(self):
        o = self.metadata.get("resolution")
        return None if o is None else int(o)

    @property
    def difficulty(self):
        o = self.metadata.get("difficulty")
        return None if o is None else int(o)

    @property
    def previewstart(self):
        o = self.metadata.get("previewstart")
        return None if o is None else int(o)

    @property
    def previewend(self):
        o = self.metadata.get("previewend")
        return None if o is None else int(o)

    @property
    def genre(self):
        return self.metadata.get("genre")

    @property
    def mediastream(self):
        return self.metadata.get("mediastream")

    def ticks_to_secs(self, ticks):
        return ticks  # TODO: Placeholder

    def load_raw(self, rawsong: RawSong):
        for md in rawsong.metadata:
            self.metadata[md.key] = md.value
        for block in rawsong.datablocks:
            if block.name == "SyncTrack":
                for event in block.events:
                    self._sync_track.append(event)
            elif block.name == "Events":
                for event in block.events:
                    self._events.append(event)
            else:
                self.charts[block.name] = Chart(self, block)

    def __hash__(self):
        return hash(
            (tuple(self.sync_track),
             tuple(self.events),
             tuple(self.charts.values()))
        )

    def __repr__(self):
        return f"<Song(metadata = {self.metadata}, sync_track = {self.sync_track}, events = {self.events}, charts = {self.charts})>"

    def __str__(self):
        return repr(self)
