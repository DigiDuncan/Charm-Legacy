from nindex import Index
from charm.song import Chart, TempoCalculator
from charm.lib.instruments.guitar import Guitar


class TempoTape:
    def __init__(self, index: Index, tempo_calc: TempoCalculator, scanner_width: float) -> None:
        self._index = index
        self._tempo_calc = tempo_calc
        self.scanner_width = scanner_width

        self.current_position = 0  # seconds

        self.current_items = []
        self.dirty_ids = []

    @property
    def timeslice(self):
        offset = self.scanner_width / 2
        end = self._tempo_calc.secs_to_ticks(self.current_position + offset)
        start = self._tempo_calc.secs_to_ticks(self.current_position - offset)
        start = max(0, start)
        return slice(start, end, 1)

    def scan(self):
        self.current_items = self._index[self.timeslice]
        self.current_items = [i for i in self.current_items if i.id not in self.dirty_ids]

    def set_position(self, position: float):
        self.current_position = position

    def scroll(self, amount: float):
        self.current_position += amount


class ScoreCalculator:
    def __init__(self, chart: Chart, guitar: Guitar):
        self.chart = chart
        self.song = self.chart.song
        self.guitar = guitar
        self._hitwindow = 0.140

        self.chord_tape = TempoTape(self.chart.chord_by_ticks, self.song.tempo_calc, self._hitwindow)

        self._events = []

        self.score = 0
        self.streak = 0
        self.accuracies = []
        self.multiplier = 1

    def update(self, time):
        pass

# --- EVENTS ---


class ScoreEvent:
    def __init__(self, ticks: int):
        self.ticks = ticks

    def __lt__(self, other):
        self.ticks < other.ticks

    def __eq__(self, other):
        self.ticks == other.ticks

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self.ticks}>"


class AccurateScoreEvent(ScoreEvent):
    def __init__(self, ticks: int, target: int):
        super().__init__(ticks)
        self.target = target

    @property
    def offset(self):
        return self.ticks - self.target


class ChordMissed(ScoreEvent):
    def __init__(self, ticks: int):
        super().__init__(ticks)


class ChordHit(AccurateScoreEvent):
    def __init__(self, ticks: int, target: int):
        super().__init__(ticks, target)


class SustainBreak(ScoreEvent):
    def __init__(self, ticks: int):
        super().__init__(ticks)


class StarPowerActivate(ScoreEvent):
    def __init__(self, ticks: int):
        super().__init__(ticks)


class ExtraneousInput(ScoreEvent):
    def __init__(self, ticks: int):
        super().__init__(ticks)
