# from charm.objects.songinfo import SongInfo
import pygame
from pygame.constants import K_SPACE

from charm.classes import examplesong
from charm.lib import nygame
# from charm.lib.constants import difficulties, frets, instruments
from charm.lib.display import display
# from charm.objects.highway import Highway
# from charm.objects.note import Note
# from charm.test import chparse_test
from charm.test.lyric_animation_test import LyricAnimator

song = examplesong.example_song
gamemode = examplesong.example_gamemode


class Game():
    def __init__(self):
        self.running = True
        self.size = (800, 600)
        self.clock = nygame.time.Clock()
        self.paused = False

        self.screen = display.add_layer(pygame.Surface(self.size))

    def run(self):
        pygame.init()

        display.set_mode(self.size)

        pygame.mixer.music.load("vocals.ogg")
        pygame.mixer.music.set_volume(0.0)
        pygame.mixer.music.play(0)
        la = LyricAnimator(self.clock)

        while self.running:
            # Clear the screen
            self.screen.fill((0, 0, 0))

            # Window close button
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == K_SPACE:
                        if pygame.mixer.music.get_busy() == 1:
                            self.pause()
                        else:
                            self.unpause()
                elif event.type == pygame.QUIT:
                    self.running = False

            # note = Note(instruments.GUITAR, frets.ORANGE)
            # self.screen.blit(note.image, (0, 0))

            # highway = Highway(1000, gamemode, song, instruments.GUITAR, difficulties.EXPERT)
            # self.screen.blit(highway.image, (0, (0 - highway.image.get_height() + self.screen.get_height())))

            # songinfo = SongInfo(gamemode, song, instruments.GUITAR, difficulties.EXPERT)
            # self.screen.blit(songinfo.image, (self.screen.get_width() - songinfo.image.get_width() - 5, 0))

            dest = la.image.get_rect()
            dest.center = self.screen.get_rect().center

            self.screen.blit(la.image, dest)

            if self.paused:
                pause_font = pygame.font.SysFont("Lato Medium", 24)
                pause_screen = pause_font.render("|| PAUSED", True, (0, 255, 255))
                self.screen.blit(pause_screen,
                                 (self.screen.get_width() - pause_screen.get_width() - 5,
                                  self.screen.get_height() - pause_screen.get_height() - 5)
                                 )

            # Final draw stage
            display.flip()
            # Timing loop
            self.clock.tick_busy_loop(60)

    def pause(self):
        self.paused = True
        pygame.mixer.music.pause()

    def unpause(self):
        self.paused = False
        pygame.mixer.music.unpause()


def main():
    g = Game()
    g.run()
    # chparse_test.test()


# This is needed, or else calling `python -m <name>` will mean that main() is called twice.
if __name__ == "__main__":
    main()
