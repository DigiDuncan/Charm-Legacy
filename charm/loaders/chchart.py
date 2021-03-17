from __future__ import annotations
from itertools import product
import re

from typing import Dict, List, Tuple, Union

from charm.song import Chart, Event, Note, Song, SPEvent, TempoCalculator, TempoEvent, TimeDelta, TimeStamp
from charm.loaders.raw_chchart import RawEvent, RawNote, RawStarPower, RawTempo, RawAnchor, RawTS, RawMetadata, load_raw


class LoadException(Exception):
    pass


class DuplicateChartException(LoadException):
    pass


class InvalidEventException(LoadException):
    pass


class InvalidHeaderException(LoadException):
    pass


class InvalidLineTypeException(LoadException):
    pass


class InvalidMetadataException(LoadException):
    pass


class InvalidSynctrackDataException(LoadException):
    pass


class MissingEventsBlockException(LoadException):
    pass


class MissingSongBlockException(LoadException):
    pass


class MissingSyncTrackBlockException(LoadException):
    pass


class UnparsedMetadataException(LoadException):
    pass


def note_from_raw(song: Song, chart: Chart, rawnote: RawNote) -> Note:
    time = TimeStamp(song, rawnote.time)
    length = TimeDelta(time, rawnote.length)
    note = Note(song, chart, time, rawnote.kind, length)
    return note


def spevent_from_raw(song: Song, chart: Chart, rawspevent: RawStarPower) -> SPEvent:
    time = TimeStamp(song, rawspevent.time)
    length = TimeDelta(time, rawspevent.length)
    spevent = SPEvent(song, chart, time, rawspevent.kind, length)
    return spevent


def event_from_raw(song: Song, chart: Chart, rawevent: RawEvent) -> Event:
    time = TimeStamp(song, rawevent.time)
    event = Event(song, chart, time, rawevent.data)
    return event


DIFFICULTIES = ("Easy", "Medium", "Hard", "Expert")
INSTRUMENTS = ("Single", "DoubleGuitar", "DoubleBass", "DoubleRhythm", "Keyboard", "Drums", "GHLGuitar", "GHLBass")
DIFFINST_MAP = {d + i: (d, i) for d, i in product(DIFFICULTIES, INSTRUMENTS)}    # Precalculate all DifficultyInstrument pairings


def chart_from_raw(song: Song, header: str, lines: List[RawNote, RawEvent, RawTempo, RawAnchor, RawTS, RawStarPower, RawMetadata]) -> Chart:
    try:
        difficulty, instrument = DIFFINST_MAP[header]
    except KeyError:
        raise InvalidHeaderException(f"Invalid Header: {header}")

    chart = Chart(song, instrument, difficulty)

    notes = []
    star_powers = []
    events = []
    for line in lines:
        if isinstance(line, RawNote):
            notes.append(note_from_raw(song, chart, line))
        elif isinstance(line, RawStarPower):
            star_powers.append(spevent_from_raw(song, chart, line))
        elif isinstance(line, RawEvent):
            events.append(event_from_raw(song, chart, line))
        else:
            raise InvalidLineTypeException(f"Bad line type {line}")

    chart.notes = notes
    chart.star_powers = star_powers
    chart.events = events
    chart.finalize()
    return chart


def tryint(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


# TODO: Handle metadata smarter
def set_metadata(song, lines: List[RawMetadata]) -> Dict[str, Union[str, int]]:
    metadata = {}
    for md in lines:
        if not isinstance(md, RawMetadata):
            raise InvalidMetadataException(f"Invalid metadata {md}")
        metadata[md.key] = md.value
    # TODO: Which metadata fields are required, and which are optional?
    song.full_name = metadata.pop("Name", None)
    song.title, song.subtitle = song.full_name, None
    if song.full_name is not None:
        RE_PARENTHETICAL = re.compile(r"(.*)(\(.*\).*)")
        if m := RE_PARENTHETICAL.match(song.full_name):
            song.title, song.subtitle = m.groups()

    song.alt_title = "UNUSED"
    song.artists = metadata.pop("Artist", None)
    song.album = metadata.pop("Album", None)
    song.year = metadata.pop("Year", None)
    song.charter = metadata.pop("Charter", None)
    song.offset = tryint(metadata.pop("Offset", None))
    song.resolution = tryint(metadata.pop("Resolution"))
    song.difficulty = tryint(metadata.pop("Difficulty", None))
    song.previewstart = tryint(metadata.pop("PreviewStart", None))
    song.previewend = tryint(metadata.pop("PreviewEnd", None))
    song.genre = metadata.pop("Genre", None)
    song.mediastream = metadata.pop("MediaStream", None)  # TODO: Should this be MusicStream?
    # TODO: Do something with this unparsed metadata entries
    metadata.pop("Player2", None)
    metadata.pop("MediaType", None)
    metadata.pop("MusicStream", None)
    metadata.pop("GuitarStream", None)
    if len(metadata) > 0:
        raise UnparsedMetadataException(f"Unparsed metadata: {list(metadata.keys())}")


def parse_synctrack(song, lines: List[RawTempo, RawTS]) -> Tuple[List[RawTempo], List[RawTS]]:
    raw_tempos = []
    timesigs = []
    for line in lines:
        if isinstance(line, RawTempo):
            raw_tempos.append(line)
        elif isinstance(line, RawTS):
            timesigs.append(line)   # TODO: Put these in a proper class
        else:
            raise InvalidSynctrackDataException(f"Invalid synctrack data {line}")

    tempos = []
    for raw_tempo in raw_tempos:
        ticks_per_second = song.resolution * raw_tempo.mbpm / 1000 / 60
        tempo = TempoEvent(song, raw_tempo.time, ticks_per_second)
        tempos.append(tempo)
    tempo_calc = TempoCalculator(tempos)

    return tempo_calc, timesigs


def parse_events(song, lines: List[RawEvent]):
    events = []
    for line in lines:
        if not isinstance(line, RawEvent):
            raise InvalidEventException(f"Invalid event {line}")
        events.append(event_from_raw(song, None, line))
    return sorted(events)


def song_from_raw(datablocks: Dict[str, List[RawNote, RawEvent, RawTempo, RawAnchor, RawTS, RawStarPower, RawMetadata]]) -> Song:
    if "Song" not in datablocks:
        raise MissingSongBlockException("Missing Song block")
    if "Events" not in datablocks:
        raise MissingEventsBlockException("Missing Events block")
    if "SyncTrack" not in datablocks:
        raise MissingSyncTrackBlockException("Missing SyncTrack block")

    song = Song()
    set_metadata(song, datablocks.pop("Song"))
    song.tempo_calc, song.timesigs = parse_synctrack(song, datablocks.pop("SyncTrack"))
    song.events = parse_events(song, datablocks.pop("Events"))
    part_vocals = datablocks.pop("PART VOCALS", None)    # TODO Handle vocals section

    charts = {}
    for block, lines in datablocks.items():
        chart = chart_from_raw(song, block, lines)
        key = (chart.difficulty, chart.instrument)
        if key in charts:
            raise DuplicateChartException("Duplicate chart: {chart.difficulty} {chart.instrument}")
        charts[key] = chart
    song.charts = charts

    song.finalize()

    return song


def load(f) -> Song:
    datablocks = load_raw(f)
    song = song_from_raw(datablocks)
    return song
