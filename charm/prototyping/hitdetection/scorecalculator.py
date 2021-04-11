from charm.song import Chart
from charm.prototyping.hitdetection.inputrecorder import InputRecorder


class ScoreCalculator:
    def __init__(self, chart: Chart, input_recorder: InputRecorder):
        self.chart = chart
        self.input_recorder = input_recorder

        self._score = 0
        self._previous_score = 0
        self.streak = 0
        self._sp_amount = 0
        self._sp_on = False

        self._calculating = False

    @property
    def score(self):
        return self._previous_score if self._calculating else self._score

    @property
    def multiplier(self):
        mult = 0
        if self.streak < 10:
            mult = 1
        elif 10 <= self.streak < 20:
            mult = 2
        elif 20 <= self.streak < 30:
            mult = 3
        elif 30 <= self.streak:
            mult = 4

        if self._sp_on:
            mult *= 2

        return mult

    def hit_note(self):
        self.streak += 1
        self._score += (50 * self.multiplier)
        self._calculating = False

    def miss_note(self):
        self.streak = 0
        self._calculating = False

    def update(self, tracktime):
        self._calculating = True
        self._previous_score = self._score

        # Reset the score every calculation
        self._score = 0
        self.streak = 0
        self._sp_amount = 0

        current_tick = self.chart.song.tempo_calc.secs_to_ticks(tracktime)
        for chord in self.chart.chord_by_ticks[:current_tick]:
            relevant_events = self.input_recorder[tracktime - 0.070:tracktime + 0.070]
            if chord.flag == "note":
                try:
                    strum = next((e for e in relevant_events if "strum" in e.events))
                except StopIteration:
                    self.miss_note()
                    return

                # One note strum, can be anchored
                if len(chord.frets) == 1:
                    note = chord.frets[0]
                    if note == 7 and strum.states["green"] is False and strum.states["red"] is False and strum.states["yellow"] is False and strum.states["blue"] is False and strum.states["orange"] is False:
                        self.hit_note()
                    elif note == 0 and strum.states["green"] is True and strum.states["red"] is False and strum.states["yellow"] is False and strum.states["blue"] is False and strum.states["orange"] is False:
                        self.hit_note()
                    elif note == 1 and strum.states["red"] is True and strum.states["yellow"] is False and strum.states["blue"] is False and strum.states["orange"] is False:
                        self.hit_note()
                    elif note == 2 and strum.states["yellow"] is True and strum.states["blue"] is False and strum.states["orange"] is False:
                        self.hit_note()
                    elif note == 3 and strum.states["blue"] is True and strum.states["orange"] is False:
                        self.hit_note()
                    elif note == 4 and strum.states["orange"] is True:
                        self.hit_note()

                else:
                    shape = [
                        0 in chord.frets,
                        1 in chord.frets,
                        2 in chord.frets,
                        3 in chord.frets,
                        4 in chord.frets
                    ]

                    held_chord = [
                        strum.states["green"],
                        strum.states["red"],
                        strum.states["yellow"],
                        strum.states["blue"],
                        strum.states["orange"]
                    ]

                    if shape == held_chord:
                        self.hit_note()
                    else:
                        self.miss_note()
