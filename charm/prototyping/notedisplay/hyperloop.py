from importlib import resources as pkg_resources
from itertools import count, takewhile
import math
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from nygame import DigiText as T
import pygame
import pygame.transform
import pygame.image
import pygame.draw
from pygame import Rect, transform
from pygame.surface import Surface
from pygame.constants import SRCALPHA

from charm.lib.instruments.instrument import Instrument
from charm.lib.pgutils import Quad, warp_surface
from charm.song import Chart, Chord
from charm.prototyping.notedisplay.inputdisplay import InputDisplay, init as input_init

import charm.data.images.spritesheets as image_folder

from .spriteloader import SpriteSheet

HIT_WINDOW = 0.140  # 140ms
sprite_sheet = None


def init():
    global sprite_sheet
    with pkg_resources.path(image_folder, "gh.png") as p:  # TODO: HARDCODE
        sprite_sheet = SpriteSheet.load(p)


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
        self.length: float = 0.75  # TODO: HARDCODE
        self.lanes = 5  # TODO: HARDCODE
        self.strike_fadetime = 0.5
        self.visible_chords: List[Chord] = []
        self._image = Surface(size, SRCALPHA)
        self.bg_tile_height = 0
        self.bg_image: Optional[Surface] = None
        self.bg_image_sp: Optional[Surface] = None
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
    def px_per_sec(self):
        return self.size[1] / self.length

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
        img = str(self.bg)
        imgsplit = img.rsplit(".", 1)
        spimg = imgsplit[0] + "_sp." + imgsplit[1]
        bg_tile = pygame.image.load(img)
        bg_tile.convert_alpha()
        bg_tile_sp = pygame.image.load(spimg)
        bg_tile_sp.convert_alpha()
        w, h = self.size
        # Scale height to fit hyperloop width but maintain aspect ratio.
        aspect = bg_tile.get_rect().height / bg_tile.get_rect().width
        tile_height = int(w * aspect)
        bg_tile = pygame.transform.smoothscale(bg_tile, (w, tile_height))
        bg_tile_sp = pygame.transform.smoothscale(bg_tile_sp, (w, tile_height))

        tile_count = (math.ceil(h / tile_height) + 1)
        full_height = tile_height * tile_count

        rect = bg_tile.get_rect()
        self.bg_tile_height = tile_height
        self.bg_image = Surface((w, full_height))
        self.bg_image_sp = Surface((w, full_height))

        for i in range(tile_count):
            rect.y = i * tile_height
            self.bg_image.blit(bg_tile, rect)
            self.bg_image_sp.blit(bg_tile_sp, rect)

    def update(self, tracktime: float):
        self.track_ticks = self.secs_to_ticks(tracktime)
        self.visible_chords = self.chart.chord_by_ticks[self.track_ticks:self.end]
        visible_sustains = self.chart.chord_by_ticks[min(c.tick_start for c in self.chart.chords if c.tick_end >= self.track_ticks):self.track_ticks]
        self.visible_chords = visible_sustains + self.visible_chords
        last_fade = self.secs_to_ticks(self.tracktime - self.strike_fadetime)
        self.old_chords: List[Chord] = self.chart.chord_by_ticks[last_fade:self.track_ticks]
        if self.id:
            self.id.update()

    def draw(self):
        self._image.fill("clear")

        if self.sp:
            if self.bg_image_sp:
                self.draw_bg(self.bg_image_sp)
            else:
                if self.bg_image:
                    self.draw_bg(self.bg_image)
        else:
            if self.bg_image:
                self.draw_bg(self.bg_image)
        self.draw_beatlines()
        if self.id:
            self.draw_input()
        self.draw_strikes()
        self.draw_chords()
        self.draw_zero()
        self.draw_countdown()

        if self.lefty:
            self._image = transform.flip(self._image, True, False)
        if self.tilt:
            self.project()

    def project(self):
        w, h = self.size
        self._image = warp_surface(self._image,
                                   Quad((0, 0), (w, 0), (w, h), (0, h)),
                                   Quad((w * 0.25, h / 2.5), (w * 0.75, h / 2.5), (w, h), (0, h)))

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
        fret_strikes = [0.0, 0.0, 0.0, 0.0, 0.0]  # TODO: HARDCODE
        for chord in self.old_chords:
            timediff = self.tracktime - chord.start
            # 0 - 1
            fade = max(0, self.strike_fadetime - timediff) / self.strike_fadetime
            for fret in chord.frets:
                if fret == 7:  # TODO: HARDCODE
                    continue
                fret_strikes[fret] = max(fret_strikes[fret], fade)

        for fret, fade in enumerate(fret_strikes):
            self.draw_fret(fret, "strike", self.tracktime, fade=fade, spact=self.sp)

    def draw_chords(self):
        for chord in self.visible_chords[::-1]:
            for fret in chord.frets:
                self.draw_fret(fret, chord.flag, chord.start, spact=self.sp, length=chord.length)

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

    def draw_fret(self, fretnum: int, mode: str, secs: float, fade: float = 1, spact: bool = True, length = 0):
        x = self.get_fretx(fretnum)
        y = self.gety(secs)
        sprite = sprite_sheet.get(fretnum=fretnum, mode=mode, spact=spact)
        # Center fret sprites
        x -= sprite.get_width() / 2
        y -= sprite.get_height() / 2
        sprite.set_alpha(255 * fade)
        if length != 0:
            sustain_img = sprite_sheet.get(fretnum=fretnum, mode="sustainbody", spact=spact)
            sustaincap_img = sprite_sheet.get(fretnum=fretnum, mode="sustaintop", spact=spact)
            width = sustain_img.get_width()
            height = math.ceil(length * self.px_per_sec) - sustaincap_img.get_height()
            sustain_img = pygame.transform.scale(sustain_img, (width, height))
            sx = self.get_fretx(fretnum)
            sy = self.gety(secs)
            sustain_dest = sustain_img.get_rect()
            sustain_dest.midbottom = (sx, sy)
            sustaincap_dest = sustaincap_img.get_rect()
            sustaincap_dest.midbottom = sustain_dest.midtop
            self._image.blit(sustain_img, sustain_dest)
            self._image.blit(sustaincap_img, sustaincap_dest)
        if secs >= self.tracktime:
            self._image.blit(sprite, (x, y))

    def draw_bg(self, bg_image: Surface):
        bg_rect = bg_image.get_rect()
        offset = ((self.tracktime * self.px_per_sec) % self.bg_tile_height) - self.bg_tile_height
        bg_rect.y = offset

        self._image.blit(bg_image, bg_rect)

        for i in range(self.lanes):
            x = self.get_fretx(i)
            # TODO: Once the strikeline is in, this will look better, but for now, just use the bottom.
            # y = self.size[1] - sprite_sheet.get(fretnum=i, mode="note", spact=False).get_height()
            y = self.size[1]
            pygame.draw.line(self._image, (64, 64, 64), (x, y), (x, 0), width = 1)

    def draw_countdown(self):
        for start, length in self.chart.countdowns.items():
            end = start + length
            if start < self.track_ticks < end:
                timenum = int(self.ticks_to_secs(end - self.track_ticks))
                size = 96
                if timenum == 0:
                    timenum = "Go!"
                    size = 72
                timetext = T(f"{timenum}", font="Lato Medium", size=size, color="white")
                rect = timetext.get_rect()
                rect.center = self._image.get_rect().center
                timetext.render_to(self._image, rect)

    def gety(self, secs: float) -> float:
        secs_until = secs - self.tracktime
        perc_screen = secs_until / self.length
        pixels = perc_screen * self.size[1]
        y = self.size[1] - pixels
        return y - 32

    def get_fretx(self, fret: int):
        if fret == 7:
            fret = 2  # TODO: Gross and hardcoded fix for opens
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
