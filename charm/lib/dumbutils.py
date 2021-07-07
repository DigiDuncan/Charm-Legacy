from charm.prototyping.notedisplay.inputdebug import CHARM
from charm.song import Song

import pygame.transform
from pygame import Surface


def beatbounce(surface: Surface, song: Song, time: float, scale = 1.25):
    tempo = song.tempo_calc.tempo_by_secs[time]
    start = tempo.start
    bpm = tempo.mbpm / 1000
    sec_per_beat = (1 / bpm) * 60
    current_start = start
    while start < time:
        current_start = start
        start += sec_per_beat

    # https://www.desmos.com/calculator/ybomko2ah8
    e = sec_per_beat / 2
    x = time - current_start
    s = scale

    current_scale = (-((s - 1) / e) * x) + s
    current_scale = max(current_scale, 1)

    return pygame.transform.rotozoom(surface, 0, current_scale)
