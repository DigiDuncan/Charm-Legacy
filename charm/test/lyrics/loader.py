from nygame.emoji import emojize
import re

RE_RESOLUTION = re.compile(r"^ *Resolution *= *(\d+)$")
RE_MBPM = re.compile(r"^ *(\d+) *= *B +(\d+)$")
RE_PHRASE_START = re.compile(r"^ *(\d+) = E \"phrase_start\"$")
RE_LYRIC = re.compile(r"^ *(\d+) = E \"lyric (.*)\"$")
RE_PHRASE_END = re.compile(r"^ *(\d+) = E \"phrase_end\"$")


def load_raw(f):
    resolution = None
    mbpms = []
    phrases = []
    phrase_ends = []
    words = []
    for line in f:
        if match := RE_RESOLUTION.match(line):
            if resolution is not None:
                raise ValueError("Cannot have multiple resolutions")
            resolution = int(match.group(1))
        elif match := RE_MBPM.match(line):
            tick_start = int(match.group(1))
            mbpm = int(match.group(2))
            mbpms.append(RawMBPM(tick_start, mbpm))
        elif match := RE_PHRASE_START.match(line):
            tick_start = int(match.group(1))
            phrases.append(RawPhrase(tick_start))
        elif match := RE_LYRIC.match(line):
            tick_start = int(match.group(1))
            text = match.group(2)
            words.append(RawWord(tick_start, text))
        elif match := RE_PHRASE_END.match(line):
            tick_end = int(match.group(1))
            phrase_ends.append(tick_end)
    if resolution is None:
        raise ValueError("Missing resolution")
    if not any(True for m in mbpms if m.tick_start == 0):
        raise ValueError("Missing initial mbpm")
    mbpms = sorted(mbpms)
    phrases = sorted(phrases)

    ip = iter(phrases[::-1])
    try:
        p = next(ip)
        for phrase_end in sorted(phrase_ends)[::-1]:
            while not(p.tick_start < phrase_end):
                p = next(ip)
            if p.tick_end is not None:
                raise ValueError("Phrase has more than one end")
            p.tick_end = phrase_end
    except StopIteration:
        raise ValueError(f"Phrase end did not have a match phrase start: {phrase_end!r}")

    for p, np in zip(phrases[:-1], phrases[1:]):
        if p.tick_end is None:
            p.tick_end = np.tick_start

    ip = iter(phrases)
    try:
        p = next(ip)
        for word in sorted(words):
            while not(p.tick_start <= word.tick_start < p.tick_end):
                p = next(ip)
            p.words.append(word)
    except StopIteration:
        raise ValueError(f"Word was not part of a phrase: {word!r}")

    return resolution, mbpms, phrases


class RawMBPM:
    def __init__(self, tick_start, mbpm):
        self.tick_start = tick_start
        self.mbpm = mbpm

    def __lt__(self, other):
        self.tick_start < other.tick_start


class RawPhrase:
    def __init__(self, tick_start):
        self.tick_start = tick_start
        self.tick_end = None
        self.words = []

    def __lt__(self, other):
        self.tick_start < other.tick_start


class RawWord:
    def __init__(self, tick_start, text):
        self.tick_start = tick_start
        self.text = text

    def __lt__(self, other):
        self.tick_start < other.tick_start


class TicksPerSecond():
    def __init__(self, tick_start, start, tps):
        self.tick_start = tick_start
        self.start = start
        self.tps = tps

    def __lt__(self, other):
        self.tick_start < other.tick_start


class BPMCalculator:
    def __init__(self, resolution, mbpms):
        self.tps = []
        for mbpm in mbpms:
            start = self.ticks2secs(mbpm.tick_start)
            tps = resolution * mbpm.mbpm / 1000 / 60
            self.tps.append(TicksPerSecond(mbpm.tick_start, start, tps))

    def ticks2secs(self, ticks):
        if ticks == 0:
            return 0
        curr_tps = next(tps for tps in self.tps if tps.tick_start <= ticks)
        curr_ticks = ticks - curr_tps.tick_start
        curr_seconds = curr_ticks / curr_tps.tps
        seconds = curr_tps.start + curr_seconds
        return seconds


class LyricPhrase():
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.words = []

    def get_on_text(self, tracktime):
        return "".join(w.text for w in self.words if w.is_on(tracktime - self.start))

    def get_off_text(self, tracktime):
        return "".join(w.text for w in self.words if not w.is_on(tracktime - self.start))

    def get_text(self):
        return "".join(w.text for w in self.words)

    def is_active(self, tracktime):
        return self.start <= tracktime < self.end

    def is_waiting(self, tracktime):
        return self.start > tracktime

    def is_done(self, tracktime):
        return self.end <= tracktime

    def __lt__(self, other):
        return self.start < other.start


def clean_word(word: str):
    if word.endswith("-"):
        word = word.removesuffix("-")
    else:
        word = word + " "
    word = word.replace("=", "-").replace("''", "\"").replace("+", "").replace("#", "").replace("^", "")
    word = emojize(word)
    return word


class LyricWord:
    def __init__(self, offset, text):
        self.offset = offset
        self.text = clean_word(text)

    def is_on(self, curr_offset):
        return self.offset <= curr_offset

    def __lt__(self, other):
        return self.offset < other.offset


def load_lyrics(f):
    resolution, mbpms, raw_phrases = load_raw(f)
    bpmcalc = BPMCalculator(resolution, mbpms)

    phrases = []
    for raw_phrase in raw_phrases:
        phrase_start = bpmcalc.ticks2secs(raw_phrase.tick_start)
        phrase_end = bpmcalc.ticks2secs(raw_phrase.tick_end)
        phrase = LyricPhrase(phrase_start, phrase_end)
        phrases.append(phrase)
        for raw_word in raw_phrase.words:
            word_start = bpmcalc.ticks2secs(raw_word.tick_start)
            offset = word_start - phrase_start
            word = LyricWord(offset, raw_word.text)
            phrase.words.append(word)

    return phrases
