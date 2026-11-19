"""Matched-control design for operating performance and long-run returns (Barber and Lyon 1996, 1997).

For each event with a Sharadar ticker, the control is a firm in the same Fama-French industry with
as-reported annual data in year t-1, market cap within 70-130% of the event firm, and no CEO turnover
in the Gentry database within three years either side; among those, the closest operating ROA
(EBITDA / assets) at t-1. If none qualifies, the closest market cap in the industry is used and flagged.

Outputs analysis/out/ops_matched.parquet with, for event and control:
  roa_{k}         EBITDA / total assets in fiscal year t+k, k in -1..3 (t = calendar year of the event)
  d_roa_{k}       roa_k - roa_{-1};  abn_d_roa_{k} = event minus control
  sales_g_{k}, rnd_at_{k}, capex_at_{k}
  bhr_{h}y_ctrl   control buy-and-hold return over the event's window; mbhar_{h}y = event bhr - control bhr
Inputs are as-reported (ARY) to avoid restated numbers the market had not seen.
"""

import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path.home()))
import fce_db  # noqa: E402

HERE = pathlib.Path(__file__).parent / "out"
HORIZONS = {1: 252, 3: 756, 5: 1260}


def num(s):
    return pd.to_numeric(s, errors="coerce")


def main():
    con = fce_db.connect()
    ev = pd.read_parquet(HERE / "returns.parquet")
    sf = pd.read_sql(
        """select ticker, calendardate, assets, ebitda, netinc, revenue, marketcap, rnd, capex
                        from sharadar.sf1 where dimension = 'ARY'""",
        con,
    )
    for c in ["assets", "ebitda", "netinc", "revenue", "marketcap", "rnd", "capex"]:
        sf[c] = num(sf[c])
    sf["year"] = pd.to_datetime(sf["calendardate"]).dt.year
    sf = sf.sort_values("calendardate").drop_duplicates(["ticker", "year"], keep="last")
    sf["roa"] = sf["ebitda"] / sf["assets"].where(sf["assets"] > 0)
    tk = pd.read_sql(
        """select ticker, famaindustry, (regexp_match(secfilings, 'CIK=0*([0-9]+)'))[1]::bigint as cik
                        from sharadar.tickers where "table" = 'SF1'""",
        con,
    ).drop_duplicates("ticker")
    sf = sf.merge(tk, on="ticker", how="left")
    turn = pd.read_sql(
        """select c.cik, g.fyear from world.ceo_turnover_gentry g join world.gvkey_cik c using(gvkey)
                          where g.departure_code not in (9)""",
        con,
    )
    turn_years = turn.groupby("cik")["fyear"].apply(set).to_dict()
    panel = sf.set_index(["ticker", "year"])

    def series(t, y0):
        out = {}
        for k in (-1, 0, 1, 2, 3):
            row = panel.loc[(t, y0 + k)] if (t, y0 + k) in panel.index else None
            out[f"roa_{k}"] = None if row is None else row["roa"]
            prev = panel.loc[(t, y0 + k - 1)] if (t, y0 + k - 1) in panel.index else None
            out[f"sales_g_{k}"] = (
                None if row is None or prev is None or not prev["revenue"] else row["revenue"] / prev["revenue"] - 1
            )
            out[f"rnd_at_{k}"] = None if row is None or not row["assets"] else (row["rnd"] or 0) / row["assets"]
            out[f"capex_at_{k}"] = None if row is None or not row["assets"] else abs(row["capex"] or 0) / row["assets"]
        return out

    base = sf.dropna(subset=["roa", "marketcap", "famaindustry"])
    rows = []
    for _, e in ev.iterrows():
        y0 = pd.Timestamp(e["event_date"]).year
        me = base[(base["ticker"] == e["ticker"]) & (base["year"] == y0 - 1)]
        if me.empty:
            continue
        me = me.iloc[0]
        pool = base[
            (base["year"] == y0 - 1) & (base["famaindustry"] == me["famaindustry"]) & (base["ticker"] != e["ticker"])
        ]
        pool = pool[[not any(abs(y - y0) <= 3 for y in turn_years.get(c, ())) for c in pool["cik"]]]
        size = pool[(pool["marketcap"] >= 0.7 * me["marketcap"]) & (pool["marketcap"] <= 1.3 * me["marketcap"])]
        relaxed = size.empty
        cand = pool if relaxed else size
        if cand.empty:
            continue
        key = (cand["marketcap"] / me["marketcap"]).apply(np.log).abs() if relaxed else (cand["roa"] - me["roa"]).abs()
        ctrl = cand.loc[key.idxmin()]
        r = {
            "event_id": e["event_id"],
            "ctrl_ticker": ctrl["ticker"],
            "match_relaxed": int(relaxed),
            "famaindustry": me["famaindustry"],
            "mcap_m1": me["marketcap"],
            "ctrl_mcap_m1": ctrl["marketcap"],
        }
        a, b = series(e["ticker"], y0), series(ctrl["ticker"], y0)
        for k, v in a.items():
            r[k] = v
            r[k + "_ctrl"] = b[k]
        for k in (0, 1, 2, 3):
            if r.get(f"roa_{k}") is not None and r.get("roa_-1") is not None:
                r[f"d_roa_{k}"] = r[f"roa_{k}"] - r["roa_-1"]
            if r.get(f"roa_{k}_ctrl") is not None and r.get("roa_-1_ctrl") is not None:
                r[f"d_roa_{k}_ctrl"] = r[f"roa_{k}_ctrl"] - r["roa_-1_ctrl"]
            if f"d_roa_{k}" in r and f"d_roa_{k}_ctrl" in r:
                r[f"abn_d_roa_{k}"] = r[f"d_roa_{k}"] - r[f"d_roa_{k}_ctrl"]
        rows.append(r)
    m = ev.merge(pd.DataFrame(rows), on="event_id", how="inner")

    # control firm buy-and-hold over the same windows (same delisting rule as event_study.py)
    from event_study import delist_return

    ct = tuple(m["ctrl_ticker"].unique())
    px = pd.read_sql(
        "select ticker, date, closeadj from sharadar.sep where ticker in %(t)s and closeadj > 0", con, params={"t": ct}
    )
    act = pd.read_sql(
        "select ticker, date::date as date, action from sharadar.actions where ticker in %(t)s", con, params={"t": ct}
    )
    px["date"] = pd.to_datetime(px["date"])
    act["date"] = pd.to_datetime(act["date"])
    g = {t: d.set_index("date")["closeadj"].astype(float).sort_index() for t, d in px.groupby("ticker")}
    ga = dict(list(act.groupby("ticker")))
    for h, n in HORIZONS.items():
        vals = []
        for _, e in m.iterrows():
            s = g.get(e["ctrl_ticker"])
            if s is None or pd.isna(e.get(f"bhr_{h}y")):
                vals.append(np.nan)
                continue
            start = pd.Timestamp(e["day0"]) + pd.Timedelta(days=3)
            end = start + pd.Timedelta(days=int(n * 365 / 252))
            w = s[(s.index >= start) & (s.index <= end)]
            if len(w) < 2:
                vals.append(np.nan)
                continue
            bh = w.iloc[-1] / w.iloc[0]
            if s.index.max() < end:
                bh *= 1 + delist_return(ga.get(e["ctrl_ticker"], act.iloc[:0]), s.index.max())[1]
            vals.append(bh - 1)
        m[f"bhr_{h}y_ctrl"] = vals
        m[f"mbhar_{h}y"] = m[f"bhr_{h}y"] - m[f"bhr_{h}y_ctrl"]
    m.to_parquet(HERE / "ops_matched.parquet", index=False)
    print(len(m), "matched events;", int(m["match_relaxed"].sum()), "relaxed matches")
    print(
        m.groupby("forced")[["abn_d_roa_1", "abn_d_roa_3", "mbhar_1y", "mbhar_3y", "mbhar_5y"]]
        .agg(["mean", "median", "count"])
        .T
    )


if __name__ == "__main__":
    main()
