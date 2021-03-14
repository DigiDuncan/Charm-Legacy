from __future__ import annotations

from dataclasses import dataclass
from typing import List, Union


@dataclass
class RawNote:
    time: int
    kind: int
    length: int


@dataclass
class RawEvent:
    time: int
    data: str


@dataclass
class RawBPMEvent:
    time: int
    mpbm: int


@dataclass
class RawTSEvent:
    time: int
    numerator: int
    denominator: Union[int, None]

    def __post_init__(self):
        self.denominator = 4 if self.denominator is None else self.denominator


@dataclass
class RawMetadata:
    name: str
    artist: str
    charter: str
    album: str
    year: str
    offset: int
    resolution: int
    difficulty: int
    preview_start: int
    preview_end: int
    genre: str
    music_stream: str


@dataclass
class RawSyncTrack:
    events: List[Union[RawBPMEvent, RawTSEvent]]


@dataclass
class RawEventsList:
    events: List[RawEvent]


@dataclass
class RawChart:
    name: str
    notes: List[RawNote]


@dataclass
class RawSong:
    metadata: RawMetadata
    sync_track: RawSyncTrack
    events: RawEventsList
    charts: List[RawChart]
