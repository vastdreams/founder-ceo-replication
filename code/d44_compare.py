"""D-44: the founder results before and after the forced resignations coded as retirements join the sample.

Before: paper/d44_before.json, the statistics as they stood before D-44 (frozen when D-44 was written; committed so the
comparison reproduces). After: the same keys from the current outputs. Writes outputs/d44_stats.json with keys
d44.before.<key> and d44.after.<key>; combine_results.py builds the before/after table from it.
"""

import json
import pathlib

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "outputs"
PAPER = HERE.parent / "paper"

# key -> the outputs file that holds it after the re-run
KEYS = {
    "fa.n_kept": "founder_appendix_stats.json",
    "exit.forced_founder.bankruptcy_5y": "returns_stats.json",
    "fg.founder.ind.rev.y3.median": "founder_growth_stats.json",
    "fg.founder.pr.rev.y3.median": "founder_growth_stats.json",
}
for b in ("sp", "ind", "pr3", "roa", "pr"):
    for m in ("ret.mean", "ret.median", "usd.median", "ret.count"):
        KEYS[f"fv.founder.{b}.slideann.{m}"] = "founder_value_stats.json"
ALPHA_FILE = "founder_alpha_stats.json"
ALPHA_KEYS = ()  # filled from paper/d44_before.json["_alpha_keys"] when the alpha results exist


def pick(r):
    return {k: r.get(k) for k in ("value", "n", "p") if r.get(k) is not None}


def main():
    before = json.loads((PAPER / "d44_before.json").read_text())
    keys = dict(KEYS)
    for k in before.get("_alpha_keys", []):
        keys[k] = ALPHA_FILE
    cache, out = {}, {}
    for k, f in keys.items():
        if f not in cache:
            p = OUT / f
            cache[f] = json.loads(p.read_text()) if p.exists() else {}
        if k in before:
            out[f"d44.before.{k}"] = before[k]
        if k in cache[f]:
            out[f"d44.after.{k}"] = pick(cache[f][k])
    (OUT / "d44_stats.json").write_text(json.dumps(out, indent=1))
    print("d44 stats", len(out))


if __name__ == "__main__":
    main()
