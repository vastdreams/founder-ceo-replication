"""Independent recomputation of the Sacked paper's headline numbers (operator, 25 Nov 2026: every number has
provenance, and the headline numbers are checked by code that does not use the pack's analysis).

Nothing here imports from analysis/. The event file analysis/out/founder_value.parquet is read only for identifiers
and flags (event id, ticker, day 0, dismissal, fraud, founder, scandal, well-dated, competitor tickers); every return,
delisting and test below is recomputed from the raw tables with this file's own SQL and arithmetic:
  sharadar.sep (closeadj), sharadar.actions, public.fmp_daily_prices and public.fmp_dividends (SPY total return),
  world.ff5_daily (trading calendar and the market for the market model).
Two benchmarks, the industry average and the profitability-matched firm, have no competitor list in the event file;
for them the aggregate (mean and N) is re-derived from the event file's per-event gaps with plain pandas (level B).

Run on the database host:  python verify/recompute_headline.py  ->  verify/headline_recomputed.json
"""

import json
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path.home()))
import fce_db  # noqa: E402  database connector only

HERE = pathlib.Path(__file__).resolve().parent
EV = HERE.parent / "analysis" / "out" / "founder_value.parquet"


def q(sql, params=None):
    return pd.read_sql(sql, fce_db.connect(), params=params)


