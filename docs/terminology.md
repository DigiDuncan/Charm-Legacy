# Song
`.chart` files contain "Songs."

# Block
```
[HEADER]                # Block Header
{
    ??? = ???           # Block Element
    {TICKS} = ???       # Song Element
}
```

# Elements
```
{KEY} = {VALUE}             # Metadata Element
{TICKS} = N {F} {L}         # Note Element
{TICKS} = E {TEXT}          # Event Element
{TICKS} = B {MBPM}          # Tempo Element
{TICKS} = A {MBPM}          # Anchor Element
{TICKS} = TS {NUM} {DENOM}  # Time Signature Element
{TICKS} = TS {NUM}          # Time Signature Element
```

# Metadata Block
```
[Song]
    {KEY} = {VALUE}         # Metadata Element
```

# Chart Blocks
```
[DifficultyInstrument]
    {TICKS} = N {F} {L}               # Note (F in [0,1,2,3,4,7])
                 ^                    # Fret
                     ^                # Length
    {TICKS} = N  5   0                # HOPO Flag (Hammer-Ons and Pull-Offs)
    {TICKS} = N  6   0                # Tap Flag

    {TICKS} = S  2  {L}               # Star Power Phrase
    {TICKS} = E solo                  # Solo Event Start
    {TICKS} = E soloend               # Solo Event End
```

# Chord
```
Chord           # Group of notes that share the same TICKS
Chord Frets     # List of frets held down by chord notes
Chord Flag      # Flag that affects this chord (Tap/Hopo/Note in priority order)
Chord Length    # Length of longest note in chord
```

## Frets
```
0   # Green
1   # Red
2   # Yellow
3   # Blue
4   # Orange
7   # Open
```

# SyncTrack Block
```
[SyncTrack]
    {TICKS} = B {MBPM}          # Tempo
    {TICKS} = A {MBPM}          # Anchor Tempo
    {TICKS} = TS {NUM} {DENOM}  # Time Signature (NUM / DENOM)
    {TICKS} = TS {NUM}          # Time Signature (NUM / 4)
```

## Time Signatures
Measure bars display on screen according to the Time Signature

# Events Block
```
[Events]
    Lyric Elements                  # See "Lyrics in Events Block"
    {TICKS} = E "section {NAME}"    # Section
    {TICKS} = E {???}               # More bullshit
```

# Lyrics

## Lyrics in Events Block
```
[Events]
    {TICKS} = E "phrase_start"      # Lyric Phrase Start
    {TICKS} = E "phrase_end"        # Lyric Phrase End
    {TICKS} = E "lyric {WORD}"      # Lyric Word
    {TICKS} = E "lyric {WORD}-"     # Lyric Partial Word
```

## Lyrics in Lyrics Block
```
[PART VOCALS]
    {TICKS} = N 105 {L}     # Lyric Phrase
    {TICKS} = N 106 {L}     # Lyric Phrase (also)
    {TICKS} = N {P} {L}     # Lyric Word Prefix
                 ^          # Pitch (36-84)
    {TICKS} = E "{WORD}"    # Lyric Word
    {TICKS} = N {???} {L}   # Lyric bullshit
```

## Special characters
```
-   # Partial Word
=   # Translates directly to '-'
+   # Pitch shift
#   # Freestyle
^   # Freestyle (more relaxed)
%   # ???
```
