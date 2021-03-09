from charm.lib.utils import clamp, nice_time
import pygame
import nygame
from nygame import music, DigiText as T
from pygame.constants import K_DOWN, K_LEFT, K_RIGHT, K_SPACE, K_UP

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
        self._volume = 0.05
        self.la = LyricAnimator()
        self.pause_image = draw_pause()

    def loop(self, events):
        self.la.update(music.elapsed)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == K_SPACE:
                    music.playpause()
                if event.key == K_LEFT and self.la.prev_phrase is not None:
                    music.elapsed = self.la.prev_phrase.start
                elif event.key == K_RIGHT and self.la.next_phrase is not None:
                    music.elapsed = self.la.next_phrase.start
                if event.key == K_UP:
                    self.set_volume(self.volume + 0.01)
                if event.key == K_DOWN:
                    self.set_volume(self.volume - 0.01)

        # note = Note(instruments.GUITAR, frets.ORANGE)
        # self.screen.blit(note.image, (0, 0))

        # highway = Highway(1000, gamemode, song, instruments.GUITAR, difficulties.EXPERT)
        # self.screen.blit(highway.image, (0, (0 - highway.image.get_height() + self.screen.get_height())))

        # songinfo = SongInfo(gamemode, song, instruments.GUITAR, difficulties.EXPERT)
        # self.screen.blit(songinfo.image, (self.screen.get_width() - songinfo.image.get_width() - 5, 0))

        self.render_lyrics()
        self.render_clock()
        self.render_pause()
        self.render_volume()

    def render_lyrics(self):
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

    def render_volume(self):
        text = T(f"VOL {'|' * int(self.volume * 100)}", font="Lato Medium", size=24, color="green")
        text.render_to(self.surface, (5, 70))

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = clamp(0, value, 0.3)

    def set_volume(self, value):
        self.volume = value
        music.volume = self.volume

    def run(self):
        self.set_volume(0.05)
        music.play("song.mp3")
        super().run()


def main():
    g = Game()
    g.run()
    # chparse_test.test()


# This is needed, or else calling `python -m <name>` will mean that main() is called twice.
if __name__ == "__main__":
    main()
