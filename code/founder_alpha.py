"""What an investor earns after a founder firing, against the stock market (paper/DECISIONS.md D-43).

Forward-looking: the position is opened once the firing is public, at the close of trading day +1 after the
announcement (well-dated firings; robustness: the close of day 0, and every firing entered at the close of the
trading day after the database's left_ceo_office date). Horizons are 1, 3, 6, 12 and 36 months of 21 trading days.

Benchmarks: the S&P 500 total return (SPY, dividend-adjusted; primary), and as context rows the industry average and
the mean of the three closest competitors, both as defined in founder_value.py.

Measures, per group, entry rule, benchmark and horizon
  $100 in the firm against $100 in the benchmark: mean and median value; share of firms ending above the benchmark
  buy-and-hold gap (firm minus benchmark): mean with the skewness-adjusted t of Lyon, Barber and Tsai (1999) and a
            bootstrap p-value and 95% interval (10,000 draws, seed fixed); median with the Wilcoxon signed-rank test
  calendar-time portfolio: each calendar month, every firm in months 1..H after the month of entry, equal- and
            value-weighted (market value at day -31); excess return on the market (CAPM) and on the five Fama-French
            factors plus momentum, Newey-West lag 6; every month with at least one firm; Holm across the five holding
            periods per weighting and model; minimum detectable alpha = 2.8 x its standard error (80% power, 5%)

Delisting: founder_value.Book (the delisting return, then the proceeds held in the market to the end of the window);
calendar portfolios use calendar_alpha.monthly_returns (the delisting return in the last month).

Groups: founder (a founder fired for any reason but fraud: the main sample), forced (every firing but fraud) and
retired (voluntary retirements) as context; founder firings over fraud and over a personal scandal are named case by
case ($100 against the S&P 500 at 12 months), never averaged.

Reuse: founder_value.py reports the firm-minus-S&P 500 gap from the close of day +1 at 12, 36 and 60 months on every
firing (fv.founder.sp.m12 ...). This script adds the short horizons, the well-dated entry and its robustness, the
$100 line, the share beating the market, the bootstrap and the calendar-time alpha.

Inputs : analysis/out/founder_value.parquet (market value at day -31, the three competitors, the industry), the
         labelled events (founder_value.load_events), datasource.*
Output : outputs/founder_alpha_stats.json (keys fwd.*, fwdalpha.*, fwdcase.*)
"""

import json
import pathlib

import calendar_alpha as ca
import datasource
import founder_value as fv
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "outputs"
R: dict = {}
MIN_CELL = 10
MONTH = 21
HOR = {"m1": 1, "m3": 3, "m6": 6, "m12": 12, "m36": 36}
ENTRIES = ("d1", "d0", "lco")
BENCH = ("sp", "ind", "pr3")
HOLD = (1, 3, 6, 12, 36)
RNG = np.random.default_rng(20261124)
BOOT = 10_000


def put(key, value, **kw):
    ok = value is not None and np.isfinite(value)
    R[key] = {"value": float(value) if ok else None, **{k: v for k, v in kw.items() if v is not None}}


def skew_t(x):
    """Lyon, Barber and Tsai (1999) skewness-adjusted t and its two-sided p (t distribution, n-1)."""
    n = len(x)
    sd = x.std(ddof=1)
    if n < 3 or sd == 0:
        return np.nan, np.nan
    s = x.mean() / sd
    g = stats.skew(x, bias=False)
    t = np.sqrt(n) * (s + g * s * s / 3 + g / (6 * n))
    return t, 2 * stats.t.sf(abs(t), n - 1)


def boot(x):
    """Bootstrap 95% interval of the mean and the p-value of mean = 0 (resampling the centred data)."""
    idx = RNG.integers(0, len(x), size=(BOOT, len(x)))
    means = x[idx].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    centred = means - x.mean()
    p = float(np.mean(np.abs(centred) >= abs(x.mean())))
    return lo, hi, p


