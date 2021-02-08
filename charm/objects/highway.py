import importlib.resources as pkg_resources
import math

import pygame

from charm.classes.songdata import Track
from charm.lib.constants import frets
from charm.objects.note import Note as DrawNote


class Highway:
    def __init__(self, pixels_per_second, resolution, track):
        self.pixels_per_second = pixels_per_second
        self.resolution = resolution
        self.track: Track = track
        self.note_size = (64, 64)

        self.current_time = 0

    @property
    def notes(self):
        noteslist = []
        for chord in self.track.chords:
            for note in chord.notes:
                noteslist.append(note)
        return noteslist

    @property
    def image(self):
        # Draw a blank highway.
        # Get highway length
        lasttick = self.track.last_chord.position + self.track.last_chord.longest_note_length
        height = 1000  # Need to really calculate chart length.
        # TODO: Support non-5-lane highways.
        lanes = 5
        width = math.ceil(self.note_size[0] / 4) * (lanes + 1) + self.note_size[0] * lanes
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        surf.fill((128, 128, 128))

        w = self.note_size[0] / 4 * 3
        for i in range(lanes):
            pygame.draw.line(surf, "WHITE", (w, 0), (w, height), 3)
            from charm.data.images import gh

            fretmap = {frets.OPEN: "open", frets.GREEN: "green", frets.RED: "red", frets.YELLOW: "yellow", frets.BLUE: "blue", frets.ORANGE: "orange"}
            with pkg_resources.path(gh, f"strikeline_{fretmap[i+1]}.png") as p:
                img = pygame.image.load(p)
            img.convert_alpha()
            surf.blit(img, (w - self.note_size[1] / 2, height - self.note_size[1] * 1.25))
            w += self.note_size[0] + math.ceil(self.note_size[0] / 4)

        bpm_events = self.track.bpm_events
        time_sig_events = self.track.time_sig_events

        return surf
