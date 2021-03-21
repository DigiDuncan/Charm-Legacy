from charm.prototyping.notedisplay.hyperloop import HyperloopDisplay, init as hyperloop_init
from charm.lib.nargs import nargs
from enum import Enum
from pathlib import Path

import nygame
import pygame
from nygame import DigiText as T
from nygame import music
from pygame.constants import K_DOWN, K_HOME, K_LEFT, K_RIGHT, K_SPACE, K_UP, MOUSEWHEEL

from charm.lib.args import InvalidArgException, tryint
from charm.lib.utils import clamp, nice_time
from charm.loaders import chchart
from charm.prototyping import loader_test
from charm.prototyping.lyricanimator.lyricanimator import LyricAnimator

# from charm.lib.constants import instruments, frets
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
        songpath = Path("./charm/data/charts/run_around_the_character_code/run_around_the_character_code.chart")
        with songpath.open("r", encoding="utf-8") as f:
            song = chchart.load(f)
        self.la = LyricAnimator(songpath)   # TODO: Update to take Song object
        hyperloop_init()
        self.nd = HyperloopDisplay(song.charts[('Expert', 'Single')], size=(400, 500))
        music.load(songpath.parent / song.musicstream)
        self.pause_image = draw_pause()

    def loop(self, events):
        self.la.update(music.elapsed)
        self.nd.update(music.elapsed)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == K_SPACE:
                    music.playpause()
                elif event.key == K_LEFT and self.la.prev_phrase is not None:
                    music.elapsed = self.la.prev_phrase.start
                elif event.key == K_RIGHT and self.la.next_phrase is not None:
                    music.elapsed = self.la.next_phrase.start
                elif event.key == K_HOME:
                    music.elapsed = 0
                elif event.key == K_UP:
                    self.volume += 1
                elif event.key == K_DOWN:
                    self.volume -= 1
            elif event.type == MOUSEWHEEL:
                music.elapsed -= event.y / 20

        # note = Note(instruments.GUITAR, frets.ORANGE)
        # self.surface.blit(note.image, (0, 0))

        self.render_lyrics()
        self.render_notes()
        self.render_clock()
        self.render_pause()
        self.render_volume()
        self.render_phrase()

    def render_lyrics(self):
        dest = self.la.image.get_rect()
        dest.centerx = self.surface.get_rect().centerx
        dest.top = self.surface.get_rect().top
        self.surface.blit(self.la.image, dest)

    def render_notes(self):
        dest = self.nd.image.get_rect()
        dest.centerx = self.surface.get_rect().centerx
        dest.bottom = self.surface.get_rect().bottom
        self.surface.blit(self.nd.image, dest)

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
        phrase_index = 'None' if self.la.active_phrase_index is None else self.la.active_phrase_index + 1
        phrase_count = len(self.la.phrases)
        text = T(f"Phrase: {phrase_index}/{phrase_count}", font="Lato Medium", size=24, color="green")
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


def list_charts():
    """
    List all available charts
    """
    charts_root = Path(R".\charm\data\charts")
    charts = list(charts_root.rglob("*.chart"))
    return charts


def strch(chart):
    r"""
    Convert a chart Path object to a string path relative to .\charm\data\charts
    """
    charts_root = Path(R".\charm\data\charts")
    return str(chart.relative_to(charts_root))


class Mode(Enum):
    LyricAnimator = Default = "lyrics"
    BulkTest = "bulk"
    SingleTest = "single"
    ListCharts = "charts"


def play_chart(n=1):
    charts = list_charts()
    i = tryint(n)
    if i is None or not (1 <= i <= len(charts)):
        raise InvalidArgException(
            f"Invalid chart selection: {n!r}\n"
            f"Please enter a number between 1-{len(charts)} or use 'charts' to list all available charts."
        )
    chart = charts[i - 1]
    print(f"Testing chart {i}: {strch(chart)}")
    with open(chart, encoding="utf-8 sig") as f:
        song = chchart.load(f)
        print(song)


def print_charts():
    charts = list_charts()
    w = len(str(len(charts)))
    print("Available Charts:")
    for i, chart in enumerate(charts, start=1):
        print(f"{i:>{w}}: {strch(chart)}")


@nargs
def run(mode=Mode.Default.value, *args, **kwargs):
    try:
        mode = Mode(mode)
    except ValueError:
        mode = None
    if mode == Mode.LyricAnimator:
        Game().run()
    elif mode == Mode.BulkTest:
        loader_test.main(**kwargs)
    elif mode == Mode.SingleTest:
        play_chart(*args)
    elif mode == Mode.ListCharts:
        print_charts()
    else:
        valid_modes = " / ".join(m.value for m in Mode)
        print(
            f"Unrecognized mode: {mode!r}\n"
            f"Please use one of the following modes: {valid_modes}."
        )


def main():
    try:
        run()
    except InvalidArgException as e:
        print(e)
        return


# This is needed, or else calling `python -m <name>` will mean that main() is called twice.
if __name__ == "__main__":
    main()
