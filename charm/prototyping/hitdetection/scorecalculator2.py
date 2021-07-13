from charm.song import Chart
from charm.lib.instruments.guitar import Guitar


class ScoreCalculator:
    def __init__(self, chart: Chart, guitar: Guitar):
        self.chart = chart
        self.song = self.chart.song
        self.guitar = guitar

        self._hitwindow = 0.140
        self.hitwindow = self.song.tempo_calc.secs_to_ticks(self._hitwindow)

        self._events = []

# --- EVENTS ---


class ScoreEvent:
    def __init__(self, ticks: int):
        self.ticks = ticks

    def __lt__(self, other):
        self.ticks < self.ticks

    def __eq__(self, other):
        self.ticks == self.ticks

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
