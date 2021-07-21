from charm.lib.utils import findindex


def test_findindex():
    items = [1, 2, 3, 4, 5, 6]
    assert findindex(items, lambda i: i > 4) == 4
    assert findindex(items, lambda i: i == "number") is None
