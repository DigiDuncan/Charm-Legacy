from enum import Enum


class Mode(Enum):
    LyricAnimator = Default = "lyrics"
    BulkTest = "bulk"
    SingleTest = "single"
    ListCharts = "charts"


def trymode(s, *, default=None):
    try:
        return Mode(s)
    except ValueError:
        return default


def tryint(s, *, default=None):
    try:
        return int(s)
    except (ValueError, TypeError):
        return default


def trypop(items, *, default=None):
    try:
        return items.pop(0)
    except IndexError:
        return default


class InvalidArgException(Exception):
    pass


def get_mode(args):
    """
    Gets mode from first argument, using Mode enum
    Defaults to LyricAnimator
    Raises an InvalidArgException is a bad mode argument is provided
    """

    # Try to get next arg. If none available, then get default mode.
    # Try to match the arg to the mode. If we don't match, complain and return None.
    arg = trypop(args, default=Mode.Default)
    mode = trymode(arg)

    if mode is None:
        valid_modes = " / ".join(m.value for m in Mode)
        raise InvalidArgException(
            f"Unrecognized mode: {arg!r}\n"
            f"Please use one of the following modes: {valid_modes}."
        )

    return mode


def get_selected_chart(args, chart_cnt):
    """
    Gets the index of the selected chart in Single mode
    Defaults to first chart
    """
    arg = trypop(args, default="1")
    i = tryint(arg)

    if i is None or not (1 <= i <= chart_cnt):
        raise InvalidArgException(
            f"Invalid chart selection: {arg!r}\n"
            f"Please enter a number between 1-{chart_cnt} or use 'charts' to list all available charts."
        )

    return i
