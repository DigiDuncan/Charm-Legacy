from charm.classes.songdata import BPMEvent, Note, Chord, Lyric, LyricPhrase, Track, Song
from charm.classes.gamemode import Gamemode
from charm.lib.constants import difficulties, frets, instruments

example_song = Song(
    name = "Example Song",
    artist = "DigiDuncan",
    album = "The Best Album",
    genre = "Example",
    difficulty = 3,
    charter = "DigiSoft",
    year = 2021,
    track = 1,
    length = 10000,
    resolution = 480,
    offset = 0,
    tracks = [
        Track(
            instrument = instruments.GUITAR,
            difficulty = difficulties.EXPERT,
            chords = [
                Chord(
                    position = 480,
                    flag = "normal",
                    notes = [Note(frets.GREEN, 0)]
                ),
                Chord(
                    position = 720,
                    flag = "normal",
                    notes = [Note(frets.RED, 480), Note(frets.YELLOW, 480)]
                )
            ],
            bpm_events = [BPMEvent(0, 120)]
        )
    ],
    lyricphrases = [
        LyricPhrase(
            position = 480,
            length = 480,
            lyrics = [
                Lyric(word = "Wow,", rel_position = 0, length = 200),
                Lyric(word = "cool!", rel_position = 200, length = 200)
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
    sprite_size = (64, 64),
    diff_names = {
        difficulties.EASY: "Easy",
        difficulties.MEDIUM: "Medium",
        difficulties.HARD: "Hard",
        difficulties.EXPERT: "Expert"
    }
)
