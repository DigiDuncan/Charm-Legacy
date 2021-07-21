from charm.prototyping.hitdetection.scorecalculator import anchored_shape


def test_anchor_gry():
    assert anchored_shape((True, True, True, False, False)) == 2


def test_anchor_none():
    assert anchored_shape((False, False, False, False, False)) is None


def test_anchor_gyo():
    assert anchored_shape((True, False, True, False, True)) == 4
