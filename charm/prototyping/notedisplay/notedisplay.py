import importlib.resources as pkg_resources
from importlib import import_module

import pygame

from charm.lib.utils import cache_on
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
    def __init__(self, chart, *, size: tuple = (400, 100)):
        self.chart = chart
        self._image = pygame.Surface(size)
        self._image.fill("BLUE")
        image_folder = import_module("charm.data.images.gh")
        self.tracktime = 0
        self.last_drawn = None

        self.note_images = {}
        self.note_positions = {}

        for i in range(8):
            if i not in fretmap:
                continue
            with pkg_resources.path(image_folder, f"note_{fretmap[i]}.png") as p:
                note_img = pygame.image.load(p)
            with pkg_resources.path(image_folder, f"hopo_{fretmap[i]}.png") as p:
                hopo_img = pygame.image.load(p)
            with pkg_resources.path(image_folder, f"tap_{fretmap[i]}.png") as p:
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
            return next(c for c in self.chart.chords if self.tracktime <= c.start <= self.tracktime + HIT_WINDOW)
        except StopIteration:
            return None

    def draw(self):
        surf = self._image
        surf.fill("black")
        if self.active_chord is None:
            return surf

        if self.active_chord.mode == "tap":
            for note in self.active_chord.notes:
                surf.blit(self.note_images[('tap', note.kind)], self.note_positions[note.kind])
            return surf
        if self.active_chord.mode == "hopo":
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
