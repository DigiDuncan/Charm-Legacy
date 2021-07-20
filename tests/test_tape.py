from charm.lib.tape import BufferedTape, Tape


class Event:
    def __init__(self, name, start) -> None:
        self.start = start
        self.name = name

    def __repr__(self) -> str:
        return f"<{self.name}: {self.start}>"


events = [
    Event("one", 1),
    Event("two", 2),
    Event("three", 3)
]

chords = [
    Event("green", 1),
    Event("red", 2),
    Event("yellow", 3)
]


def test_tape():
    tape = Tape(events, "start")
    after_two = tape.get_items(2)
    assert after_two == events[:2]
    up_to_three = tape.get_items(3)
    assert up_to_three == [events[2]]
    nothing = tape.get_items(10)
    assert nothing == []


def test_bufferedtape():
    tape = BufferedTape(chords, "start", 1.1)
    tape.set_position(0)
    assert tape.current_items == [chords[0]]
    tape.set_position(1)
    assert tape.current_items == chords[:2]
    tape.set_position(5)
    assert tape.current_items == []


def test_taperewind():
    tape = Tape(events, "start")
    after_two = tape.get_items(2)
    assert after_two == events[:2]
    tape.jump_to(0)
    after_one = tape.get_items(1)
    assert after_one == events[:1]


def test_bufferedtaperewind():
    tape = BufferedTape(chords, "start", 1.1)
    tape.set_position(2)
    assert tape.current_items == chords
    tape.set_position(0)
    assert tape.current_items == chords[:1]