def main():
    ev = pd.read_parquet(
        EV,
        columns=[
            "event_id",
            "ticker",
            "day0",
            "forced",
            "who",
            "why",
            "criminal",
            "dated",
            "pr_ticker",
            "pr3_ticker",
            "ind_slideann",
            "roa_slideann",
        ],
    )
    ev["day0"] = pd.to_datetime(ev["day0"])
    # the case checks' exclusions (D-37, D-38, D-44): departures the sources show were planned successions leave
    # every group; read from the decision files, not from the pack's code
    drop = set()
    for f in ("d37_corrections.csv", "d38_corrections.csv", "d44_corrections.csv"):
        c = pd.read_csv(HERE.parent / "paper" / f)
        drop |= set(c[(c["field"] == "sample") & (c["new"] == "not a firing")]["event_id"].astype(int))
    ev = ev[~ev["event_id"].astype(int).isin(drop)]
    ff = q("select date, mkt_rf, rf from world.ff5_daily order by date")
    ff["date"] = pd.to_datetime(ff["date"])
    cal = pd.DatetimeIndex(ff["date"])
    mkt = pd.Series((ff["mkt_rf"].values + ff["rf"].values) / 100.0, index=cal)
    spx = q("select date, close from public.fmp_daily_prices where symbol = 'SPY' and close > 0 order by date")
    dv = q("select date, dividend from public.fmp_dividends where symbol = 'SPY' and dividend > 0")
    spx["date"], dv["date"] = pd.to_datetime(spx["date"]), pd.to_datetime(dv["date"])
    s = spx.set_index("date")["close"]
    d = dv.set_index("date")["dividend"].reindex(s.index).fillna(0.0)
    sp_ret = ((s + d) / s.shift(1) - 1).dropna()
    sp_idx = (1 + sp_ret).cumprod()

    # groups from the final hand-checked flags (forced: a dismissal; who: founder or hired; why: fraud, scandal,
    # coup or other), as the paper defines them in Section 3
    founder_m = (ev.forced == 1) & (ev.why != "fraud") & (ev.who == "founder")
    car_m = (ev.dated == 1) & (ev.forced == 1) & ev.why.isin(["fraud", "scandal"])
    tick = set(ev.loc[founder_m | car_m, "ticker"].dropna())
    for col in ("pr_ticker", "pr3_ticker"):
        for x in ev.loc[founder_m, col].dropna():
            tick.update(str(x).split(";"))
    px = q(
        "select ticker, date, closeadj from sharadar.sep where ticker = any(%(t)s) and closeadj > 0", {"t": list(tick)}
    )
    px["date"] = pd.to_datetime(px["date"])
    P = px.pivot(index="date", columns="ticker", values="closeadj").reindex(cal)
    del px
    alltick = list(set(ev["ticker"].dropna()))
    lastpx = q(
        "select ticker, max(date) as last from sharadar.sep where ticker = any(%(t)s) group by ticker", {"t": alltick}
    )
    lastpx = dict(zip(lastpx["ticker"], pd.to_datetime(lastpx["last"])))
    act = q(
        "select ticker, date, action from sharadar.actions where ticker = any(%(t)s) and action = 'bankruptcyliquidation'",
        {"t": alltick},
    )
    act["date"] = pd.to_datetime(act["date"])

    def pos(day):
        i = cal.searchsorted(day)
        return i if i < len(cal) else None

    def ret(t, i0, i1):
        """Buy-and-hold return from the close of i0 to the close of i1; a stock that stops trading inside the window
        is held at its last price (stated convention of this check)."""
        if t not in P.columns or i0 < 0 or i1 >= len(cal):
            return np.nan
        w = P[t].iloc[i0 : i1 + 1]
        a, b = w.iloc[0], w.ffill().iloc[-1]
        return b / a - 1 if pd.notna(a) and pd.notna(b) else np.nan

    def spr(i0, i1):
        a = sp_idx.asof(cal[i0])
        b = sp_idx.asof(cal[i1])
        return b / a - 1

    out = {}
    rows = []
    for e in ev.itertuples():
        i = pos(e.day0) if pd.notna(e.day0) else None
        if i is None or pd.isna(e.ticker):
            continue
        i0, i1 = i - 31, i + 1
        firm = ret(e.ticker, i0, i1)
        r = {"event_id": e.event_id, "firm": firm, "sp": firm - spr(i0, i1) if pd.notna(firm) else np.nan}
        r["pr"] = firm - ret(e.pr_ticker, i0, i1) if pd.notna(e.pr_ticker) else np.nan
        if pd.notna(e.pr3_ticker):
            cr = [ret(t, i0, i1) for t in str(e.pr3_ticker).split(";")]
            r["pr3"] = firm - np.mean(cr) if not np.isnan(cr).any() else np.nan
            r["inv_pr3"] = 100 * (1 + np.mean(cr)) if not np.isnan(cr).any() else np.nan
        else:
            r["pr3"] = r["inv_pr3"] = np.nan
        r["inv_firm"] = 100 * (1 + firm) if pd.notna(firm) else np.nan
        r["inv_sp"] = 100 * (1 + spr(i0, i1))
        # market-model CAR over days -1..+1, estimated on days -250..-30
        if e.ticker in P.columns and i - 250 >= 1 and i + 1 < len(cal):
            rr = P[e.ticker].pct_change()
            est = pd.DataFrame({"r": rr.iloc[i - 250 : i - 29], "m": mkt.iloc[i - 250 : i - 29]}).dropna()
            if len(est) >= 120:
                beta, alpha = np.polyfit(est["m"], est["r"], 1)
                w = pd.DataFrame({"r": rr.iloc[i - 1 : i + 2], "m": mkt.iloc[i - 1 : i + 2]})
                r["car"] = float((w["r"] - alpha - beta * w["m"]).sum()) if w["r"].notna().all() else np.nan
        # bankruptcy within 60 months: last price within 1,260 trading days, and a bankruptcy or liquidation action
        # within 60 days of that last price; firms not followed for 60 months are left out
        last = lastpx.get(e.ticker)
        if last is not None:
            end = i + 1260
            gone = (end < len(cal) and last < cal[end]) or (end >= len(cal) and last < cal[-1] - pd.Timedelta(days=10))
            followed = end < len(cal) or gone
            a = act[act["ticker"] == e.ticker]
            r["followed60"] = bool(followed)
            r["bankrupt60"] = bool(gone and len(a) and ((a["date"] - last).abs() <= pd.Timedelta(days=60)).any())
        rows.append(r)
    R = pd.DataFrame(rows).merge(ev, on="event_id")
    founder = R[(R.forced == 1) & (R.why != "fraud") & (R.who == "founder")]
    forced = R[(R.forced == 1) & (R.why != "fraud")]
    retired = R[(R.forced == 0) & (R.criminal == 0)]

    def put(k, x, level="A"):
        x = pd.Series(x).dropna()
        out[k] = {"value": float(x.mean()), "n": int(len(x)), "level": level}

    for b in ("sp", "pr", "pr3"):
        put(f"fv.founder.{b}.slideann.ret.mean", founder[b])
    for b, col in (("ind", "ind_slideann"), ("roa", "roa_slideann")):
        put(f"fv.founder.{b}.slideann.ret.mean", founder[col], level="B")
    for k, col in (("inv_firm", "inv_firm"), ("inv_pr3", "inv_pr3"), ("inv_sp", "inv_sp")):
        x = founder[col].dropna()
        out[f"founder.d1.{k}.median"] = {"value": float(x.median()), "n": int(len(x)), "level": "A"}
    sub = founder[founder["inv_pr3"].notna()]
    out["fvinv.founder.firm_pr3.d1.median"] = {
        "value": float(sub["inv_firm"].median()),
        "n": int(len(sub)),
        "level": "A",
    }
    out["fvinv.founder.pr3.d1.median"] = {"value": float(sub["inv_pr3"].median()), "n": int(len(sub)), "level": "A"}
    for g, d in (("forced", forced), ("retired", retired)):
        f = d[d["followed60"] == True]  # noqa: E712
        out[f"exit.{g}.bankruptcy_5y"] = {"value": float(f["bankrupt60"].mean()), "n": int(len(f)), "level": "A"}
    wd = R[R["dated"] == 1]
    put("car.conduct.mm_m1p1.mean", wd[(wd.forced == 1) & (wd.why == "scandal")]["car"])
    put("car.criminal.mm_m1p1.mean", wd[(wd.forced == 1) & (wd.why == "fraud")]["car"])
    (HERE / "out").mkdir(exist_ok=True)
    R.to_csv(HERE / "out" / "headline_events.csv", index=False)  # per-event check file, kept off git
    (HERE / "headline_recomputed.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
