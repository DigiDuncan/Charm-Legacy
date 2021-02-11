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

    def to_json(self):
        return {"ticks": self.ticks}

    @classmethod
    def from_json(cls, jsondata) -> Timestamp:
        return Timestamp(ticks = jsondata["ticks"])


class TimeDelta:
    def __init__(self, position: Timestamp, ticks: int):
        self.position = position
        self.ticks = ticks
        self.length: float = None
    # TODO: This is not finished at all.

    def to_json(self):
        return {
            "position": self.position,
            "ticks": self.ticks
        }

    @classmethod
    def from_json(cls, jsondata) -> TimeDelta:
        return TimeDelta(
            position = jsondata["position"],
            ticks = jsondata["ticks"]
        )


class Event:
    def __init__(self, song: "Song", position: Timestamp):
        self.song = song
        self.position = position

    def to_json(self):
        return {"position": self.position}

    @classmethod
    def from_json(cls, jsondata) -> Event:
        # TODO: This will fail because it has no song passed in. How fix?
        return Event(position = jsondata["position"])


class ChartEvent(Event):
    def __init__(self, song: "Song", chart: "Chart", position: Timestamp):
        self.chart = chart
        super().__init__(song, position)

    def to_json(self):
        # TODO: This will fail because it has no song or chart passed in. How fix?
        return {"position": self.position}

    @classmethod
    def from_json(cls, jsondata) -> ChartEvent:
        return ChartEvent(position = jsondata["position"])


class Lyric(Event):
    def __init__(self, song: "Song", position: Timestamp,
                 word: str, length: TimeDelta, partial: bool = False):
        self.word = word
        self.partial = partial
        self.length = length
        super().__init__(song, position)

    def to_json(self):
        return {
            "position": self.position,
            "word": self.word,
            "partial": self.partial,
            "length": self.length
        }

    @classmethod
    def from_json(cls, jsondata) -> Lyric:
        return Lyric(
            position = Timestamp.from_json(jsondata["position"]),
            word = jsondata["word"],
            partial = jsondata["partial"],
            length = TimeDelta.from_json(jsondata["partial"])
        )


class LyricPhrase(Event):
    def __init__(self, song: "Song", position: Timestamp,
                 length: TimeDelta, lyrics: List[Lyric]):
        self.length = length
        self.lyrics = lyrics
        super().__init__(song, position)

    def to_json(self):
        return {
            "position": Timestamp.to_json(self.position),
            "length": self.length,
            "lyrics": [lyric.to_json() for lyric in self.lyrics]
        }

    @classmethod
    def from_json(cls, jsondata) -> LyricPhrase:
        return LyricPhrase(
            position = Timestamp.from_json(jsondata["position"]),
            length = jsondata["length"],
            lyrics = Lyric.from_json(jsondata["lyrics"])
        )


class BPMEvent(Event):
    def __init__(self, song: "Song", position: Timestamp,
                 bpm: float):
        self.bpm = bpm
        super().__init__(song, position)

    def to_json(self):
        return {
            "position": Timestamp.to_json(self.position),
            "bpm": self.bpm
        }

    @classmethod
    def from_json(cls, jsondata) -> BPMEvent:
        return BPMEvent(
            position = Timestamp.from_json(jsondata["position"]),
            bpm = jsondata["bpm"]
        )


class TSEvent(Event):
    def __init__(self, song: "Song", position: Timestamp,
                 time_signature: Tuple[int, int]):
        self.time_signature = time_signature
        super().__init__(song, position)

    def to_json(self):
        return {
            "position": Timestamp.to_json(self.position),
            "time_signature": self.time_signature
        }

    @classmethod
    def from_json(cls, jsondata) -> TSEvent:
        return TSEvent(
            position = Timestamp.from_json(jsondata["position"]),
            time_signature = jsondata["time_signature"]
        )


class GenericEvent(Event):
    def __init__(self, song: "Song", position: Timestamp,
                 data: dict):
        self.data = data
        super().__init__(song, position)

    def to_json(self):
        return {
            "position": Timestamp.to_json(self.position),
            "data": self.data
        }

    @classmethod
    def from_json(cls, jsondata) -> GenericEvent:
        return GenericEvent(
            position = Timestamp.from_json(jsondata["position"]),
            data = jsondata["data"]  # This might break if there are non-builtins in the data.
        )


class Note(ChartEvent):
    def __init__(self, song: "Song", chart: "Chart", position: Timestamp,
                 fret: int, length: TimeDelta = TimeDelta(position, 0), flag: str = "normal"):  # Can't reference position here?
        self.fret = fret
        self.flag = flag  # Flags might need to be bytes? ¯\_(ツ)_/¯
        self.length = length
        super().__init__(song, chart, position)

    def to_json(self):
        return {
            "position": Timestamp.to_json(self.position),
            "fret": self.fret,
            "flag": self.flag,
            "length": TimeDelta.to_json(self.length)
        }

    @classmethod
    def from_json(cls, jsondata) -> Note:
        return Note(
            position = Timestamp.from_json(jsondata["position"]),
            fret = jsondata["fret"],
            flag = jsondata["flag"],
            length = TimeDelta.from_json(jsondata["length"])
        )


