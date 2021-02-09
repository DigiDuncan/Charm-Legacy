import importlib.resources as pkg_resources
import math
from importlib import import_module

import pygame

from charm.classes.gamedefinition import GameDefinition
from charm.classes.songdata import Song
from charm.objects.note import Note as GameNote


class Highway:
    def __init__(self, pixels_per_second, game_definition: GameDefinition, song: Song, track_id: int):
        self.pixels_per_second = pixels_per_second
        self.song = song
        self.resolution = song.resolution
        self.track = song.tracks[track_id]

        self.game_definition = game_definition
        self.note_size = self.game_definition.sprite_size
        self.lane_count = self.game_definition.lane_count
        self.fret_map = self.game_definition.note_names

        self.current_time = 0

    @property
    def notes(self):
        noteslist = []
        for chord in self.track.chords:
            for note in chord.notes:
                noteslist.append(note)
        return noteslist

    @property
    def lasttick(self) -> int:
        return self.track.last_chord.position + self.track.last_chord.longest_note_length

    @property
    def width(self) -> int:
        return math.ceil(self.note_size[0] / 4) * (self.lane_count + 1) + self.note_size[0] * self.lane_count

    @property
    def height(self) -> int:
        return 1000  # Need to really calculate chart length.

    @property
    def image_folder(self):
        return import_module("charm.data.images." + self.game_definition.image_folder)

    @property
    def strikeline(self) -> pygame.Surface:
        sl_width = (self.note_size[0] * self.lane_count) + ((self.note_size[0] / 4) * (self.lane_count - 1))
        surf = pygame.Surface((sl_width, self.note_size[1]), pygame.SRCALPHA)
        w = 0
        for i in range(self.lane_count):
            with pkg_resources.path(self.image_folder, f"strikeline_{self.fret_map[i+1]}.png") as p:
                img = pygame.image.load(p)
            img.convert_alpha()
            surf.blit(img, (w, 0))
            w += self.note_size[0] + math.ceil(self.note_size[0] / 4)

        return surf

    @property
    def image(self) -> pygame.Surface:
        # Draw a blank highway.
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        surf.fill((128, 128, 128))

        # Put lane lines on.
        w = self.note_size[0] / 4 * 3
        for i in range(self.lane_count):
            pygame.draw.line(surf, "WHITE", (w, 0), (w, self.height), 3)
            w += self.note_size[0] + math.ceil(self.note_size[0] / 4)

        # Tack the strikeline on the bottom.
        surf.blit(self.strikeline, (self.note_size[0] / 4, self.height - (self.note_size[1] * 1.25)))

        bpm_events = self.track.bpm_events
        time_sig_events = self.track.time_sig_events

        return surf
