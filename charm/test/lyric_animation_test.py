from charm.lib.utils import nice_time
from charm.lib import nygame
from charm.test.lyrics.stillalive import lyrics

import pygame


def clean_lyric(word: str, last_word = False):
    if word.endswith("-"):
        word = word[:-1]
    elif last_word is False:
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
        self.phrases = phrases
        self.width = size[0]
        self.height = size[1]
        self.font = font
        self.start = None

    @property
    def current_time(self):
        ticks = nygame.time.get_ticks_sec()
        if self.start is None:
            self.start = ticks
        return ticks - self.start

    @property
    def image(self) -> pygame.Surface:
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surf.fill((0, 0, 0))

        current_phrase = None
        for p in self.phrases:
            if p["time"] <= self.current_time <= (p["end_time"] + 1):
                current_phrase = p

        current_line = ""
        if current_phrase:
            for w in current_phrase["words"]:
                current_line += clean_lyric(w["word"])
        current_line = current_line.rstrip()

        current_font = None
        current_size = 48
        while current_font is None and current_size > 4:
            font = pygame.font.SysFont(self.font, current_size)
            if font.size(current_line)[0] <= (self.width * 0.75):
                current_font = font
            current_size -= 2

        text_surf = pygame.Surface(current_font.size(current_line), pygame.SRCALPHA)

        if current_phrase:
            on = ""
            off = ""
            for w in current_phrase["words"]:
                if w["time"] <= (self.current_time - current_phrase["time"]):
                    on += clean_lyric(w["word"])
                else:
                    off += clean_lyric(w["word"])
            off = off.rstrip()

            on_surf = current_font.render(on, True, (255, 255, 0))
            off_surf = current_font.render(off, True, (128, 128, 128))

            text_surf.blit(on_surf, (0, 0))
            text_surf.blit(off_surf, (on_surf.get_width(), 0))

            text_surf.set_alpha(
                255 - (max(0, self.current_time - current_phrase["end_time"]) * 255)
            )

        time_font = pygame.font.SysFont(self.font, 24)
        time_surf = time_font.render(f"{nice_time(self.current_time, True)} | {self.clock.get_fps():.1f}FPS", True, (0, 255, 0))

        surf.blit(time_surf, (0, 0))
        surf.blit(text_surf, (
            (surf.get_width() - text_surf.get_width()) / 2,
            (surf.get_height() - text_surf.get_height()) / 2
        ))

        return surf
