from charm.lib.constants import frets
from charm.objects.songdata import Note, Chord, Lyric, LyricPhrase, Track, Song

example_song = Song(
    name = "Example Song",
    artist = "DigiDuncan",
    album = "The Best Album",
    difficulty = 3,
    charter = "DigiSoft",
    year = 2021,
    track = 1,
    length = 10000,
    resolution = 480,
    offest = 0,
    tracks = [
        Track(
            instrument = "GUITAR",
            chords = [
                Chord(
                    position = 480,
                    flag = "normal",
                    star_power = False,
                    notes = [Note(frets.GREEN, 0)]
                ),
                Chord(
                    position = 720,
                    flag = "normal",
                    star_power = False,
                    notes = [Note(frets.RED, 480), Note(frets.YELLOW, 480)]
                )
            ]
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
