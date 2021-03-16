from operator import itemgetter
from itertools import islice
from pathlib import Path
from traceback import format_exc
from typing import DefaultDict

from tqdm import tqdm
import psutil

from charm.loaders import chchart
from charm.lib.nip import zip_all


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


SENTINEL = object()


def ninput(prompt, *, default=SENTINEL, default_label=None, converter=lambda a: a):
    if default is SENTINEL:
        default = None
    else:
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


def get_input():
    lastpath = load_path()
    path_kwargs = {}
    if lastpath is not None:
        path_kwargs["default"] = lastpath

    chart_root = None
    while chart_root is None:
        chart_root = input_path("Recursively search what directory for charts?", **path_kwargs)
        if chart_root is not None and not chart_root.exists():
            print(f"Sorry, {chart_root} doesn't exist, try again.")
            chart_root = None

    save_path(chart_root)
    in_limit = input_int("Limit number of charts scanned to...", default=None, default_label="unlimited")

    in_filter = None
    while in_filter is None:
        in_filter = ninput("Which suffixes do you want to parse? <chart/all>", default="chart")
        if in_filter not in ("chart", "all"):
            print(f"Sorry, {in_filter} is not valid, try 'chart' or 'all'.")
            in_filter = None

    return chart_root, in_limit, in_filter


def get_suffix(path):
    if path.suffix == ".chart":
        suffix = ".chart"
    # midis are so old sometimes the extension is uppercase
    elif path.suffix.lower() in [".mid", ".midi"]:
        suffix = ".mid"
    # .bak, .backup, .eof
    else:
        suffix = "other"
    return suffix


class DontBeNoneException(Exception):
    ...


def process_charts(charts):
    print("\nProcessing charts...")

    bad_charts = []

    counts = {
        ".chart": 0,
        ".mid": 0,
        "other": 0
    }
    p = psutil.Process()
    basemem = p.memory_info().rss

    t = tqdm(charts, unit = " charts")
    for n, chart_path in enumerate(t):
        suffix = get_suffix(chart_path)
        counts[suffix] += 1
        if suffix != ".chart":
            continue

        try:
            with chart_path.open(encoding = "utf-8 sig") as f:
                c = chchart.load(f)
            if c is None:
                raise DontBeNoneException("Don't be None!")
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            bad_charts.append((chart_path, type(e), format_exc()))
        mem_used = p.memory_info().rss - basemem
        mem_per_chart = mem_used / (n + 1)
        t.set_postfix(Nemory=tqdm.format_sizeof(mem_used, "B", 1024), ChartCost=tqdm.format_sizeof(mem_per_chart, "B", 1024))

    return bad_charts, counts


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

    return raw_errors, error_counts, sources, full_errors


def gen_output(raw_errors, error_counts, counts):
    print("\nGenerating output file...")

    lines = []
    lines.append("=== RAW ERRORS ===")
    if raw_errors:
        for name, error in raw_errors:
            lines.append(f"\"{name}\": {error}")
    else:
        lines.append("No errors!")

    lines.append("\n\n=== ERROR COUNT ===")
    if error_counts:
        for e, c in sorted(error_counts.items(), key=itemgetter(1), reverse=True):
            lines.append(f"{e}: {c}")
    else:
        lines.append("No errors!")

    lines.append("\n\n=== TOTALS ===")
    for n, c in counts.items():
        lines.append(f"{n}s: {c}")

    chart_count = sum(c for n, c in counts.items() if n != "other")
    total_count = sum(c for c in counts.values())
    error_count = len(raw_errors)
    success_count = chart_count - error_count
    if chart_count > 0:
        success_rate = success_count / chart_count
    else:
        success_rate = 1

    lines.append(f"Total Charts: {chart_count}")
    lines.append(f"Total: {total_count}")
    lines.append(f"Errors: {error_count}")
    lines.append(f"Success Rate: {success_rate:.3%}")

    return "\n".join(lines)


def run(chart_root, in_limit, in_filter):
    # Clone Hero requires charts be named "notes.chart" or "notes.mid[i]."
    if in_filter == "chart":
        glob_filter = "notes.chart"
    else:
        glob_filter = "notes.*"
    print("\nCounting charts...")
    charts_iter = islice(chart_root.rglob(glob_filter), in_limit)
    charts = list(tqdm(charts_iter, unit = " charts"))
    print(f"{len(charts)} charts found")

    bad_charts, counts = process_charts(charts)
    raw_errors, error_counts, sources, full_errors = process_errors(bad_charts, chart_root)
    out = gen_output(raw_errors, error_counts, counts)

    output_path = Path() / "dist" / "output.zip"
    zip_all(output_path, copy = sources, create = full_errors | {"log.txt": out}, progress = True)


def main():
    try:
        chart_root, in_limit, in_filter = get_input()
        run(chart_root, in_limit, in_filter)
    except KeyboardInterrupt:
        print("Goodbye")
