"""Were founders missed among dismissals coded as hired CEOs? (review fix, 24 Nov 2026)

Inputs: paper/founder_cases/hired_dismissals_for_founder_check.csv (every dismissal not over fraud whose hand-checked
founder code is not "yes": event_id, cik, firm, CEO, date; exported from analysis/out/founder_value.parquet) and
founder_universe/wikidata_founders.csv (Wikidata P112 "founded by", linked to SEC CIK). A CEO is flagged when the
firm's Wikidata founders include someone with the same surname; flagged names are then read against the founder rule
(founders, not heirs). Writes outputs/founder_missed_stats.json.
"""

import csv
import json
import pathlib
import re

PACK = pathlib.Path(__file__).resolve().parents[1]


def surname(name: str) -> str:
    n = re.sub(r"[^a-z ]", "", re.sub(r",? (jr|sr|iii|ii|phd|ph\.d\.|j\.d\.)\.?", "", name.lower())).split()
    return n[-1] if n else ""


def main():
    wd = {}
    for r in csv.DictReader(open(PACK / "founder_universe" / "wikidata_founders.csv")):
        try:
            wd.setdefault(int(r["cik"]), []).append(r["founder"])
        except ValueError:
            continue
    rows = []
    for line in open(PACK / "paper" / "founder_cases" / "hired_dismissals_for_founder_check.csv"):
        p = line.rstrip("\n").split(",")
        if len(p) < 5 or p[0] == "event_id":
            continue
        try:
            rows.append((p[0], int(float(p[1])), p[2], ",".join(p[3:-1]).strip('"'), p[-1]))
        except ValueError:
            continue
    covered = [r for r in rows if r[1] in wd]
    hits = [(r, f) for r in covered for f in wd[r[1]] if surname(r[3]) and surname(r[3]) == surname(f)]
    events_hit = sorted({r[0] for r, _ in hits})
    # every surname match is an heir (son or grandson of the founder), read case by case: Motorola (Galvin),
    # Timken, Tech Data (Raymund), SITE Centers (Wolstein); none founded the firm
    out = {
        "fmiss.n_hired": {"value": len(rows), "n": len(rows)},
        "fmiss.n_wikidata": {"value": len(covered), "n": len(rows)},
        "fmiss.n_surname_match": {"value": len(events_hit), "n": len(covered)},
        "fmiss.n_founder_found": {"value": 0, "n": len(covered)},
    }
    (PACK / "outputs" / "founder_missed_stats.json").write_text(json.dumps(out, indent=1))
    print(out)


if __name__ == "__main__":
    main()
