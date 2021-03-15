from __future__ import annotations
from charm.song import Song, Chart, TimeStamp, TimeDelta, Note, SPEvent, Event

from typing import Dict, List

from charm.loaders.raw_chchart import load_raw, RawNote, RawStarPower, RawEvent

RE_PARENTHETICAL = r"(.*)(\(.*\).*)"


def note_from_raw(song, chart, rawnote: RawNote):
    time = TimeStamp(song, rawnote.time)
    length = TimeDelta(time, rawnote.length)
    note = Note(song, chart, time, rawnote.kind, length)
    return note


def spevent_from_raw(song, chart, rawspevent: RawStarPower):
    time = TimeStamp(song, rawspevent.time)
    length = TimeDelta(time, rawspevent.length)
    spevent = SPEvent(song, chart, time, rawspevent.kind, length)
    return spevent


def event_from_raw(song, chart, rawevent: RawEvent):
    time = TimeStamp(song, rawevent.time)
    event = Event(song, chart, time, rawevent.data)
    return event


def chart_from_raw(song, instrument, lines: List):
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


def song_from_raw(datablocks: Dict[str, List]):
    song = Song()
    if "Song" not in datablocks:
        raise ValueError("Missing Song block")
    if "Events" not in datablocks:
        raise ValueError("Missing Events block")
    if "SyncTrack" not in datablocks:
        raise ValueError("Missing SyncTrack block")

    for block, lines in datablocks.items():
        if block == "Song":
            for md in lines:
                song.metadata[md.key] = md.value
        elif block == "SyncTrack":
            for line in lines:
                song._sync_track.append(line)
        elif block == "Events":
            for line in lines:
                song._events.append(line)
        else:
            song.charts[block] = chart_from_raw(song, block, lines)
    return song


def load(f):
    datablocks = load_raw(f)
    song = song_from_raw(datablocks)
    return song


if __name__ == "__main__":
    song = load(r"C:\Users\nfear\Desktop\Coding\Charm\charm\test\lyrics\run_around_the_character_code.chart")
    print(song)
