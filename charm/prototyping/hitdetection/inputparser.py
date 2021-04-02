from typing import List

from charm.prototyping.hitdetection.inputrecorder import Input, InputRecorder
from charm.song import Chart


class InputParser:
    def __init__(self, chart: Chart, inputrecorder: InputRecorder):
        self.chart = chart
        self.inputrecorder = inputrecorder

    @property
    def cleaned_inputs(self, *, start, stop):
        first_note_time = self.chart.song.tempo_calc.ticks_to_secs(self.chart.notes[0].tick_start)
        last_note_time = self.chart.song.tempo_calc.ticks_to_secs(self.chart.notes[0].tick_start)

        inputs = self.inputrecorder[first_note_time:last_note_time]

        return inputs  # TODO: Not done.
