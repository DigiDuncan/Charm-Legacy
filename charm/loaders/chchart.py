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

    def __str__(self):
        return f"<{repr(self)}>"

    def __post_init__(self):
        for attr, attrtype in self.__annotations__.items():
            if attrtype == "int":
                oldval = getattr(self, attr)
                if oldval is None:
                    return
                setattr(self, attr, int(oldval))


@dataclass
class RawMetadata(RawLine):
    RE_LINE = re.compile(RE_LINE_TPL.format(r"([A-Za-z][A-Za-z0-9_]*)", RE_QUOTED_TPL))
    key: str
    value: str


class RawTimedLine(RawLine):
    def __lt__(self, other):
        return self.time < other.time


@dataclass
class RawNote(RawTimedLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"N", RE_NUM_TPL + r"\s+" + RE_NUM_TPL))
    time: int
    kind: int
    length: int


@dataclass
class RawEvent(RawTimedLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"E", RE_QUOTED_TPL))
    time: int
    data: str


@dataclass
class RawMBPM(RawTimedLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"B", RE_NUM_TPL))
    time: int
    mpbm: int


@dataclass
class RawAnchor(RawTimedLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"A", RE_NUM_TPL))
    time: int
    mpbm: int


@dataclass
class RawTS(RawTimedLine):
    RE_LINE = re.compile(
        RE_ITEM_TPL.format(r"TS", RE_NUM_TPL + r"(?:\s+" + RE_NUM_TPL + ")?")
    )
    time: int
    numerator: int
    denominator: int = None


@dataclass
class RawStarPower(RawTimedLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"S", RE_NUM_TPL + r"\s+" + RE_NUM_TPL))
    time: int
    kind: int
    length: int


if __name__ == "__main__":
    with open(r"C:\Users\nfear\Desktop\Coding\Charm\charm\data\charts\run_around_the_character_code\run_around_the_character_code.chart") as f:
        print(load(f))
