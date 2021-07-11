# Charm (Gamemode)
This document aims to describe the *Charm* gamemode, a gamemode derived from [*Guitar Hero*](guitar-hero.md), but adapted to be more arcade-y and have additional features. As of such, reading that document first (or a pre-existing knowledge of the gamemode) are essentially required.

## First, Some Technical Notes
*Charm* plans to use `.chart` files, and as of such utilizes events. Some of these events, `N` events, use integers as flags to denote things like fret type and note flags. As per the [`.chart` specification](https://docs.google.com/document/d/1v2v0U-9HQ5qHeccpExDOLJ5CMPZZ3QytPmAG5WF0Kzs/edit), *Charm* plans to reserve block `N 255` through `N 287`, using `N 255` - `N 271` for new frets as they arise, and `N 272` - `N 287` for new note flags.

*Charm* gamemode charts should probably mark that they are such using `Charm = true` in the `[Song]` header, or similar, so that we don't try to load GH/CH charts as *Charm* mode charts, or vice versa. (*Clone Hero* will likely have no clue what to do with our notes but might be able to load the chart in a broken state which would suck for everyone.)

Also, it should be noted that *Charm* uses the term "Charm Power" over "Star Power", though they are functionally the same thing.

## New Kinds Of Notes

*Charm* mode adds a few new kinds of notes. Many of these notes should be used as spice for charts; a little thrown in could make a chart a lot of fun, too much and you have an unplayable mess or worse.

### Slap Notes (Whammy Notes)
Slap notes (`N 255`) are a new "fret" altogether, utilizing the whammy bar of the guitar controller as a meaningful input. To activate a slap note, the player depresses the whammy bar beyond some threshold. To activate another one afterward, the whammy bar must have been let go during the interim.

Due to the activation method, "Tap" or "HOPO" slap notes are invalid, as are most other modifiers (other than Charm Power.)

Slap notes appear visually as white and yellow, thin bars across the entire highway, like an open note but thinner.

### Directional Notes (Up-Notes and Down-Notes)
Up-Notes and Down-Notes (`N 272` and `N 273` flags, respectively) are notes that must be strummed in that direction or fail activation.

These can not be mixed with the "Tap" or "HOPO" flags, as in some or all cases, those notes are not strummed at all. Though in theory a HOPO directional note *could* make sense (in that when it's required to strum the note, you'd have to do so in the indicated direction,) it'd be terrible to play and confusing, so support isn't planned.

They visually appear as similar to their standard note counterparts, but in the shape of an arrow pointing up or down.

### "Bomb"<sup id="a2">[2](#f2)</sup> Notes
Bomb Notes (`N 274` flag) denote a note that if hit, breaks your combo. These notes should be avoided. They are activated the same way as tap notes. They visually appear as large colored Xs.

### Fake Notes
Fake Notes (`N 275` flag) are notes that are not real. There is no penalty for not hitting them, and no gain for hitting them. They do not add to combo and are strictly visual. They are rendered under all other notes and appear as the original note but in grayscale.

## New Kinds Of Events
Other than modchart events (pending), *Charm* adds a couple new events that modify gameplay.

### Precision Section
A "precision section" of a chart (`E precision_start` and `E precision_end`) denotes a time in which the hit window of the engine decreases, making note timing more difficult.

This is shown visually by the highway tinting red during this time.<sup id="a1">[1](#f1)</sup>

### Loose Section
A "loose section" of a chart (`E loose_start` and `E loose_end`) denotes a time in which the hit window of the engine increases, making note timing easier.

This is shown visually by the highway tinting green during this time.<sup id="a1">[1](#f1)</sup>

<hr />

## Footnotes
<b id="f1">1</b>: This might need to be changed to suit colorblind people, or at least get a secondary visual indicator. Also might look dumb with custom highways? A lot to think about here.[↩](#a1)

<b id="f2">2</b>: Name not final. [↩](#a2)
