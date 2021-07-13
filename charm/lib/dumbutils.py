from functools import lru_cache, wraps
from charm.song import Song

import pygame.transform
from pygame import Surface


@lru_cache(2048)
def zoom(surface: Surface, scale: float):
    return pygame.transform.rotozoom(surface, 0, scale)


def beatbounce(surface: Surface, song: Song, time: float, scale = 1.25):
    # return surface
    tempo = song.tempo_calc.tempo_by_secs.lteq(time)
    start = tempo.start
    bpm = tempo.mbpm / 1000
    sec_per_beat = (1 / bpm) * 60

    t = time - start
    y = t // sec_per_beat
    current_start = start + (y * sec_per_beat)

    # https://www.desmos.com/calculator/ybomko2ah8
    e = sec_per_beat / 2
    x = time - current_start
    s = scale

    current_scale = (-((s - 1) / e) * x) + s
    current_scale = round(max(current_scale, 1), 2)
    if current_scale == 1:
        return surface

    return zoom(surface, current_scale)


def beatbouncedeco(song = "song", time = "tracktime", scale = 1.25):
    def wrapper(fn):
        @wraps(fn)
        def wrapped(self, *args, **kwargs):
            surf = fn(self, *args, **kwargs)
            return beatbounce(surf, getattr(self, song), getattr(self, time), scale)
        return wrapped
    return wrapper
