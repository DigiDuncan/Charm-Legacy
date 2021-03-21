import importlib.resources as pkg_resources

import pygame
from pygame.constants import SRCALPHA
import charm.data.images.gh as image_folder

HIT_WINDOW = 0.140  # 140ms

fretnames = {
    0: "green",
    1: "red",
    2: "yellow",
    3: "blue",
    4: "orange",
    7: "open"
}

flags = {
    "note",
    "hopo",
    "tap"
}

fret_images = {
    "note": {},
    "hopo": {},
    "tap": {}
}

strike_images = {
}

hit_images = {
}


def init():
    for flag in flags:
        for fret, name in fretnames.items():
            with pkg_resources.path(image_folder, f"{flag}_{name}.png") as p:
                img = pygame.image.load(p)
                img.convert_alpha()
            fret_images[flag][fret] = img

    for fret, name in fretnames.items():
        if name == "open":
            continue
        with pkg_resources.path(image_folder, f"strikeline_{name}.png") as p:
            img = pygame.image.load(p)
            img.convert_alpha()
        strike_images[fret] = img

    for fret, name in fretnames.items():
        if name == "open":
            continue
        with pkg_resources.path(image_folder, f"strikeline_{name}.png") as p:
            img = pygame.image.load(p)
            img.convert_alpha()
        hit_images[fret] = img


def getone(items):
    try:
        return next(items)
    except StopIteration:
        return None


class HyperloopDisplay:
    def __init__(self, chart, *, size: tuple = (400, 400)):
        self.chart = chart
        self.size = size
        self._image = pygame.Surface(size, SRCALPHA)
        self.tracktime = 0
        self.length = 1
        self.last_drawn = None
        self.chord_stream = iter(c for c in self.chart.chords)
        self.visible_chords = []
        self.upcoming_chord = next(self.chord_stream)
        self.fret_strikes = [-1, -1, -1, -1, -1]

    @property
    def end(self):
        return self.tracktime + self.length

    def get_fret_pos(self, f, diff=0):
        if diff < 0:
            diff = 0
        w, h = self.size
        fw, fh = 64, 64
        fcnt = 5

        wspace = w / fcnt
        x = (wspace * f) + (wspace / 2) - (fw / 2)

        y = h - fh - (h * (diff / self.length))

        if f == 7:
            x = 0
            y += 16

        return x, y

    def update(self, tracktime):
        self.tracktime = tracktime
        # Remove tracks that have become hidden
        while self.visible_chords and self.visible_chords[0].start < self.tracktime:
            oldchord = self.visible_chords.pop(0)
            for fret in fretnames:
                if fret == 7:
                    continue
                for hit in oldchord.frets:
                    self.fret_strikes[hit] = self.tracktime
        # Add tracks that have become visible
        while self.upcoming_chord and self.upcoming_chord.start < self.end:
            self.visible_chords.append(self.upcoming_chord)
            self.upcoming_chord = getone(self.chord_stream)

    def draw(self):
        self._image.fill(0x00000000)
        for fret, name in fretnames.items():
            if name == "open":
                continue
            pos = self.get_fret_pos(fret)
            since_strike = self.tracktime - self.fret_strikes[fret]
            fadetime = 0.5
            fade = max(fadetime - since_strike, 0)
            strike_images[fret].set_alpha(fade / fadetime * 255)
            self._image.blit(strike_images[fret], pos)

        for chord in self.visible_chords:
            diff = chord.start - self.tracktime
            for fret in chord.frets:
                pos = self.get_fret_pos(fret, diff)
                self._image.blit(fret_images[chord.flag][fret], pos)

    @property
    def image(self) -> pygame.Surface:
        # Don't rerender what we just rendered
        to_draw = self.tracktime
        if to_draw != self.last_drawn:
            self.draw()
            self.last_drawn = to_draw
        return self._image
