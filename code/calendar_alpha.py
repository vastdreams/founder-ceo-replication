"""Calendar-time alpha: the long run measured as a risk-adjusted return, not only against the market or a matched firm.

Each calendar month, the portfolio holds every firm whose board fired its CEO (for any reason but a crime, sample.py)
in the previous 1 to H months, equally weighted and value-weighted by market value at the fiscal year-end before the
event. The portfolio's return minus the risk-free rate is regressed on the Fama-French five factors and momentum;
the intercept is the alpha, the average monthly return the factors do not explain (Fama 1998; Lyon, Barber and Tsai
1999). The same is done for retirements, and for the firing-minus-retirement portfolio. Months with fewer than 10
firms in a portfolio are dropped. A firm that stops trading takes its delisting return in its last month (0 for a
takeover, -100% for a bankruptcy, -30% otherwise, as event_study.py), after which it leaves the portfolio.

Inputs : analysis/out/returns.parquet (via stats_returns.load_labelled), out/ops_matched.parquet (market value),
         datasource.prices, datasource.actions, datasource.factors
Output : outputs/alpha_stats.json (alpha.{group}.{weight}.{H}m: monthly alpha, t, months, mean firms)
"""

import json
import pathlib

import datasource
import numpy as np
import pandas as pd
import statsmodels.api as sm
from event_study import delist_return
from stats_returns import load_labelled

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "outputs"
MIN_FIRMS = 10
R: dict = {}


def put(key, value, **kw):
    R[key] = {"value": None if value is None or not np.isfinite(value) else float(value), **kw}


def monthly_returns(tickers) -> pd.DataFrame:
    """Calendar-month total returns per security, with the delisting return added in the last month."""
    p = datasource.prices(tickers)
    p["month"] = p["date"].dt.to_period("M")
    last = p.groupby(["ticker", "month"])["closeadj"].last().reset_index()
    last["ret"] = last.groupby("ticker")["closeadj"].pct_change()
    acts = datasource.actions(tickers)
    acts["date"] = pd.to_datetime(acts["date"])
    lastday = p.groupby("ticker")["date"].max()
    end = p["date"].max() - pd.Timedelta(days=45)
    for t, day in lastday.items():
        if day >= end:
            continue  # still trading at the end of the data
        _, dl = delist_return(acts[acts["ticker"] == t], day)
        i = last.index[(last["ticker"] == t) & (last["month"] == day.to_period("M"))]
        if len(i):
            last.loc[i, "ret"] = (1 + last.loc[i, "ret"].fillna(0)) * (1 + dl) - 1
    return last.dropna(subset=["ret"])[["ticker", "month", "ret"]]


def monthly_factors() -> pd.DataFrame:
    f = datasource.factors()
    f["month"] = f["date"].dt.to_period("M")
    cols = ["mkt_rf", "smb", "hml", "rmw", "cma", "mom", "rf"]
    g = f.groupby("month")[cols].apply(lambda x: (1 + x / 100).prod() - 1)
    return g


def portfolio(events: pd.DataFrame, rets: pd.DataFrame, horizon: int, weight: str) -> pd.DataFrame:
    """Monthly portfolio return of the firms in months 1..horizon after their event."""
    rows = []
    for _, e in events.iterrows():
        start = pd.Timestamp(e["event_date"]).to_period("M") + 1
        rows.append(
            pd.DataFrame(
                {
                    "ticker": e["ticker"],
                    "month": pd.period_range(start, periods=horizon, freq="M"),
                    "w": e["mcap_m1"] if weight == "vw" else 1.0,
                }
            )
        )
    hold = pd.concat(rows).merge(rets, on=["ticker", "month"], how="inner").dropna(subset=["w"])
    hold = hold[hold["w"] > 0]
    g = hold.groupby("month")
    port = pd.DataFrame({"ret": g.apply(lambda x: np.average(x["ret"], weights=x["w"])), "n": g.size()})
    return port[port["n"] >= MIN_FIRMS]


def alpha(port: pd.DataFrame, fac: pd.DataFrame, excess: bool = True):
    x = port.join(fac, how="inner")
    y = x["ret"] - (x["rf"] if excess else 0)
    m = sm.OLS(y, sm.add_constant(x[["mkt_rf", "smb", "hml", "rmw", "cma", "mom"]])).fit(
        cov_type="HAC", cov_kwds={"maxlags": 6}
    )
    return (
        m.params["const"],
        m.tvalues["const"],
        m.pvalues["const"],
        int(m.nobs),
        float(x["n"].mean()) if "n" in x else None,
    )


def main():
    d = load_labelled()
    ops = pd.read_parquet(HERE / "out" / "ops_matched.parquet")[["event_id", "mcap_m1"]]
    d = d.merge(ops, on="event_id", how="left").dropna(subset=["ticker", "event_date"])
    groups = {
        "forced": d[d["forced"] == 1],
        "retired": d[d["forced"] == 0],
        "forced_founder": d[(d["forced"] == 1) & (d["founder_v0"] == 1)],
        "conduct": d[(d["forced"] == 1) & (d["conduct"] == 1)],
    }
    rets = monthly_returns(d["ticker"].unique())
    fac = monthly_factors()
    for h in (12, 36):
        for wt in ("ew", "vw"):
            ports = {}
            for g, ev in groups.items():
                port = portfolio(ev, rets, h, wt)
                ports[g] = port
                if len(port) < 24:
                    continue
                a, t, p, n, firms = alpha(port, fac)
                put(f"alpha.{g}.{wt}.{h}m", a, t=t, p=p, n=n, firms=firms)
            diff = ports["forced"][["ret"]].join(ports["retired"][["ret"]], rsuffix="_r", how="inner")
            diff = pd.DataFrame({"ret": diff["ret"] - diff["ret_r"], "n": ports["forced"]["n"].reindex(diff.index)})
            a, t, p, n, firms = alpha(diff, fac, excess=False)
            put(f"alphadiff.forced_vs_retired.{wt}.{h}m", a, t=t, p=p, n=n, firms=firms)
    OUT.joinpath("alpha_stats.json").write_text(json.dumps(R, indent=1))
    for k, v in R.items():
        print(
            f"{k:42s} {v['value'] * 100 if v['value'] is not None else None!s:>10.10} %/month  t={v.get('t'):.2f} months={v.get('n')} firms={v.get('firms')}"
        )


if __name__ == "__main__":
    main()
