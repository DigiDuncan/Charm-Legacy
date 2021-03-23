import importlib.resources as pkg_resources

from pygame import Rect, Surface, image, transform
from pygame.constants import SRCALPHA
import charm.data.images.spritesheets as image_folder

HIT_WINDOW = 0.140  # 140ms

fretnums = {
    "green": 0,
    "red": 1,
    "yellow": 2,
    "blue": 3,
    "orange": 4,
    "open": 7
}

fretmap = {
    "green": 0,
    "red": 1,
    "yellow": 2,
    "blue": 3,
    "orange": 4,
    "sp": 5,
    "open": (6, 5),
    "opensp": (11, 5)
}

flagmap = {
    "note": 0,
    "hopo": 1,
    "tap": 2,
    "strike": 6
}

gh_sheet: Surface = None

fret_images = {}


def get_sprite(flag, fret):
    return fret_images[flag][fret]


def set_sprite(flag, fretname, sprite):
    fret_images[flag][fretname] = sprite
    if fretname in fretnums:
        fretnum = fretnums[fretname]
        fret_images[flag][fretnum] = sprite


def init():
    global gh_sheet

    SPRITE_SIZE = 64

    with pkg_resources.path(image_folder, "gh.png") as p:
        gh_sheet = image.load(p)
        gh_sheet.convert_alpha()

    for flag, sy in flagmap.items():
        fret_images[flag] = {}
        for fret, sxw in fretmap.items():
            sw = 1
            try:
                sx, sw = sxw
            except TypeError:
                sx = sxw
            x = sx * SPRITE_SIZE
            y = sy * SPRITE_SIZE
            w = sw * SPRITE_SIZE
            h = SPRITE_SIZE
            img = gh_sheet.subsurface(Rect(x, y, w, h))
            set_sprite(flag, fret, img)


def getone(items):
    try:
        return next(items)
    except StopIteration:
        return None


class HyperloopDisplay:
    def __init__(self, chart, *, size: tuple = (400, 400), lefty = False):
        self.chart = chart
        self.size = size
        self.lefty = lefty
        self._image = Surface(size, SRCALPHA)
        self.tracktime = 0
        self.length = 0.75
        self.last_drawn = None
        self.chord_stream = iter(c for c in self.chart.chords)
        self.visible_chords = []
        self.upcoming_chord = next(self.chord_stream)
        self.strike_fadetime = 0.5

    @property
    def end(self):
        return self.tracktime + self.length

    def get_fret_pos(self, f, diff=0):
        if diff < 0:
            diff = 0
        w, h = self.size
        fw, fh = 64, 64
        fcnt = 5

        wspace = w / fcnt
        x = (wspace * f) + (wspace / 2) - (fw / 2)

        y = h - fh - (h * (diff / self.length))

        if f == 7:
            x = 0
            y += 16

        return x, y

    def update(self, tracktime):
        self.tracktime = tracktime
        self.visible_chords = self.chart[self.tracktime - self.strike_fadetime:self.end]

    def draw(self):
        self._image.fill("clear")

        fret_strikes = [0, 0, 0, 0, 0]
        for chord in self.visible_chords:
            diff = chord.start - self.tracktime
            if diff < 0:
                for fret in chord.frets:
                    fade = max(0, self.strike_fadetime + diff)  # 0 to 0.5
                    fade /= self.strike_fadetime                # 0 t0 1
                    fret_strikes[fret] = max(fret_strikes[fret], fade)
                continue
            for fret in chord.frets:
                pos = self.get_fret_pos(fret, diff)
                self._image.blit(get_sprite(chord.flag, fret), pos)

        for fret, fade in enumerate(fret_strikes):
            fade_alpha = 255 * fade
            sprite = get_sprite("strike", fret)
            sprite.set_alpha(fade_alpha)

            pos = self.get_fret_pos(fret)
            self._image.blit(sprite, pos)

    @property
    def image(self) -> Surface:
        # Don't rerender what we just rendered
        to_draw = self.tracktime
        if to_draw != self.last_drawn:
            self.draw()
            self.last_drawn = to_draw
        if self.lefty:
            return transform.flip(self._image, True, False)
        return self._image
