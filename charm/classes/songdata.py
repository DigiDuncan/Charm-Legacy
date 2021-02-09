from dataclasses import dataclass, field
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

    @property
    def longest_note_length(self):
        ln = 0
        for note in self.notes:
            if note.length > ln:
                ln - note.length
        return ln


@jsonable
@dataclass
class BPMEvent:
    position: int
    bpm: float


@jsonable
@dataclass
class TSEvent:
    position: int
    time_sig: tuple


@jsonable
@dataclass
class SPEvent:
    position: int
    length: int


@jsonable
@dataclass
class Track:
    instrument: str
    difficulty: int
    chords: List[Chord]
    bpm_events: List[BPMEvent]
    star_power_events: List[SPEvent] = field(default_factory=list)
    time_sig_events: List[TSEvent] = TSEvent(0, (4, 4))

    @property
    def last_chord(self) -> Chord:
        lc = self.chords[0]
        for chord in self.chords:
            if chord.position > lc.position:
                lc = chord
        return lc


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

    def get_track(self, instrument, difficulty):
        for t in self.tracks:
            if t.instrument == instrument and t.difficulty == difficulty:
                return t
        return None
