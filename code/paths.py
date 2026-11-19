"""Event-time return paths for the figures, from the same market model and conventions as event_study.py.

ar_daily     daily abnormal return for trading days -30..+60 around day 0, one row per event and day:
             ar_mm  market model (estimation window [-250,-30], >= 120 days), the paper's announcement measure;
             ar_ma  market-adjusted (firm minus market, no estimated alpha), used for every window longer than a
                    few days, because a forced-exit firm's pre-event alpha is strongly negative and projecting it
                    forward inflates later abnormal returns.
bhar_monthly buy-and-hold abnormal return from day +2 to the end of month m (m = 1..60, 21 trading days a
             month), computed exactly as event_study.py computes the 1-, 3- and 5-year BHAR: firm returns
             compound for 21*m trading days, the Shumway delisting return applies if the stock leaves the file
             first, and the market compounds over the matching calendar span. A month is missing when the
             horizon runs past the price file's end for a firm still listed.
Inputs : analysis/out/events.parquet, prices, factors and corporate actions via datasource.py
Outputs: analysis/out/ar_daily.parquet, analysis/out/bhar_monthly.parquet
"""

import pathlib

import numpy as np
import pandas as pd
from event_study import delist_return, load

HERE = pathlib.Path(__file__).parent / "out"
DATA_END = pd.Timestamp("2026-06-01")
DAYS = range(-30, 61)
MONTHS = range(1, 61)


def paths(e, s, ff, acts):
    r = s.pct_change().dropna()
    r = r[~r.index.duplicated()]
    j = ff.index.intersection(r.index)
    if len(j) < 200:
        return [], []
    r, f = r.loc[j], ff.loc[j]
    days = r.index
    pos = days.searchsorted(e["event_date"])
    if pos < 250 or pos >= len(days):
        return [], []
    est = slice(pos - 250, pos - 29)
    y = r.iloc[est] - f["rf"].iloc[est]
    if y.notna().sum() < 120:
        return [], []
    b1, *_ = np.linalg.lstsq(np.column_stack([np.ones(len(y)), f["mkt_rf"].iloc[est]]), y.values, rcond=None)
    ar = (r - f["rf"]) - (b1[0] + b1[1] * f["mkt_rf"])
    ma = r - f["mkt"]
    daily = [
        (e["event_id"], d, float(ar.iloc[pos + d]), float(ma.iloc[pos + d])) for d in DAYS if 0 <= pos + d < len(days)
    ]
    last_price = s.index.max()
    kind, dlret = delist_return(acts, last_price)
    start = pos + 2
    d0 = days[min(start, len(days) - 1)]
    monthly = []
    for m in MONTHS:
        n = 21 * m
        end_date = d0 + pd.Timedelta(days=int(n * 365 / 252))
        if end_date > DATA_END and last_price >= DATA_END:
            break
        firm = np.prod(1 + r.iloc[start : start + n].values)
        delisted = last_price < end_date
        if delisted:
            firm *= 1 + dlret
        mk = ff["mkt"][(ff.index >= d0) & (ff.index <= end_date)]
        monthly.append((e["event_id"], m, float(firm - np.prod(1 + mk.values)), int(delisted)))
    return daily, monthly


def main():
    ev, px, ff, act = load()
    g = {t: d.set_index("date")["closeadj"].astype(float) for t, d in px.groupby("ticker")}
    ga = dict(list(act.groupby("ticker")))
    D, M = [], []
    for _, e in ev.iterrows():
        s = g.get(e["ticker"])
        if s is None:
            continue
        a, b = paths(e, s, ff, ga.get(e["ticker"], act.iloc[:0]))
        D += a
        M += b
    pd.DataFrame(D, columns=["event_id", "day", "ar_mm", "ar_ma"]).to_parquet(HERE / "ar_daily.parquet", index=False)
    pd.DataFrame(M, columns=["event_id", "month", "bhar", "delisted"]).to_parquet(
        HERE / "bhar_monthly.parquet", index=False
    )
    print("daily rows", len(D), "monthly rows", len(M))


if __name__ == "__main__":
    main()
