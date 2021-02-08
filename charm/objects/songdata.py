from dataclasses import dataclass
from typing import List, Literal

from charm.lib.njson import jsonable


@jsonable
@dataclass
class Note:
    """A single note.
    `fret: int`, 0 = open, 1-5 = green, red, yellow, blue, orange, (or 1-6 for GHL, etc)
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
    flag: Literal["normal", "hopo", "tap", "forced"]
    notes: List[Note]
    star_power: bool = False


@jsonable
@dataclass
class Track:
    instrument: str
    chords: List[Chord]


@jsonable
@dataclass
class Lyric:
    word: str
    rel_position: int
    length: int
    append_space: bool = True


@jsonable
@dataclass
class LyricPhrase:
    position: int
    length: int
    lyrics: List[Lyric]


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
    resolution: int
    offset: int
    tracks: List[Track]
    lyricphrases: List[LyricPhrase]
