from typing import List
from charm.song import Chart
from charm.prototyping.hitdetection.inputrecorder import InputRecorder
from nygame import Index


class ScoreCounter:
    def __init__(self):
        self.score = 0
        self.streak = 0
        self._sp_amount = 0
        self._sp_on = False

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
        self.score += (50 * self.multiplier)

    def miss_note(self):
        self.streak = 0


class ScoreCalculator:
    def __init__(self, chart: Chart, input_recorder: InputRecorder):
        self.chart = chart
        self.input_recorder = input_recorder

    def get_score(self, tracktime):
        # Reset the score every calculation
        counter = ScoreCounter()
        inputs = InputTracker(self.input_recorder.inputs)

        current_tick = self.chart.song.tempo_calc.secs_to_ticks(tracktime)

        for chord in self.chart.chord_by_ticks[:current_tick]:
            if chord.flag != "note":
                continue
            chord_min = chord.start - 0.07
            chord_max = chord.start + 0.07

            inputs.update(chord_min, chord_max)

            if is_hit(inputs.active, chord):
                counter.hit_note()
            else:
                counter.miss_note()

        return counter.score


class InputTracker:
    def __init__(self, inputs):
        self.inputs = iter(inputs)
        self.active = []
        self.next_input = None
        self.next()

    def next(self):
        try:
            self.next_input = next(self.inputs)
        except StopIteration:
            self.next_input = None

    def update(self, min, max):
        # Remove stale inputs
        while self.active and self.active[0].start < min:
            del self.active[0]

        # Fetch new inputs
        while self.next_input and self.next_input.start <= max:
            if "strum_on" in self.next_input.events:
                self.active.append(self.next_input)
            self.next()


def is_hit(active_inputs, chord):
    if not active_inputs:
        return False

    shape = [
        0 in chord.frets,
        1 in chord.frets,
        2 in chord.frets,
        3 in chord.frets,
        4 in chord.frets
    ]

    for i, strum in enumerate(active_inputs):
        # One note strum, can be anchored
        held_chord = [
            strum.state["green"],
            strum.state["red"],
            strum.state["yellow"],
            strum.state["blue"],
            strum.state["orange"]
        ]
        if len(chord.frets) == 1:
            held_chord = anchor_chord(held_chord)

        if shape == held_chord:
            del active_inputs[i]
            return True

    return False


def anchor_chord(frets):
    anchored = []
    for f in frets[::-1]:
        if any(anchored):
            f = False
        anchored.insert(0, f)
    return anchored
