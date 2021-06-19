from glob import glob
from pathlib import Path
from typing import Dict, List

import nygame
from nygame import DigiText as T
import pygame
from pygame import Surface
from pygame import K_UP, K_DOWN

from ...lib.pgutils import stacksurfs
from ...loaders import chchart


class MenuItem:
    def __init__(self, key: str, title: str, artist: str):
        self.key = key
        self.title = title
        self.artist = artist

        self.selected = False

    @property
    def color(self):
        return "red" if self.selected else "green"

    def render(self):
        titlesurf = T(self.title, font = "Lato Semibold", size = 32, color = self.color, underline = True).render()
        artistsurf = T(self.artist, font = "Lato Medium", size = 24, color = self.color).render()
        return stacksurfs((titlesurf, artistsurf))


def draw_loading():
    T.size = 72
    T.color = (0, 255, 255)
    pause_text = T("🕒", font="Segoe UI Emoji") + T(" LOADING", font="Lato Medium")
    rect = pause_text.get_rect()
    surf = Surface((rect.width, rect.height))
    surf.fill("black")
    pause_text.render_to(surf, rect)
    return surf


class Game(nygame.Game):
    def __init__(self, path):
        super().__init__(fps = 120, showfps = True)

        # Static stuff
        self.path = path
        self.loading_image = draw_loading()

        # Variable stuff
        self.loading = True
        self.selected = 0

        # Show a loading screen because...
        self.render_loading()

        # Load a bunch of stuff.
        self.load_self()

    def load_self(self):

        songpath = Path(self.path)
        songfolder = songpath.as_posix()

        charts = glob(songfolder + R"/**/notes.chart", recursive = True)
        chartfolders = [Path(p).parent for p in charts]

        self.data: List[Dict] = []
        for chart in chartfolders:
            songpath = chart / "notes.chart"
            with songpath.open("r", encoding="utf-8") as f:
                song = chchart.load(f)
            self.data.append({
                "path": chart,
                "title": song.title,
                "artist": song.artists,
                "playlist": chart.parent.stem
            })

        print(self.data)

    def render_loading(self):
        if self.loading:
            rect = self.loading_image.get_rect()
            rect.center = self.surface.get_rect().center
            self.surface.blit(self.loading_image, rect)

    def loop(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == K_DOWN:
                    self.selected += 1
                elif event.key == K_UP:
                    self.selected -= 1

        # self.selected %= len(self.menu.items)
        # self.menu.selected = self.selected

        # self.menu.update()

        # menusurf = self.menu.render()

        # self.surface.blit(menusurf, (5, 5))
