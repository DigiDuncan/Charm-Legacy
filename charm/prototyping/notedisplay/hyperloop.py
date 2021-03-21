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
        self.strike_fadetime = 0.5

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
        self.visible_chords = self.chart[self.tracktime - self.strike_fadetime:self.end]

    def draw(self):
        self._image.fill("clear")

        fret_strikes = [0, 0, 0, 0, 0]
        for chord in self.visible_chords:
            diff = chord.start - self.tracktime
            if diff < 0:
                for fret in chord.frets:
                    fade = max(0, self.strike_fadetime + diff)  # 0 to 0.5
                    fade /= self.strike_fadetime                # 0 t0 1
                    fret_strikes[fret] = max(fret_strikes[fret], fade)
                continue
            for fret in chord.frets:
                pos = self.get_fret_pos(fret, diff)
                self._image.blit(fret_images[chord.flag][fret], pos)

        for fret, fade in enumerate(fret_strikes):
            fade_alpha = 255 * fade
            strike_images[fret].set_alpha(fade_alpha)

            pos = self.get_fret_pos(fret)
            self._image.blit(strike_images[fret], pos)


    @property
    def image(self) -> pygame.Surface:
        # Don't rerender what we just rendered
        to_draw = self.tracktime
        if to_draw != self.last_drawn:
            self.draw()
            self.last_drawn = to_draw
        return self._image
