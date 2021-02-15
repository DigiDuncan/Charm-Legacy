import re
from pathlib import Path
from traceback import format_exc
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


in_path = Path(input("Recursively search what directory for charts? > "))
in_limit = input("Limit number of charts scanned to... (hit ENTER for no limit) > ")
if in_limit != "":
    in_number = int(in_limit)
    in_limit = int(in_limit)
else:
    in_number = input("How many charts are you expecting? (hit ENTER for unknown) > ")
    in_limit = None
    if in_number == "":
        in_number = None
    else:
        in_number = int(in_number)

charts = in_path.rglob("notes.*")  # Clone Hero requires charts be named "notes.chart" or "notes.mid[i]."

bad_charts = {}
bad_charts_expanded = {}

i = 0

chart_c = 0
mid_c = 0
other_c = 0

print("Processing charts...")
for chart in tqdm.tqdm(charts, unit = " charts", total = in_number):
    i += 1
    if in_limit is not None and i > in_limit:
        break
    if chart.suffix.lower() in [".mid", ".midi"]:  # midis are so old sometimes the extension is uppercase
        mid_c += 1
    elif chart.suffix == ".chart":
        chart_c += 1
        try:
            with chart.open(encoding = "utf-8 sig") as f:
                c = chparse.parse.load(f)
            if c is None:
                raise ValueError("Don't be None!")
        except Exception as e:
            bad_charts[str(chart.absolute())] = e
            bad_charts_expanded[str(chart.absolute())] = format_exc()
    else:  # .bak, .backup, .eof
        other_c += 1

errors = {}
raw_errors = {}
sources = {}
full_errors = {}

print("\nProcessing errors...")
for c, e in tqdm.tqdm(bad_charts.items(), unit = " errors"):
    full_path = Path(c)
    new_path = " - ".join(c.parent.relative_to(full_path).parts)
    sources[f"{new_path}.chart"] = c
    full_errors[f"{new_path}.error"] = bad_charts_expanded[c]

    raw_errors[new_path] = type(e)
    if type(e) in errors.keys():
        errors[type(e)] += 1
    else:
        errors[type(e)] = 1

print("\nGenerating output file...")

out = ""
out += ("=== RAW ERRORS ===\n")
for name, error in raw_errors.items():
    out += (f"\"{name}\": {error}\n")
if raw_errors == {}:
    out += ("No errors!\n")
out += ("\n\n=== ERROR COUNT ===\n")
for e in sorted(errors, key=errors.get, reverse=True):
    out += (f"{e}: {errors[e]}\n")
if errors == {}:
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
