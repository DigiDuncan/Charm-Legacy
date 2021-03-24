import importlib.resources as pkg_resources
from itertools import count, filterfalse, takewhile, tee
from typing import Union

import pygame
from pygame import Rect, Surface, image, transform
from pygame.constants import SRCALPHA

import charm.data.images.spritesheets as image_folder
from charm.loaders.chchart import Chart

HIT_WINDOW = 0.140  # 140ms

fretnums = {
    "green": 0,
    "red": 1,
    "yellow": 2,
    "blue": 3,
    "orange": 4,
    "open": 7
}

fretmap = {
    "green": 0,
    "red": 1,
    "yellow": 2,
    "blue": 3,
    "orange": 4,
    "sp": 5,
    "open": (6, 5),
    "opensp": (11, 5)
}

flagmap = {
    "note": 0,
    "hopo": 1,
    "tap": 2,
    "strike": 6
}

gh_sheet: Surface = None

fret_images = {}


def get_sprite(flag: str, fret: Union[str, int]) -> Surface:
    return fret_images[flag][fret]


def set_sprite(flag: str, fretname: str, sprite: Surface):
    fret_images[flag][fretname] = sprite
    if fretname in fretnums:
        fretnum = fretnums[fretname]
        fret_images[flag][fretnum] = sprite


def init():
    global gh_sheet

    SPRITE_SIZE = 64

    with pkg_resources.path(image_folder, "gh.png") as p:
        gh_sheet = image.load(p)
        gh_sheet.convert_alpha()

    for flag, sy in flagmap.items():
        fret_images[flag] = {}
        for fret, sxw in fretmap.items():
            sw = 1
            try:
                sx, sw = sxw
            except TypeError:
                sx = sxw
            x = sx * SPRITE_SIZE
            y = sy * SPRITE_SIZE
            w = sw * SPRITE_SIZE
            h = SPRITE_SIZE
            img = gh_sheet.subsurface(Rect(x, y, w, h))
            set_sprite(flag, fret, img)


def getone(items):
    try:
        return next(items)
    except StopIteration:
        return None


