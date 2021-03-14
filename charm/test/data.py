from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Union

RE_PARENTHETICAL = r"(.*)(\(.*\).*)"


@dataclass(order = True)
class RawNote:
    time: int
    kind: int
    length: int


@dataclass(order = True)
class RawSPEvent:
    time: int
    kind: int
    length: int


@dataclass(order = True)
class RawEvent:
    time: int
    data: str


@dataclass(order = True)
class RawBPMEvent:
    time: int
    mpbm: int


@dataclass(order = True)
class RawAnchorEvent:
    time: int
    mpbm: int


@dataclass(order = True)
class RawTSEvent:
    time: int
    numerator: int
    denominator: Union[int, None]


@dataclass
class RawMetadata:
    key: str
    value: str


@dataclass
class RawDataBlock:
    name: str
    events: List[Union[RawEvent, RawAnchorEvent, RawBPMEvent, RawNote, RawSPEvent, RawTSEvent]]


@dataclass
class RawSong:
    metadata: List[RawMetadata]
    datablocks: List[RawDataBlock]


class Chart:
    def __init__(self, song, block = None):
        self.song = song
        if block is not None:
            self.load_block(block)

    def load_block(self, block):
        pass


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
    def artist(self):
        return self.metadata.get("artist")

    @property
    def album(self):
        return self.metadata.get("album")

    @property
    def year(self):
        return self.metadata.get("year")

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
