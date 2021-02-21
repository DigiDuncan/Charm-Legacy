from operator import itemgetter

from charm.lib.utils import nice_time
from charm.lib import nygame, digifont
from charm.test.lyrics.run_around import lyrics

import pygame
import pygame.freetype
import pygame.draw


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
        return pygame.mixer.music.get_pos() / 1000 + 5

    def get_current_phrase(self):
        now = self.current_time
        try:
            phrase = next(p for p in self.phrases if p["time"] <= now < p["end_time"] + p["fade"])
        except StopIteration:
            phrase = None
        return phrase

    def draw_phrase_to(self, surf, dest):
        surf.fill("#000000")
        current_phrase = self.get_current_phrase()

        if current_phrase is None:
            return None

        phrase_offset = self.current_time - current_phrase["time"]
        words = current_phrase["words"]
        full_text = "".join(w["clean"] for w in words)
        on_text = "".join(w["clean"] for w in words if w["time"] <= phrase_offset)
        off_text = "".join(w["clean"] for w in words if w["time"] > phrase_offset)

        font = fit_text(full_text, self.font, self.width)
        digitext = digifont.Text(font=font)
        digitext.add_span(on_text, color="#ffff00")
        digitext.add_span(off_text, color="#808080")
        pygame.draw.line(surf, "red", surf.get_rect().midleft, surf.get_rect().midright)
        # digitext.render_to(surf, surf.get_rect().center)
        rect = digitext.get_rect()
        dest = ((surf.get_width() / 2) - (rect.w / 2), (surf.get_height() / 2))
        digitext.render_to(surf, dest)
        # if current_phrase["fade"]:
        #    self.text_surf.set_alpha(
        #        (1 - (max(0, self.current_time - current_phrase["end_time"]) / current_phrase["fade"])) * 255
        #    )

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


def get_font(name, size):
    if (name, size) not in fonts:
        fonts[(name, size)] = pygame.freetype.SysFont(name, size)
    return fonts[(name, size)]


def precache_fonts(name):
    for size in range(48, 4, -2):
        get_font(name, size)


def fit_text(text, fontname, width):
    for size in range(36, 4, -2):
        font = get_font(fontname, size)
        if font.get_rect(text).w <= (width * 0.9):
            return font
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
