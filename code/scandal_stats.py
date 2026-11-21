"""Scandals that did and did not end the CEO's job: counts and the market's reaction when the scandal first broke.

paper/scandal_review.csv comes from scandal_scan.py: personal-conduct reports about sitting CEOs of the sample's
firms in the New York Times Archive, 1998 to 2023, each checked by hand (agent_note). Rows the check marks as the
wrong firm, not a scandal or not a sitting CEO are dropped; rows it marks "departed" count as departures the
database misses. The return is the market-adjusted return over trading days -1 to +1 around the first report
(day 0, the first trading day on or after it). The sample is small (most firings in the database never reached the
Times), so the statistics are descriptive.

Inputs : paper/scandal_review.csv, datasource.gvkey_cik, datasource.securities, datasource.prices, datasource.factors
Output : outputs/scandal_stats.json
"""

import json
import pathlib

import datasource
import numpy as np
import pandas as pd
from scipy import stats

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "outputs"
R: dict = {}


def put(key, value, **kw):
    R[key] = {"value": None if value is None or (isinstance(value, float) and np.isnan(value)) else float(value), **kw}


def main():
    d = pd.read_csv(HERE.parent / "paper" / "scandal_review.csv")
    note = d["agent_note"].fillna("")
    d = d[~note.str.startswith(("wrong firm", "not a scandal", "not a sitting"))].copy()
    d["departed"] = ((d["departed_12m"] == 1) | d["agent_note"].fillna("").str.startswith("departed")).astype(int)
    put("scandal.n_events", len(d))
    put("scandal.n_departed", int(d["departed"].sum()))
    put("scandal.n_kept", int((d["departed"] == 0).sum()))
    known = d["in_known_conduct_firings"].fillna(False).astype(bool) if "in_known_conduct_firings" in d else None
    if known is not None:
        put("scandal.n_known_firings_found", int(known.sum()))
    links = datasource.gvkey_cik()
    sec = datasource.securities("SEP")
    sec = sec[sec["category"].fillna("").str.contains("Common Stock")]
    d = d.merge(links[["gvkey", "cik"]], on="gvkey", how="left").merge(
        sec[["cik", "ticker", "firstpricedate", "lastpricedate"]], on="cik", how="left"
    )
    d["day"] = pd.to_datetime(d["first_report_date"])
    d = d[(d["day"] >= pd.to_datetime(d["firstpricedate"])) & (d["day"] <= pd.to_datetime(d["lastpricedate"]))]
    d = d.drop_duplicates("event_id")
    px = datasource.prices(d["ticker"].unique())
    px["ret"] = px.groupby("ticker")["closeadj"].pct_change()
    ff = datasource.factors().set_index("date")
    mkt = (ff["mkt_rf"] + ff["rf"]) / 100
    cars = {}
    for _, e in d.iterrows():
        p = px[px["ticker"] == e["ticker"]].set_index("date")["ret"].dropna()
        days = p.index[p.index >= e["day"]]
        if not len(days):
            continue
        i = p.index.get_loc(days[0])
        if i < 1 or i + 1 >= len(p):
            continue
        w = p.iloc[i - 1 : i + 2]
        cars[e["event_id"]] = float((w - mkt.reindex(w.index).fillna(0)).sum())
    d["car"] = d["event_id"].map(cars)
    for name, x in (("all", d), ("departed", d[d["departed"] == 1]), ("kept", d[d["departed"] == 0])):
        c = x["car"].dropna()
        put(
            f"scandal.{name}.first_report.car_m1p1.mean",
            c.mean() if len(c) else None,
            n=len(c),
            p=stats.ttest_1samp(c, 0).pvalue if len(c) > 2 else None,
        )
    out = d[["company", "ceo_name", "first_report_date", "scandal_type", "departed", "car"]].sort_values(
        "first_report_date"
    )
    R["_cases"] = json.loads(out.to_json(orient="records"))
    OUT.joinpath("scandal_stats.json").write_text(json.dumps(R, indent=1, default=str))
    for k, v in R.items():
        if k != "_cases":
            print(k, v)
    print(out.to_string())


if __name__ == "__main__":
    main()