def describe(prefix, firm, other):
    m = ~(np.isnan(firm) | np.isnan(other))
    firm, other = firm[m], other[m]
    n = len(firm)
    put(prefix + ".n", n, n=n)
    if n < MIN_CELL:
        return
    gap = firm - other
    put(prefix + ".inv_firm.mean", 100 * (1 + firm.mean()), n=n)
    put(prefix + ".inv_firm.median", 100 * (1 + np.median(firm)), n=n)
    put(prefix + ".inv_bench.mean", 100 * (1 + other.mean()), n=n)
    put(prefix + ".inv_bench.median", 100 * (1 + np.median(other)), n=n)
    put(prefix + ".beat_share", float(np.mean(gap > 0)), n=n, p=float(stats.binomtest(int((gap > 0).sum()), n).pvalue))
    t, p = skew_t(gap)
    lo, hi, pb = boot(gap)
    put(prefix + ".gap.mean", gap.mean(), n=n, t=t, p=p, p_boot=pb, ci_low=lo, ci_high=hi)
    try:
        pw = stats.wilcoxon(gap).pvalue
    except ValueError:
        pw = None
    put(prefix + ".gap.median", float(np.median(gap)), n=n, p=pw)


def industry_pools(d):
    """event_id -> tickers of every other S&P 1500 firm in the same Fama-French industry (founder_value's 'ind')."""
    sf = datasource.fundamentals()[["ticker", "calendardate", "datekey", "marketcap"]]
    sf["marketcap"] = pd.to_numeric(sf["marketcap"], errors="coerce")
    sf["year"] = pd.to_datetime(sf["calendardate"]).dt.year
    sf = sf.sort_values(["ticker", "year", "calendardate", "datekey"], ascending=[True, True, False, True])
    sf = sf.drop_duplicates(["ticker", "year"], keep="first")
    tk = datasource.securities("SF1").sort_values(["ticker", "permaticker"], kind="stable")
    sf = sf.merge(tk[["ticker", "famaindustry", "cik"]].drop_duplicates("ticker"), on="ticker", how="left")
    base = sf.dropna(subset=["marketcap"])
    base = base[base["marketcap"] > 0]
    universe = set(datasource.gvkey_cik()["cik"].dropna().astype(int))
    by_year = dict(list(base.groupby("year")))
    me = base.set_index(["ticker", "year"])["famaindustry"]
    out = {}
    for e in d.itertuples():
        y = e.day0.year - 1
        key = (e.ticker, y)
        if key not in me.index or y not in by_year:
            continue
        fam = me.loc[key]
        if isinstance(fam, pd.Series):
            fam = fam.iloc[0]
        if pd.isna(fam):
            continue
        pool = by_year[y]
        pool = pool[(pool["famaindustry"] == fam) & (pool["ticker"] != e.ticker) & pool["cik"].isin(universe)]
        if len(pool):
            out[e.event_id] = list(pool["ticker"])
    return out


def load_prices(tickers, cal):
    """The cached price matrix of founder_value.py, only the columns needed (D-43 memory limit on Persona)."""
    cache = HERE / "out" / "fv_px_closeadj.parquet"
    asked = set(json.loads((HERE / "out" / "fv_px_closeadj.tickers.json").read_text()))
    if not set(tickers) <= asked:
        return fv.price_matrix(tickers, cal)[sorted(set(tickers))]
    import pyarrow.parquet as pq

    have = set(pq.read_schema(cache).names)
    cols = sorted(set(tickers) & have)
    m = pd.read_parquet(cache, columns=[c for c in cols if c not in ("date", "__index_level_0__")])
    if not isinstance(m.index, pd.DatetimeIndex):  # the index is restored from the pandas metadata
        raise SystemExit("price cache read without its date index")
    return m.reindex(cal)


def monthly_from_matrix(px, dl, data_end):
    """Calendar-month total returns from the daily matrix; a stock that stops trading more than 45 days before the
    end of the data takes its delisting return in its last month (as calendar_alpha.monthly_returns)."""
    me = px.groupby(px.index.to_period("M")).last()
    r = me.pct_change(fill_method=None)
    last = px.apply(lambda s: s.last_valid_index())
    for t, lv in last.items():
        if lv is None or pd.isna(lv) or lv >= data_end - pd.Timedelta(days=45):
            continue
        mth = lv.to_period("M")
        if mth in r.index and pd.notna(r.at[mth, t]):
            r.at[mth, t] = (1 + r.at[mth, t]) * (1 + dl.get(t, -0.30)) - 1
    out = r.stack().rename("ret").reset_index()
    out.columns = ["month", "ticker", "ret"]
    return out


