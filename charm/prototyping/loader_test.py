from operator import itemgetter
from itertools import islice
from pathlib import Path
from traceback import format_exc
from typing import DefaultDict, Literal, Tuple

from tqdm import tqdm
import psutil

from charm.loaders import chchart
from charm.lib.nip import build_all, zip_all
from charm.lib.args import InvalidArgException, tryint


path_path = Path(".loaderpath")


def save_path(p):
    path_path.write_text(str(p))


def load_path():
    try:
        p_str = path_path.read_text()
        if p_str == "":
            raise FileNotFoundError
        p = Path(p_str)
    except FileNotFoundError:
        p = None
    return p


def ninput(prompt, *, default=None, default_label=None, converter=lambda a: a):
    if default is not None:
        if default_label is None:
            default_label = default
        prompt += f" [{default_label}]"
    prompt += " > "
    answer = input(prompt)
    if answer != "":
        answer = converter(answer)
    else:
        answer = default
    return answer


def input_path(*args, **kwargs):
    return ninput(*args, **kwargs, converter = lambda a: Path(a.strip('"')))


def input_int(*args, **kwargs):
    return ninput(*args, **kwargs, converter = int)


def get_input(chart_root=None, in_limit=None, in_filter=None) -> Tuple[Path, int, Literal["chart", "all"]]:
    """
    Gets user input for runtime options
    Optionally loads values from command-line arguments first
    If values were not set at command-line, then the user is prompted to enter a value
    """
    lastpath = load_path()

    # None is unset
    while chart_root is None:
        chart_root = input_path("Recursively search what directory for charts?", default=lastpath)
        if chart_root is not None and not chart_root.exists():
            print(f"Sorry, {chart_root} doesn't exist, try again.")
            chart_root = None

    save_path(chart_root)

    # None is unset, 0 is unlimited
    if in_limit is None:
        in_limit = input_int("Limit number of charts scanned to...", default=0, default_label="unlimited")

    # None is unset
    while in_filter is None:
        in_filter = ninput("Which suffixes do you want to parse? <chart/all>", default="chart")
        if in_filter not in ("chart", "all"):
            print(f"Sorry, {in_filter} is not valid, try 'chart' or 'all'.")
            in_filter = None

    return chart_root, in_limit, in_filter


def get_suffix(path):
    if path.suffix == ".chart":
        suffix = "chart"
    # midis are so old sometimes the extension is uppercase
    elif path.suffix.lower() in [".mid", ".midi"]:
        suffix = "mid"
    # .bak, .backup, .eof
    else:
        suffix = "other"
    return suffix


class DontBeNoneException(Exception):
    ...


def fqcn(o):
    """
    Get fully qualified class name
    """
    module = o.__class__.__module__
    if module is None or module == str.__class__.__module__:
        return o.__class__.__name__  # Avoid reporting __builtin__
    else:
        return f"{module}.{o.__class__.__name__}"


def process_charts(charts):
    print("\nProcessing charts...")

    bad_charts = []
    unparsed_metadata = set()
    counts = DefaultDict(int)

    p = psutil.Process()
    basemem = p.memory_info().rss
    try:
        t = tqdm(charts, unit = " charts")
        for n, chart_path in enumerate(t):
            suffix = get_suffix(chart_path)
            if suffix != "chart":
                counts[suffix] += 1
                continue

            try:
                with chart_path.open(encoding = "utf-8 sig") as f:
                    c = chchart.load(f)
                if c is None:
                    raise DontBeNoneException("Don't be None!")
            except KeyboardInterrupt as e:
                raise e
            except Exception as e:
                if isinstance(e, chchart.UnparsedMetadataException):
                    unparsed_metadata.update(e.keys)
                bad_charts.append((chart_path, fqcn(e), format_exc()))

            mem_used = p.memory_info().rss - basemem
            mem_per_chart = mem_used / (n + 1)
            t.set_postfix(Nemory=tqdm.format_sizeof(mem_used, "B", 1024), ChartCost=tqdm.format_sizeof(mem_per_chart, "B", 1024))
            counts[suffix] += 1
    except KeyboardInterrupt:
        print(f"CTRL-C received. Stopped processing after {max(counts.values())} charts.")
    return bad_charts, sorted(unparsed_metadata), counts.items()


