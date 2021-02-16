from charm.lib import nygame

import pygame

lyrics = [
    {
        "time": 5,
        "end_time": 6.5,
        "words": [
            {"time": 0, "word": "Wow, "},
            {"time": 0.5, "word": "this "},
            {"time": 0.75, "word": "is "},
            {"time": 1, "word": "cool!"},
        ]
    },
    {
        "time": 8,
        "end_time": 10,
        "words": [
            {"time": 0, "word": "I "},
            {"time": 0.5, "word": "real"},
            {"time": 0.75, "word": "ly "},
            {"time": 1, "word": "like "},
            {"time": 1.25, "word": "it!"}
        ]
    }
]


class LyricAnimator:
    def __init__(self, clock: nygame.time.Clock, phrases: list = lyrics, *,
                 size: tuple = (600, 400), font = "Arial"):
        self.clock = clock
        self.phrases = phrases
        self.width = size[0]
        self.height = size[1]
        self.font = font

    @property
    def current_time(self):
        return nygame.time.get_ticks_sec()

    @property
    def image(self) -> pygame.Surface:
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surf.fill((0, 0, 0))

        current_phrase = None
        for p in self.phrases:
            if p["time"] <= self.current_time <= p["end_time"]:
                current_phrase = p

        current_line = ""
        if current_phrase:
            for w in current_phrase["words"]:
                current_line += w["word"]

        current_font = None
        current_size = 24
        while current_font is None and current_size > 4:
            font = pygame.font.SysFont(self.font, current_size)
            if font.size(current_line)[0] <= (self.width * 0.75):
                current_font = font
                break
            current_size - 2

        text_surf = pygame.Surface(current_font.size(current_line), pygame.SRCALPHA)

        if current_phrase:
            on = ""
            off = ""
            for w in current_phrase["words"]:
                if w["time"] <= (self.current_time - current_phrase["time"]):
                    on += w["word"]
                else:
                    off += w["word"]

            on_surf = current_font.render(on, True, (255, 255, 0))
            off_surf = current_font.render(off, True, (128, 128, 128))

            text_surf.blit(on_surf, (0, 0))
            text_surf.blit(off_surf, (on_surf.get_width(), 0))

        time_surf = current_font.render(str(self.current_time), True, (0, 255, 0))

        surf.blit(time_surf, (0, 0))
        surf.blit(text_surf, (
            (surf.get_width() - text_surf.get_width()) / 2,
            (surf.get_height() - text_surf.get_height()) / 2
        ))

        return surf
