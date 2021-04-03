from pathlib import Path
from typing import List, Literal, Optional

import pygame.image
import pygame.transform
from pygame.surface import Surface
from pygame.rect import Rect

FretName = Literal["green", "red", "yellow", "blue", "orange", "open"]
FretNum = Literal[0, 1, 2, 3, 4, 5, 7]
Mode = Literal["note", "hopo", "tap", "strike", "sustaintop", "sustainbody"]

SPRITEMAP_Y = [
    # mode          spnote  y   h
    ("note",        False,  0,  1),
    ("hopo",        False,  1,  1),
    ("tap",         False,  2,  1),
    ("note",        True,   3,  1),
    ("hopo",        True,   4,  1),
    ("tap",         True,   5,  1),
    ("strike",      False,  6,  1),
    ("sustaintop",  False,  7,  1),
    ("sustainbody", False,  8,  1)
]

SPRITEMAP_X = [
    # fretname  fretnum spact   x   w
    ("green",   0,      False,  0,  1),
    ("red",     1,      False,  1,  1),
    ("yellow",  2,      False,  2,  1),
    ("blue",    3,      False,  3,  1),
    ("orange",  4,      False,  4,  1),
    ("open",    7,      False,  5,  5),
    ("green",   0,      True,   10, 1),
    ("red",     1,      True,   11, 1),
    ("yellow",  2,      True,   12, 1),
    ("blue",    3,      True,   13, 1),
    ("orange",  4,      True,   14, 1),
    ("open",    7,      True,   15, 5),
]


class Sprite():
    def __init__(self, fretname: FretName, fretnum: FretNum, mode: Mode, spnote: bool, spact: bool, img: Surface):
        self.fretname: FretName = fretname
        self.fretnum: FretNum = fretnum
        self.mode: Mode = mode
        self.spnote: bool = spnote
        self.spact: bool = spact
        self.img: Surface = img


class SpriteSheet:
    SPRITE_SIZE = 64

    def __init__(self, sprites: List[Sprite]):
        self.sprites = sprites
        self.fretname_index = {(spr.fretname, spr.mode, spr.spnote, spr.spact): spr.img for spr in sprites}
        self.fretnum_index = {(spr.fretnum, spr.mode, spr.spnote, spr.spact): spr.img for spr in sprites}

    def get(self, *, fretname: Optional[FretName] = None, fretnum: Optional[FretNum] = None, mode: Mode = "note", spnote: bool = False, spact: bool = False) -> Surface:
        if fretname is not None and fretnum is not None:
            raise ValueError("fretname or fretnum arguments are mutually exclusive.")

        if fretname is not None:
            return self.fretname_index[(fretname, mode, spnote, spact)]
        elif fretnum is not None:
            return self.fretnum_index[(fretnum, mode, spnote, spact)]

        raise ValueError("Either fretname or fretnum argument must be provided.")

    @classmethod
    def load(cls, p: Path):
        gh_sheet = pygame.image.load(p)
        gh_sheet.convert_alpha()
        if gh_sheet.get_size() != (1280, 640):
            gh_sheet = pygame.transform.scale(gh_sheet, (1280, 640))  # TODO: This is hacky and needs to be flexible.

        sprites: List[Sprite] = []
        SPRITE_SIZE = 64
        for (mode, spnote, y, h) in SPRITEMAP_Y:
            for (fretname, fretnum, spact, x, w) in SPRITEMAP_X:
                subrect = Rect(x, y, w, h)
                subrect.x *= SPRITE_SIZE
                subrect.y *= SPRITE_SIZE
                subrect.w *= SPRITE_SIZE
                subrect.h *= SPRITE_SIZE
                img = gh_sheet.subsurface(subrect)
                sprites.append(Sprite(fretname, fretnum, mode, spnote, spact, img))

        return cls(sprites)