def main():
    d = fv.load_events()
    v = pd.read_parquet(HERE / "out" / "founder_value.parquet")
    keep = [c for c in ("event_id", "mv31", "pr3_ticker") if c in v.columns]
    d = d.merge(v[keep], on="event_id", how="left")
    d["day0"] = pd.to_datetime(d["day0"])
    d["lco"] = pd.to_datetime(d["left_ceo_office"], errors="coerce") if "left_ceo_office" in d else pd.NaT
    if "coname" not in d:
        d["coname"] = d["ticker"]
    d["group"] = np.select(
        [(d["forced"] == 0), (d["forced"] == 1) & (d["criminal"] == 0)], ["retired", "forced"], default="fraud"
    )

    ff = datasource.factors()
    ff["date"] = pd.to_datetime(ff["date"])
    ff = ff.set_index("date").sort_index()
    cal = ff.index
    mkt = (ff["mkt_rf"].astype(float) + ff["rf"].astype(float)) / 100.0
    M = np.cumprod(1 + mkt.values)
    pr3 = {e: str(t).split(";") for e, t in zip(d["event_id"], d["pr3_ticker"]) if isinstance(t, str) and t}
    pool_t = industry_pools(d)
    tickers = (
        set(d["ticker"].dropna()) | {t for ts in pr3.values() for t in ts} | {t for ts in pool_t.values() for t in ts}
    )
    px = load_prices(tickers, cal)
    print("prices", px.shape, flush=True)
    act = datasource._sql("select ticker, date::date as date, action from sharadar.actions")
    act["date"] = pd.to_datetime(act["date"])
    act = act[act["ticker"].isin(px.columns)]
    dl = fv.delist_table(act, px)
    book = fv.Book(px, M, dl)
    pools = {e: np.array([book.col[t] for t in ts if t in book.col], dtype=int) for e, ts in pool_t.items()}
    pools = {e: c for e, c in pools.items() if len(c)}
    spx = datasource.sp500().set_index("date")["closeadj"].astype(float)
    spx = spx[~spx.index.duplicated()].reindex(cal)
    sp_last = spx.last_valid_index()
    SP = spx.ffill().where(cal <= sp_last).values
    px_last = px.apply(lambda s: s.last_valid_index()).dropna().max()
    end = cal.get_loc(min(sp_last, px_last))  # a window must close on or before the end of the data

    def entry_row(e, rule):
        if rule == "lco":
            if pd.isna(e.lco):
                return None
            i = cal.searchsorted(e.lco)
            return i + 1 if i + 1 < len(cal) else None
        if e.dated != 1 or e.day0 not in cal:
            return None
        pos = cal.get_loc(e.day0)
        return pos + 1 if rule == "d1" else pos

    rows = []
    for e in d.itertuples():
        if e.ticker not in book.col:
            continue
        me = book.col[e.ticker]
        comp3 = [book.col[t] for t in pr3.get(e.event_id, []) if t in book.col]
        for rule in ENTRIES:
            i0 = entry_row(e, rule)
            if i0 is None:
                continue
            r = {"event_id": e.event_id, "rule": rule, "entry": cal[i0]}
            for h, months in HOR.items():
                i1 = i0 + MONTH * months
                if i1 > end:
                    continue
                f = book.ret([me], i0, i1)[0]
                r[f"firm_{h}"] = f
                r[f"sp_{h}"] = SP[i1] / SP[i0] - 1 if not (np.isnan(SP[i0]) or np.isnan(SP[i1])) else np.nan
                pool = pools.get(e.event_id)
                if pool is not None:
                    x = book.ret(pool, i0, i1)
                    x = x[~np.isnan(x)]
                    r[f"ind_{h}"] = x.mean() if len(x) >= 3 else np.nan
                if len(comp3) == 3:
                    x = book.ret(comp3, i0, i1)
                    r[f"pr3_{h}"] = x.mean() if not np.isnan(x).any() else np.nan
            rows.append(r)
    w = pd.DataFrame(rows).merge(
        d[["event_id", "group", "who", "why", "ticker", "coname", "mv31", "day0"]], on="event_id", how="left"
    )
    w.to_parquet(HERE / "out" / "founder_alpha.parquet", index=False)

    cells = {
        "founder": (w["group"] == "forced") & (w["who"] == "founder"),
        "forced": w["group"] == "forced",
        "retired": w["group"] == "retired",
    }
    for g, mask in cells.items():
        for rule in ENTRIES:
            s = w[mask & (w["rule"] == rule)]
            for b in BENCH:
                for h in HOR:
                    if f"firm_{h}" not in s or f"{b}_{h}" not in s:
                        continue
                    describe(f"fwd.{g}.{rule}.{b}.{h}", s[f"firm_{h}"].to_numpy(float), s[f"{b}_{h}"].to_numpy(float))

    # named cases: founder firings over fraud or a personal scandal, $100 against the S&P 500 at 12 months
    named = w[(w["who"] == "founder") & ((w["group"] == "fraud") | (w["why"] == "scandal"))]
    for e, g in named.groupby("event_id"):
        r = g[g["rule"] == "d1"]
        r = r if len(r) else g[g["rule"] == "lco"]
        if r.empty or pd.isna(r.iloc[0].get("firm_m12")):
            continue
        r = r.iloc[0]
        why = "fraud" if r["group"] == "fraud" else "scandal"
        put(f"fwdcase.{e}.inv_firm.m12", 100 * (1 + r["firm_m12"]), n=1, firm=r["coname"], why=why, rule=r["rule"])
        put(f"fwdcase.{e}.inv_sp.m12", 100 * (1 + r["sp_m12"]), n=1, firm=r["coname"], why=why, rule=r["rule"])

    # calendar-time portfolios
    ev_t = sorted(set(w["ticker"].dropna()) & set(px.columns))
    rets = monthly_from_matrix(px[ev_t], dl, cal[end])
    del book
    fac = ca.monthly_factors()
    for g, mask in cells.items():
        for rule in ("d1", "lco"):
            ev = w[mask & (w["rule"] == rule)].drop_duplicates("event_id")
            for wt in ("ew", "vw"):
                for model in ("capm", "ff6"):
                    keys = []
                    for H in HOLD:
                        hold = []
                        for e in ev.itertuples():
                            start = pd.Timestamp(e.entry).to_period("M") + 1
                            weight = e.mv31 if wt == "vw" else 1.0
                            if weight is None or not np.isfinite(weight) or weight <= 0:
                                continue
                            hold.append(
                                pd.DataFrame(
                                    {
                                        "ticker": e.ticker,
                                        "month": pd.period_range(start, periods=H, freq="M"),
                                        "w": weight,
                                    }
                                )
                            )
                        if not hold:
                            continue
                        h = pd.concat(hold).merge(rets, on=["ticker", "month"], how="inner")
                        gm = h.groupby("month")
                        port = pd.DataFrame(
                            {"ret": gm.apply(lambda x: np.average(x["ret"], weights=x["w"])), "n": gm.size()}
                        ).join(fac, how="inner")
                        if len(port) < 24:
                            continue
                        cols = ["mkt_rf"] if model == "capm" else ["mkt_rf", "smb", "hml", "rmw", "cma", "mom"]
                        fit = sm.OLS(port["ret"] - port["rf"], sm.add_constant(port[cols])).fit(
                            cov_type="HAC", cov_kwds={"maxlags": 6}
                        )
                        a, se = fit.params["const"], fit.bse["const"]
                        key = f"fwdalpha.{g}.{rule}.{wt}.{model}.{H}m"
                        put(
                            key,
                            a,
                            n=int(fit.nobs),
                            t=float(fit.tvalues["const"]),
                            p=float(fit.pvalues["const"]),
                            se=float(se),
                            ci_low=float(a - 1.96 * se),
                            ci_high=float(a + 1.96 * se),
                            firms=float(port["n"].mean()),
                            firms_min=int(port["n"].min()),
                            mde=float(2.8 * se),
                            vol=float((port["ret"] - port["rf"]).std()),
                        )
                        keys.append(key)
                    # Holm across the holding periods of this weighting and model
                    ps = sorted((R[k]["p"], k) for k in keys if R[k].get("p") is not None)
                    m, run = len(ps), 0.0
                    for i, (p, k) in enumerate(ps):
                        run = max(run, min(1.0, (m - i) * p))
                        R[k]["p_holm"] = run

    OUT.joinpath("founder_alpha_stats.json").write_text(json.dumps(R, indent=1))
    for k in sorted(R):
        if k.startswith(("fwd.founder.d1.sp.", "fwdalpha.founder.d1.")) and (
            "gap" in k or "fwdalpha" in k or "inv" in k
        ):
            r = R[k]
            print(f"{k:48s} {r['value']!s:>12.12} n={r.get('n')} p={r.get('p')} firms={r.get('firms')}")


if __name__ == "__main__":
    main()
