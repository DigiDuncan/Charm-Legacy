import pygame

from charm.classes.gamedefinition import GameDefinition
from charm.classes.songdata import Song


class SongInfo:
    def __init__(self, game_definition: GameDefinition, song: Song, instrument: str, difficulty: str):
        self.game_definition = game_definition
        self.song = song
        self.track = self.song.get_track(instrument, difficulty)

    @property
    def image(self):
        text = (f"Name: {self.song.name}\n"
                f"Artist: {self.song.artist}\n"
                f"Album: {self.song.album}\n"
                f"Year: {self.song.year}\n"
                f"Charter: {self.song.charter}\n"
                f"Difficulty Rating: {'*' * self.song.difficulty}\n"
                f"Year: {self.song.year}\n"
                "\n"
                f"Instrument: {self.track.instrument}\n"
                f"Difficulty: {self.game_definition.diff_names[self.track.difficulty]}\n")
        surf = pygame.Surface((300, 600), pygame.SRCALPHA)
        current_height = 0
        for line in text.splitlines():
            font = pygame.font.Font(pygame.font.get_default_font(), 16)
            text_surf = font.render(line, True, "WHITE")
            current_height += text_surf.get_height() + 1
            surf.blit(text_surf, (0, current_height))
        return surf