class HyperloopDisplay:
    def __init__(self, chart: Chart, *, size: tuple = (400, 400), lefty = False):
        self.chart = chart
        self.secs_to_ticks = self.chart.song.tempo_calc.secs_to_ticks
        self.ticks_to_secs = self.chart.song.tempo_calc.ticks_to_secs
        self.size = size
        self.lefty = lefty
        self.track_ticks = 0
        self.length = 0.75
        self.px_per_sec = size[1] / self.length
        self.strike_fadetime = 0.5
        self.visible_chords = []
        self._image = Surface(size, SRCALPHA)
        self.last_drawn = None

    @property
    def tracktime(self):
        return self.ticks_to_secs(self.track_ticks)

    @property
    def end(self):
        return self.secs_to_ticks(self.tracktime + self.length)

    def get_visible_beats(self):
        # This needs to be updated to handle multiple timesigs
        timesig = self.chart.song.timesig_by_ticks[self.track_ticks]

        ticks_per_quarternote = self.chart.song.resolution
        ticks_per_wholenote = ticks_per_quarternote * 4
        beats_per_measure = timesig.numerator
        beats_per_wholenote = timesig.denominator
        ticks_per_beat = ticks_per_wholenote / beats_per_wholenote
        ticks_per_measure = ticks_per_beat * beats_per_measure

        ticks_since_timesig = self.track_ticks - timesig.tick_start

        first_measure = self.track_ticks - (ticks_since_timesig % ticks_per_measure)
        first_beat = self.track_ticks - (ticks_since_timesig % ticks_per_beat)

        measures = list(takewhile(lambda m: m <= self.end, count(first_measure, ticks_per_measure)))
        beats = list(takewhile(lambda b: b <= self.end, count(first_beat, ticks_per_beat)))
        quarterbeats = list(takewhile(lambda b: b <= self.end, count(first_beat, ticks_per_beat / 2)))

        #     measureLine.tickOffset = 0
        #     measureLine.repetitions = 1
        #     measureLine.tickGap = resolution * (4 / denominator * numerator)
        #     measureLine.repetitionCycleOffset = 0
        #     beatLine.tickGap = measureLine.tickGap / numerator
        #     beatLine.tickOffset = beatLine.tickGap
        #     beatLine.repetitions = numerator - 1
        #     beatLine.repetitionCycleOffset = beatLine.tickOffset
        #     quarterBeatLine.tickGap = beatLine.tickGap
        #     quarterBeatLine.tickOffset = beatLine.tickGap / 2
        #     quarterBeatLine.repetitions = numerator
        #     quarterBeatLine.repetitionCycleOffset = 0

        return measures, beats, quarterbeats

    def update(self, tracktime):
        self.track_ticks = self.secs_to_ticks(tracktime)
        self.visible_chords = self.chart.chord_by_ticks[self.track_ticks:self.end]
        last_fade = self.secs_to_ticks(self.tracktime - self.strike_fadetime)
        self.old_chords = self.chart.chord_by_ticks[last_fade:self.track_ticks]

    def draw(self):
        self._image.fill("clear")

        self.draw_beatlines()
        self.draw_strikes()
        self.draw_chords()
        self.draw_zero()

        if self.lefty:
            self._image = transform.flip(self._image, True, False)

    def draw_beatlines(self):
        measures, beats, quarterbeats = self.get_visible_beats()
        for q in quarterbeats:
            y = self.gety(self.ticks_to_secs(q))
            pygame.draw.line(self._image, (64, 64, 64), (0, y), (self.size[0], y), width = 1)
        for b in beats:
            y = self.gety(self.ticks_to_secs(b))
            pygame.draw.line(self._image, (128, 128, 128), (0, y), (self.size[0], y), width = 1)
        for m in measures:
            y = self.gety(self.ticks_to_secs(m))
            pygame.draw.line(self._image, (128, 128, 128), (0, y), (self.size[0], y), width = 5)

    def draw_strikes(self):
        fret_strikes = [0, 0, 0, 0, 0]
        for chord in self.old_chords:
            timediff = self.tracktime - chord.start
            # 0 - 1
            fade = max(0, self.strike_fadetime - timediff) / self.strike_fadetime
            for fret in chord.frets:
                fret_strikes[fret] = max(fret_strikes[fret], fade)

        for fret, fade in enumerate(fret_strikes):
            self.draw_fret(fret, "strike", self.tracktime, fade=fade)

    def draw_chords(self):
        for chord in self.visible_chords[::-1]:
            for fret in chord.frets:
                self.draw_fret(fret, chord.flag, chord.start)

    def draw_zero(self):
        y = self.gety(self.tracktime)
        pygame.draw.line(self._image, (128, 0, 0), (0, y), (self.size[0], y), width = 3)

    def draw_fret(self, fret, flag, secs, fade=1):
        x = self.get_fretx(fret)
        y = self.gety(secs)
        sprite = get_sprite(flag, fret)
        x -= sprite.get_width() / 2
        y -= sprite.get_height() / 2
        sprite.set_alpha(255 * fade)
        self._image.blit(sprite, (x, y))

    def gety(self, secs):
        secs_until = secs - self.tracktime
        perc_screen = secs_until / self.length
        pixels = perc_screen * self.size[1]
        y = self.size[1] - pixels
        return y - 32

    def get_fretx(self, fret):
        w = self.size[0]
        fret_count = 5
        fret_space = w / fret_count
        fret_space_mid = fret_space / 2
        x = (fret_space * fret) + fret_space_mid
        return x

    @property
    def image(self) -> Surface:
        # Don't rerender what we just rendered
        to_draw = self.track_ticks
        if to_draw != self.last_drawn:
            self.draw()
            self.last_drawn = to_draw
        return self._image
