from operator import itemgetter

from charm.lib.utils import nice_time
from charm.lib import nygame
from charm.test.lyrics.stillalive import lyrics

import pygame


def clean_lyric(word: str):
    if word.endswith("-"):
        word = word.removesuffix("-")
    else:
        word = word + " "
    word = word.replace("=", "-").replace("''", "\"")
    return word


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
#     }
# ]


class LyricAnimator:
    def __init__(self, clock: nygame.time.Clock, phrases: list = lyrics, *,
                 size: tuple = (600, 400), font = "Lato Medium"):
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
        ticks = nygame.time.get_ticks_sec()
        if self.start is None:
            self.start = ticks
        return ticks - self.start

    def get_current_phrase(self):
        now = self.current_time
        try:
            phrase = next(p for p in self.phrases if p["time"] <= now < p["end_time"] + p["fade"])
        except StopIteration:
            phrase = None
        return phrase

    def draw_phrase_surf(self):
        current_phrase = self.get_current_phrase()

        if current_phrase is None:
            return None

        phrase_offset = self.current_time - current_phrase["time"]
        words = current_phrase["words"]
        off_text = "".join(w["clean"] for w in words).rstrip()
        on_text = "".join(w["clean"] for w in words if w["time"] <= phrase_offset).rstrip()

        font = fit_text(off_text, self.font, self.width)

        text_surf = pygame.Surface(font.size(off_text), pygame.SRCALPHA)

        off_surf = font.render(off_text, True, (128, 128, 128))
        on_surf = font.render(on_text, True, (255, 255, 0))

        text_surf.blit(off_surf, (0, 0))
        text_surf.blit(on_surf, (0, 0))

        if current_phrase["fade"]:
            text_surf.set_alpha(
                (1 - (max(0, self.current_time - current_phrase["end_time"]) / current_phrase["fade"])) * 255
            )
        return text_surf

    def draw_time_surf(self):
        time_font = pygame.font.SysFont(self.font, 24)
        return time_font.render(f"{nice_time(self.current_time, True)} | {self.clock.get_fps():.1f}FPS", True, (0, 255, 0))

    @property
    def image(self) -> pygame.Surface:
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surf.fill((0, 0, 0))

        surf.blit(self.draw_time_surf(), (0, 0))

        text_surf = self.draw_phrase_surf()

        if text_surf:
            surf.blit(text_surf, (
                (surf.get_width() - text_surf.get_width()) / 2,
                (surf.get_height() - text_surf.get_height()) / 2
            ))

        return surf


fonts = {}


def get_font(name, size):
    if (name, size) not in fonts:
        fonts[(name, size)] = pygame.font.SysFont(name, size)
    return fonts[(name, size)]


def precache_fonts(name):
    for size in range(48, 4, -2):
        get_font(name, size)


def fit_text(text, fontname, width):
    for size in range(48, 4, -2):
        font = get_font(fontname, size)
        if font.size(text)[0] <= (width * 0.75):
            return font
    return None


def prep_phrases(phrases):
    for phrase in phrases:
        for word in phrase["words"]:
            word["clean"] = clean_lyric(word["word"])
    phrases[-1]["fade"] = 1
    for p, np in zip(phrases[:-1], phrases[1:]):
        p["fade"] = min(np["time"] - p["end_time"], 1)
