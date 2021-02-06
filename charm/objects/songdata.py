from dataclasses import dataclass
from typing import List, Literal

from charm.lib.njson import jsonable


@jsonable
@dataclass
class Note:
    """A single note.
    `fret: int`, 0 = open, 1-5 = green, red, yellow, blue, orange
    `length: int` the length in ticks? of this note
    """
    fret: int
    length: int


@jsonable
@dataclass
class Chord:
    """A chord (many notes together).
    `position: int`, this chords position in the track.
    `flag: str`, either normal, hopo, or tap (can't be hopo and tap)
    `star_power: bool`, this note is part of a star power phrase
    `notes: List[Note]`, a list of notes.
    """
    position: int
    flag: Literal["normal", "hopo", "tap"]
    star_power: bool
    notes: List[Note]


@jsonable
@dataclass
class Track:
    instrument: str
    chords: List[Chord]


@jsonable
@dataclass
class Song:
    name: str
    artist: str
    album: str
    difficulty: int
    charter: str
    year: int
    genre: str
    track: int
    length: int
    tracks: List[Track]
