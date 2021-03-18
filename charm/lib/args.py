def tryint(s, *, default=None):
    try:
        return int(s)
    except (ValueError, TypeError):
        return default


class InvalidArgException(Exception):
    pass
