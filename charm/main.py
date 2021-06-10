from enum import Enum
from itertools import cycle
from pathlib import Path

import nygame
import pygame
from nygame import DigiText as T
from nygame import music
from nygame.emoji import emojize
from pygame.constants import K_EQUALS, K_HOME, K_KP7, K_KP_MINUS, K_KP_PLUS, K_KP4, K_KP6, K_MINUS, K_PAUSE, K_7, K_RETURN, K_l, K_s, MOUSEWHEEL, SRCALPHA
from pygame.surface import Surface

from charm.lib import instruments
from charm.lib.args import InvalidArgException, tryint
from charm.lib.nargs import nargs
from charm.lib.pgutils import stacksurfs
from charm.lib.utils import clamp, linear_one_to_zero, nice_time
from charm.loaders import chchart
from charm.prototyping import loader_test
from charm.prototyping.hitdetection.inputrecorder import InputRecorder
from charm.prototyping.hitdetection.scorecalculator import ScoreCalculator
from charm.prototyping.notedisplay.hyperloop import HyperloopDisplay, init as hyperloop_init
from charm.prototyping.lyricanimator.lyricanimator import LyricAnimator


def draw_pause():
    T.size = 42
    T.color = (0, 255, 255)
    pause_text = T("⏸", font="Segoe UI Emoji") + T(" PAUSED", font="Lato Medium")
    return pause_text.render()


def draw_loading():
    T.size = 72
    T.color = (0, 255, 255)
    pause_text = T("🕒", font="Segoe UI Emoji") + T(" LOADING", font="Lato Medium")
    rect = pause_text.get_rect()
    surf = Surface((rect.width, rect.height))
    surf.fill("black")
    pause_text.render_to(surf, rect)
    return surf


class SongDataDisplay:
    def __init__(self, game: "Game"):  # Maybe *don't* pass in the Game?
        self.game = game

        self.image = Surface(self.game.surface.get_size(), flags = SRCALPHA)

    def render_clock(self):
        timestr = nice_time(music.elapsed, True)
        text = T(f"{timestr} [{self.game.song.tempo_calc.secs_to_ticks(music.elapsed)}]", font="Lato Medium", size=24, color="green")
        return text.render()

    def render_volume(self):
        text = T(f"VOL {'|' * int(music.volume)}", font="Lato Medium", size=24, color="green")
        return text.render()

    def render_phrase(self):
        phrase_count = len(self.game.song.lyrics)
        text = T(f"Lyric Phrase: {self.game.la.phrase_number}/{phrase_count}", font="Lato Medium", size=24, color="green")
        return text.render()

    def render_bpm(self):
        tempo = self.game.song.tempo_calc.tempo_by_secs[music.elapsed]
        ts = self.game.song.timesig_by_ticks[self.game.song.tempo_calc.secs_to_ticks(music.elapsed)]
        ticks_per_quarternote = self.game.song.resolution
        ticks_per_wholenote = ticks_per_quarternote * 4
        beats_per_wholenote = ts.denominator
        ticks_per_beat = ticks_per_wholenote / beats_per_wholenote
        bpm = tempo.ticks_per_sec / ticks_per_beat * 60

        text = T(f"{bpm:.03f}BPM | {ts.numerator}/{ts.denominator}", font="Lato Medium", size=24, color="green")
        return text.render()

    def render_score(self):
        multmap = {1: "green", 2: "yellow", 3: "blue", 4: "purple"}
        text = T(f"Score: {self.game.sc.get_score(music.elapsed)}", font="Lato Medium", size=24, color="green")
        extra_text = T(f"{self.game.sc.multiplier}x", font="Lato Medium", size=24, color="cyan" if self.game.nd.sp else multmap[self.game.sc.multiplier]) + T(f" | {self.game.sc.streak} streak", font="Lato Medium", size=24, color="green")
        renderedtext = text.render()
        renderedextratext = extra_text.render()
        return stacksurfs((renderedtext, renderedextratext), 5)

    def render_notespeed(self):
        text = T(f"Note Speed: {self.game.nd.length} sec/screen", font="Lato Medium", size=24, color="green")
        return text.render()

    def update(self):
        self.image.fill((0, 0, 0, 0))
        data = []
        data.append(self.render_clock())
        if self.game.song:
            data.append(self.render_volume())
            data.append(self.render_bpm())
        if self.game.nd:
            data.append(self.render_notespeed())
        if self.game.la:
            if self.game.la.phrase_number is not None:
                data.append(self.render_phrase())
        if self.game.sc:
            data.append(self.render_score())
        datasurf = stacksurfs(data, 5)
        self.image.blit(datasurf, (0, 22))


