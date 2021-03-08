from charm.lib.utils import nice_time
import pygame
import nygame
from nygame import music, DigiText as T
from pygame.constants import K_LEFT, K_RIGHT, K_SPACE

# from charm.classes.examplesong import (
#    example_song as song,
#    example_gamemode as gamemode
# )
from charm.test.lyric_animation_test import LyricAnimator


def draw_pause():
    T.size = 42
    T.color = (0, 255, 255)
    pause_text = T("⏸", font="Segoe UI Emoji") + T(" PAUSED", font="Lato Medium")
    return pause_text.render()


class Game(nygame.Game):
    def __init__(self):
        super().__init__(size = (800, 600), fps = 120, showfps = True)
        self.paused = False
        self.la = LyricAnimator()
        self.pause_image = draw_pause()

    def loop(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == K_SPACE:
                    music.playpause()
                if event.key == K_LEFT:
                    self.la.selected -= 1
                elif event.key == K_RIGHT:
                    self.la.selected += 1

        # note = Note(instruments.GUITAR, frets.ORANGE)
        # self.screen.blit(note.image, (0, 0))

        # highway = Highway(1000, gamemode, song, instruments.GUITAR, difficulties.EXPERT)
        # self.screen.blit(highway.image, (0, (0 - highway.image.get_height() + self.screen.get_height())))

        # songinfo = SongInfo(gamemode, song, instruments.GUITAR, difficulties.EXPERT)
        # self.screen.blit(songinfo.image, (self.screen.get_width() - songinfo.image.get_width() - 5, 0))

        self.render_lyrics()
        self.render_clock()
        self.render_pause()

    def render_lyrics(self):
        self.la.update(music.elapsed)
        dest = self.la.image.get_rect()
        dest.center = self.surface.get_rect().center
        self.surface.blit(self.la.image, dest)

    def render_pause(self):
        if music.paused:
            rect = self.pause_image.get_rect()
            rect.bottomright = self.surface.get_rect().bottomright
            rect.move_ip((-5, -5))
            self.surface.blit(self.pause_image, rect)

    def render_clock(self):
        text = T(nice_time(self.la.tracktime, True), font="Lato Medium", size=24, color="green")
        text.render_to(self.surface, (5, 45))

    def run(self):
        music.volume = 0.05
        music.play("vocals.ogg")
        super().run()


def main():
    g = Game()
    g.run()
    # chparse_test.test()


# This is needed, or else calling `python -m <name>` will mean that main() is called twice.
if __name__ == "__main__":
    main()
