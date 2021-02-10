import importlib.resources as pkg_resources

import pygame

import charm.data.fonts
from charm.classes.gamemode import Gamemode
from charm.classes.songdata import Song


class SongInfo:
    def __init__(self, gamemode: Gamemode, song: Song, instrument: str, difficulty: str):
        self.gamemode = gamemode
        self.song = song
        self.chart = self.song.get_chart(instrument, difficulty)

    @property
    def image(self):
        text = (f"Name: {self.song.name}\n"
                f"Artist: {self.song.artist}\n"
                f"Album: {self.song.album}\n"
                f"Year: {self.song.year}\n"
                f"Charter: {self.song.charter}\n"
                f"Difficulty Rating: {'X' * self.song.difficulty}\n"
                "\n"
                f"Instrument: {self.chart.instrument}\n"
                f"Difficulty: {self.gamemode.diff_names[self.chart.difficulty]}\n")
        surf = pygame.Surface((300, 600), pygame.SRCALPHA)
        current_height = 0
        for line in text.splitlines():
            f = pkg_resources.open_binary(charm.data.fonts, "Exo-MediumItalic.ttf")
            font = pygame.font.Font(f, 16)
            text_surf = font.render(line, True, "WHITE")
            current_height += text_surf.get_height() + 1
            surf.blit(text_surf, (surf.get_width() - text_surf.get_width(), current_height))
        return surf
