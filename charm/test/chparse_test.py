import importlib.resources as pkg_resources

import chparse
from chparse import Difficulties, Instruments

from charm.data import example

with pkg_resources.open_text(example, "notes_moon.chart", "utf-8 sig") as f:
    chart = chparse.parse.load(f)


def test():
    print(repr(chart))
    sections = {}
    notes = []
    lyrics = {}
    sync = {}
    for event in chart.events:
        if event.event.startswith("section"):
            sections[event.time] = event.event.removeprefix("section ")
        elif event.event.startswith("lyric"):
            lyrics[event.time] = event.event.removeprefix("lyric ")
    for note in chart.instruments[Difficulties.EXPERT][Instruments.GUITAR]:
        notes.append(note)

    print(
        f"Sections: {sections}\n"
        f"Lyrics: {lyrics}\n"
        f"Notes {notes}"
    )
