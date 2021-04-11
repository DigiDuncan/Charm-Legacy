from dataclasses import dataclass
from typing import List

from charm.prototyping.hitdetection.inputrecorder import InputRecorder
from charm.song import Chart


@dataclass
class ParsedInput:
    tick: int
    eventtype: str
    eventdata: str


class InputParser:
    def __init__(self, chart: Chart, inputrecorder: InputRecorder):
        self.chart = chart
        self.inputrecorder = inputrecorder

    @property
    def cleaned_inputs(self, *, start = None, stop = None):
        first_note_time = self.chart.song.tempo_calc.ticks_to_secs(self.chart.notes[0].tick_start)
        last_note_time = self.chart.song.tempo_calc.ticks_to_secs(self.chart.notes[-1].tick_start)

        # You can mess around before or after the notes.
        inputs = self.inputrecorder[first_note_time:last_note_time]

        # You can mess around during countdowns.
        for countdown_start, countdown_length in self.chart.countdowns.items():
            countdown_start_secs = self.chart.song.tempo_calc.ticks_to_secs(countdown_start)
            countdown_end_secs = self.chart.song.tempo_calc.ticks_to_secs(countdown_start + countdown_length)
            del inputs[countdown_start_secs:countdown_end_secs]

        current_state = {
            "green":     False,
            "red":       False,
            "yellow":    False,
            "blue":      False,
            "orange":    False,
            "strumup":   False,
            "strumdown": False,
            "start":     False,
            "select":    False,
            "tilt":      False,
            "whammy":    False,
        }
        last_state = None
        parsed_inputs: List[ParsedInput] = []

        for inp in inputs:
            ...
            parsed_inputs.append(self.calculate_input(last_state, current_state))
            last_state = current_state

        return parsed_inputs  # TODO: Not done.

    def calculate_input(self, last_state, current_state):
        return ParsedInput()
