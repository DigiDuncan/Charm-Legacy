from __future__ import annotations
from itertools import product
import re

from typing import Dict, List, Tuple, Union

from charm.song import Chart, Event, Note, Song, SPEvent, TimeDelta, TimeStamp
from charm.loaders.raw_chchart import RawEvent, RawNote, RawStarPower, RawTempo, RawAnchor, RawTS, RawMetadata, load_raw


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
        raise ValueError(f"Invalid Header: {header}")

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
            raise ValueError(f"Bad line type {line}")

    chart.setup(notes, star_powers, events)
    return chart


def tryint(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


# TODO: Handle metadata smarter
def parse_metadata(song, lines: List[RawMetadata]) -> Dict[str, Union[str, int]]:
    metadata = {}
    for md in lines:
        if not isinstance(md, RawMetadata):
            raise ValueError(f"Invalid metadata {md}")
        metadata[md.key] = md.value

    # TODO: Which metadata fields are required, and which are optional?
    song.full_name = metadata.pop("Name", None)
    RE_PARENTHETICAL = re.compile(r"(.*)(\(.*\).*)")
    if m := RE_PARENTHETICAL.match(song.full_name):
        song.title, song.subtitle = m.groups()
    else:
        song.title, song.subtitle = song.full_name, None

    song.alt_title = "UNUSED"
    song.artists = metadata.pop("Artist", None)
    song.album = metadata.pop("Album", None)
    song.year = metadata.pop("Year", None)
    song.charter = metadata.pop("Charter", None)
    song.offset = tryint(metadata.pop("Offset", None))
    song.resolution = tryint(metadata.pop("Resolution", None))
    song.difficulty = tryint(metadata.pop("Difficulty", None))
    song.previewstart = tryint(metadata.pop("PreviewStart", None))
    song.previewend = tryint(metadata.pop("PreviewEnd", None))
    song.genre = metadata.pop("Genre", None)
    song.mediastream = metadata.pop("MediaStream", None)  # TODO: Should this be MusicStream?
    # TODO: Do something with this unparsed metadata entries
    metadata.pop("Player2", None)
    metadata.pop("MediaType", None)
    metadata.pop("MusicStream", None)
    if len(metadata) > 0:
        raise ValueError(f"Unparsed metadata: {list(metadata.keys())}")


def parse_synctrack(lines: List[RawTempo, RawTS]) -> Tuple[List[RawTempo], List[RawTS]]:
    tempos = []
    timesigs = []
    for line in lines:
        if isinstance(line, RawTempo):
            tempos.append(line)
        elif isinstance(line, RawTS):
            timesigs.append(line)
        else:
            raise ValueError(f"Invalid synctrack data {line}")
    tempos.sort()
    timesigs.sort()
    # TODO: Return a Tempo Calculator
    return tempos, timesigs


def parse_events(song, lines: List[RawEvent]):
    events = []
    for line in lines:
        if not isinstance(line, RawEvent):
            raise ValueError(f"Invalid event {line}")
        events.append(event_from_raw(song, None, line))
    return sorted(events)


def song_from_raw(datablocks: Dict[str, List[RawNote, RawEvent, RawTempo, RawAnchor, RawTS, RawStarPower, RawMetadata]]) -> Song:
    if "Song" not in datablocks:
        raise ValueError("Missing Song block")
    if "Events" not in datablocks:
        raise ValueError("Missing Events block")
    if "SyncTrack" not in datablocks:
        raise ValueError("Missing SyncTrack block")

    song = Song()
    tempos, timesigs = parse_synctrack(datablocks.pop("SyncTrack"))
    parse_metadata(song, datablocks.pop("Song"))
    events = parse_events(song, datablocks.pop("Events"))
    charts = {}
    for block, lines in datablocks.items():
        chart = chart_from_raw(song, block, lines)
        key = (chart.difficulty, chart.instrument)
        if key in charts:
            raise ValueError("Duplicate chart: {chart.difficulty} {chart.instrument}")
        charts[key] = chart

    song.setup(events, charts, tempos, timesigs)

    return song


def load(f) -> Song:
    datablocks = load_raw(f)
    song = song_from_raw(datablocks)
    return song


if __name__ == "__main__":
    song = load(r"C:\Users\nfear\Desktop\Coding\Charm\charm\test\lyrics\run_around_the_character_code.chart")
    print(song)
