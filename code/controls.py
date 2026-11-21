"""Controls a referee asks for when firing firms are compared with others: past returns, debt and distress.

Per departure, at the fiscal year-end before the announcement (as-reported, earliest filing, as ops_matched.py):
  prior_ret_12m  buy-and-hold return over trading days -252 to -31 before the announcement
  leverage       total liabilities over total assets
  btm            book equity over market value
  altman_z       Altman (1968): 1.2 WC/TA + 1.4 RE/TA + 3.3 EBIT/TA + 0.6 MV/TL + 1.0 Sales/TA
  distress       Altman Z below 1.81 (the distress zone)
  loss           net income below zero
The optional fundamentals columns (liabilities, equity, workingcapital, retearn, ebit) come from Sharadar SF1 or
Compustat (LT, CEQ, WCAP, RE, OIADP); without them only prior_ret_12m is written.

Inputs : analysis/out/returns.parquet, datasource.prices, datasource.fundamentals
Output : analysis/out/controls.parquet
"""

import pathlib

import datasource
import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).parent


def main():
    ev = pd.read_parquet(HERE / "out" / "returns.parquet")[["event_id", "ticker", "event_date"]].dropna()
    ev["event_date"] = pd.to_datetime(ev["event_date"])
    px = datasource.prices(ev["ticker"].unique())
    out = []
    by_px = {t: g.set_index("date")["closeadj"] for t, g in px.groupby("ticker")}
    for t, g in ev.groupby("ticker"):
        p = by_px.get(t)
        if p is None:
            out += [(e, np.nan) for e in g["event_id"]]
            continue
        for _, e in g.iterrows():
            idx = p.index.searchsorted(e["event_date"])
            if idx < 252:
                out.append((e["event_id"], np.nan))
                continue
            out.append((e["event_id"], p.iloc[idx - 31] / p.iloc[idx - 252] - 1))
    c = pd.DataFrame(out, columns=["event_id", "prior_ret_12m"])
    f = datasource.fundamentals()
    f = f[f["ticker"].isin(set(ev["ticker"]))].copy()
    for k in ("assets", "liabilities", "equity", "workingcapital", "retearn", "ebit", "revenue", "netinc", "marketcap"):
        if k in f:
            f[k] = pd.to_numeric(f[k], errors="coerce")
    f = f.sort_values(["ticker", "calendardate", "datekey"]).drop_duplicates(["ticker", "calendardate"])
    by_t = dict(list(f.groupby("ticker")))
    rows = []
    for _, e in ev.iterrows():
        x = by_t.get(e["ticker"], f.iloc[0:0])
        x = x[x["calendardate"] < e["event_date"]]
        if not len(x):
            continue
        r = x.iloc[-1]
        get = lambda k, r=r: r[k] if k in r and pd.notna(r[k]) else np.nan  # noqa: E731
        ta, tl = get("assets"), get("liabilities")
        row = {"event_id": e["event_id"], "loss": float(get("netinc") < 0) if pd.notna(get("netinc")) else np.nan}
        if pd.notna(ta) and ta > 0:
            row["leverage"] = tl / ta if pd.notna(tl) else np.nan
            mv = get("marketcap")
            row["btm"] = get("equity") / mv if pd.notna(mv) and mv > 0 else np.nan
            z = (1.2 * get("workingcapital") + 1.4 * get("retearn") + 3.3 * get("ebit") + 1.0 * get("revenue")) / ta
            z += 0.6 * mv / tl if pd.notna(tl) and tl > 0 and pd.notna(mv) else np.nan
            row["altman_z"] = z
            row["distress"] = float(z < 1.81) if pd.notna(z) else np.nan
        rows.append(row)
    c = c.merge(pd.DataFrame(rows), on="event_id", how="left")
    c.to_parquet(HERE / "out" / "controls.parquet", index=False)
    print(c.describe().T[["count", "mean", "50%"]].round(3).to_string())


if __name__ == "__main__":
    main()
