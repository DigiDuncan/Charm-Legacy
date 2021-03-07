from operator import itemgetter

from charm.lib.utils import nice_time
from charm.test.lyrics.stillalive import lyrics

import pygame
import pygame.freetype
import pygame.draw

import nygame
from nygame import DigiText as T


# lyrics = [
#     {
#         "time": 3,
#         "end_time": 4.5,
#         "words": [
#             {"time": 0, "word": "Wow,"},
#             {"time": 0.5, "word": "this"},
#             {"time": 0.75, "word": "is"},
#             {"time": 1, "word": "cool!"},
#         ]
#     },
#     {
#         "time": 5.5,
#         "end_time": 8,
#         "words": [
#             {"time": 0, "word": "I"},
#             {"time": 0.5, "word": "real-"},
#             {"time": 0.75, "word": "ly"},
#             {"time": 1, "word": "like"},
#             {"time": 1.25, "word": "it!"}
#         ]
#     },
#     {
#         "time": 9,
#         "end_time": 10.5,
#         "words": [
#             {"time": 0, "word": "This"},
#             {"time": 0.1, "word": "is"},
#             {"time": 0.2, "word": "way"},
#             {"time": 0.3, "word": "too"},
#             {"time": 0.4, "word": "long,"},
#             {"time": 0.5, "word": "thus"},
#             {"time": 0.6, "word": "it"},
#             {"time": 0.7, "word": "must"},
#             {"time": 0.8, "word": "be"},
#             {"time": 0.9, "word": "shrunk"},
#             {"time": 1.0, "word": "in"},
#             {"time": 1.1, "word": "size!"},
#         ]
#     },
#     {
#         "time": 11.5,
#         "end_time": 12.5,
#         "words": [
#             {"time": 0, "word": "fast"},
#             {"time": 0.5, "word": "fade"}
#         ]
#     },
#     {
#         "time": 13,
#         "end_time": 14,
#         "words": [
#             {"time": 0, "word": "<i>I-"},
#             {"time": 0.25, "word": "tal-"},
#             {"time": 0.5, "word": "ics</i>"},
#         ]
#     },
# ]


class LyricAnimator:
    def __init__(self, clock: nygame.time.Clock, phrases: list = lyrics, *,
                 size: tuple = (600, 500), font = "Lato Medium"):
        self.clock = clock
        self.phrases = sorted(phrases, key=itemgetter("time"))
        self.width = size[0]
        self.height = size[1]
        self.font = font
        self.start = None

        prep_phrases(self.phrases)
        precache_fonts(font)

    @property
    def current_time(self):
        return pygame.mixer.music.get_pos() / 1000

    def get_current_phrase(self):
        now = self.current_time
        i = ((n, p) for n, p in enumerate(self.phrases) if p["time"] <= now < p["end_time"] + p["fade"])
        try:
            n, phrase = next(i)
        except StopIteration:
            return None, None
        try:
            next_phrase = self.phrases[n + 1] if self.phrases[n + 1]["time"] <= phrase["end_time"] + 3 else None
        except IndexError:
            return phrase, None
        return phrase, next_phrase

    def draw_phrase_to(self, surf, dest):
        surf.fill("#000000")
        current_phrase = self.get_current_phrase()

        if current_phrase[0] is None:
            return None

        phrase_offset = self.current_time - current_phrase[0]["time"]
        words = current_phrase[0]["words"]
        full_text = "".join(w["clean"] for w in words)
        on_text = "".join(w["clean"] for w in words if w["time"] <= phrase_offset)
        off_text = "".join(w["clean"] for w in words if w["time"] > phrase_offset)

        T.font = self.font
        if current_phrase[1] is not None:
            next_words = current_phrase[1]["words"]
            next_text = "".join(w["clean"] for w in next_words)
            next_fontsize = fit_text(next_text, self.font, self.width * 0.75, 24)
            next_digitext = T(next_text, color="#505050", size=next_fontsize)

        fontsize = fit_text(full_text, self.font, self.width)
        digitext = T(on_text, color="#ffff00", size = fontsize) + T(off_text, color="#808080", size = fontsize)
        pygame.draw.line(surf, "red", surf.get_rect().midleft, surf.get_rect().midright)
        # digitext.render_to(surf, surf.get_rect().center)
        rect = digitext.get_rect()
        dest = ((surf.get_width() / 2) - (rect.w / 2), (surf.get_height() / 2))  # Causes wiggle
        digitext.render_to(surf, dest)
        # if current_phrase["fade"]:
        #    self.text_surf.set_alpha(
        #        (1 - (max(0, self.current_time - current_phrase["end_time"]) / current_phrase["fade"])) * 255
        #    )
        if current_phrase[1] is not None:
            next_rect = next_digitext.get_rect()
            next_dest = ((surf.get_width() / 2) - (next_rect.w / 2), (surf.get_height() / 2) + 40)
            next_digitext.render_to(surf, next_dest)

    def draw_time_surf(self):
        time_font = pygame.font.SysFont(self.font, 24)
        return time_font.render(f"{nice_time(self.current_time, True)} | {self.clock.get_fps():.1f}FPS", True, (0, 255, 0))

    @property
    def image(self) -> pygame.Surface:
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surf.fill((0, 0, 0))

        self.draw_phrase_to(surf, (0, 0))

        surf.blit(self.draw_time_surf(), (0, 0))

        return surf


fonts = {}
largest_font = 30


def clean_lyric(word: str):
    if word.endswith("-"):
        word = word.removesuffix("-")
    else:
        word = word + " "
    word = word.replace("=", "-").replace("''", "\"").replace("+", "").replace("#", "").replace("^", "")
    return word


def get_font(name, size):
    if (name, size) not in fonts:
        fonts[(name, size)] = pygame.freetype.SysFont(name, size)
    return fonts[(name, size)]


def precache_fonts(name):
    for size in range(largest_font, 4, -2):
        get_font(name, size)


def fit_text(text, fontname, width, maxsize = None):
    return 30
    for size in range(maxsize or largest_font, 4, -2):
        font = get_font(fontname, size)
        if font.get_rect(text).w <= (width * 0.95):
            return size
    return None


def prep_phrases(phrases):
    # Clean lyrics
    for phrase in phrases:
        for word in phrase["words"]:
            word["clean"] = clean_lyric(word["word"])
        phrase["words"][-1]["clean"] = phrase["words"][-1]["clean"].rstrip()

    # Calculate fades
    phrases[-1]["fade"] = 1
    for p, np in zip(phrases[:-1], phrases[1:]):
        p["fade"] = min(np["time"] - p["end_time"], 1)
