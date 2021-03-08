from charm.lib.utils import cache_on
from charm.test.lyrics.run_around import lyrics

import pygame
import pygame.freetype
import pygame.draw

from nygame import DigiText as T
from nygame.emoji import emojize


def clean_word(word: str):
    if word.endswith("-"):
        word = word.removesuffix("-")
    else:
        word = word + " "
    word = word.replace("=", "-").replace("''", "\"").replace("+", "").replace("#", "").replace("^", "")
    word = emojize(word)
    return word


class LyricWord():
    def __init__(self, offset, text):
        self.offset = offset
        self.text = clean_word(text)

    def is_on(self, curr_offset):
        return self.offset <= curr_offset

    def __lt__(self, other):
        return self.offset < other.offset

    @classmethod
    def parse(cls, j):
        return cls(j["time"], j["word"])


class LyricPhrase():
    def __init__(self, start, end, words):
        self.start = start
        self.end = end
        self.words = sorted(LyricWord.parse(w) for w in words)
        self.words[-1].text = self.words[-1].text.rstrip()
        self.next = None

    def get_on_text(self, tracktime):
        return "".join(w.text for w in self.words if w.is_on(tracktime - self.start))

    def get_off_text(self, tracktime):
        return "".join(w.text for w in self.words if not w.is_on(tracktime - self.start))

    def get_text(self):
        return "".join(w.text for w in self.words)

    def render_to(self, surf, tracktime, fontname, offset=(0, 0)):
        full_text = self.get_text()
        on_text = self.get_on_text(tracktime)
        off_text = self.get_off_text(tracktime)
        fontsize = fit_text(full_text, fontname, surf.get_width() * 0.75, 24)
        T.font = fontname
        T.size = fontsize
        digitext = T(on_text, color="#ffff00") + T(off_text, color="#808080")
        dest_rect = digitext.get_rect()
        dest_rect.centerx = surf.get_rect().centerx
        dest_rect.y = surf.get_rect().centery
        dest_rect.move_ip(offset)
        digitext.render_to(surf, dest_rect)

    @property
    def fade(self):
        if self.next is None:
            return 1
        return min(self.next.start - self.end, 1)

    @property
    def fade_end(self):
        return self.end + self.fade

    def is_active(self, tracktime):
        return self.start <= tracktime < self.end

    def is_waiting(self, tracktime):
        return self.start > tracktime

    def is_done(self, tracktime):
        return self.end <= tracktime

    def __lt__(self, other):
        return self.start < other.start

    @classmethod
    def parse(cls, j):
        return cls(j["time"], j["end_time"], j["words"])


class LyricAnimator:
    def __init__(self, phrases: list = lyrics, *,
                 size: tuple = (600, 500), font = "Segoe UI Emoji", show_next=False):
        self.phrases = sorted(LyricPhrase.parse(p) for p in phrases)
        self.width, self.height = size
        self.font = font
        self._image = None
        self.tracktime = 0
        self.last_drawn = None
        self.show_next = show_next

        for p, np in zip(self.phrases, self.phrases[1:] + [None]):
            p.next = np

    @property
    @cache_on("tracktime")
    def active_phrase(self):
        try:
            return next(p for p in self.phrases if p.is_active(self.tracktime))
        except StopIteration:
            return None

    @property
    @cache_on("tracktime")
    def next_phrase(self):
        try:
            return next(p for p in self.phrases if p.is_waiting(self.tracktime))
        except StopIteration:
            return None

    @property
    @cache_on("tracktime")
    def prev_phrase(self):
        try:
            return next(p for p in self.phrases[::-1] if p.is_done(self.tracktime))
        except StopIteration:
            return None

    @property
    @cache_on("tracktime")
    def on_text(self):
        return self.active_phrase and self.active_phrase.get_on_text(self.tracktime)

    @property
    @cache_on("tracktime")
    def off_text(self):
        return self.active_phrase and self.active_phrase.get_off_text(self.tracktime)

    @property
    @cache_on("tracktime")
    def next_text(self):
        return self.next_phrase and self.next_phrase.get_text()

    def draw(self):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        pygame.draw.line(surf, "red", surf.get_rect().midleft, surf.get_rect().midright)

        if self.active_phrase is not None:
            self.active_phrase.render_to(surf, self.tracktime, self.font)

        if self.show_next and self.next_phrase is not None:
            self.next_phrase.render_to(surf, self.tracktime, self.font, offset=(0, 40))

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
