import sys
from functools import wraps


def cleave(items, pred=bool):
    hit = []
    miss = []
    for i in items:
        (hit if pred(i) else miss).append(i)
    return hit, miss


def parse_kwarg(k):
    """
    Parse a kwarg in the format `--key` or `--key=value`
    """
    k = k.removeprefix("--")
    k, _, v = k.partition("=")
    if not v:
        v = True
    return k, v


def parse_switch(s):
    """
    Parse a switch in the format `-k` or `-kvalue`
    """
    s = s.removeprefix("-")
    s, v = s[:1], s[1:]
    if not v:
        v = True
    return s, v


def parse_cmdargs(cmdargs):
    raw_kwargs, args = cleave(cmdargs, lambda a: a.startswith("--"))
    raw_switches, args = cleave(args, lambda a: a.startswith("-"))
    kwargs = dict(map(parse_kwarg, raw_kwargs))
    switches = dict(map(parse_switch, raw_switches))
    kwargs |= switches
    return args, kwargs


def nargs(fn):
    @wraps(fn)
    def wrapped(cmdargs=sys.argv[1:]):
        args, kwargs = parse_cmdargs(cmdargs)
        return fn(*args, **kwargs)
    return wrapped


if __name__ == "__main__":
    @nargs
    def any_func(*args, **kwargs):
        print(args)
        print(kwargs)
    any_func()
