from __future__ import annotations

import re

from dataclasses import dataclass
from typing import Union

RE_BLOCK_HEADER = re.compile(r"^\[([A-Za-z ]+)\]\s*$")
RE_BLOCK_PADDING = re.compile(r"^[\{\}]$")
RE_QUOTED_TPL = r"\"?([^\"]+)\"?"
RE_NUM_TPL = r"(\d+)"
RE_LINE_TPL = r"^\s*{}\s*=\s*{}\s*$"
RE_ITEM_TPL = RE_LINE_TPL.format(RE_NUM_TPL, r"{}\s+{}")


def load(f):
    blocks = {}
    curr_block = None
    for line in f:
        if m := RE_BLOCK_PADDING.match(line):
            continue
        elif m := RE_BLOCK_HEADER.match(line):
            curr_block = m.group(1)
            if curr_block in blocks:
                raise ValueError(f"Duplicate block: {curr_block}")
            blocks[curr_block] = []
        else:
            lineobj = parse_line(line)
            if lineobj is None:
                raise ValueError(f"Couldn't parse: {line}")
            blocks[curr_block].append(lineobj)
    return blocks


def parse_line(line):
    # parse RawMetadata last, because it's ambigious
    rawclasses = [RawNote, RawEvent, RawMBPM, RawAnchor, RawTS, RawStarPower, RawMetadata]
    parsed = (c.parse(line) for c in rawclasses)
    succesfully_parsed = (obj for obj in parsed if obj is not None)
    try:
        lineobj = next(succesfully_parsed)
    except StopIteration:
        lineobj = None
    return lineobj


class RawLine:
    @classmethod
    def parse(cls, line):
        if m := cls.RE_LINE.match(line):
            return cls(*m.groups())
        return None


@dataclass
class RawMetadata(RawLine):
    RE_LINE = re.compile(RE_LINE_TPL.format(r"([A-Za-z][A-Za-z0-9_]*)", RE_QUOTED_TPL))
    key: str
    value: str


@dataclass(order = True)
class RawNote(RawLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"N", RE_NUM_TPL + r"\s+" + RE_NUM_TPL))
    time: int
    kind: int
    length: int


@dataclass(order = True)
class RawEvent(RawLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"E", RE_QUOTED_TPL))
    time: int
    data: str


@dataclass(order = True)
class RawMBPM(RawLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"B", RE_NUM_TPL))
    time: int
    mpbm: int


@dataclass(order = True)
class RawAnchor(RawLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"A", RE_NUM_TPL))
    time: int
    mpbm: int


@dataclass(order = True)
class RawTS(RawLine):
    RE_LINE = re.compile(
        RE_ITEM_TPL.format(r"TS", RE_NUM_TPL + r"(?:\s+" + RE_NUM_TPL + ")?")
    )
    time: int
    numerator: int
    denominator: Union[int, None] = None


@dataclass(order = True)
class RawStarPower(RawLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"S", RE_NUM_TPL + r"\s+" + RE_NUM_TPL))
    time: int
    one: int
    two: int


if __name__ == "__main__":
    with open(r"C:\Users\nfear\Desktop\Coding\Charm\charm\test\lyrics\run_around_the_character_code.chart") as f:
        print(load(f))
