"""The rule-based planned-succession screen of D-38 item 2, applied to every departure, and its validation.

A departure is flagged when either holds, using only fields held for every event:
  (a) day 0 (after the D-37 and D-38 date fixes) came 90 or more calendar days before the database's left_ceo_office;
  (b) the database notes or the coded evidence quote say the CEO stayed on as chairman or executive chairman, and the
      same text names the chief operating officer or the president as the successor.

Validation: the 163 hand-checked departures, the 103 founder departures of D-35 (founder_cases.csv) and the 60 hired
firings of the audit (hired_audit.csv). The truth is the hand verdict: the 12 founder and 5 hired "not a firing" cases
(d37_corrections.csv, d38_corrections.csv, field "sample") are planned successions; every other hand-checked case is
not. Day 0 is computed here without dropping those cases, so they can be scored.

Inputs : datasource.gentry(), analysis/out/redate.parquet, analysis/out/event_coding_final.jsonl,
         paper/date_corrections.csv, paper/d37_corrections.csv, paper/d38_corrections.csv,
         paper/founder_cases/founder_cases.csv, paper/founder_cases/hired_audit.csv
Outputs: analysis/out/screen.parquet (event_id, gap_days, flag_a, flag_b, flag); outputs/screen_stats.json
"""

import json
import pathlib
import re

import datasource
import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).parent
PAPER = HERE.parent / "paper"
OUT = HERE.parent / "outputs"
GAP_DAYS = 90
CHAIR = re.compile(
    r"\b(remain\w*|stay\w*|stays|continu\w*|retain\w*|keep\w*|kept|will be|become\w*|became|move\w* into|"
    r"serve\w*|named|as)\b[^.;]{0,40}?\b(non-?executive |executive )?chair(man|woman|person)?\b",
    re.I,
)
SUCCESSOR = re.compile(
    r"(\b(chief operating officer|coo)\b[^.;]{0,120}\b(succeed\w*|named|appointed|promoted|elected|will become|"
    r"became|take\w* over|took over|replac\w*|hands? (the )?reins)\b)|"
    r"(\b(succeed\w*|successor|named|appointed|promoted|elected|replac\w*|hands? (the )?reins)\b[^.;]{0,80}"
    r"\b(chief operating officer|coo|president)\b)",
    re.I,
)


def day0_all() -> pd.DataFrame:
    """Day 0 for every departure, as build_events.py sets it, but with no departure dropped."""
    g = datasource.gentry()
    g = g[pd.to_numeric(g["departure_code"], errors="coerce").isin([3, 4, 5])]
    ev = pd.DataFrame(
        {
            "event_id": g["dismissal_dataset_id"].astype(int),
            "event_date": g["date_departure_announced"].fillna(g["left_ceo_office"]),
            "left_ceo_office": g["left_ceo_office"],
            "notes": g["notes"].fillna(""),
            "forced": pd.to_numeric(g["departure_code"]).isin([3, 4]).astype(int),
        }
    )
    ev["event_date"] = pd.to_datetime(ev["event_date"])
    rd = HERE / "out" / "redate.parquet"
    if rd.exists():
        r = pd.read_parquet(rd)[["event_id", "announce_date"]]
        ev = ev.merge(r, on="event_id", how="left")
        ev["event_date"] = pd.to_datetime(ev["announce_date"]).fillna(ev["event_date"])
        ev = ev.drop(columns="announce_date")
    fixes = {}
    dc = PAPER / "date_corrections.csv"
    if dc.exists():
        c = pd.read_csv(dc)
        fixes.update(zip(c["event_id"], pd.to_datetime(c["announce_date"])))
    for name in ("d37_corrections.csv", "d38_corrections.csv", "d44_corrections.csv"):
        f = PAPER / name
        if f.exists():
            c = pd.read_csv(f)
            c = c[(c["field"] == "event_date") & (c["new"] != c["old"])]
            fixes.update(zip(c["event_id"], pd.to_datetime(c["new"])))
    hit = ev["event_id"].isin(fixes)
    ev.loc[hit, "event_date"] = ev.loc[hit, "event_id"].map(fixes)
    return ev


def main():
    ev = day0_all()
    coding = pd.DataFrame([json.loads(x) for x in open(HERE / "out" / "event_coding_final.jsonl")])
    ev = ev.merge(coding[["event_id", "reason_evidence"]], on="event_id", how="left")
    text = ev["notes"] + " " + ev["reason_evidence"].fillna("")
    ev["gap_days"] = (pd.to_datetime(ev["left_ceo_office"]) - ev["event_date"]).dt.days
    ev["flag_a"] = (ev["gap_days"] >= GAP_DAYS).astype(int)
    ev["flag_b"] = [int(bool(CHAIR.search(t)) and bool(SUCCESSOR.search(t))) for t in text]
    ev["flag"] = ((ev["flag_a"] + ev["flag_b"]) > 0).astype(int)
    ev[["event_id", "forced", "gap_days", "flag_a", "flag_b", "flag"]].to_parquet(HERE / "out" / "screen.parquet")

    # validation on the hand-checked departures
    planned = set()
    for name in ("d37_corrections.csv", "d38_corrections.csv"):
        c = pd.read_csv(PAPER / name)
        planned |= set(c.loc[c["field"] == "sample", "event_id"].astype(int))
    checked = set(pd.read_csv(PAPER / "founder_cases" / "founder_cases.csv")["event_id"].astype(int))
    checked |= set(pd.read_csv(PAPER / "founder_cases" / "hired_audit.csv")["event_id"].astype(int))
    v = ev[ev["event_id"].isin(checked)].copy()
    v["truth"] = v["event_id"].isin(planned).astype(int)
    R = {}

    def put(k, val, n):
        R[k] = {"value": None if val is None or (isinstance(val, float) and np.isnan(val)) else float(val), "n": int(n)}

    pos, neg = v[v["truth"] == 1], v[v["truth"] == 0]
    put("screen.validation.n_checked", len(v), len(v))
    put("screen.validation.n_planned", len(pos), len(v))
    for rule in ("flag", "flag_a", "flag_b"):
        put(f"screen.validation.{rule}.sensitivity", pos[rule].mean() if len(pos) else np.nan, len(pos))
        put(f"screen.validation.{rule}.true_positives", int(pos[rule].sum()), len(pos))
        put(f"screen.validation.{rule}.false_positives", int(neg[rule].sum()), len(neg))
        put(f"screen.validation.{rule}.false_positive_rate", neg[rule].mean(), len(neg))
        put(f"screen.validation.{rule}.specificity", 1 - neg[rule].mean(), len(neg))
        flagged = v[v[rule] == 1]
        put(f"screen.validation.{rule}.precision", flagged["truth"].mean() if len(flagged) else np.nan, len(flagged))
    f = ev[ev["forced"] == 1]
    put("screen.forced.n", len(f), len(f))
    put("screen.forced.flagged", int(f["flag"].sum()), len(f))
    put("screen.forced.flag_a", int(f["flag_a"].sum()), len(f))
    put("screen.forced.flag_b", int(f["flag_b"].sum()), len(f))
    R["_validation_cases"] = v[["event_id", "truth", "gap_days", "flag_a", "flag_b", "flag"]].to_dict("records")
    (OUT / "screen_stats.json").write_text(json.dumps(R, indent=1, default=str))
    for k, r in R.items():
        if not k.startswith("_"):
            print(f"{k:50s} {r['value']} (n={r['n']})")


if __name__ == "__main__":
    main()
