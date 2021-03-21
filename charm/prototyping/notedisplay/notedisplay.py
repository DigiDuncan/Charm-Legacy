import importlib.resources as pkg_resources
from importlib import import_module
from pathlib import Path

import pygame

from charm.lib.utils import cache_on
from charm.loaders import chchart
from charm.song import Chord

HIT_WINDOW = 0.140  # 140ms

fretmap = {
    0: "green",
    1: "red",
    2: "yellow",
    3: "blue",
    4: "orange",
    7: "open"
}


class NoteDisplay:
    def __init__(self, chartfile, *, size: tuple = (400, 100)):
        self.chartfile = chartfile
        self.size = size
        self._image = pygame.Surface(self.size)
        self._image.fill("BLUE")
        self.image_folder = import_module("charm.data.images.gh")
        self.tracktime = 0
        self.last_drawn = None

        with Path(chartfile).open("r", encoding="utf-8") as f:
            self.song = chchart.load(f)

        self.chart = self.song.charts[('Expert', 'Single')]

        self.note_images = {}
        self.note_positions = {}

        for i in range(8):
            if i not in fretmap:
                continue
            with pkg_resources.path(self.image_folder, f"note_{fretmap[i]}.png") as p:
                note_img = pygame.image.load(p)
            with pkg_resources.path(self.image_folder, f"hopo_{fretmap[i]}.png") as p:
                hopo_img = pygame.image.load(p)
            with pkg_resources.path(self.image_folder, f"tap_{fretmap[i]}.png") as p:
                tap_img = pygame.image.load(p)
            note_img.convert_alpha()
            hopo_img.convert_alpha()
            tap_img.convert_alpha()
            self.note_images[('note', i)] = note_img
            self.note_images[('hopo', i)] = hopo_img
            self.note_images[('tap', i)] = tap_img

        for i in range(5):
            w = 80 * i
            self.note_positions[i] = (w, 0)
        self.note_positions[7] = (0, 16)

    def update(self, tracktime):
        self.tracktime = tracktime

    @property
    @cache_on("tracktime")
    def active_chord(self) -> Chord:
        try:
            return next(c for c in self.chart.chords if self.tracktime <= c.time.ticks.secs <= self.tracktime + HIT_WINDOW)
        except StopIteration:
            return None

    def draw(self):
        surf = pygame.Surface(self.size)
        if self.active_chord is None:
            return surf
        tap = False
        hopo = False
        for note in self.active_chord.notes:
            if note.kind == 6:
                tap = True
            if note.kind == 5:
                hopo = True
        if tap is True:
            for note in self.active_chord.notes:
                surf.blit(self.note_images[('tap', note.kind)], self.note_positions[note.kind])
            return surf
        if hopo is True:
            for note in self.active_chord.notes:
                surf.blit(self.note_images[('hopo', note.kind)], self.note_positions[note.kind])
            return surf
        for note in self.active_chord.notes:
            surf.blit(self.note_images[('note', note.kind)], self.note_positions[note.kind])
        return surf

    @property
    def image(self) -> pygame.Surface:
        # Don't rerender what we just rendered
        to_draw = None if self.active_chord is None else tuple(n.kind for n in self.active_chord.notes)
        if to_draw != self.last_drawn:
            self._image = self.draw()
            self.last_drawn = to_draw
        return self._image
