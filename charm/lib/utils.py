from typing import Tuple


def nice_time(seconds: float, milliseconds = False):
    ms = seconds % 1
    ms = int(ms * 1000)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    h, m, s = int(h), int(m), int(s)
    o = f'{h:}:{m:02}:{s:02d}'
    if milliseconds:
        o += f'.{ms:03d}'
    return o


def clamp(minVal, val, maxVal):
    if minVal is None:
        minVal = float("-inf")
    if maxVal is None:
        maxVal = float("inf")
    return max(minVal, min(maxVal, val))


def default_itemgetter(name, default=None):
    def getter(o):
        return getattr(o, name, default)
    return getter


def maxTuple(d: dict, absolute = False) -> Tuple:
    rev = {v: k for k, v in d.items()}
    absmap = {abs(v): v for v in d.values()}
    if absolute:
        values = []
        for v in d.values():
            values.append(abs(v))
        maxv = max(values)
        return (rev[absmap[maxv]], absmap[maxv])
    else:
        values = []
        for v in d.values():
            values.append(v)
        maxv = max(values)
        return (rev[maxv], maxv)


def degreesToXY(degrees: int) -> dict:
    # TODO: Genericize this.
    degmap = {
        0:   {"x": 0,  "y": -1},
        90:  {"x": 1,  "y": 0},
        180: {"x": 0,  "y": 1},
        270: {"x": -1, "y": 0}
    }

    degrees = degrees % 360
    if degrees not in degmap.keys():
        raise ValueError(f"{degrees} is not a supported degree.")

    return degmap[degrees]
