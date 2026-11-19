"""Rebuild every statistic from the files in data/ and compare with results/combined_results.json.

Run: python check.py   (needs pandas, numpy, scipy, statsmodels, pyarrow)
It copies data/ into code/out/, runs founder_final, stats_returns, stats_ops, board_outcomes and
combine_results, then checks that every statistic matches the published payload to 1e-9.
"""
import json, pathlib, shutil, subprocess, sys

ROOT = pathlib.Path(__file__).parent
OUT = ROOT / "code" / "out"
OUT.mkdir(exist_ok=True)
for f in (ROOT / "data").iterdir():
    if f.suffix in (".parquet", ".jsonl"):
        shutil.copy(f, OUT / f.name)
(ROOT / "paper").mkdir(exist_ok=True)
shutil.copy(ROOT / "data" / "founder_review.csv", ROOT / "paper" / "founder_review.csv")
published = json.loads((ROOT / "results" / "combined_results.json").read_text())
(ROOT / "outputs").mkdir(exist_ok=True)
for step in ["founder_final.py", "stats_returns.py", "stats_ops.py", "board_outcomes.py", "combine_results.py"]:
    r = subprocess.run([sys.executable, "-W", "ignore", step], cwd=ROOT / "code", capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"{step} failed:\n{r.stderr[-2000:]}")
rebuilt = json.loads((ROOT / "outputs" / "combined_results.json").read_text())
pub = {s["stat_id"]: s.get("value") for sec in published["sections"] for s in sec["statistics"]}
new = {s["stat_id"]: s.get("value") for sec in rebuilt["sections"] for s in sec["statistics"]}
bad = [k for k in pub if k not in new or (pub[k] is None) != (new[k] is None) or (pub[k] is not None and abs(pub[k] - new[k]) > 1e-9)]
print(f"{len(pub)} statistics checked, {len(bad)} differ")
for k in bad[:20]:
    print("  ", k, pub.get(k), new.get(k))
sys.exit(1 if bad else 0)
