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
import re

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
    7706: ("CarMax", "Austin Ligon"),
    3135: ("ICN Pharmaceuticals", "Milan Panic"),
    5615: ("Atmel", "George Perlegos"),
}
VARS = {"mcap_m1": "mcap", "roa_-1": "roa", "sales_g_-1": "salesg", "rnd_at_-1": "rnd", "capex_at_-1": "capex"}


def main():
    R.clear()
    d = load_labelled()
    # descriptives use every departure; the named cases need a precise announcement date for their three-day return
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
    big = g["forced_founder"][(g["forced_founder"]["forced_llm"] == "yes") & (g["forced_founder"]["dated"] == 1)]
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
        default = re.sub(r"\s+(Inc|Corp|Co|Ltd|Plc)\b.*$|\s+-.*$", "", str(e["coname"]).title()).strip()
        name = re.sub(r",.*$", "", str(e["exec_fullname"]))
        name = " ".join(w for w in name.split() if not re.fullmatch(r"[A-Z]\.", w))
        company, ceo = DISPLAY.get(eid, (default, name))
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
    # Sample flow: from every firing in the database (1998-2023) to the main sample, and the founders likewise.
    ev = pd.read_parquet(HERE / "out" / "events.parquet")
    ev["year"] = pd.to_datetime(ev["event_date"]).dt.year
    fe = ev[ev["code"].isin([3, 4]) & ev["year"].between(1998, 2023)]
    put("flow.forced_db", len(fe))
    put("flow.forced_cik", int(fe["cik"].notna().sum()))
    put("flow.forced_priced", int(fe["permaticker"].notna().sum()))
    allr = load_labelled()
    fr = allr[allr["forced"] == 1]
    put("flow.forced_returns", len(fr))
    put("flow.forced_dated", int((fr["dated"] == 1).sum()))
    fv = pd.read_csv(HERE.parent / "paper" / "founder_review.csv")
    put("flow.founder_model", int((fv["model_code"] == "yes").sum()))
    put("flow.founder_confirmed", int((fv["decision"] == "yes").sum()))
    fy = fv[fv["decision"] == "yes"].merge(ev[["event_id", "year"]], on="event_id", how="left")
    put("flow.founder_in_years", int(fy["year"].between(1998, 2023).sum()))
    put("flow.founder_returns", int(((fr["founder_v0"] == 1)).sum()))
    put("flow.founder_dated", int(((fr["founder_v0"] == 1) & (fr["dated"] == 1)).sum()))
    # The paper's opening case, from the same price file: Nvidia's close on 12 November 2026 against 11 November (the
    # board accepted Huang's resignation on 11 November), and from 6 November, the last close before the board's
    # 8 November statement, to the last day in the file.
    import datasource

    hook = HERE / "out" / "hook_stats.json"  # the two Nvidia returns, published for readers without the price file
    try:
        nv = datasource.prices(["NVDA"]).set_index("date")["closeadj"]
        if pd.Timestamp("2026-11-12") in nv.index:
            put("hook.nvda.day_ret", nv[pd.Timestamp("2026-11-12")] / nv[pd.Timestamp("2026-11-11")] - 1, n=1)
            put("hook.nvda.since_board_statement", nv.iloc[-1] / nv[pd.Timestamp("2026-11-06")] - 1, n=1)
            hook.write_text(json.dumps({k: R[k] for k in ("hook.nvda.day_ret", "hook.nvda.since_board_statement")}))
    except Exception:  # nosec B110 - no price source: use the published values
        if hook.exists():
            R.update(json.loads(hook.read_text()))
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
