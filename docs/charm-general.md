# Charm: General Documentation

## Accuracy Mode
Certain gamemodes in *Charm* don't count accuracy by default, but they all have the option to turn on or off **Accuracy Mode**. Accuracy mode adds two key features, [Judgements](#judgements) and [Grades](grades).

Along with Accuracy Mode, *Charm* will have a seperate mode (name TBD), which shows Judgements and Grades to the player, but without affecting score.

### Judgements
As you play, very note you hit falls within a certain *hit window*. Depending on how close to 0ms (or rather, the notes optimal hit time) your hit lands, depends on how well it's judged. Different judgements give certain point values.

The following table assumes a ±70ms hit window, the default for *Guitar Hero* gamemode. However, the percentage of the window each judgement fills is the same for each gamemode (by default, they can be modified by the user and loaded into presets.)

| Name                       | Sprite | ±ms (min) | ±ms (max) | ±%              | Percent Range | Points |
|----------------------------|--------|-----------|-----------|-----------------|---------------|--------|
| Charming! (Super Charming) |<img src="../charm/data/images/judgements/supercharming.png" alt="Super Charming" width="64"/>| 0         | 10        | 0% / 14.29%     | 14.29%        | 1000   |
| Charming                   |<img src="../charm/data/images/judgements/charming.png" alt="Charming" width="64"/>| 10        | 25        | 14.29% / 35.71% | 21.43%        | 1000   |
| Excellent                  |<img src="../charm/data/images/judgements/excellent.png" alt="Excellent" width="64"/>| 25        | 35        | 35.71% / 50%    | 14.29%        | 800    |
| Great                      |<img src="../charm/data/images/judgements/great.png" alt="Great" width="64"/>| 35        | 45        | 50% / 64.29%    | 14.29%        | 600    |
| Good                       |<img src="../charm/data/images/judgements/good.png" alt="Good" width="64"/>| 45        | 60        | 64.29% / 85.71% | 21.43%        | 400    |
| OK                         |<img src="../charm/data/images/judgements/ok.png" alt="OK" width="64"/>| 60        | 70        | 85.71% / 100%   | 14.29%        | 200    |
| Miss                       |<img src="../charm/data/images/judgements/miss.png" alt="Miss" width="64"/>| 70        | Inf       | N/A             | N/A           | 0      |

Here's a visualization of the above window:

![Hit window, visualized.](images/hit_window.png)

### Grades
At the end of the song, you are given a grade, a letter representing how well you did in the song.

The percent value (PV) used to determine your grade is calculated by the formula `final_score / total_possible_score`, where `total_possible_score` would be the score if the user had hit all the notes in the song with `Charming!` and never broke combo (including overstrums, etc.), but ignoring multiplier, star power (or equivalent), and sustain breaks.

`final_score` also is calculated as if multipliers, star power, sustain breaks, etc. did not factor in.

| Grade | Sprite                                                            | PV   |
|-------|-------------------------------------------------------------------|------|
| SS    |<img src="../charm/data/images/grades/SS.png" alt="SS" width="32"/>| 100% |
| S     |<img src="../charm/data/images/grades/S.png" alt="S" width="32"/>  | >95% |
| A     |<img src="../charm/data/images/grades/A.png" alt="A" width="32"/>  | >90% |
| B     |<img src="../charm/data/images/grades/B.png" alt="B" width="32"/>  | >80% |
| C     |<img src="../charm/data/images/grades/C.png" alt="C" width="32"/>  | >70% |
| D     |<img src="../charm/data/images/grades/D.png" alt="D" width="32"/>  | >60% |
| F     |<img src="../charm/data/images/grades/F.png" alt="F" width="32"/>  | <60% |

## Full Combo
Full Combo is a seperate system for both [Judgements](#judgements) and [Grades](grades), and enabled regardless of [Accuracy Mode](#accuracy-mode). If a player hits every note in the song, and never breaks combo (what this means varies by game type), the player has "FC'd" the song, and an FC icon appears on that song. They are let know of this on the stats screen after the song.
