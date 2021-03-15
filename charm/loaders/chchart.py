from __future__ import annotations

from typing import Dict, List

from charm.song import Chart, Event, Note, Song, SPEvent, TimeDelta, TimeStamp
from charm.loaders.raw_chchart import RawEvent, RawNote, RawStarPower, RawMBPM, RawAnchor, RawTS, RawMetadata, load_raw


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


def chart_from_raw(song: Song, instrument: str, lines: List[RawNote, RawEvent, RawMBPM, RawAnchor, RawTS, RawStarPower, RawMetadata]) -> Chart:
    chart = Chart(song, instrument)
    for line in lines:
        if isinstance(line, RawNote):
            chart._notes.append(note_from_raw(song, chart, line))
        elif isinstance(line, RawStarPower):
            chart._star_powers.append(spevent_from_raw(song, chart, line))
        elif isinstance(line, RawEvent):
            chart._events.append(event_from_raw(song, chart, line))
        else:
            raise ValueError(f"Bad line type {line}")
    return chart


def song_from_raw(datablocks: Dict[str, List[RawNote, RawEvent, RawMBPM, RawAnchor, RawTS, RawStarPower, RawMetadata]]) -> Song:
    if "Song" not in datablocks:
        raise ValueError("Missing Song block")
    if "Events" not in datablocks:
        raise ValueError("Missing Events block")
    if "SyncTrack" not in datablocks:
        raise ValueError("Missing SyncTrack block")

    metadata = {md.key: md.value for md in datablocks.pop("Song")}
    synctrack = datablocks.pop("SyncTrack")
    events = datablocks.pop("Events")
    song = Song(metadata, synctrack, events)

    for block, lines in datablocks.items():
        song.charts[block] = chart_from_raw(song, block, lines)

    return song


def load(f) -> Song:
    datablocks = load_raw(f)
    song = song_from_raw(datablocks)
    return song


if __name__ == "__main__":
    song = load(r"C:\Users\nfear\Desktop\Coding\Charm\charm\test\lyrics\run_around_the_character_code.chart")
    print(song)
