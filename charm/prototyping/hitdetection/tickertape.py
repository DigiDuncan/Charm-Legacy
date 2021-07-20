import random


class ChartEvent():
    def __init__(self, time, id):
        self.time = time
        self.id = id
        self.type = "demo"

    @property
    def end_time(self):
        return self.time + 75

    def __str__(self):
        return f"{self.id}: {self.time}-{self.end_time}"


def load_events():
    chart_events = []
    now = 0
    value = 0
    while now < 10000:
        now += random.randint(10, 60)
        value += 1
        chart_events.append(ChartEvent(now, value))
    return chart_events


def is_a_hit(event, input):
    return True


hit_events = {}
miss_events = {}


def process_input(time, events, strums, taps):
    print(f"{time}: " + ", ".join(str(e) for e in events))
    # Do something with chart events
    used_events = []
    for event in events:
        mode = event.type
        if mode == "hopo":
            if event.id - 1 in hit_events:
                mode = "tap"
            elif event.id - 1 in miss_events:
                mode = "strum"
            else:
                mode = "kraken"

        if mode == "tap":
            for tap in taps:
                if tap.used:
                    continue
            if is_a_hit(event, tap):
                tap.used = True
                used_events.append(event)
                hit_events[event.id] = event

        elif mode == "strum":
            for strum in strums:
                if strum.used:
                    continue
            if is_a_hit(event, strum):
                strum.used = True
                used_events.append(event)
                hit_events[event.id] = event

    for e in used_events:
        events.remove(e)


chart_events = load_events()

event_index = 0
active_events = []
active_strums = []
active_taps = []


def update(time, new_strums, new_taps):
    global event_index
    while event_index < len(chart_events) and chart_events[event_index].time <= time:
        active_events.append(chart_events[event_index])
        event_index += 1
    while active_events and active_events[0].end_time < time:
        active_events.pop(0)

    for s in new_strums:
        active_strums.append(s)
    while active_strums and active_strums[0].end_time < time:
        active_strums.pop(0)

    for t in new_taps:
        active_taps.append(t)

    while len(active_taps) > 1 and active_taps[1].time <= time:
        active_taps.pop(0)

    process_input(time, active_events, active_strums, active_taps)


def GO():
    now = 0
    while now < 10000:
        update(now, [], [])
        now += random.randint(5, 50)


GO()
