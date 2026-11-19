"""Level 2: rebuild the event-level files from your own licensed data, then every statistic, and compare with ours.

1. Build the canonical tables in data/inputs (see DATA.md), for example:
       cd code && python -m adapters.gentry && python -m adapters.french
       cd code && python -m adapters.sharadar /path/to/sharadar_exports      # or
       cd code && python -m adapters.crsp_compustat /path/to/wrds_exports
   data/inputs already holds the free tables gentry, gvkey_cik, wikidata_founders and sec_filings.
2. python run_level2.py

It runs build_events, event_study, paths and ops_matched on your data (FCE_DATA_SOURCE=files), takes the published
codes and hand reviews (the language-model coding is Level 3 and optional), rebuilds the statistics, tables and
figure series, and reports how close your event-level returns and headline statistics are to ours. With Sharadar the
match is exact; with CRSP and Compustat expect small differences (different price adjustments, delisting dates and
matched firms) and the same conclusions.
"""

import json
import os
import pathlib
import shutil
import subprocess
import sys

import numpy as np
import pandas as pd

from check import compare

ROOT = pathlib.Path(__file__).resolve().parent
CODE, OUT, PAPER = ROOT / "code", ROOT / "outputs", ROOT / "paper"
BUILD = ["build_events.py", "event_study.py", "paths.py", "ops_matched.py"]
STATS = ["founder_final.py", "stats_returns.py", "stats_ops.py", "board_outcomes.py", "describe.py", "figure_series.py",
         "combine_results.py", "figures.py"]
HEADLINE = ["car.forced.mm_m1p1.mean", "car.forced_founder.mm_m1p1.mean", "car.conduct.mm_m1p1.mean",
            "car.financial_misconduct.mm_m1p1.mean", "drift.forced.pre_m30m2.mean", "mbhar.forced.3y.median",
            "exit.forced.delisted_5y", "board.forced.director_turnover.mean"]


def run(steps):
    env = {**os.environ, "FCE_DATA_SOURCE": "files", "FCE_DATA_DIR": str(ROOT / "data" / "inputs")}
    for step in steps:
        print("running", step, flush=True)
        r = subprocess.run([sys.executable, "-W", "ignore", step], cwd=CODE, env=env, capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"{step} failed:\n{r.stderr[-3000:]}")


def main():
    (CODE / "out").mkdir(exist_ok=True)
    run(BUILD)
    for name in ("event_coding_final.jsonl", "board_raw.jsonl", "pre1998_tsr.parquet"):
        shutil.copy(ROOT / "data" / "events" / name, CODE / "out" / name)
    for f in (ROOT / "data" / "reviews").glob("*.csv"):
        shutil.copy(f, PAPER / f.name)
    (PAPER / "figdata").mkdir(parents=True, exist_ok=True)
    OUT.mkdir(exist_ok=True)
    shutil.copy(ROOT / "results" / "pre1998_stats.json", OUT / "pre1998_stats.json")
    run(STATS)
    ours = pd.read_parquet(ROOT / "data" / "events" / "returns.parquet")[["event_id", "car_mm_m1p1", "bhar_3y"]]
    yours = pd.read_parquet(CODE / "out" / "returns.parquet")[["event_id", "car_mm_m1p1", "bhar_3y"]]
    m = ours.merge(yours, on="event_id", suffixes=("_ours", "_yours"))
    print(f"\nevents with returns: ours {len(ours):,}, yours {len(yours):,}, both {len(m):,}")
    for c in ("car_mm_m1p1", "bhar_3y"):
        a, b = m[f"{c}_ours"], m[f"{c}_yours"]
        ok = a.notna() & b.notna()
        print(f"{c}: correlation {np.corrcoef(a[ok], b[ok])[0, 1]:.4f}, median absolute difference {np.median(np.abs(a[ok] - b[ok])):.5f}")
    published = json.loads((ROOT / "results" / "combined_results.json").read_text())
    rebuilt = json.loads((OUT / "combined_results.json").read_text())
    flat = lambda p: {s["stat_id"]: s for sec in p["sections"] for s in sec["statistics"]}  # noqa: E731
    a, b = flat(published), flat(rebuilt)
    print("\nheadline statistic                              ours        yours")
    for k in HEADLINE:
        print(f"  {k:44s} {a[k]['formatted']:>9s}   {b.get(k, {}).get('formatted', 'n/a'):>9s}")
    bad = compare(published, rebuilt, tol=1e-6)
    print(f"\n{len(bad)} of {len(a)} statistics differ from ours beyond 1e-6 (expected with a different vendor; zero with Sharadar)")


if __name__ == "__main__":
    main()
