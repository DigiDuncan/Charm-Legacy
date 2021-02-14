from pathlib import Path

import chparse
import tqdm

in_path = input("Recursively search what directory for charts? > ")
in_limit = input("Limit number of charts scanned to... (hit ENTER for no limit) > ")
if in_limit:
    in_number = in_limit
else:
    in_number = input("How many charts are you expecting? > ")

in_limit = int(in_limit)
in_number = int(in_number)

charts = Path(in_path).rglob("notes.*")  # Clone Hero requires charts be named "notes.chart" or "notes.mid[i]."

bad_charts = {}

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
    else:  # .bak, .backup, .eof
        other_c += 1

errors = {}
raw_errors = {}

print("\nProcessing errors...")
for c, e in tqdm.tqdm(bad_charts.items(), unit = " errors"):
    raw_errors[c] = str(e)
    if str(e) in errors.keys():
        errors[str(e)] += 1
    else:
        errors[str(e)] = 1

# Print the errors
print("\n=== RAW ERRORS ===")
for name, error in raw_errors.items():
    print(f"{name}: {error}")
if raw_errors == {}:
    print("No errors!")
print("\n=== ERROR COUNT ===")
for e in sorted(errors, key=errors.get, reverse=True):
    print(f"{e}: {errors[e]}")
if errors == {}:
    print("No errors!")
print("\n=== TOTALS ===")
print(f".charts: {chart_c}\n.mids: {mid_c}\nOthers: {other_c}\nTotal Charts: {chart_c + mid_c}\nTotal: {chart_c + mid_c + other_c}\nErrors: {len(raw_errors)}")
