from importlib import resources as pkg_resources
from charm.lib.instruments.instrument import Instrument
import math
from itertools import count, takewhile
from pathlib import Path
from typing import Callable, Iterator, List, Optional, Tuple, TypeVar

import pygame
import pygame.transform
import pygame.image
import pygame.draw
import PIL.Image
from pygame import Rect, transform
from pygame.surface import Surface
from pygame.constants import SRCALPHA

from charm.song import Chart, Chord
from charm.prototyping.notedisplay.inputdisplay import InputDisplay, init as input_init

import charm.data.images.spritesheets as image_folder

from .spriteloader import SpriteSheet

HIT_WINDOW = 0.140  # 140ms
sprite_sheet = None


def init():
    global sprite_sheet
    with pkg_resources.path(image_folder, "gh.png") as p:
        sprite_sheet = SpriteSheet.load(p)


T = TypeVar("T")


def getone(items: Iterator[T]) -> Optional[T]:
    try:
        return next(items)
    except StopIteration:
        return None


class HyperloopDisplay:
    def __init__(self, chart: Chart, instrument: Optional[Instrument], *, size: Tuple[int, int] = (400, 400), lefty: bool = False, hitwindow_vis: bool = False, bg: Optional[str] = None):
        self.chart = chart
        self.instrument = instrument
        self.secs_to_ticks: Callable[[float], int] = self.chart.song.tempo_calc.secs_to_ticks
        self.ticks_to_secs: Callable[[int], float] = self.chart.song.tempo_calc.ticks_to_secs
        self.size = size
        self.lefty = lefty
        self.bg: Optional[Path] = None if bg is None else Path(bg)
        self.track_ticks: int = 0
        self.length: float = 0.75
        self.px_per_sec = size[1] / self.length  # This will mess up with BPM scaling, eventually.
        self.strike_fadetime = 0.5
        self.visible_chords: List[Chord] = []
        self._image = Surface(size, SRCALPHA)
        self.bg_tile_height = 0
        self.bg_image: Optional[Surface] = None
        self.last_drawn = None
        self.tilt: bool = False
        self.sp: bool = False
        self.hitwindow_vis = hitwindow_vis

        self.create_bg()
        input_init()
        self.id: Optional[InputDisplay] = None
        if self.instrument:
            self.id = InputDisplay(self.instrument, size=(400, 100))

    @property
    def tracktime(self):
        return self.ticks_to_secs(self.track_ticks)

    @property
    def end(self):
        return self.secs_to_ticks(self.tracktime + self.length)

    def get_visible_beats(self) -> Tuple[List[float], List[float], List[float]]:
        # This needs to be updated to handle multiple timesigs
        timesig = self.chart.song.timesig_by_ticks[self.track_ticks]
        if timesig is None:
            return [], [], []

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

    def create_bg(self):
        if self.bg is None:
            return
        bg_tile = pygame.image.load(str(self.bg))
        bg_tile.convert_alpha()
        w, h = self.size
        # Scale height to fit hyperloop width but maintain aspect ratio.
        aspect = bg_tile.get_rect().height / bg_tile.get_rect().width
        tile_height = int(w * aspect)
        bg_tile = pygame.transform.smoothscale(bg_tile, (w, tile_height))

        tile_count = (math.ceil(h / tile_height) + 1)
        full_height = tile_height * tile_count

        rect = bg_tile.get_rect()
        self.bg_tile_height = tile_height
        self.bg_image = Surface((w, full_height))

        for i in range(tile_count):
            rect.y = i * tile_height
            self.bg_image.blit(bg_tile, rect)

    def update(self, tracktime: float):
        self.track_ticks = self.secs_to_ticks(tracktime)
        self.visible_chords = self.chart.chord_by_ticks[self.track_ticks:self.end]
        last_fade = self.secs_to_ticks(self.tracktime - self.strike_fadetime)
        self.old_chords: List[Chord] = self.chart.chord_by_ticks[last_fade:self.track_ticks]
        if self.id:
            self.id.update()

    def draw(self):
        self._image.fill("clear")

        if self.bg_image:
            self.draw_bg(self.bg_image)
        self.draw_beatlines()
        if self.id:
            self.draw_input()
        self.draw_strikes()
        self.draw_chords()
        self.draw_zero()

        if self.lefty:
            self._image = transform.flip(self._image, True, False)
        if self.tilt:
            self.project()

    def project(self):
        def surfaceToPillow(surf: Surface) -> PIL.Image.Image:
            strFormat = 'RGBA'
            raw_str = pygame.image.tostring(surf, strFormat, False)
            pill = PIL.Image.frombytes(strFormat, surf.get_size(), raw_str)
            return pill

        def pillowToSurface(pill: PIL.Image.Image) -> pygame.surface.Surface:
            strFormat = 'RGBA'
            raw_str = pill.tobytes("raw", strFormat)
            surf = pygame.image.fromstring(raw_str, pill.size, strFormat)
            return surf
        pill = surfaceToPillow(self._image)
        # TODO: This doesn't work anymore because I changed the resolution of the screen...
        # *･゜ﾟ･*:.｡. .｡.:*･゜ﾟ･* MAGIC NUMBERS *･゜ﾟ･*:.｡. .｡.:*･゜ﾟ･*
        data = [3, 0.7, -400, 0, 2.76, 0, 0, 0.0035]
        pill = pill.transform(pill.size, PIL.Image.PERSPECTIVE, data=data)
        self._image = pillowToSurface(pill)

    def draw_beatlines(self):
        measures, beats, quarterbeats = self.get_visible_beats()
        for q in quarterbeats:
            y = self.gety(self.ticks_to_secs(int(q)))
            pygame.draw.line(self._image, (64, 64, 64), (0, y), (self.size[0], y), width = 1)
        for b in beats:
            y = self.gety(self.ticks_to_secs(int(b)))
            pygame.draw.line(self._image, (128, 128, 128), (0, y), (self.size[0], y), width = 1)
        for m in measures:
            y = self.gety(self.ticks_to_secs(int(m)))
            pygame.draw.line(self._image, (128, 128, 128), (0, y), (self.size[0], y), width = 5)

    def draw_strikes(self):
        fret_strikes = [0.0, 0.0, 0.0, 0.0, 0.0]
        for chord in self.old_chords:
            timediff = self.tracktime - chord.start
            # 0 - 1
            fade = max(0, self.strike_fadetime - timediff) / self.strike_fadetime
            for fret in chord.frets:
                fret_strikes[fret] = max(fret_strikes[fret], fade)

        for fret, fade in enumerate(fret_strikes):
            self.draw_fret(fret, "strike", self.tracktime, fade=fade, spact=self.sp)

    def draw_chords(self):
        for chord in self.visible_chords[::-1]:
            for fret in chord.frets:
                self.draw_fret(fret, chord.flag, chord.start, spact=self.sp)

    def draw_zero(self):
        y = self.gety(self.tracktime)
        pygame.draw.line(self._image, (128, 0, 0), (0, y), (self.size[0], y), width = 3)
        if self.hitwindow_vis:
            hitwindow_size = self.px_per_sec * HIT_WINDOW
            hit_rect = Rect(0, 0, self.size[0], hitwindow_size)
            hit_rect.centery = y
            hit_surf = Surface((self.size[0], hitwindow_size), SRCALPHA)
            hit_surf.fill((255, 0, 0, 64))
            self._image.blit(hit_surf, hit_rect)

    def draw_input(self):
        dest = self.id.image.get_rect()
        dest.centerx = self._image.get_rect().centerx
        dest.bottom = self._image.get_rect().bottom
        self._image.blit(self.id.image, dest)

    def draw_fret(self, fretnum: int, mode: str, secs: float, fade: float = 1, spact: bool = True):
        x = self.get_fretx(fretnum)
        y = self.gety(secs)
        sprite = sprite_sheet.get(fretnum=fretnum, mode=mode, spact=spact)
        # Center fret sprites
        x -= sprite.get_width() / 2
        y -= sprite.get_height() / 2
        sprite.set_alpha(255 * fade)
        self._image.blit(sprite, (x, y))

    def draw_bg(self, bg_image: Surface):
        bg_rect = bg_image.get_rect()
        offset = ((self.tracktime * self.px_per_sec) % self.bg_tile_height) - self.bg_tile_height
        bg_rect.y = offset

        self._image.blit(bg_image, bg_rect)

    def gety(self, secs: float) -> float:
        secs_until = secs - self.tracktime
        perc_screen = secs_until / self.length
        pixels = perc_screen * self.size[1]
        y = self.size[1] - pixels
        return y - 32

    def get_fretx(self, fret: int):
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
