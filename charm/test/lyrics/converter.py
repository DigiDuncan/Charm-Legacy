import pprint
import re

RE_PHRASE_START = re.compile(r"(\d+) \"phrase_start\"")
RE_LYRIC = re.compile(r"(\d+) \"lyric (.*)\"")
RE_PHRASE_END = re.compile(r"(\d+) \"phrase_end\"")

with open("./charm/test/lyrics/run_around.chart", mode="r") as f:
    lines = f.readlines()

writeto = open("run_around.txt", mode="w")

tps = 702

printer = pprint.PrettyPrinter(indent=4, width=120, stream=writeto)


def ticks_to_seconds(ticks):
    return int(ticks) / tps


lyrics = []
current_phrase = {}
for line in lines:
    if match := RE_PHRASE_START.match(line):
        current_phrase["time"] = ticks_to_seconds(match.group(1))
        current_phrase["words"] = []
    if match := RE_LYRIC.match(line):
        current_phrase["words"].append(
            {"time": ticks_to_seconds(match.group(1)) - current_phrase["time"],
             "word": match.group(2)})
    if match := RE_PHRASE_END.match(line):
        current_phrase["end_time"] = ticks_to_seconds(match.group(1))
        lyrics.append(current_phrase)
        current_phrase = {}

printer.pprint(lyrics)
