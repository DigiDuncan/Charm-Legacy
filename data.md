# Data
Songs, Gamemodes, etc. contain a lot of important data to define various attributes about asepcts of the gameplay. These data points are layed out in the following document.

## Song
A Song has some metadata on it's highest level, to define certain attributes for sorting, as well a few important chart-related data points:

* `name: str`, the name of the song.
* `artist: str`, the name of the artist.
* `album: str`, the name of the album.
* `track`: The track index of the song on the album.
* `year: int?`, the year the song was released. This is usually an `int` representing a year, but some charts have stupid ones like `"All The Time"` or something. Some games display non-integer values for `year` as `"Unknown Year"`, which helps with sorting, but ruins some jokes.
* `genre: str`, the genre of the song.
* `rating: int`, how hard the song is, usually a number between 0 and 6.
* `charter: str`, the name of the person who charted (created the chart for) the song.
* `length: int`, the amount of milliseconds<sup>?</sup> the song lasts for. Used only<sup>?</sup> for sorting.

And the more helpful data:

* `resolution: int`, the "ticks per beat" of the charts contained in the song[^1].
* `offset: int`[^2], the offset in milliseconds<sup>?</sup> that the ticks are pushed forward. (An offset of 100 would mean tick 0 refers to the time 0.1s.)
* `charts: List[Chart]`: Every chart associated with this song.
* `lyricphrases: List[LyricPhrase]`: A list of LyricPhrases associated with this song, sorted by position.

### Functions

* `get_chart(instrument: str, difficulty: int) -> Chart | None`, get the chart that matches the input parameters, or None. 

## Gamemode

*Charm* can[^3] play charts from various games and gamemodes, not all of them from the *Guitar Hero* series. For this reason, Gamemode objects define the layout and gameplay style of various games/modes.

* `name: str`, the name of this gamemode, and ID that isn't displayed to the user.
* `instruments: List[str]`, a list of valid instruments that this gamemode encompasses.
* `lane_count: int`, Since *Charm* plays VSRG (vertical-scrolling rhythm game)s, each game has an amount of lanes. 5 for *Guitar Hero* guitars, bass, and keys; 3 for *Guitar Hero: Live*, 4 for *Dance Dance Revolution*, etc.
* `image_folder: str`, the name of the subfolder in `charm.data.images` that contains the sprites for notes in this gamemode.
* `notes: Dict[int, dict]`[^4] a map of a fret ID and these keys;
    * `name: str`, the name of this fret
    * `lane: int`, the lane this note shows up in
* `sprite_size: Tuple[int, int]`: A Tuple of (width, height) for the size of the note images in this game mode.[^5]
* `diff_names: Dict[int, str]`, a map of difficulty IDs and names.

## Note

Notes are key to any rhythm game. Thus, they must have good data to go along with them!

* `fret: int`, the fret ID of this note.
* `position: TimeStamp`, the position in the chart this note shows up.
* `length: TimeDelta`, the length of this note.
* `flag: str`, either `"normal"`, `"hopo"`, `"tap"`, etc. for GH, can be others for other gamemodes.

## Lyric

This represents a single lyric, which is always part of a larger LyricPhrase.

* `word: str`, the word to be displayed.
* `position: TimeStamp`, the position (absolute) of this lyric in the song.
* `length: TimeDelta`, the length this lyric lasts for.
* `partial: bool = False`, essentially whether or not to append a space at the end of the word or not (False means you should, unless it's at the end of the phrase.)

## LyricPhrase

Contains Lyrics, represents a "line" of text.

* `position: TimeStamp`, where the phrase appears in the song.
* `length: TimeDelta`, how long to show this phrase on screen.
* lyrics: `List[Lyrics]`, all the Lyrics this phrase contains, sorted by position.


## Events

Events can happen in the chart at a time. Besides that, it's pretty vague! Let's be less vague. All Events have a...

* `position: TimeStamp`, the position of the event in the chart.

### BPMEvent

* `bpm: float`, the current BPM going forward, until the next BPMEvent.

### TSEvent

* `time_sig: Tuple[int, int]`, the current time signature represented as (numerator, denominator) going forward, until the next TSEvent.

### SPEvent

* `length: TimeDelta`, how long this star power phrase lasts for.

### GenericEvent

Always plan for the future. We could make our own! `ChartSwapEvent`? `ScreenModifierEvent`? The world is ours to change!


## Chart

Charts are individual maps of notes and events. They are what the player selects to play.

* `instrument: str`, what instrument this chart is for.
* `difficulty: int`, the difficulty ID of this chart, representing something like Easy or Expert.
* `notes: List[Note]`, the list of all notes in this chart, sorted by position.
* `events: List[Event]`, the list of all events in this chart, sorted by position.

### Functions

* `.chords -> List[Chord]`, a list of all Chords in the chart sorted by position, a Chord being an object with the following properties:
  * `notes: List[Note]`, a list of all notes in this chord sorted by position (defined as starting at the same time as each other)
  * `position: Timestamp`, the start time off all notes in this chord.
  * `flag: str`, the flag on this chord (e.g.: `"hopo"`, `"tap"`), which all notes will have.
* `get_chords(start: TimeStamp, stop: TimeStamp) -> List[Chord]`, gets all the chords in a range of times, sorted by position.
* `get_notes(start: TimeStamp, stop: TimeStamp) -> List[Note]`, gets all the notes in a range of times, sorted by position.
* `get_events(start: TimeStamp, stop: TimeStamp, event_type: type = None) -> List[Even]`, gets all the events in a range of times, sorted by position, optionally of a certain type.

___
## Footnotes

[^1]: Can this not vary from chart to chart?

[^2]: Can this be a float?

[^3]: Well, not yet.

[^4]: This is kinda clunky.

[^5]: This might be changed to be more flexible?
