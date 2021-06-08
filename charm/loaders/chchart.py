from __future__ import annotations

import re
from itertools import groupby, product
from typing import Dict, List, Tuple, Union

from nygame.emoji import emojize

from charm.loaders.raw_chchart import RawEvent, RawLyric, RawNote, RawPhraseEnd, RawPhraseStart, RawSection, RawStarPower, RawTempo, RawAnchor, RawTS, RawMetadata, load_raw
from charm.song import Chart, Chord, Event, LyricPhrase, LyricWord, Note, Section, Song, SPEvent, TSEvent, TempoCalculator, TempoEvent


class LoadException(Exception):
    pass


class DuplicateChartException(LoadException):
    pass


class InvalidEventException(LoadException):
    pass


class InvalidHeaderException(LoadException):
    pass


class InvalidLineTypeException(LoadException):
    pass


class InvalidMetadataException(LoadException):
    pass


class InvalidSynctrackDataException(LoadException):
    pass


class MissingEventsBlockException(LoadException):
    pass


class MissingSongBlockException(LoadException):
    pass


class MissingSyncTrackBlockException(LoadException):
    pass


class UnmatchedPhraseStartException(LoadException):
    pass


class UnmatchedPhraseEndException(LoadException):
    pass


class UncontainedLyricWordException(LoadException):
    pass


class UnparsedMetadataException(LoadException):
    def __init__(self, keys):
        super().__init__(f"Unparsed metadata: {keys}")
        self.keys = keys


def note_from_raw(song: Song, chart: Chart, rawnote: RawNote) -> Note:
    note = Note(song, chart, rawnote.tick_start, rawnote.fret, rawnote.tick_length)
    return note


def spevent_from_raw(song: Song, chart: Chart, rawspevent: RawStarPower) -> SPEvent:
    spevent = SPEvent(song, chart, rawspevent.tick_start, rawspevent.kind, rawspevent.tick_length)
    return spevent


def event_from_raw(song: Song, chart: Chart, rawevent: RawEvent) -> Event:
    event = Event(song, chart, rawevent.tick_start, rawevent.data)
    return event


DIFFICULTIES = ("Easy", "Medium", "Hard", "Expert")
INSTRUMENTS = ("Single", "DoubleGuitar", "DoubleBass", "DoubleRhythm", "Keyboard", "Drums", "GHLGuitar", "GHLBass")
DIFFINST_MAP = {d + i: (d, i) for d, i in product(DIFFICULTIES, INSTRUMENTS)}    # Precalculate all DifficultyInstrument pairings


def chart_from_raw(song: Song, header: str, lines: List[RawNote, RawEvent, RawTempo, RawAnchor, RawTS, RawStarPower, RawMetadata]) -> Chart:
    try:
        difficulty, instrument = DIFFINST_MAP[header]
    except KeyError:
        raise InvalidHeaderException(f"Invalid Header: {header}")

    chart = Chart(song, instrument, difficulty)

    notes = []
    star_powers = []
    events = []
    for line in lines:
        if isinstance(line, RawNote):
            notes.append(note_from_raw(song, chart, line))
        elif isinstance(line, RawStarPower):
            star_powers.append(spevent_from_raw(song, chart, line))
        elif isinstance(line, RawEvent):
            events.append(event_from_raw(song, chart, line))
        else:
            raise InvalidLineTypeException(f"Bad line type {line}")

    chart.notes = notes
    chart.star_powers = star_powers
    chart.events = events
    chart.chords = [notes_to_chord(song, chart, list(notes)) for _, notes in groupby(chart.notes, key=lambda n: n.tick_start)]
    chart.finalize()
    return chart


def notes_to_chord(song, chart, notes):
    frets = [n.fret for n in notes]
    if 6 in frets:
        flag = "tap"
    elif 5 in frets:
        flag = "forced"
    else:
        flag = "note"
    notes = [n for n in notes if n.fret not in (5, 6)]
    chord = Chord(song, chart, flag, notes)
    return chord


