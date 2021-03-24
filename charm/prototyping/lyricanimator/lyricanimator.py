import pygame
import pygame.draw
import pygame.freetype
from nygame import DigiText as T

from charm.song import Chart


class LyricAnimator:
    def __init__(self, chart: Chart, *, size: tuple = (700, 100), font = "Segoe UI Emoji", show_next=False, show_baseline = False):
        self.chart = chart
        self.secs_to_ticks = self.chart.song.tempo_calc.secs_to_ticks
        self.ticks_to_secs = self.chart.song.tempo_calc.ticks_to_secs
        self.width, self.height = size
        self.font = font
        self._image = None
        self.track_ticks = 0
        self.last_drawn = None
        self.show_next = show_next
        self.show_baseline = show_baseline

    @property
    def tracktime(self):
        return self.ticks_to_secs(self.track_ticks)

    @property
    def phrase_index(self):
        return self.chart.song.lyric_by_ticks.index(self.track_ticks)

    @property
    def prev_phrase_index(self):
        curr_index = self.phrase_index
        if curr_index is None:
            return None
        if curr_index == 0:
            return None
        return curr_index - 1

    @property
    def next_phrase_index(self):
        curr_index = self.phrase_index
        if curr_index is None:
            return 0
        if curr_index + 1 == len(self.chart.song.lyrics):
            return None
        return curr_index + 1

    @property
    def curr_phrase(self):
        return self.chart.song.lyric_by_ticks[self.track_ticks]

    @property
    def next_phrase(self):
        next_index = self.next_phrase_index
        if next_index is None:
            return None
        return self.chart.song.lyrics[next_index]

    @property
    def prev_phrase(self):
        prev_index = self.prev_phrase_index
        if prev_index is None:
            return None
        return self.chart.song.lyrics[prev_index]

    @property
    def phrase_number(self):
        if self.phrase_index is None:
            return None
        return self.phrase_index + 1

    @property
    def active_phrase(self):
        phrase = self.curr_phrase
        if phrase is None:
            return None
        if not (self.track_ticks < phrase.tick_end):
            return None
        return phrase

    @property
    def on_text(self):
        phrase = self.active_phrase
        if phrase is None:
            return None
        return phrase.get_on_text(self.track_ticks)

    @property
    def off_text(self):
        phrase = self.active_phrase
        if phrase is None:
            return None
        return phrase.get_off_text(self.track_ticks)

    @property
    def next_text(self):
        phrase = self.next_phrase
        if phrase is None:
            return None
        return phrase.get_text()

    def draw(self):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        if self.show_baseline:
            pygame.draw.line(surf, "red", surf.get_rect().midleft, surf.get_rect().midright)

        if self.active_phrase is not None:
            render_phrase_to(self.active_phrase, surf, self.track_ticks, self.font)

        if self.show_next and self.next_phrase is not None:
            render_phrase_to(self.next_phrase, surf, self.track_ticks, self.font, offset=(0, 40))

        return surf

    def update(self, tracktime):
        self.track_ticks = self.secs_to_ticks(tracktime)

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


def render_phrase_to(phrase, surf, track_ticks, fontname, offset=(0, 0)):
    full_text = phrase.get_text()
    on_text = phrase.get_on_text(track_ticks)
    off_text = phrase.get_off_text(track_ticks)
    fontsize = fit_text(full_text, fontname, surf.get_width(), 24)
    T.font = fontname
    T.size = fontsize
    digitext = T(on_text, color="#ffff00") + T(off_text, color="#808080")
    dest_rect = digitext.get_rect()
    dest_rect.centerx = surf.get_rect().centerx
    dest_rect.y = surf.get_rect().centery
    dest_rect.move_ip(offset)
    digitext.render_to(surf, dest_rect)