class Chord(ChartEvent):
    def __init__(self, song: "Song", chart: "Chart", position: Timestamp,
                 notes: List[Note]):
        self.notes = notes
        self.flag = self.notes[0].flag  # This might not work.
        super().__init__(song, chart, position)

    def to_json(self):
        return {
            "position": Timestamp.to_json(self.position),
            "notes": [note.to_json() for note in self.notes]
        }

    @classmethod
    def from_json(cls, jsondata) -> Chord:
        return Chord(
            position = Timestamp.from_json(jsondata["position"]),
            notes = [Note.from_json(d) for d in jsondata["notes"]]
        )


class SPEvent(ChartEvent):
    def __init__(self, song: "Song", chart: "Chart", position: Timestamp,
                 length: TimeDelta):
        self.length = length
        super().__init__(song, chart, position)

    def to_json(self):
        return {
            "position": Timestamp.to_json(self.position),
            "length": self.length
        }

    @classmethod
    def from_json(cls, jsondata) -> SPEvent:
        return SPEvent(
            position = Timestamp.from_json(jsondata["position"]),
            length = jsondata["length"]
        )


class GenericChartEvent(ChartEvent):
    def __init__(self, song: "Song", chart: "Chart", position: Timestamp,
                 data: dict):
        self.data = data
        super().__init__(song, chart, position)

    def to_json(self):
        return {
            "position": Timestamp.to_json(self.position),
            "data": self.data
        }

    @classmethod
    def from_json(cls, jsondata) -> GenericChartEvent:
        return GenericChartEvent(
            position = Timestamp.from_json(jsondata["position"]),
            data = jsondata["data"]  # This might break if there are non-builtins in the data.
        )


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

    def get_events(self, start: Timestamp, stop: Timestamp) -> List[ChartEvent]:
        return [e for e in self.events if e >= start and e <= stop]

    def get_non_note_events(self, start: Timestamp, stop: Timestamp) -> List[ChartEvent]:
        return [e for e in self.events if e not in self.notes and e >= start and e <= stop]

    def to_json(self):
        return {
            "instrument": self.instrument,
            "difficulty": self.difficulty,
            "events": [e.to_json() for e in self.events]
        }

    @classmethod
    def from_json(cls, jsondata) -> Chart:
        return Chart(
            instrument = jsondata["instrument"],
            difficulty = jsondata["difficulty"],
            events = ...  # TODO: Uhoh. How do you tell what kind of event it is?!
        )


class Song:
    def __init__(self, name: str, artist: str, album: str, track: int, year: str, genre: str, rating: int, charter: str, length: int,
                 resolution: int, offset: int, charts: Dict[Tuple[str, int], Chart] = None, events: List[Event] = None,
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
        self.events = events

    @property
    def lyricphrases(self):
        return [e for e in self.events if isinstance(e, LyricPhrase)]

    def get_chart(self, instrument: str, difficulty: int) -> Chart:
        return self.charts[(instrument, difficulty)]

    def set_chart(self, instrument: str, difficulty: int, chart: Chart):
        chart.song = self
        self.charts[(instrument, difficulty)] = chart

    def get_lyricphrases(self, start: Timestamp, stop: Timestamp) -> List[LyricPhrase]:
        return [c for c in self.lyricphrases if c >= start and c <= stop]

    def get_events(self, start: Timestamp, stop: Timestamp) -> List[Event]:
        return [e for e in self.events if e >= start and e <= stop]

    def to_json(self):
        return {
            "name": self.name,
            "alt_name": self.alt_name,
            "artist": self.artist,
            "album": self.album,
            "track": self.track,
            "year": self.year,
            "genre": self.genre,
            "rating": self.rating,
            "charter": self.charter,
            "length": self.length,
            "resolution": self.resolution,
            "offset": self.offset,
            "charts": self.charts,
            "lyricphrases": self.lyricphrases
        }

    def from_json(cls, jsondata):
        return Song(
            name = jsondata["name"],
            alt_name = jsondata["alt_name"],
            artist = jsondata["artist"],
            album = jsondata["album"],
            track = jsondata["track"],
            year = jsondata["year"],
            genre = jsondata["genre"],
            rating = jsondata["rating"],
            charter = jsondata["charter"],
            length = jsondata["length"],
            resolution = jsondata["resolution"],
            offset = jsondata["offset"],
            charts = [Chart.from_json(d) for d in jsondata["charts"]],
            lyricphrases = [LyricPhrase.from_json(d) for d in jsondata["lyricphrases"]]
        )