def tryint(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


# TODO: Handle metadata smarter
def set_metadata(song, lines: List[RawMetadata]) -> Dict[str, Union[str, int]]:
    metadata = {}
    for md in lines:
        if not isinstance(md, RawMetadata):
            raise InvalidMetadataException(f"Invalid metadata {md}")
        metadata[md.key] = md.value
    # TODO: Which metadata fields are required, and which are optional?
    song.full_name = metadata.pop("Name", None)
    song.title, song.subtitle = song.full_name, None
    if song.full_name is not None:
        RE_PARENTHETICAL = re.compile(r"(.*)(\(.*\).*)")
        if m := RE_PARENTHETICAL.match(song.full_name):
            song.title, song.subtitle = m.groups()

    song.alt_title = "UNUSED"
    song.artists = metadata.pop("Artist", None)
    song.album = metadata.pop("Album", None)
    song.year = metadata.pop("Year", None)
    song.charter = metadata.pop("Charter", None)
    song.offset = tryint(metadata.pop("Offset", None))
    song.resolution = tryint(metadata.pop("Resolution"))
    song.difficulty = tryint(metadata.pop("Difficulty", None))
    song.previewstart = tryint(metadata.pop("PreviewStart", None))
    song.previewend = tryint(metadata.pop("PreviewEnd", None))
    song.genre = metadata.pop("Genre", None)
    song.mediastream = metadata.pop("MediaStream", None)
    song.musicstream = metadata.pop("MusicStream", None)
    # TODO: Do something with these unparsed metadata entries
    for tag in ["Player2", "GuitarStream", "MediaType", "ArtistText", "CountOff", "GuitarVol", "BandVol", "HoPo", "OriginalArtist"]:
        metadata.pop(tag, None)
    if len(metadata) > 0:
        raise UnparsedMetadataException(list(metadata.keys()))


def parse_synctrack(song, lines: List[RawTempo, RawTS]) -> Tuple[TempoCalculator, List[TSEvent]]:
    raw_tempos: List[RawTempo] = []
    raw_timesigs: List[RawTS] = []
    for line in lines:
        if isinstance(line, RawTempo):
            raw_tempos.append(line)
        elif isinstance(line, RawTS):
            raw_timesigs.append(line)
        else:
            raise InvalidSynctrackDataException(f"Invalid synctrack data {line}")

    tempos = []
    for raw_tempo in raw_tempos:
        ticks_per_second = song.resolution * raw_tempo.mbpm / 1000 / 60
        tempo = TempoEvent(song, raw_tempo.tick_start, ticks_per_second)
        tempos.append(tempo)
    tempo_calc = TempoCalculator(tempos)

    timesigs = []
    for rts in raw_timesigs:
        ticks_per_second = song.resolution * raw_tempo.mbpm / 1000 / 60
        timesig = TSEvent(song, rts.tick_start, rts.numerator, 2 ** rts.denominator if rts.denominator is not None else 4)
        timesigs.append(timesig)

    return tempo_calc, timesigs


def parse_events(song: Song, raw_events: List[Union[RawEvent, RawLyric, RawPhraseStart, RawPhraseEnd, RawSection]]) -> Tuple[List[Event], List[LyricPhrase], List[Section]]:
    raw_lyrics = []
    raw_phrase_events = []
    raw_sections = []
    events = []
    for e in raw_events:
        if isinstance(e, RawLyric):
            raw_lyrics.append(e)
        elif isinstance(e, RawPhraseStart) or isinstance(e, RawPhraseEnd):
            raw_phrase_events.append(e)
        elif isinstance(e, RawSection):
            raw_sections.append(e)
        elif isinstance(e, RawEvent):
            events.append(event_from_raw(song, None, e))
        else:
            raise InvalidEventException(f"Invalid event {e}")

    raw_sections.sort()
    sections = [Section(song, sect.tick_start, sect.text) for sect in raw_sections]

    if not raw_phrase_events:
        return events, [], sections

    raw_phrase_events.sort()

    # Can't start with a phrase end
    if isinstance(raw_phrase_events[0], RawPhraseEnd):
        raise UnmatchedPhraseEndException("Phrase end found with no matching phrase start.")
    # Can't end with a phrase start
    if isinstance(raw_phrase_events[-1], RawPhraseStart):
        raise UnmatchedPhraseStartException("Phrase start found with no matching phrase end.")
    # Pair the events into start-end or start-start pairs
    phrase_pairs = zip(raw_phrase_events[:-1], raw_phrase_events[1:])
    # Remove any end-start pairs
    phrase_pairs = [(start, end) for start, end in phrase_pairs if not (isinstance(start, RawPhraseEnd) and isinstance(end, RawPhraseStart))]
    # Check for any end-end pairs
    if any((start, end) for start, end in phrase_pairs if isinstance(start, RawPhraseEnd) and isinstance(end, RawPhraseEnd)):
        raise UnmatchedPhraseEndException("Phrase end found with no matching phrase start.")

    # Reduce to LyricPhrase objects
    phrases = [LyricPhrase(song, start.tick_start, end.tick_start - start.tick_start) for start, end in phrase_pairs]
    # Create LyricWord objects
    words = [LyricWord(song, raw.tick_start, clean_word(raw.text)) for raw in raw_lyrics]
    # Attach LyricWord objects to LyricPhrase objects
    words.sort()
    iter_phrases = iter(phrases)
    curr_phrase = next(iter_phrases)
    try:
        for word in words:
            while not curr_phrase.contains(word):
                curr_phrase = next(iter_phrases)
            curr_phrase.words.append(word)
    except StopIteration:
        raise UncontainedLyricWordException("LyricWord does not have a matching phrase")

    for p in phrases:
        p.finalize()

    return events, phrases, sections


def clean_word(word: str):
    if word.endswith("-"):
        word = word.removesuffix("-")
    else:
        word = word + " "
    replacements = {
        "=": "-",
        "''": "\"",
        "`": "\"",
        "+": "",
        "#": "",
        "^": "",
        "_": " "
    }
    for old, new in replacements.items():
        word = word.replace(old, new)
    word = emojize(word)
    return word


def song_from_raw(datablocks: Dict[str, List[RawNote, RawEvent, RawTempo, RawAnchor, RawTS, RawStarPower, RawMetadata]]) -> Song:
    if "Song" not in datablocks:
        raise MissingSongBlockException("Missing Song block")
    if "Events" not in datablocks:
        raise MissingEventsBlockException("Missing Events block")
    if "SyncTrack" not in datablocks:
        raise MissingSyncTrackBlockException("Missing SyncTrack block")

    song = Song()
    set_metadata(song, datablocks.pop("Song"))
    song.tempo_calc, song.timesigs = parse_synctrack(song, datablocks.pop("SyncTrack"))
    song.events, song.lyrics, song.sections = parse_events(song, datablocks.pop("Events"))
    part_vocals = datablocks.pop("PART VOCALS", None)    # TODO Handle vocals section

    charts = {}
    for block, lines in datablocks.items():
        chart = chart_from_raw(song, block, lines)
        key = (chart.difficulty, chart.instrument)
        if key in charts:
            raise DuplicateChartException(f"Duplicate chart: {chart.difficulty} {chart.instrument}")
        charts[key] = chart
    song.charts = charts

    song.finalize()

    return song


def load(f) -> Song:
    datablocks = load_raw(f)
    song = song_from_raw(datablocks)
    return song
