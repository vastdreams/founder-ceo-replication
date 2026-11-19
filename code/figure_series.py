"""The series the figures draw, aggregated from the event-level files. Small, licence-free, kept in the repository.

event_time   mean cumulative market-adjusted abnormal return (firm minus market) from day -30, by trading day -30..+60, with the 95%
             confidence band (cross-sectional), on events with all 91 days.
long_run     mean and median market-adjusted BHAR by month 1..60 (paths.py), with the number of events measured
             at each month: the horizon and its N side by side.
exits        cumulative share of firms that stopped trading by month 1..60, by how (acquired, bankrupt, other),
             on events with a complete five-year horizon, so the denominator is fixed.
per_year     forced exits by year and dismissal type; retirements by year.
reasons      mean CAR[-1,+1] and 95% interval by coded reason (forced exits, at least 10 cases).
roa          median abnormal change in ROA against the matched firm, fiscal years 0..3 against year -1.
board        director turnover and who stays on the board, from outputs/board_stats.json.
matched      median BHAR against the matched firm at 12, 36 and 60 months, from outputs/ops_stats.json.
Output: outputs/figure_series.json, copied to paper/figdata/figure_series.json for the server's figure redraw.
"""

import json
import pathlib
import shutil

import numpy as np
import pandas as pd
from stats_returns import load_labelled

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "outputs"


def ci(x):
    x = pd.Series(x).dropna()
    if len(x) < 2:
        return None, None, None, len(x)
    m, se = x.mean(), x.std(ddof=1) / np.sqrt(len(x))
    return float(m), float(m - 1.96 * se), float(m + 1.96 * se), int(len(x))


def main():
    d = load_labelled()
    f, r = d[d["forced"] == 1], d[d["forced"] == 0]
    groups = {
        "forced": f,
        "retired": r,
        "forced_founder": f[f["founder_v0"] == 1],
        "forced_nonfounder": f[f["founder_v0"] == 0],
        "conduct": f[f["conduct"] == 1],
        "performance": f[f["conduct"] == 0],
        "financial_misconduct": f[f["primary_reason"] == "financial_misconduct"],
        "sex_or_relationship": f[f["primary_reason"].isin(["relationship_with_employee", "other_sexual_misconduct"])],
    }
    S = {}
    ar = pd.read_parquet(HERE / "out" / "ar_daily.parquet")
    wide = ar.pivot(index="event_id", columns="day", values="ar_ma").dropna()
    cum = wide.cumsum(axis=1)
    S["event_time"] = {"days": [int(c) for c in cum.columns]}
    for g, x in groups.items():
        c = cum[cum.index.isin(x["event_id"])]
        mean = c.mean()
        se = c.std(ddof=1) / np.sqrt(len(c))
        S["event_time"][g] = {
            "n": int(len(c)),
            "mean": mean.round(6).tolist(),
            "lo": (mean - 1.96 * se).round(6).tolist(),
            "hi": (mean + 1.96 * se).round(6).tolist(),
        }
    bm = pd.read_parquet(HERE / "out" / "bhar_monthly.parquet")
    S["long_run"] = {"months": list(range(1, 61))}
    for g, x in groups.items():
        b = bm[bm["event_id"].isin(x["event_id"])].groupby("month")["bhar"]
        S["long_run"][g] = {
            "mean": b.mean().round(6).tolist(),
            "median": b.median().round(6).tolist(),
            "n": b.count().astype(int).tolist(),
        }
    first = bm[bm["delisted"] == 1].groupby("event_id")["month"].min()
    S["exits"] = {"months": list(range(1, 61))}
    for g in ("forced", "retired", "forced_founder"):
        x = groups[g].dropna(subset=["bhar_5y"])
        m = x["event_id"].map(first)
        out = {"n": int(len(x))}
        for kind in ("acquired", "bankruptcy", "other"):
            k = (
                x["delist_kind_5y"].isin(["delisted_other", "unknown"])
                if kind == "other"
                else x["delist_kind_5y"].eq(kind)
            )
            out[kind] = [round(float(((m <= mm) & k).sum() / len(x)), 6) for mm in range(1, 61)]
        S["exits"][g] = out
    ev = pd.read_parquet(HERE / "out" / "events.parquet")
    ev = ev[ev["code"].isin([3, 4, 5])].copy()
    ev["year"] = pd.to_datetime(ev["event_date"]).dt.year
    ev = ev[(ev["year"] >= 1998) & (ev["year"] <= 2023)]
    yrs = list(range(1998, 2024))
    S["per_year"] = {"years": yrs}
    for name, code in (("performance", 3), ("conduct", 4), ("retired", 5)):
        cnt = ev[ev["code"] == code].groupby("year").size()
        S["per_year"][name] = [int(cnt.get(y, 0)) for y in yrs]
    fy = groups["forced_founder"].groupby("year").size()
    S["per_year"]["founder"] = [int(fy.get(y, 0)) for y in yrs]
    S["reasons"] = []
    for reason, x in f.groupby("primary_reason"):
        m, lo, hi, n = ci(x["car_mm_m1p1"])
        if n >= 10:
            S["reasons"].append({"reason": reason, "mean": m, "lo": lo, "hi": hi, "n": n})
    for g in (
        "forced",
        "retired",
        "forced_founder",
        "forced_nonfounder",
        "conduct",
        "performance",
        "financial_misconduct",
        "sex_or_relationship",
    ):
        m, lo, hi, n = ci(groups[g]["car_mm_m1p1"])
        S.setdefault("groups", []).append({"group": g, "mean": m, "lo": lo, "hi": hi, "n": n})
    ops = pd.read_parquet(HERE / "out" / "ops_matched.parquet")
    S["roa"] = {"years": [0, 1, 2, 3]}
    for g, flag in (("forced", 1), ("retired", 0)):
        x = ops[ops["forced"] == flag]
        S["roa"][g] = {
            "median": [
                float(x[f"abn_d_roa_{k}"].clip(*x[f"abn_d_roa_{k}"].quantile([0.01, 0.99])).median()) for k in range(4)
            ],
            "n": [int(x[f"abn_d_roa_{k}"].notna().sum()) for k in range(4)],
        }
    bs = json.loads((OUT / "board_stats.json").read_text())
    S["board"] = {
        k: {"value": v.get("value"), "n": v.get("n")}
        for k, v in bs.items()
        if k.startswith("board.") and k.endswith(".mean")
    }
    ops_s = json.loads((OUT / "ops_stats.json").read_text())
    S["matched"] = {
        g: {str(h): {k: ops_s.get(f"mbhar.{g}.{h}y.median", {}).get(k) for k in ("value", "n", "p")} for h in (1, 3, 5)}
        for g in ("forced", "retired", "forced_founder")
    }
    (OUT / "figure_series.json").write_text(json.dumps(S))
    fd = HERE.parent / "paper" / "figdata"
    fd.mkdir(exist_ok=True)
    shutil.copy(OUT / "figure_series.json", fd / "figure_series.json")
    lr = S["long_run"]["forced"]
    print("event_time n", {g: S["event_time"][g]["n"] for g in groups})
    print("forced mean BHAR m1..6", [round(v, 3) for v in lr["mean"][:6]], "n", lr["n"][:6])
    print("forced n at 12/36/60", lr["n"][11], lr["n"][35], lr["n"][59])
    print(
        "exits forced at 12/36/60",
        [round(sum(S["exits"]["forced"][k][i] for k in ("acquired", "bankruptcy", "other")), 3) for i in (11, 35, 59)],
    )


if __name__ == "__main__":
    main()
