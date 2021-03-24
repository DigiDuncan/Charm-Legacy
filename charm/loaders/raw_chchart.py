from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Union

RE_BLOCK_HEADER = re.compile(r"^\[([A-Za-z ]+)\]\s*$")
RE_BLOCK_PADDING = re.compile(r"^[\{\}]$")
RE_QUOTED_TPL = r"\"?([^\"]+)\"?"
RE_NUM_TPL = r"(\d+)"
RE_LINE_TPL = r"^\s*{}\s*=\s*{}\s*$"
RE_ITEM_TPL = RE_LINE_TPL.format(RE_NUM_TPL, r"{}\s+{}")


class RawLoadException(Exception):
    pass


class DuplicateBlockException(RawLoadException):
    pass


class LineParseException(RawLoadException):
    pass


def load_raw(f) -> Dict[str, List[RawNote, RawEvent, RawTempo, RawAnchor, RawTS, RawStarPower, RawMetadata]]:
    blocks = {}
    curr_block = None
    for line in f:
        if m := RE_BLOCK_PADDING.match(line):
            continue
        elif m := RE_BLOCK_HEADER.match(line):
            curr_block = m.group(1)
            if curr_block in blocks:
                raise DuplicateBlockException(f"Duplicate block: {curr_block}")
            blocks[curr_block] = []
        else:
            lineobj = parse_line(line)
            if lineobj is None:
                raise LineParseException(f"Couldn't parse: {line}")
            blocks[curr_block].append(lineobj)
    return blocks


def parse_line(line) -> Union[RawNote, RawLyric, RawPhraseStart, RawPhraseEnd, RawEvent, RawTempo, RawAnchor, RawTS, RawStarPower, RawMetadata, None]:
    # parse RawMetadata last, because it's ambigious
    # parse RawLyric, RawPhraseStart and RawPhraseEnd before RawEvent, because they're subtypes of RawEvent
    rawclasses = [RawNote, RawLyric, RawPhraseStart, RawPhraseEnd, RawEvent, RawTempo, RawAnchor, RawTS, RawStarPower, RawMetadata]
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
        return self.tick_start < other.tick_start


@dataclass
class RawNote(RawTimedLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"N", RE_NUM_TPL + r"\s+" + RE_NUM_TPL))
    tick_start: int
    fret: int
    tick_length: int


@dataclass
class RawEvent(RawTimedLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"E", RE_QUOTED_TPL))
    tick_start: int
    data: str


@dataclass
class RawLyric(RawTimedLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"E", r"\"lyric ([^\"]+)\""))
    tick_start: int
    text: str


@dataclass
class RawPhraseStart(RawTimedLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"E", r"\"phrase_start\""))
    tick_start: int


@dataclass
class RawPhraseEnd(RawTimedLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"E", r"\"phrase_end\""))
    tick_start: int


@dataclass
class RawTempo(RawTimedLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"B", RE_NUM_TPL))
    tick_start: int
    mbpm: int


@dataclass
class RawAnchor(RawTimedLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"A", RE_NUM_TPL))
    tick_start: int
    mbpm: int


@dataclass
class RawTS(RawTimedLine):
    RE_LINE = re.compile(
        RE_ITEM_TPL.format(r"TS", RE_NUM_TPL + r"(?:\s+" + RE_NUM_TPL + ")?")
    )
    tick_start: int
    numerator: int
    denominator: int = None


@dataclass
class RawStarPower(RawTimedLine):
    RE_LINE = re.compile(RE_ITEM_TPL.format(r"S", RE_NUM_TPL + r"\s+" + RE_NUM_TPL))
    tick_start: int
    kind: int
    tick_length: int
