import bisect
from pathlib import Path

import pygame
import pygame.draw
import pygame.freetype
from nygame import DigiText as T

from charm.loaders.chlyrics import load_lyrics


class LyricAnimator:
    def __init__(self, chart, *, size: tuple = (700, 100), font = "Segoe UI Emoji", show_next=False, show_baseline = False):
        with Path(chart).open("r", encoding="utf-8") as f:
            self.phrases = load_lyrics(f)   # TODO: Update this to use lyrics from Song object
        self.phrase_starts = [p.start for p in self.phrases]
        self.width, self.height = size
        self.font = font
        self._image = None
        self.tracktime = 0
        self.last_drawn = None
        self.show_next = show_next
        self.show_baseline = show_baseline

        for p, np in zip(self.phrases, self.phrases[1:] + [None]):
            p.next = np

    @property
    def active_phrase(self):
        phrase = self.phrases[self.phrase_index]
        if self.tracktime >= phrase.end:
            return None
        return phrase

    @property
    def phrase_index(self):
        phrase_index = bisect.bisect_left(self.phrase_starts, self.tracktime)
        return phrase_index

    @property
    def next_phrase(self):
        try:
            phrase = self.phrases[self.phrase_index + 1]
        except IndexError:
            phrase = None
        return phrase

    @property
    def prev_phrase(self):
        try:
            phrase = self.phrases[self.phrase_index - 1]
        except IndexError:
            phrase = None
        return phrase

    @property
    def on_text(self):
        return self.active_phrase and self.active_phrase.get_on_text(self.tracktime)

    @property
    def off_text(self):
        return self.active_phrase and self.active_phrase.get_off_text(self.tracktime)

    @property
    def next_text(self):
        return self.next_phrase and self.next_phrase.get_text()

    def draw(self):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        if self.show_baseline:
            pygame.draw.line(surf, "red", surf.get_rect().midleft, surf.get_rect().midright)

        if self.active_phrase is not None:
            render_phrase_to(self.active_phrase, surf, self.tracktime, self.font)

        if self.show_next and self.next_phrase is not None:
            render_phrase_to(self.next_phrase, surf, self.tracktime, self.font, offset=(0, 40))

        return surf

    def update(self, tracktime):
        self.tracktime = tracktime

    @property
    def image(self) -> pygame.Surface:
        # Don't rerender what we just rendered
        to_draw = (self.on_text, self.off_text, self.next_text)
        if to_draw != self.last_drawn:
            self._image = self.draw()
            self.last_drawn = to_draw
        return self._image



fonts = {}
largest_font = 30


def get_font(name, size):
    if (name, size) not in fonts:
        fonts[(name, size)] = pygame.freetype.SysFont(name, size)
    return fonts[(name, size)]


def precache_fonts(name):
    for size in range(largest_font, 4, -2):
        get_font(name, size)


def fit_text(text, fontname, width, maxsize = None):
    for size in range(maxsize or largest_font, 4, -2):
        font = get_font(fontname, size)
        if font.get_rect(text).w <= (width * 0.95):
            return size
    return None


def render_phrase_to(phrase, surf, tracktime, fontname, offset=(0, 0)):
    full_text = phrase.get_text()
    on_text = phrase.get_on_text(tracktime)
    off_text = phrase.get_off_text(tracktime)
    fontsize = fit_text(full_text, fontname, surf.get_width(), 24)
    T.font = fontname
    T.size = fontsize
    digitext = T(on_text, color="#ffff00") + T(off_text, color="#808080")
    dest_rect = digitext.get_rect()
    dest_rect.centerx = surf.get_rect().centerx
    dest_rect.y = surf.get_rect().centery
    dest_rect.move_ip(offset)
    digitext.render_to(surf, dest_rect)
