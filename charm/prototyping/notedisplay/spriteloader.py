from pathlib import Path
from typing import Dict, Optional, Union
from pygame.rect import Rect

from pygame.surface import Surface
from pygame import image

class SpriteSheet:
    SPRITE_SIZE = 64

    FRETNUMS = {
        "green": 0,
        "red": 1,
        "yellow": 2,
        "blue": 3,
        "orange": 4,
        "open": 7,
        "greensp": 10,
        "redsp": 11,
        "yellowsp": 12,
        "bluesp": 13,
        "orangesp": 14,
        "opensp": 17
    }

    FRETMAP = {
        "green": 0,
        "red": 1,
        "yellow": 2,
        "blue": 3,
        "orange": 4,
        "greensp": 5,
        "redsp": 6,
        "yellowsp": 7,
        "bluesp": 8,
        "orangesp": 9,
        "open": (10, 5),
        "opensp": (15, 5)
    }

    FLAGMAP = {
        "note": 0,
        "hopo": 1,
        "tap": 2,
        "strike": 6
    }

    def __init__(self):
        self.fret_images: Dict[str, Dict[Union[str, int], Surface]] = {}

    def get_sprite(self, flag: str, fret: Union[str, int]) -> Surface:
        return self.fret_images[flag][fret]

    def set_sprite(self, flag: str, fretname: str, sprite: Surface):
        self.fret_images[flag][fretname] = sprite
        if fretname in self.FRETNUMS:
            fretnum = self.FRETNUMS[fretname]
            self.fret_images[flag][fretnum] = sprite

    @classmethod
    def load(cls, p: Path):
        self = cls()
        gh_sheet: Optional[Surface] = None

        gh_sheet = image.load(p)
        gh_sheet.convert_alpha()
        if gh_sheet.get_size()[1] == 1280:
            gh_sheet = pygame.transform.scale(gh_sheet, (1280, 640))  # TODO: This is hacky and needs to be flexible.
        for flag, sy in cls.FLAGMAP.items():
            self.fret_images[flag] = {}
            for fret, sxw in cls.FRETMAP.items():
                sw = 1
                if isinstance(sxw, int):
                    sx = sxw
                else:
                    sx, sw = sxw
                x = sx * cls.SPRITE_SIZE
                y = sy * cls.SPRITE_SIZE
                w = sw * cls.SPRITE_SIZE
                h = cls.SPRITE_SIZE
                img = gh_sheet.subsurface(Rect(x, y, w, h))
                self.set_sprite(flag, fret, img)
        return self
