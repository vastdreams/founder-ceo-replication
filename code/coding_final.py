"""Final model labels: the v2 pass (notes plus SEC 8-Ks, press releases, Wikipedia and NYT) for every event it
coded, and the v1 pass (dataset notes only) for the rest. Hand reviews in paper/founder_review.csv and
paper/conduct_review.csv still override these labels downstream (D-07).
Output: analysis/out/event_coding_final.jsonl
"""

import json
import pathlib

HERE = pathlib.Path(__file__).parent / "out"


def load(v):
    p = HERE / f"event_coding_{v}.jsonl"
    rows = {}
    if p.exists():
        for line in open(p):
            r = json.loads(line)
            rows[r["event_id"]] = r
    return rows


def main():
    rows = load("v1")
    v2 = {k: r for k, r in load("v2").items() if "error" not in r}
    rows.update(v2)
    with open(HERE / "event_coding_final.jsonl", "w") as f:
        for r in rows.values():
            f.write(json.dumps(r) + "\n")
    print("events", len(rows), "from v2", len(v2))


if __name__ == "__main__":
    main()
