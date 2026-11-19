"""Who gets fired: firm characteristics before the departure, and the largest founder removals in the sample.

Descriptives use the fiscal year before the departure (year -1) from the as-reported annual statements and the
market value at the month before the announcement (ops_matched.py). Medians with Mann-Whitney U tests.
Cases are the forced founder exits in the strict sample (the evidence-based coding also reads the exit as forced)
with the largest market value before the announcement. The dismissal type is
the CEO dismissal database's own code (3 = job performance, 4 = legal violations or personal conduct); the
outcomes are this paper's CAR[-1,+1], 3-year market-adjusted BHAR and what happened to the listing within 5 years.
Inputs : analysis/out/ops_matched.parquet, stats_returns.load_labelled()
Output : outputs/describe_stats.json (stats plus the case rows)
"""

import json
import pathlib

import numpy as np
import pandas as pd
from scipy import stats
from stats_returns import R, load_labelled, put

HERE = pathlib.Path(__file__).parent
N_CASES = 12
# Display names for the case table: the security's current name is not the name readers know (Altaba was Yahoo).
DISPLAY = {
    7398: ("Yahoo", "Jerry Yang"),
    49: ("WorldCom", "Bernard Ebbers"),
    8761: ("Wynn Resorts", "Steve Wynn"),
    6350: ("Chesapeake Energy", "Aubrey McClendon"),
    7657: ("Monster Worldwide", "Andrew McKelvey"),
    7758: ("Ralph Lauren", "Ralph Lauren"),
    9053: ("Chipotle", "Steve Ells"),
    5723: ("AES", "Dennis Bakke"),
    6659: ("Mercury Interactive", "Amnon Landan"),
    3455: ("Symbol Technologies", "Jerome Swartz"),
    8370: ("WWE", "Vince McMahon"),
    6352: ("Cree", "Neal Hunter"),
    7961: ("Career Education", "John Larson"),
    9469: ("Acadia Healthcare", "Joey Jacobs"),
}
VARS = {"mcap_m1": "mcap", "roa_-1": "roa", "sales_g_-1": "salesg", "rnd_at_-1": "rnd", "capex_at_-1": "capex"}


def main():
    R.clear()
    d = load_labelled()
    ops = pd.read_parquet(HERE / "out" / "ops_matched.parquet")[["event_id", *VARS]]
    d = d.merge(ops, on="event_id", how="left")
    g = {
        "forced": d[d["forced"] == 1],
        "retired": d[d["forced"] == 0],
        "forced_founder": d[(d["forced"] == 1) & (d["founder_v0"] == 1)],
    }
    for col, name in VARS.items():
        for k, x in g.items():
            v = x[col].replace([np.inf, -np.inf], np.nan).dropna()
            if len(v):
                put(f"desc.{k}.{name}.median", v.median(), n=len(v))
        a = g["forced"][col].replace([np.inf, -np.inf], np.nan).dropna()
        b = g["retired"][col].replace([np.inf, -np.inf], np.nan).dropna()
        if len(a) > 5 and len(b) > 5:
            put(
                f"descdiff.forced_vs_retired.{name}.diff_median",
                a.median() - b.median(),
                n=len(a) + len(b),
                p=stats.mannwhitneyu(a, b).pvalue,
            )
    # Only exits the evidence-based coding also reads as forced (strict sample, D-09).
    big = g["forced_founder"][g["forced_founder"]["forced_llm"] == "yes"]
    big = big.dropna(subset=["mcap_m1", "car_mm_m1p1"]).sort_values("mcap_m1", ascending=False)
    cases = []
    for _, e in big.head(N_CASES).iterrows():
        eid = int(e["event_id"])
        put(f"case.{eid}.car_m1p1", e["car_mm_m1p1"], n=1)
        if pd.notna(e.get("bhar_3y")):
            put(f"case.{eid}.bhar_3y", e["bhar_3y"], n=1)
        fate = "still listed"
        if pd.notna(e.get("delisted_5y")) and e["delisted_5y"] == 1:
            fate = {"acquired": "acquired", "bankruptcy": "bankrupt"}.get(e["delist_kind_5y"], "delisted")
        elif pd.isna(e.get("delisted_5y")):
            fate = "under 5 years of data"
        company, ceo = DISPLAY.get(eid, (str(e["coname"]).title(), e["exec_fullname"]))
        cases.append(
            {
                "event_id": eid,
                "company": company,
                "ceo": ceo,
                "year": int(pd.Timestamp(e["event_date"]).year),
                "dismissal": "performance" if int(e["code"]) == 3 else "legal or conduct",
                "mcap_m1": float(e["mcap_m1"]),
                "fate_5y": fate,
            }
        )
    put("case.n_listed", len(cases))
    out = HERE.parent / "outputs"
    (out / "describe_stats.json").write_text(json.dumps({**R, "_cases": cases}, indent=1))
    for c in cases:
        print(
            c["year"],
            c["company"],
            "|",
            c["ceo"],
            "|",
            c["dismissal"],
            "|",
            round(c["mcap_m1"] / 1e9, 1),
            "bn |",
            round(R[f"case.{c['event_id']}.car_m1p1"]["value"] * 100, 1),
            "% |",
            c["fate_5y"],
        )
    for k in sorted(R):
        if k.startswith("desc"):
            print(k, R[k])


if __name__ == "__main__":
    main()
