import pygame
import nygame
from pygame.constants import K_DOWN, K_HOME, K_LEFT, K_RIGHT, K_SPACE, K_UP
from nygame import music, DigiText as T

from charm.loaders import chchart

# from charm.lib.constants import instruments, frets
from charm.lib.utils import clamp, nice_time
from charm.prototyping.lyricanimator.lyricanimator import LyricAnimator
# from charm.objects.note import Note


def draw_pause():
    T.size = 42
    T.color = (0, 255, 255)
    pause_text = T("⏸", font="Segoe UI Emoji") + T(" PAUSED", font="Lato Medium")
    return pause_text.render()


class Game(nygame.Game):
    def __init__(self):
        super().__init__(size = (800, 600), fps = 120, showfps = True)
        self.paused = False
        self.volume = 6
        self.la = LyricAnimator("./charm/data/charts/run_around_the_character_code/run_around_the_character_code.chart")
        music.load("./charm/data/charts/run_around_the_character_code/run_around_the_character_code.mp3")
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
                elif event.key == K_HOME:
                    music.elapsed = 0
                if event.key == K_UP:
                    self.volume += 1
                if event.key == K_DOWN:
                    self.volume -= 1

        # note = Note(instruments.GUITAR, frets.ORANGE)
        # self.surface.blit(note.image, (0, 0))

        self.render_lyrics()
        self.render_clock()
        self.render_pause()
        self.render_volume()
        self.render_phrase()

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
        text = T(f"VOL {'|' * int(music.volume)}", font="Lato Medium", size=24, color="green")
        text.render_to(self.surface, (5, 95))

    def render_phrase(self):
        text = T(f"Phrase: {'None' if self.la.active_phrase_index is None else self.la.active_phrase_index + 1}", font="Lato Medium", size=24, color="green")
        text.render_to(self.surface, (5, 70))

    @property
    def volume(self):
        return music.volume

    @volume.setter
    def volume(self, value):
        music.volume = clamp(0, value, 38)

    def run(self):
        music.play()
        super().run()


def main():
    #g = Game()
    #g.run()
    # chparse_test.test()
    with open(r"C:\Users\nfear\Desktop\Coding\Charm\charm\data\charts\run_around_the_character_code\run_around_the_character_code.chart") as f:
        song = chchart.load(f)
        print(song)


# This is needed, or else calling `python -m <name>` will mean that main() is called twice.
if __name__ == "__main__":
    main()