class Game(nygame.Game):
    def __init__(self):
        super().__init__(size = (1280, 720), fps = 120, showfps = True)
        # Set up controller.
        pygame.joystick.init()

        # Set window title/icon.
        pygame.display.set_caption("Charm")
        charm_icon = pygame.image.load("./charm/data/images/charm-icon32t.png")
        charm_icon.convert_alpha()
        pygame.display.set_icon(charm_icon)

        # Cycle of charts.
        self.charts = cycle([
            Path("./charm/data/charts/run_around_the_character_code"),
            Path("./charm/data/charts/soulless5"),
            Path("./charm/data/charts/soflan"),
            Path("./charm/data/charts/hopotest")
        ])

        # Set up guitar and InputRecorder.
        self.guitar = None
        self.ir = None
        if instruments.Instrument.get_count() > 0:
            self.guitar = instruments.Wiitar.connect(0)
            print("Connection to Wiitar 0")
        else:
            self.guitar = instruments.Keyguitar.connect()
            print("Connection to Keyboard")
        self.ir = InputRecorder(self.guitar)

        # Initialize class variables.
        self.chart = None
        self.song = None
        self.sc = None
        self.la = None
        self.nd = None
        self.sd = SongDataDisplay(self)
        self.highway = "./charm/data/images/highway.png"

        # Static, generated images
        self.pause_image = draw_pause()
        self.loading_image = draw_loading()

        # Load default chart.
        self.load_chart()

        self.paused = False
        self.volume = 6
        self.loading_timer = 0
        self.loading_queued = None

        hyperloop_init()

    def queue_chart(self, songfolder: str = None, filename = "notes.chart", difficulty = "Expert"):
        self.loading_queued = {
            "songfolder": songfolder,
            "filename": filename,
            "difficulty": difficulty
        }
        self.loading_timer = 2
        # music.stop()

    def load_chart(self, songfolder: str = None, filename = "notes.chart", difficulty = "Expert"):
        if songfolder is None:
            songfolder = next(self.charts)

        songpath = Path(songfolder) / filename

        with songpath.open("r", encoding="utf-8") as f:
            self.song = chchart.load(f)

        self.chart = self.song.charts[(difficulty, 'Single')]

        # self.sc = ScoreCalculator(self.chart, self.ir)
        self.la = LyricAnimator(self.chart)   # TODO: Update to take Song object
        self.nd = HyperloopDisplay(self.chart, self.guitar, size=(400, 620), hitwindow_vis = False, bg = self.highway)
        musicstream = None

        possiblesongs = [self.song.musicstream, "song.ogg", "song.mp3", "guitar.ogg", "guitar.mp3"]
        for possiblesong in possiblesongs:
            if musicstream is not None:
                break
            if possiblesong is None:
                continue
            musicfile = songfolder / possiblesong
            if musicfile.exists():
                musicstream = musicfile

        if musicstream is None:
            raise ValueError("No valid music file found!")

        music.play(musicstream)

    def loop(self, events):
        # print(self.guitar.debug)
        instruments.Instrument.update(music.elapsed, events)

        for event in events:
            mods = pygame.key.get_mods()
            if event.type == pygame.KEYDOWN:
                if event.key == K_PAUSE:
                    music.playpause()
                elif event.key == K_KP4 and self.la.prev_phrase is not None:
                    music.elapsed = self.la.prev_phrase.start + 0.0001
                elif event.key == K_KP6 and self.la.next_phrase is not None:
                    music.elapsed = self.la.next_phrase.start + 0.0001
                elif event.key == K_HOME:
                    music.elapsed = 0
                elif event.key == K_KP_PLUS:
                    self.volume += 1
                elif event.key == K_KP_MINUS:
                    self.volume -= 1
                elif event.key in (K_7, K_KP7):
                    self.nd.tilt = not self.nd.tilt
                elif event.key == K_s:
                    self.nd.sp = not self.nd.sp
                elif event.key == K_l:
                    self.nd.lefty = not self.nd.lefty
                elif event.key == K_MINUS:
                    self.nd.length -= 0.05
                elif event.key == K_EQUALS:
                    self.nd.length += 0.05
                elif event.key == K_RETURN:
                    try:
                        self.queue_chart()
                    except chchart.UnparsedMetadataException as e:
                        print(e)
                self.nd.length = max(0.05, self.nd.length)
                self.nd.length = round(self.nd.length, 2)
            elif event.type == MOUSEWHEEL:
                if mods & pygame.KMOD_LSHIFT:
                    music.elapsed -= event.y
                else:
                    music.elapsed -= event.y / 10

        # Updates
        if not self.paused:
            if self.ir is not None:
                self.ir.update(music.elapsed)
            if self.sc is not None:
                self.score = self.sc.get_score(music.elapsed)
        self.la.update(music.elapsed)
        self.nd.update(music.elapsed)
        self.sd.update()

        # Draws
        self.render_notes()
        if self.chart.song.lyrics:
            self.render_lyrics()
        self.render_songdata()
        self.render_pause()
        self.render_section()
        self.render_title()
        self.render_loading()

        # Chart loading
        if self.loading_queued:
            if self.loading_timer > 0:
                self.loading_timer -= 1
            else:
                self.load_chart(**self.loading_queued)
                self.loading_queued = None

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

    def render_songdata(self):
        dest = self.sd.image.get_rect()
        dest.topleft = self.surface.get_rect().topleft
        self.surface.blit(self.sd.image, dest)

    def render_pause(self):
        if music.paused:
            rect = self.pause_image.get_rect()
            rect.bottomright = self.surface.get_rect().bottomright
            rect.move_ip((-5, -5))
            self.surface.blit(self.pause_image, rect)

    def render_loading(self):
        if self.loading_queued:
            rect = self.loading_image.get_rect()
            rect.center = self.surface.get_rect().center
            self.surface.blit(self.loading_image, rect)

    def render_section(self):
        current_tick = self.song.tempo_calc.secs_to_ticks(music.elapsed)
        current_section = ""
        if cs := self.song.section_by_ticks[current_tick]:
            current_section = cs.text

        text = T(emojize(current_section), font="Segoe UI Emoji", size=24, color="yellow")
        rect = text.get_rect()
        rect.bottomleft = self.surface.get_rect().bottomleft
        rect.move_ip(5, -5)
        text.render_to(self.surface, rect)

    def render_title(self):
        time = music.elapsed
        # https://www.desmos.com/calculator/h0tyxihzzq
        opacity = linear_one_to_zero(3, 1, time)
        titletext = T(self.song.title, font = "Lato Medium", size = 72)
        artisttext = T(self.song.artists, font = "Lato Medium", size = 48)
        rect = titletext.get_rect()
        rect.center = self.surface.get_rect().center
        rect2 = artisttext.get_rect()
        rect2.midtop = rect.midbottom
        rect2.move_ip(0, 5)
        titlesurf = titletext.render()
        titlesurf.set_alpha(255 * opacity)
        artistsurf = artisttext.render()
        artistsurf.set_alpha(255 * opacity)
        self.surface.blit(titlesurf, rect)
        self.surface.blit(artistsurf, rect2)

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
