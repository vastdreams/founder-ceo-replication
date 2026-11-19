"""Short- and long-run stock returns around CEO departures.

Inputs : analysis/out/events.parquet (build_events.py); datasource.prices (closeadj = split- and dividend-adjusted
         close, so its daily change is a total return); datasource.actions (delisting type); datasource.factors
         (Ken French, percent). See DATA.md.
Outputs: analysis/out/returns.parquet, one row per event with
  car_mm_{w}   market-model cumulative abnormal return, estimation window [-250,-30], >= 120 days
  car_ff5_{w}  Fama-French five-factor plus momentum abnormal return, same estimation window
  bhar_{h}y    buy-and-hold return minus buy-and-hold market (Mkt-RF + RF) over h years from day +2
  delist_*     whether and how the stock left the price file inside each horizon
Delisting rule (Shumway 1997 convention): the return after the last price is 0 for acquisitions and
mergers, -30% for performance delistings, -100% for bankruptcy or liquidation. Market return
compounds over the full horizon either way.
"""

import pathlib

import numpy as np
import pandas as pd

import datasource  # noqa: E402

HERE = pathlib.Path(__file__).parent / "out"
WINDOWS = {"m1p1": (-1, 1), "0p1": (0, 1), "m5p5": (-5, 5), "m30p30": (-30, 30)}
HORIZONS = {1: 252, 3: 756, 5: 1260}
FACTORS = ["mkt_rf", "smb", "hml", "rmw", "cma", "mom"]
DELIST_ZERO = {"acquisitionby", "mergerfrom", "mergerto", "acquisitionof"}
DELIST_BANKRUPT = {"bankruptcyliquidation"}


def load():
    ev = pd.read_parquet(HERE / "events.parquet")
    ev = ev[ev["permaticker"].notna()].copy()
    tick = tuple(ev["ticker"].dropna().unique())
    px = datasource.prices(tick)
    ff = datasource.factors()
    act = datasource.actions(tick)
    ff["date"] = pd.to_datetime(ff["date"])
    px["date"] = pd.to_datetime(px["date"])
    act["date"] = pd.to_datetime(act["date"])
    for c in FACTORS + ["rf"]:
        ff[c] = ff[c].astype(float) / 100.0
    ff["mkt"] = ff["mkt_rf"] + ff["rf"]
    return ev, px, ff.set_index("date").sort_index(), act


def delist_return(acts: pd.DataFrame, last_date) -> tuple[str, float]:
    a = acts[(acts["date"] >= last_date - pd.Timedelta(days=10)) & (acts["date"] <= last_date + pd.Timedelta(days=60))]
    kinds = set(a["action"].str.lower())
    if kinds & DELIST_BANKRUPT:
        return "bankruptcy", -1.0
    if kinds & DELIST_ZERO:
        return "acquired", 0.0
    if kinds:
        return "delisted_other", -0.30
    return "unknown", -0.30


def one(e, s, ff, acts):
    r = s.pct_change().dropna()
    r = r[~r.index.duplicated()]
    j = ff.index.intersection(r.index)
    if len(j) < 200:
        return None
    r, f = r.loc[j], ff.loc[j]
    days = r.index
    pos = days.searchsorted(e["event_date"])  # day 0 = first trading day on/after the announcement
    if pos < 250 or pos >= len(days):
        return None
    out = {"event_id": e["event_id"], "day0": days[pos]}
    est = slice(pos - 250, pos - 29)
    y = r.iloc[est] - f["rf"].iloc[est]
    if y.notna().sum() < 120:
        return None
    X1 = np.column_stack([np.ones(len(y)), f["mkt_rf"].iloc[est]])
    b1, *_ = np.linalg.lstsq(X1, y.values, rcond=None)
    X5 = np.column_stack([np.ones(len(y))] + [f[c].iloc[est] for c in FACTORS])
    b5, *_ = np.linalg.lstsq(X5, y.values, rcond=None)
    resid_sd = np.std(y.values - X1 @ b1, ddof=2)
    out["beta_mm"], out["sigma_est"] = b1[1], resid_sd
    for name, (a, b) in WINDOWS.items():
        lo, hi = pos + a, pos + b
        if lo < 0 or hi >= len(days):
            continue
        w = slice(lo, hi + 1)
        ex = r.iloc[w] - f["rf"].iloc[w]
        ar_mm = ex - (b1[0] + b1[1] * f["mkt_rf"].iloc[w])
        ar_ff = ex - (np.column_stack([np.ones(hi - lo + 1)] + [f[c].iloc[w] for c in FACTORS]) @ b5)
        out[f"car_mm_{name}"] = ar_mm.sum()
        out[f"car_ff5_{name}"] = ar_ff.sum()
        out[f"scar_mm_{name}"] = ar_mm.sum() / (resid_sd * np.sqrt(hi - lo + 1))
    last_price = s.index.max()
    kind, dlret = delist_return(acts, last_price)
    for h, n in HORIZONS.items():
        start = pos + 2
        end_date = days[min(start, len(days) - 1)] + pd.Timedelta(days=int(n * 365 / 252))
        if end_date > pd.Timestamp("2026-06-01") and last_price >= pd.Timestamp("2026-06-01"):
            continue  # horizon not yet complete for a still-listed firm
        rr = r.iloc[start : start + n]
        mk = ff["mkt"][(ff.index >= days[min(start, len(days) - 1)]) & (ff.index <= end_date)]
        firm = np.prod(1 + rr.values)
        delisted = last_price < end_date
        if delisted:
            firm *= 1 + dlret
        out[f"bhr_{h}y"] = firm - 1
        out[f"bhar_{h}y"] = firm - np.prod(1 + mk.values)
        out[f"delisted_{h}y"] = int(delisted)
        out[f"delist_kind_{h}y"] = kind if delisted else None
    return out


def main():
    ev, px, ff, act = load()
    g = {t: d.set_index("date")["closeadj"].astype(float) for t, d in px.groupby("ticker")}
    ga = dict(list(act.groupby("ticker")))
    rows = []
    for _, e in ev.iterrows():
        s = g.get(e["ticker"])
        if s is None:
            continue
        o = one(e, s, ff, ga.get(e["ticker"], act.iloc[:0]))
        if o:
            rows.append(o)
    res = ev.merge(pd.DataFrame(rows), on="event_id", how="inner")
    res.to_parquet(HERE / "returns.parquet", index=False)
    print(len(res), "events with returns")
    print(
        res.groupby("forced")[["car_mm_m1p1", "car_ff5_m1p1", "bhar_1y", "bhar_3y", "bhar_5y"]]
        .agg(["mean", "median", "count"])
        .T
    )


if __name__ == "__main__":
    main()
