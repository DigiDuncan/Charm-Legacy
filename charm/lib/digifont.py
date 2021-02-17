from typing import List, Literal, Tuple, Union

import pygame
from PIL import Image

from charm.lib.attrdict import AttrDict


def image_to_surface(img: Image):
    return pygame.image.fromstring(
        img.tobytes(), img.size, img.mode).convert()


class Text:
    def __init__(self, chars: str, size: int, *,
                 color: Union[tuple, int, str] = 0x000000,
                 flags: dict = {}):
        self.chars = chars
        self.size = size
        self.color = color
        self.flags = AttrDict(flags)

    @property
    def colour(self):
        return self.color

    @property
    def bold(self):
        return bool(self.flags.bold)

    @bold.setter
    def bold(self, value: bool):
        self.flags.bold = bool(value)

    @property
    def italic(self):
        return bool(self.flags.italic)

    @italic.setter
    def bold(self, value: bool):
        self.flags.italic = bool(value)

    @property
    def underline(self):
        return bool(self.flags.underline)

    @underline.setter
    def underline(self, value: bool):
        self.flags.underline = bool(value)

    @property
    def strikethrough(self):
        return bool(self.flags.strikethrough)

    @strikethrough.setter
    def strikethrough(self, value: bool):
        self.flags.strikethrough = bool(value)

    @property
    def subscript(self):
        return bool(self.flags.subscript)

    @subscript.setter
    def subscript(self, value: bool):
        self.flags.subscript = bool(value)

    @property
    def superscript(self):
        return bool(self.flags.superscript)

    @superscript.setter
    def superscript(self, value: bool):
        self.flags.superscript = bool(value)


def render(texts = List[Text], *,
           size: Tuple[int, int] = None,  # size will just be "big enough the fix the text" by default
           justify = Literal["left", "center", "right"],
           wrap = False,
           parse_emoji_shortcodes = False):
    pass
