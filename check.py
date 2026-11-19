"""Level 1: rebuild every statistic, table and figure in the paper from the published event-level files.

No licensed data needed. It copies data/events and data/reviews into the working folders the code expects, runs
the statistics, the tables and the figures, and compares every statistic (value, N, p) and every table cell with
results/combined_results.json. Exit code 0 means everything matches.

    python check.py

Two inputs enter as published rather than rebuilt, because rebuilding them needs data this package cannot ship:
results/figure_series.json (aggregated daily and monthly paths; per-firm paths would expose licensed prices) and
results/pre1998_stats.json (read from proxy-statement graphs; see code/pre1998_tsr.py).
"""

import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
CODE, OUT, PAPER = ROOT / "code", ROOT / "outputs", ROOT / "paper"
STEPS = ["founder_final.py", "stats_returns.py", "stats_ops.py", "board_outcomes.py", "describe.py", "combine_results.py", "figures.py"]


def stage():
    (CODE / "out").mkdir(exist_ok=True)
    for f in (ROOT / "data" / "events").iterdir():
        shutil.copy(f, CODE / "out" / f.name)
    for f in (ROOT / "data" / "reviews").glob("*.csv"):
        shutil.copy(f, PAPER / f.name)
    (PAPER / "figdata").mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "results" / "figure_series.json", PAPER / "figdata" / "figure_series.json")
    OUT.mkdir(exist_ok=True)
    shutil.copy(ROOT / "results" / "pre1998_stats.json", OUT / "pre1998_stats.json")


def compare(published: dict, rebuilt: dict, tol: float = 1e-9) -> list[str]:
    def flat(p):
        return {s["stat_id"]: s for sec in p["sections"] for s in sec["statistics"]}

    a, b = flat(published), flat(rebuilt)
    bad = []
    for k, s in a.items():
        t = b.get(k)
        if t is None:
            bad.append(f"{k}: missing")
            continue
        for f in ("value", "n", "p", "t"):
            x, y = s.get(f), t.get(f)
            if (x is None) != (y is None) or (x is not None and abs(float(x) - float(y)) > tol * max(1.0, abs(float(x)))):
                bad.append(f"{k}.{f}: published {x}, rebuilt {y}")
    ta = {t["title"]: t["rows"] for sec in published["sections"] for t in sec["tables"]}
    tb = {t["title"]: t["rows"] for sec in rebuilt["sections"] for t in sec["tables"]}
    bad += [f"table differs: {k}" for k in ta if ta[k] != tb.get(k)]
    return bad


def main():
    stage()
    for step in STEPS:
        r = subprocess.run([sys.executable, "-W", "ignore", step], cwd=CODE, capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"{step} failed:\n{r.stderr[-3000:]}")
    published = json.loads((ROOT / "results" / "combined_results.json").read_text())
    rebuilt = json.loads((OUT / "combined_results.json").read_text())
    bad = compare(published, rebuilt)
    n = sum(len(s["statistics"]) for s in published["sections"])
    t = sum(len(s["tables"]) for s in published["sections"])
    print(f"{n} statistics and {t} tables checked, {len(bad)} differ; figures written to outputs/figures/")
    for b in bad[:30]:
        print("  ", b)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
