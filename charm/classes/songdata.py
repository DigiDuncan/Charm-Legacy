from __future__ import annotations

from typing import Dict, List, Tuple


class Timestamp:
    def __init__(self, ticks: int):
        self.ticks = ticks
        self.time: float = None

    def ticks_to_time(self, song: "Song") -> float:
        return self.ticks / 440  # TODO: Placeholder

    def time_to_ticks(self, song: "Song") -> int:
        return self.time * 440  # TODO: Placeholder


class TimeDelta:
    def __init__(self, position: Timestamp, ticks: int):
        self.position = position
        self.ticks = ticks
        self.length: float = None
    # TODO: This is not finished at all.


class Event:
    def __init__(self, song: "Song", position: Timestamp):
        self.song = song
        self.position = position


class ChartEvent(Event):
    def __init__(self, song: "Song", chart: "Chart", position: Timestamp):
        self.chart = chart
        super().__init__(song, position)


class Lyric(Event):
    def __init__(self, song: "Song", position: Timestamp,
                 word: str, partial: bool, length: TimeDelta):
        self.word = word
        self.partial = partial
        self.length = length
        super().__init__(song, position)


class LyricPhrase(Event):
    def __init__(self, song: "Song", position: Timestamp,
                 length: TimeDelta, lyrics: List[Lyric]):
        self.length = length
        self.lyrics = lyrics
        super().__init__(song, position)


class BPMEvent(Event):
    def __init__(self, song: "Song", position: Timestamp,
                 bpm: float):
        self.bpm = bpm
        super().__init__(song, position)


class TSEvent(Event):
    def __init__(self, song: "Song", position: Timestamp,
                 time_signature: Tuple[int, int]):
        self.time_signature = time_signature
        super().__init__(song, position)


class GenericEvent(Event):
    def __init__(self, song: "Song", position: Timestamp,
                 data: dict):
        self.data = data
        super().__init__(song, position)


class Note(ChartEvent):
    def __init__(self, song: "Song", chart: "Chart", position: Timestamp,
                 fret: int, flag: str, length: TimeDelta):
        self.fret = fret
        self.flag = flag  # Flags might need to be bytes? ¯\_(ツ)_/¯
        self.length = length
        super().__init__(song, chart, position)


class Chord(ChartEvent):
    def __init__(self, song: "Song", chart: "Chart", position: Timestamp,
                 notes: List[Note]):
        self.notes = notes
        self.flag = self.notes[0].flag  # This might not work.
        super().__init__(song, chart, position)


class SPEvent(ChartEvent):
    def __init__(self, song: "Song", chart: "Chart", position: Timestamp,
                 length: TimeDelta):
        self.length = length
        super().__init__(song, chart, position)


class GenericChartEvent(ChartEvent):
    def __init__(self, song: "Song", chart: "Chart", position: Timestamp,
                 data: dict):
        self.data = data
        super().__init__(song, chart, position)


class Chart:
    def __init__(self, song: "Song", instrument: str, difficulty: int, events: List[ChartEvent]):
        self.song = song
        self.instrument = instrument
        self.difficulty = difficulty
        self.events = events

    @property
    def notes(self):
        return [e for e in self.events if isinstance(e, Note)]

    @property
    def chords(self):
        last_note = None
        current_chord = []
        _chords = []
        for note in self.notes:
            if last_note is None or last_note.position == note.position:
                current_chord.append(note)
            else:
                _chords.append(Chord(self.song, self, current_chord[0].position, current_chord))
            last_note = note
        _chords.append(Chord(self.song, self, current_chord[0].position, current_chord))
        return _chords

    def get_notes(self, start: Timestamp, stop: Timestamp) -> List[Note]:
        return [n for n in self.notes if n >= start and n <= stop]

    def get_chords(self, start: Timestamp, stop: Timestamp) -> List[Chord]:
        return [c for c in self.chords if c >= start and c <= stop]

    def get_events(self, start: Timestamp, stop: Timestamp) -> List[Event]:
        return [e for e in self.events if e >= start and e <= stop]


class Song:
    def __init__(self, name: str, artist: str, album: str, track: int, year: str, genre: str, rating: int, charter: str, length: int,
                 resolution: int, offset: int, charts: Dict[Tuple[str, int], Chart] = None, lyricphrases: List[LyricPhrase] = None,
                 alt_name: str = None):
        self.name = name
        self.alt_name = alt_name  # Some songs in some games (DDR, etc.) have an alt-name, usually a Romanji version.
        self.artist = artist
        self.album = album
        self.track = track
        self.year = year
        self.genre = genre
        self.rating = rating
        self.charter = charter
        self.length = length  # Do not use for anything but display/sorting.

        self.resolution = resolution
        self.offset = offset
        self.charts = charts
        self.lyricphrases = lyricphrases

    def get_chart(self, instrument: str, difficulty: int) -> Chart:
        return self.charts[(instrument, difficulty)]

    def set_chart(self, instrument: str, difficulty: int, chart: Chart):
        self.charts[(instrument, difficulty)] = chart
