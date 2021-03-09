from charm.classes.gamemode import Gamemode
from charm.classes.songdata import BPMEvent, Chart, Lyric, LyricPhrase, Note, Section, Song, TimeDelta, Timestamp
from charm.lib.constants import difficulties, frets, instruments

example_song = Song(
    name = "Example Song",
    artist = "DigiDuncan",
    album = "The Best Album",
    track = 1,
    year = 2021,
    genre = "Example",
    rating = 3,
    charter = "DigiSoft",
    length = 10000,
    resolution = 480,
    offset = 0,
    charts = [
        Chart(
            song = ...,  # TODO: How to pass in reference of the Song we're making?
            instrument = instruments.GUITAR,
            difficulty = difficulties.EXPERT,
            events = [..., ..., BPMEvent(..., 0, 120),
                      ..., ..., Note(..., ..., Timestamp(480), frets.GREEN),
                      ..., ..., Note(..., ..., Timestamp(720), frets.RED, 480),
                      ..., ..., Note(..., ..., Timestamp(720), frets.YELLOW, 480)]
        )
    ],
    events = [
        Section(..., position = 0, name = "The Section"),
        LyricPhrase(
            song = ...,
            position = 480,
            length = 480,
            lyrics = [
                Lyric(..., Timestamp(480), word = "Wow,", length = TimeDelta(Timestamp(480), 200)),
                Lyric(..., Timestamp(600), word = "cool!", length = TimeDelta(Timestamp(600), 200))
            ]
        )
    ]
)

example_gamemode = Gamemode(
    name = "gh",
    instruments = [instruments.GUITAR],
    lane_count = 5,
    image_folder = "gh",
    note_names = {
        frets.OPEN: "open",
        frets.GREEN: "green",
        frets.RED: "red",
        frets.YELLOW: "yellow",
        frets.BLUE: "blue",
        frets.ORANGE: "orange"
    },
    note_flags = ["hopo", "tap"],
    note_positions = {
        frets.OPEN: 3,
        frets.GREEN: 1,
        frets.RED: 2,
        frets.YELLOW: 3,
        frets.BLUE: 4,
        frets.ORANGE: 5
    },
    sprite_size = (64, 64),
    diff_names = {
        difficulties.EASY: "Easy",
        difficulties.MEDIUM: "Medium",
        difficulties.HARD: "Hard",
        difficulties.EXPERT: "Expert"
    }
)
