import re
from pathlib import Path
from traceback import format_exc
from typing import DefaultDict
from zipfile import ZipFile, ZIP_DEFLATED

import chparse
import tqdm


def zip_all(dst, *, copy=None, create=None):
    if copy is None:
        copy = {}
    if create is None:
        create = {}
    with ZipFile(dst, mode="w", compression=ZIP_DEFLATED) as z:
        print("Copying files to zip...")
        for newname, srcpath in tqdm.tqdm(copy.items(), unit = " files"):
            data = Path(srcpath).read_bytes()
            z.writestr(newname, data)
        print("Writing logs to zip...")
        for newname, data in tqdm.tqdm(create.items(), unit = " files"):
            z.writestr(newname, data)


chart_root = Path(input("Recursively search what directory for charts? > "))
in_limit = input("Limit number of charts scanned to... (hit ENTER for no limit) > ")
if in_limit:
    in_number = in_limit
    in_limit = int(in_limit)
else:
    in_number = input("How many charts are you expecting? (hit ENTER for unknown) > ")
    in_limit = None
    if in_number == "":
        in_number = None
    else:
        in_number = int(in_number)

charts = chart_root.rglob("notes.*")  # Clone Hero requires charts be named "notes.chart" or "notes.mid[i]."

bad_charts = []
bad_charts_expanded = {}

i = 0

chart_c = 0
mid_c = 0
other_c = 0

print("Processing charts...")
for chart_path in tqdm.tqdm(charts, unit = " charts", total = in_number):
    i += 1
    if in_limit is not None and i > in_limit:
        break
    if chart_path.suffix.lower() in [".mid", ".midi"]:  # midis are so old sometimes the extension is uppercase
        mid_c += 1
    elif chart_path.suffix == ".chart":
        chart_c += 1
        try:
            with chart_path.open(encoding = "utf-8 sig") as f:
                c = chparse.parse.load(f)
            if c is None:
                raise ValueError("Don't be None!")
        except Exception as e:
            bad_charts.append((chart_path, e, format_exc()))
    else:  # .bak, .backup, .eof
        other_c += 1

error_counts = DefaultDict(lambda: 0)
raw_errors = []
sources = {}
full_errors = {}

print("\nProcessing errors...")
for (chart_path, e, exp) in tqdm.tqdm(bad_charts.items(), unit = " errors"):
    new_path = chart_path.parent.relative_to(chart_root)
    sources[new_path + ".chart"] = c
    full_errors[new_path + ".error"] = exp

    raw_errors.append((new_path, type(e)))
    error_counts[type(e)] += 1

print("\nGenerating output file...")

out = ""
out += ("=== RAW ERRORS ===\n")
for name, error in raw_errors:
    out += (f"\"{name}\": {error}\n")
if not raw_errors:
    out += ("No errors!\n")
out += ("\n\n=== ERROR COUNT ===\n")
for e in sorted(error_counts, key=error_counts.get, reverse=True):
    out += (f"{e}: {error_counts[e]}\n")
if not error_counts:
    out += ("No errors!\n")
out += ("\n\n=== TOTALS ===\n")
out += (f".charts: {chart_c}\n"
        f".mids: {mid_c}\n"
        f"Others: {other_c}\n"
        f"Total Charts: {chart_c + mid_c}\n"
        f"Total: {chart_c + mid_c + other_c}\n"
        f"Errors: {len(raw_errors)}\n"
        f"Success Rate: {round((chart_c + mid_c - len(raw_errors)) / (chart_c + mid_c) * 100, 3)}%")

zip_all("output.zip", copy = sources, create = full_errors | {"log.txt": out})
