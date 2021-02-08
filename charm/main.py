import pygame

from charm.classes import examplesong
from charm.lib import nygame
from charm.lib.constants import frets, instruments
from charm.lib.display import display
from charm.objects.highway import Highway
from charm.objects.note import Note

song = examplesong.example_song


class Game():
    def __init__(self):
        self.running = True
        self.size = (800, 600)
        self.clock = nygame.time.Clock()

        self.screen = display.add_layer(pygame.Surface(self.size))

    def run(self):
        pygame.init()

        display.set_mode(self.size)

        while self.running:
            # Window close button
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            note = Note(instruments.GUITAR, frets.BLUE, flag = "tap")
            # self.screen.blit(note.image, (0, 0))

            highway = Highway(1000, song.resolution, song.tracks[0])
            self.screen.blit(highway.image, (0, (0 - highway.image.get_height() + self.screen.get_height())))

            # Final draw stage
            display.flip()
            # Timing loop
            self.clock.tick_busy_loop(60)


def main():
    g = Game()
    g.run()


# This is needed, or else calling `python -m <name>` will mean that main() is called twice.
if __name__ == "__main__":
    main()