def process_errors(bad_charts, chart_root):
    print("\nProcessing errors...")

    error_counts = DefaultDict(lambda: 0)
    raw_errors = []
    sources = {}
    full_errors = {}

    for (chart_path, e_type, e_stack) in tqdm(bad_charts, unit = " errors"):
        new_path = chart_path.parent.relative_to(chart_root)
        sources[" - ".join(new_path.with_suffix(".chart").parts)] = chart_path
        full_errors[" - ".join(new_path.with_suffix(".error").parts)] = e_stack

        raw_errors.append((new_path, e_type))
        error_counts[e_type] += 1
    error_counts = sorted(error_counts.items(), key=itemgetter(1), reverse=True)
    return raw_errors, error_counts, sources, full_errors


def gen_output(raw_errors, error_counts, counts, unparsed_metadata):
    print("\nGenerating output file...")

    total_count = sum(cnt for sfx, cnt in counts)
    chart_count = sum(cnt for sfx, cnt in counts if sfx != "other")

    if chart_count == 0:
        return f"No charts found out of {total_count} files."

    error_count = len(raw_errors)
    success_count = chart_count - error_count
    success_rate = success_count / chart_count

    lines = []

    lines.append("=== RAW ERRORS ===")
    lines += ([f'"{name}": {error}' for name, error in raw_errors] or ["No errors!"])

    lines.append("")
    lines.append("")
    lines.append("=== ERROR COUNT ===")
    lines += ([f"{err}: {cnt}" for err, cnt in error_counts] or ["No errors!"])

    lines.append("")
    lines.append("")
    lines.append("=== TOTALS ===")
    lines += [f"{sfx}s: {cnt}" for sfx, cnt in counts]

    lines.append("")
    lines.append("")
    lines.append("=== UNPARSED METADATA ===")
    lines += [key for key in unparsed_metadata] or ["All metadata has been parsed."]

    lines.append("")
    lines.append("")
    lines.append(f"Total Files: {total_count}")
    lines.append(f"Total Charts: {chart_count}")
    lines.append(f"Errors: {error_count}")
    lines.append(f"Success Rate: {success_rate:.3%}")

    return "\n".join(lines)


def run(chart_root: Path, in_limit: int, in_filter: Literal["chart", "all"]):
    # Clone Hero requires charts be named "notes.chart" or "notes.mid[i]."
    if in_filter == "chart":
        glob_filter = "notes.chart"
    else:
        glob_filter = "notes.*"
    print("\nCounting charts...")
    charts_iter = chart_root.rglob(glob_filter)
    if in_limit > 0:
        charts_iter = islice(charts_iter, in_limit)
    charts = list(tqdm(charts_iter, unit = " charts"))
    print(f"{len(charts)} charts found")

    bad_charts, unparsed_metadata, counts = process_charts(charts)
    raw_errors, error_counts, sources, full_errors = process_errors(bad_charts, chart_root)
    out = gen_output(raw_errors, error_counts, counts, unparsed_metadata)

    build_path = Path() / "build"
    build_all(build_path, copy = sources, create = full_errors | {"log.txt": out}, progress = True)

    # zip_path = Path() / "dist" / "output.zip"
    # zip_all(zip_path, copy = sources, create = full_errors | {"log.txt": out}, progress = True)


def check_args(path, limit, filter):
    if path is not None:
        path = Path(path)
        if not path.exists():
            raise InvalidArgException(f"Sorry, {path} doesn't exist")

    if limit is not None:
        if limit in ("unlimited", "none"):
            limit = 0
        limit = tryint(limit)
        if limit is None or limit < 0:
            raise InvalidArgException(f"Sorry, {limit} is not a valid limit, a positive integer or 'unlimited' or 'none'.")

    if filter is not None:
        if filter not in ("all", "chart"):
            raise InvalidArgException(f"Sorry, {filter} is not a valid filter, try 'chart' or 'all'.")

    return path, limit, filter


def main(*, path=None, limit=None, filter=None):
    chart_root, limit, filter = check_args(path, limit, filter)
    try:
        chart_root, in_limit, in_filter = get_input(chart_root=chart_root, in_limit=limit, in_filter=filter)
        run(chart_root, in_limit, in_filter)
    except KeyboardInterrupt:
        print("Goodbye")
