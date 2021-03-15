import importlib.resources as pkg_resources

import pygame

from charm.lib.constants import frets, instruments


class Note:
    def __init__(self, instrument: str, fret: int, length: int = None,
                 *, flag: str = None, star_power: bool = None):
        self.instrument = instrument
        self.fret = fret
        self.length = 0 if length is None else length
        self.flag = "normal" if flag is None else flag
        self.star_power = False if star_power is None else star_power

    @property
    def image(self):
        imagename = ""
        # GH 5-lane
        if self.instrument == instruments.GUITAR:
            fretmap = {frets.OPEN: "open", frets.GREEN: "green", frets.RED: "red", frets.YELLOW: "yellow", frets.BLUE: "blue", frets.ORANGE: "orange"}
            if self.fret == frets.OPEN and self.star_power is True:
                imagename = "open_sp"
            elif self.star_power is True:
                imagename = "sp"
            else:
                imagename = fretmap[self.fret]
            flag = self.flag if self.flag != "normal" else "note"
            imagename = f"{flag}_{imagename}"
            imagename += ".png"

            from charm.data.images import gh

            with pkg_resources.path(gh, imagename) as p:
                img = pygame.image.load(p)
            img.convert_alpha()
            return img
