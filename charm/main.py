import time
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
from charm.lib.dumbutils import beatbounce
from charm.lib.nargs import nargs
from charm.lib.pgutils import stacksurfs
from charm.lib.utils import clamp, linear_one_to_zero, nice_time, truncate
from charm.loaders import chchart
from charm.prototyping import loader_test
from charm.prototyping.hitdetection.inputrecorder import InputRecorder
# from charm.prototyping.hitdetection.scorecalculator import ScoreCalculator
from charm.prototyping.menu import menu2
from charm.prototyping.notedisplay.hyperloop import HyperloopDisplay, init as hyperloop_init
from charm.prototyping.notedisplay.inputdebug import InputDebug
from charm.prototyping.lyricanimator.lyricanimator import LyricAnimator
from charm.prototyping.videoplayer.videoplayer import VideoPlayer


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


def draw_logo():
    surf = pygame.image.load("./docs/images/logo.png")
    surf.convert_alpha()
    surf.set_alpha(128)
    surf = pygame.transform.scale(surf, (137, 50))
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
        text = T(f"Lyric Phrase: {self.game.lyricanimator.phrase_number}/{phrase_count}", font="Lato Medium", size=24, color="green")
        return text.render()

    def render_bpm(self, time):
        tempo = self.game.song.tempo_calc.tempo_by_secs[time]
        ts = self.game.song.timesig_by_ticks[self.game.song.tempo_calc.secs_to_ticks(time)]
        ticks_per_quarternote = self.game.song.resolution
        ticks_per_wholenote = ticks_per_quarternote * 4
        beats_per_wholenote = ts.denominator
        ticks_per_beat = ticks_per_wholenote / beats_per_wholenote
        bpm = tempo.ticks_per_sec / ticks_per_beat * 60

        text = T(f"{bpm:.03f}BPM | {ts.numerator}/{ts.denominator}", font="Lato Medium", size=24, color="green")
        return text.render()

    def render_score(self, time):
        multmap = {1: "green", 2: "yellow", 3: "blue", 4: "purple"}
        text = T(f"Score: {self.game.scorecalculator.get_score(time)}", font="Lato Medium", size=24, color="green")
        extra_text = T(f"{self.game.scorecalculator.multiplier}x", font="Lato Medium", size=24, color="cyan" if self.game.hyperloop.sp else multmap[self.game.scorecalculator.multiplier]) + T(f" | {self.game.scorecalculator.streak} streak", font="Lato Medium", size=24, color="green")
        renderedtext = text.render()
        renderedextratext = extra_text.render()
        return stacksurfs((renderedtext, renderedextratext), 5)

    def render_notespeed(self):
        text = T(f"Note Speed: {self.game.hyperloop.length} sec/screen", font="Lato Medium", size=24, color="green")
        return text.render()

    def update(self, time):
        self.image.fill((0, 0, 0, 0))
        data = []
        data.append(self.render_clock())
        if self.game.song:
            data.append(self.render_volume())
            data.append(self.render_bpm(time))
        if self.game.hyperloop:
            data.append(self.render_notespeed())
        if self.game.lyricanimator:
            if self.game.lyricanimator.phrase_number is not None:
                data.append(self.render_phrase())
        if self.game.scorecalculator:
            data.append(self.render_score(time))
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
            Path("./charm/data/charts/chopsuey"),
            Path("./charm/data/charts/notes"),
            Path("./charm/data/charts/run_around_the_character_code"),
            Path("./charm/data/charts/soulless5"),
            Path("./charm/data/charts/soflan"),
            Path("./charm/data/charts/hopotest")
        ])

        # Set up guitar and InputRecorder.
        self.guitar = None
        self.inputrecorder = None
        self.inputdebug = None
        if instruments.Instrument.get_count() > 0:
            self.guitar = instruments.Wiitar.connect(0)
            print("Connection to Wiitar 0")
        else:
            self.guitar = instruments.Keyguitar.connect()
            print("Connection to Keyboard")
        self.inputrecorder = InputRecorder(self.guitar)
        self.inputdebug = InputDebug(self.guitar)

        # Initialize class variables.
        self.chart = None
        self.song = None
        self.scorecalculator = None
        self.lyricanimator = None
        self.hyperloop = None
        self.songdata = SongDataDisplay(self)
        self.videoplayer = None
        self.highway = "./charm/data/images/highway.png"

        # Static, generated images
        self.pause_image = draw_pause()
        self.loading_image = draw_loading()
        self.logo = draw_logo()

        # Load default chart.
        self.load_chart()

        self.paused = False
        self.volume = 6
        self.loading_timer = 0
        self.loading_queued = None
        self.frame = 0

        hyperloop_init()

    def queue_chart(self, songfolder: str = None, filename = "notes.chart", difficulty = "Expert"):
        self.loading_queued = {
            "songfolder": songfolder,
            "filename": filename,
            "difficulty": difficulty
        }
        self.loading_timer = 1
        # music.stop()

    def load_chart(self, songfolder: str = None, filename = "notes.chart", difficulty = "Expert"):
        if songfolder is None:
            songfolder = next(self.charts)

        songpath = Path(songfolder) / filename

        with songpath.open("r", encoding="utf-8") as f:
            self.song = chchart.load(f)

        self.chart = self.song.charts[(difficulty, 'Single')]

        # self.sc = ScoreCalculator(self.chart, self.ir)
        self.lyricanimator = LyricAnimator(self.chart)   # TODO: Update to take Song object
        self.hyperloop = HyperloopDisplay(self.chart, self.guitar, size=(400, 620), hitwindow_vis = False, bg = self.highway)
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

        videolist = list(songfolder.glob('*.mp4'))
        # videofile = songfolder / "video.mp4"
        if videolist:
            videofile = videolist[0]
            self.videoplayer = VideoPlayer(str(videofile.absolute()), width = 400)
        else:
            self.videoplayer = None

        if musicstream is None:
            raise ValueError("No valid music file found!")

        music.play(musicstream)

    def loop(self, events):
        now = None

        self.frame += 1

        for event in events:
            mods = pygame.key.get_mods()
            if event.type == pygame.KEYDOWN:
                if event.key == K_PAUSE:
                    now = music.elapsed
                    music.playpause()
                    time.sleep(0.01)
                elif event.key == K_KP4 and self.lyricanimator.prev_phrase is not None:
                    music.elapsed = self.lyricanimator.prev_phrase.start + 0.0001
                elif event.key == K_KP6 and self.lyricanimator.next_phrase is not None:
                    music.elapsed = self.lyricanimator.next_phrase.start + 0.0001
                elif event.key == K_HOME:
                    music.elapsed = 0
                elif event.key == K_KP_PLUS:
                    self.volume += 1
                elif event.key == K_KP_MINUS:
                    self.volume -= 1
                elif event.key in (K_7, K_KP7):
                    self.hyperloop.tilt = not self.hyperloop.tilt
                elif event.key == K_s:
                    self.hyperloop.sp = not self.hyperloop.sp
                elif event.key == K_l:
                    self.hyperloop.lefty = not self.hyperloop.lefty
                elif event.key == K_MINUS:
                    self.hyperloop.length -= 0.05
                elif event.key == K_EQUALS:
                    self.hyperloop.length += 0.05
                elif event.key == K_RETURN:
                    try:
                        self.queue_chart()
                    except chchart.UnparsedMetadataException as e:
                        print(e)
                self.hyperloop.length = max(0.05, self.hyperloop.length)
                self.hyperloop.length = round(self.hyperloop.length, 2)
            elif event.type == MOUSEWHEEL:
                if mods & pygame.KMOD_LSHIFT:
                    music.elapsed -= event.y
                else:
                    music.elapsed -= event.y / 10

        if now is None:
            now = music.elapsed
        instruments.Instrument.update(now, events)

        # Updates
        if not self.paused:
            if self.inputrecorder is not None:
                self.inputrecorder.update(now)
            if self.inputdebug is not None:
                self.inputdebug.update(now)
            if self.scorecalculator is not None:
                self.score = self.scorecalculator.get_score(now)
            if self.videoplayer is not None:
                self.videoplayer.update(now)
        self.lyricanimator.update(now)
        self.hyperloop.update(now)
        self.songdata.update(now)

        # Draws
        self.render_logo(now)
        self.render_notes()
        self.render_debug()
        if self.chart.song.lyrics:
            self.render_lyrics()
        if self.videoplayer:
            self.render_video()
        self.render_songdata()
        self.render_pause()
        self.render_section(now)
        self.render_title(now)
        self.render_loading()

        # Chart loading
        if self.loading_queued:
            if self.loading_timer > 0:
                self.loading_timer -= 1
            else:
                self.load_chart(**self.loading_queued)
                self.loading_queued = None

    def render_lyrics(self):
        dest = self.lyricanimator.image.get_rect()
        dest.centerx = self.surface.get_rect().centerx
        dest.top = self.surface.get_rect().top
        self.surface.blit(self.lyricanimator.image, dest)

    def render_notes(self):
        dest = self.hyperloop.image.get_rect()
        dest.centerx = self.surface.get_rect().centerx
        dest.bottom = self.surface.get_rect().bottom
        self.surface.blit(self.hyperloop.image, dest)

    def render_debug(self):
        dest = self.inputdebug.image.get_rect()
        dest.top = self.surface.get_rect().top
        dest.right = self.surface.get_rect().right
        self.surface.blit(self.inputdebug.image, dest)

    def render_songdata(self):
        dest = self.songdata.image.get_rect()
        dest.topleft = self.surface.get_rect().topleft
        self.surface.blit(self.songdata.image, dest)

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

    def render_logo(self, time):
        logo = self.logo
        logo = beatbounce(logo, self.song, time)
        logo_rect = logo.get_rect()
        logo_rect.bottomright = self.surface.get_rect().bottomright
        self.surface.blit(logo, logo_rect)

    def render_section(self, time):
        current_tick = self.song.tempo_calc.secs_to_ticks(time)
        current_section = ""
        if cs := self.song.section_by_ticks[current_tick]:
            current_section = cs.text

        text = T(truncate(emojize(current_section.replace("=", "-")), 32), font="Segoe UI Emoji", size=24, color="yellow")
        rect = text.get_rect()
        rect.bottomleft = self.surface.get_rect().bottomleft
        rect.move_ip(5, -5)
        text.render_to(self.surface, rect)

    def render_title(self, time):
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

    def render_video(self):
        dest = self.videoplayer.image.get_rect()
        dest.centery = self.surface.get_rect().centery
        dest.right = self.surface.get_rect().right
        self.surface.blit(self.videoplayer.image, dest)

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
    MenuTest = "menu"


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
    elif mode == Mode.MenuTest:
        menu2.Game(R"./charm/data/charts").run()
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
