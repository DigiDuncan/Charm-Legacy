from pathlib import Path

import chparse
import tqdm

charts = Path("F:/chs").rglob("notes.*")

bad_charts = {}
limit = None

i = 0

chart_c = 0
mid_c = 0
other_c = 0

for chart in tqdm.tqdm(charts, unit = " charts", total = 18600):
    i += 1
    if limit is not None and i > limit:
        break
    if chart.suffix == ".mid" or chart.suffix == ".midi":
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
    else:
        other_c += 1

errors = {}
raw_errors = {}

for c, e in tqdm.tqdm(bad_charts.items()):
    raw_errors[c] = str(e)
    if str(e) in errors.keys():
        errors[str(e)] += 1
    else:
        errors[str(e)] = 1
print(raw_errors)
print(errors)
print(f".charts: {chart_c}\n.mids: {mid_c}\nOthers: {other_c}\nTotal Charts: {chart_c + mid_c}\nTotal: {chart_c + mid_c + other_c}")
