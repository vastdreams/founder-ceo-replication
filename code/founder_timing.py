"""When the news trades: the announcement day against the long horizon (paper/DECISIONS.md D-46).

Two steps, so the heavy price work runs on the server and the analysis runs anywhere.

  python founder_timing.py extract EVENTS.csv OUTDIR   (on the database host, memory-capped)
      For every well-dated firing in EVENTS.csv: the firm's buy-and-hold index from the close of trading day -31 to
      day +130 (founder_value.Book, the paper's delisting rule), the equal-weighted industry index on the same days
      (founder_alpha.industry_pools, close-to-close), and the firm's split-adjusted open and close on days -1 to +2
      (sharadar.sep; open x closeadj/close). Also SPY's daily open, close and adjusted close (fmp_daily_prices) and the
      daily Fama-French five factors plus momentum. Writes paths.csv.gz, opens.csv.gz, spy.csv.gz, ff.csv.gz.

  python founder_timing.py release DIR     (EDGAR 8-K acceptance times -> DIR/release.csv; needs DIR/events.csv)
  python founder_timing.py minute DIR      (Alpha Vantage 1-minute bars -> DIR/minute.csv)
  python founder_timing.py analyse DIR
      DIR holds the four extracts, events.csv and release.csv (release class per event from the 8-K acceptance time).
      Writes outputs/founder_timing_stats.json and the tables behind paper/founder_cases/timing.md.

Windows are relative to the first tradeable day t* (day 0 for releases before the open or during trading hours, day
+1 for releases after the close; unknown releases keep day 0): run-up -30..-2 before day 0; on t* the overnight gap
(prior close to open) and the trading day (open to close), each against SPY's own; t*+1; +2..+5, +6..+20, +21..+60
after t*; 6 months (126 days) from the close of t*. Benchmarks: SPY with dividends (primary) and the industry
equal-weighted mean (close-to-close only). Tests per window: mean with the skewness-adjusted t (Lyon, Barber and Tsai
1999) and a firm-clustered t, median with the Wilcoxon signed-rank test; Holm across windows within each group.
Trading rules short the firm and hold SPY, from the open or the close of t*, to +5, +20, +60 and +126 days, net of 20
and 50 bp; daily calendar-time alpha (CAPM; five factors plus momentum; Newey-West lag 5) for the close-of-t* holds.
Minimum detectable effect = 2.8 x standard error (80% power, 5% two-sided).
"""

import json
import os
import pathlib
import sys

import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).parent
PRE, POST = 31, 130  # path from the close of day -31 to the close of day +130


def extract(events_csv, outdir):
    import datasource
    import founder_alpha as fa
    import founder_value as fv

    out = pathlib.Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    d = pd.read_csv(events_csv, parse_dates=["day0"])
    ff = datasource.factors()
    ff["date"] = pd.to_datetime(ff["date"])
    ff = ff.set_index("date").sort_index()
    cal = ff.index
    mkt = (ff["mkt_rf"].astype(float) + ff["rf"].astype(float)) / 100.0
    M = np.cumprod(1 + mkt.values)
    pools = fa.industry_pools(d)
    tickers = set(d["ticker"].dropna()) | {t for ts in pools.values() for t in ts}
    px = fa.load_prices(tickers, cal)
    act = datasource._sql("select ticker, date::date as date, action from sharadar.actions")
    act["date"] = pd.to_datetime(act["date"])
    act = act[act["ticker"].isin(px.columns)]
    book = fv.Book(px, M, fv.delist_table(act, px))
    rows, opn = [], []
    for e in d.itertuples():
        if e.ticker not in book.col or e.day0 not in cal:
            continue
        p0 = cal.get_loc(e.day0)
        ib = p0 - PRE
        if ib < 0:
            continue
        me = [book.col[e.ticker]]
        pool = np.array([book.col[t] for t in pools.get(e.event_id, []) if t in book.col], dtype=int)
        n = min(PRE + POST, len(cal) - 1 - ib)
        firm = [0.0] + [book.ret(me, ib, ib + k)[0] for k in range(1, n + 1)]
        ind = [0.0]
        for k in range(1, n + 1):
            x = book.ret(pool, ib, ib + k) if len(pool) else np.array([])
            x = x[~np.isnan(x)]
            ind.append(x.mean() if len(x) >= 3 else np.nan)
        rows.append({"event_id": e.event_id, "base": cal[ib].date(), "firm": json.dumps(firm), "ind": json.dumps(ind)})
        days = [cal[p0 + j] for j in (-1, 0, 1, 2) if 0 <= p0 + j < len(cal)]
        opn.append({"event_id": e.event_id, "ticker": e.ticker, "dates": [x.date() for x in days]})
    pd.DataFrame(rows).to_csv(out / "paths.csv.gz", index=False, compression="gzip")
    # split-adjusted open and close on days -1..+2 for each event
    want = {(o["ticker"], dd) for o in opn for dd in o["dates"]}
    tk = tuple(sorted({t for t, _ in want}))
    sep = datasource._sql(
        "select ticker, date, open, close, closeadj from sharadar.sep where ticker in %(t)s and close > 0",
        {"t": tk},
    )
    sep["date"] = pd.to_datetime(sep["date"]).dt.date
    sep = sep[[(t, dd) in want for t, dd in zip(sep["ticker"], sep["date"])]]
    sep.to_csv(out / "opens.csv.gz", index=False, compression="gzip")
    spy = datasource._sql(
        "select date, open, close, adj_close from public.fmp_daily_prices where symbol = 'SPY' and close > 0 order by date"
    )
    tr = datasource.sp500()  # SPY with dividends reinvested (the paper's S&P 500 total return)
    spy["date"] = pd.to_datetime(spy["date"])
    spy = spy.drop(columns=["adj_close"]).merge(tr.rename(columns={"closeadj": "adj_close"}), on="date", how="left")
    spy.to_csv(out / "spy.csv.gz", index=False, compression="gzip")
    ff.reset_index().to_csv(out / "ff.csv.gz", index=False, compression="gzip")
    print("extract", len(rows), "paths", len(sep), "opens", len(spy), "spy")


# --------------------------------------------------------------------------------------------- analysis
R: dict = {}


def put(key, value, **kw):
    if value is None or (isinstance(value, float) and not np.isfinite(value)):
        return
    R[key] = {
        "value": float(value),
        **{k: (float(v) if isinstance(v, (float, np.floating)) else v) for k, v in kw.items()},
    }


def skew_t(x):
    """Lyon, Barber and Tsai (1999) skewness-adjusted t; two-sided p from the normal."""
    from scipy import stats

    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    n = len(x)
    if n < 3 or x.std(ddof=1) == 0:
        return np.nan, np.nan
    s = x.mean() / x.std(ddof=1)
    g = stats.skew(x, bias=False)
    t = np.sqrt(n) * (s + g * s * s / 3 + g / (6 * n))
    return t, 2 * (1 - stats.norm.cdf(abs(t)))


def cluster_t(x, firm):
    """Mean with standard errors clustered by firm (intercept-only OLS)."""
    import statsmodels.api as sm

    x = np.asarray(x, float)
    ok = np.isfinite(x)
    x, g = x[ok], np.asarray(firm)[ok]
    if len(x) < 3:
        return np.nan, np.nan, np.nan
    m = sm.OLS(x, np.ones(len(x))).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(g)[0]})
    return m.tvalues[0], m.pvalues[0], m.bse[0]


def describe(key, x, firm):
    from scipy import stats

    x = np.asarray(x, float)
    ok = np.isfinite(x)
    n = int(ok.sum())
    if n < 10:
        put(key + ".n", n, n=n)
        return None
    xs, fs = x[ok], np.asarray(firm)[ok]
    st, sp = skew_t(xs)
    ct, cp, se = cluster_t(xs, fs)
    w = stats.wilcoxon(xs) if np.any(xs != 0) else None
    put(key + ".mean", xs.mean(), n=n, t=st, p=sp, t_cluster=ct, p_cluster=cp, se=se, mde=2.8 * se)
    put(key + ".median", np.median(xs), n=n, p=(w.pvalue if w is not None else np.nan))
    put(key + ".share_negative", float((xs < 0).mean()), n=n)
    return sp


def holm(keys):
    ps = [(k, R[k]["p"]) for k in keys if k in R and np.isfinite(R[k].get("p", np.nan))]
    ps.sort(key=lambda kv: kv[1])
    m, run = len(ps), 0.0
    for i, (k, p) in enumerate(ps):
        run = max(run, min(1.0, (m - i) * p))
        R[k]["p_holm"] = run


def analyse(dirpath):
    import statsmodels.api as sm

    D = pathlib.Path(dirpath)
    ev = pd.read_csv(D / "events.csv", parse_dates=["day0"])
    rel = pd.read_csv(D / "release.csv")
    paths = pd.read_csv(D / "paths.csv.gz", parse_dates=["base"])
    opens = pd.read_csv(D / "opens.csv.gz", parse_dates=["date"])
    spy = pd.read_csv(D / "spy.csv.gz", parse_dates=["date"]).drop_duplicates("date")
    if spy["adj_close"].isna().all() and (D / "sp500.csv.gz").exists():  # extracts made before the total-return merge
        tr = pd.read_csv(D / "sp500.csv.gz", parse_dates=["date"]).rename(columns={"closeadj": "adj_close"})
        spy = spy.drop(columns=["adj_close"]).merge(tr, on="date", how="left")
    spy = spy.set_index("date").sort_index()
    ff = pd.read_csv(D / "ff.csv.gz", parse_dates=["date"]).set_index("date").sort_index()
    cal = ff.index
    for c in ("open", "close", "adj_close"):
        spy[c] = spy[c].astype(float)
    spy = spy.reindex(cal)
    spy_adj = spy["adj_close"].ffill()
    spy_open_adj = spy["open"] * spy["adj_close"] / spy["close"]
    d = ev.merge(rel, on="event_id", how="left").merge(paths, on="event_id", how="inner")
    d["cls"] = d["cls"].fillna("unknown")
    d["main"] = np.where(d["group"] == "forced", 1, 0)
    opens["key"] = list(zip(opens["ticker"], opens["date"]))
    oadj = {k: (o * a / c, a) for k, o, c, a in zip(opens["key"], opens["open"], opens["close"], opens["closeadj"])}
    recs, daily = [], []
    for e in d.itertuples():
        firm = np.array(json.loads(e.firm), float)
        ind = np.array(json.loads(e.ind), float)
        ib = cal.get_loc(e.base)
        idx = lambda k, ib=ib: ib + PRE + k  # cal row of day k (relative to day 0)  # noqa: E731
        s = 1 if e.cls == "after_close" else 0  # t* offset
        F = 1 + firm
        Ix = 1 + ind

        def fr(a, b, F=F, Ix=Ix, idx=idx):  # firm and benchmarks, close of day a to close of day b
            ia, ibb = PRE + a, PRE + b
            if ia < 0 or ibb >= len(F):
                return np.nan, np.nan, np.nan
            f = F[ibb] / F[ia] - 1
            sp = spy_adj.iloc[idx(b)] / spy_adj.iloc[idx(a)] - 1
            i = Ix[ibb] / Ix[ia] - 1 if np.isfinite(Ix[ia]) and np.isfinite(Ix[ibb]) else np.nan
            return f, sp, i

        r = {"event_id": e.event_id, "ticker": e.ticker, "group": e.group, "who": e.who, "cls": e.cls}
        for name, a, b in (
            ("runup", -31, -2),
            ("t1", s, s + 1),
            ("p2_5", s + 1, s + 5),
            ("p6_20", s + 5, s + 20),
            ("p21_60", s + 20, s + 60),
            ("p6m", s, s + 126),
            ("day0_1", -2, 1),
        ):
            f, sp, i = fr(a, b)
            r[f"{name}_sp"] = f - sp
            r[f"{name}_ind"] = f - i
        # t*: overnight gap and trading day, split-adjusted, against SPY's own
        t0 = cal[idx(s)] if idx(s) < len(cal) else None
        tm1 = cal[idx(s - 1)]
        o = oadj.get((e.ticker, t0)) if t0 is not None else None
        pc = oadj.get((e.ticker, tm1))
        if o is not None and pc is not None and np.isfinite(o[0]) and pc[1] > 0 and o[0] > 0:
            ov = o[0] / pc[1] - 1
            td = o[1] / o[0] - 1
            spo = spy_open_adj.loc[t0] / spy_adj.loc[tm1] - 1
            spd = spy_adj.loc[t0] / spy_open_adj.loc[t0] - 1
            r["gap_sp"], r["day_sp"] = ov - spo, td - spd
            r["t0_sp"] = (1 + ov) * (1 + td) - 1 - ((1 + spo) * (1 + spd) - 1)
            r["open_rel"] = o[0] / pc[1]  # for the open-entry rules
        f, sp, i = fr(s - 1, s)
        r["t0cc_sp"], r["t0cc_ind"] = f - sp, f - i
        # trading rules: short the firm, long SPY; from the close of t* (and from the open of t*)
        for h in (5, 20, 60, 126):
            f, sp, _ = fr(s, s + h)
            r[f"rule_close_{h}"] = sp - f
            if "open_rel" in r and PRE + s + h < len(F):
                # from the open of t*: firm return = close(t*+h)/open(t*); SPY likewise
                f_open = (F[PRE + s + h] / F[PRE + s - 1]) / r["open_rel"] - 1
                sp_open = spy_adj.iloc[idx(s + h)] / spy_open_adj.loc[t0] - 1
                r[f"rule_open_{h}"] = sp_open - f_open
        recs.append(r)
        # daily firm returns after the close of t*, for calendar-time portfolios (126 days)
        for k in range(1, 127):
            j = PRE + s + k
            if j >= len(F) or not np.isfinite(F[j]) or not np.isfinite(F[j - 1]):
                break
            daily.append((cal[idx(s + k)], e.event_id, e.who, e.group, F[j] / F[j - 1] - 1, k))
    w = pd.DataFrame(recs)
    w.to_csv(D / "timing_events.csv", index=False)
    cells = {"founder": (w["group"] == "forced") & (w["who"] == "founder"), "forced": w["group"] == "forced"}
    wins = ["runup", "gap", "day", "t0", "t0cc", "t1", "p2_5", "p6_20", "p21_60", "p6m", "day0_1"]
    for g, m in cells.items():
        sub = w[m]
        put(f"tm.{g}.n", len(sub), n=len(sub))
        for c in ("before_open", "during", "after_close", "unknown"):
            put(f"tm.{g}.cls.{c}", int((sub["cls"] == c).sum()), n=len(sub))
        keys = []
        for win in wins:
            for b in ("sp", "ind"):
                col = f"{win}_{b}"
                if col not in sub:
                    continue
                describe(f"tm.{g}.{win}.{b}", sub[col], sub["ticker"])
                keys.append(f"tm.{g}.{win}.{b}.mean")
        holm([k for k in keys if k.endswith(".sp.mean")])
        holm([k for k in keys if k.endswith(".ind.mean")])
        for c in ("before_open", "during", "after_close", "unknown"):
            ss = sub[sub["cls"] == c]
            for win in ("gap", "day", "t0", "t1", "p2_5", "p6_20"):
                col = f"{win}_sp"
                if col in ss:
                    describe(f"tm.{g}.bycls.{c}.{win}.sp", ss[col], ss["ticker"])
        # a rule is tradeable only when the entry comes after the release: the open of t* for releases before the
        # open or after the previous close; the close of t* for every release with a known time. The all-events rows
        # (unknown times included) are reported beside them as an upper bound.
        subsets = {
            "open": {"known": sub["cls"].isin(["before_open", "after_close"]), "all": sub["cls"].notna()},
            "close": {"known": sub["cls"].isin(["before_open", "during", "after_close"]), "all": sub["cls"].notna()},
        }
        for scope in ("known", "all"):
            rk = []
            for entry in ("close", "open"):
                ss = sub[subsets[entry][scope]]
                for h in (5, 20, 60, 126):
                    col = f"rule_{entry}_{h}"
                    if col not in ss:
                        continue
                    x = ss[col].astype(float)
                    key = f"tm.{g}.rule.{scope}.{entry}.{h}"
                    describe(key, x, ss["ticker"])
                    rk.append(key + ".mean")
                    for bp in (20, 50):
                        xn = x - bp / 1e4
                        ok = np.isfinite(xn)
                        if ok.sum() >= 10:
                            put(f"{key}.net{bp}", xn[ok].mean(), n=int(ok.sum()), win_share=float((xn[ok] > 0).mean()))
            holm(rk)
    # calendar-time daily alpha of the firm portfolio held after the close of t*
    dd = pd.DataFrame(daily, columns=["date", "event_id", "who", "group", "ret", "k"])
    dd = dd[np.isfinite(dd["ret"])]
    fx = ff.copy()
    for c in ("mkt_rf", "smb", "hml", "rmw", "cma", "rf", "mom"):
        fx[c] = fx[c].astype(float) / 100.0
    for g, gm in (
        ("founder", (dd["group"] == "forced") & (dd["who"] == "founder")),
        ("forced", dd["group"] == "forced"),
    ):
        for h in (5, 20, 60, 126):
            sub = dd[gm & (dd["k"] <= h)]
            port = sub.groupby("date")["ret"].agg(["mean", "size"])
            y = (port["mean"] - fx.loc[port.index, "rf"]).astype(float)
            for model, cols in (("capm", ["mkt_rf"]), ("ff6", ["mkt_rf", "smb", "hml", "rmw", "cma", "mom"])):
                X = sm.add_constant(fx.loc[port.index, cols].astype(float))
                fit = sm.OLS(y.values, X.values).fit(cov_type="HAC", cov_kwds={"maxlags": 5})
                a, se = fit.params[0], fit.bse[0]
                put(
                    f"tm.{g}.ctime.{h}.{model}",
                    a,
                    n=int(len(y)),
                    t=fit.tvalues[0],
                    p=fit.pvalues[0],
                    se=se,
                    mde=2.8 * se,
                    firms_avg=float(port["size"].mean()),
                    unit="daily alpha",
                )
    # intraday path after release (Alpha Vantage minute bars), firm minus SPY from the first trade after release
    if (D / "minute.csv").exists():
        mn = pd.read_csv(D / "minute.csv").merge(
            w[["event_id", "group", "who", "ticker", "cls", "t0_sp"]], on="event_id"
        )
        mn = mn[mn["have"] == 1]
        # keep a minute series only if its session matches the firm's daily bar (Sharadar): Alpha Vantage may serve
        # today's owner of a reused ticker
        oo = opens.copy()
        oo["tstar"] = oo["date"].dt.strftime("%Y-%m-%d")
        mn = mn.merge(
            oo[["ticker", "tstar", "open", "close"]].rename(columns={"open": "s_open", "close": "s_close"}),
            on=["ticker", "tstar"],
            how="left",
        )
        # compare the session's open-to-close return, not price levels (Alpha Vantage's adjusted series also
        # adjusts for dividends): within 1 percentage point
        okm = abs((mn["av_close"] / mn["av_open"]) - (mn["s_close"] / mn["s_open"])) < 0.01
        put("tm.minute.checked", int(len(mn)), n=int(len(mn)), kept=int(okm.sum()))
        mn = mn[okm]
        for g, m in (
            ("founder", (mn["group"] == "forced") & (mn["who"] == "founder")),
            ("forced", mn["group"] == "forced"),
        ):
            sub = mn[m]
            put(f"tm.{g}.minute.n", len(sub), n=len(sub))
            for c in ("m5", "m30", "m60", "close"):
                describe(f"tm.{g}.minute.{c}", sub[c], sub["ticker"])
            # share of the move from the first trade to the close of t* that is in place after 30 minutes
            ok = np.isfinite(sub["m30"]) & np.isfinite(sub["close"]) & (sub["close"].abs() > 0.005)
            if ok.sum() >= 10:
                put(
                    f"tm.{g}.minute.share30",
                    float(np.median(sub.loc[ok, "m30"] / sub.loc[ok, "close"])),
                    n=int(ok.sum()),
                )
    out = HERE.parent / "outputs" / "founder_timing_stats.json"
    out.write_text(json.dumps({"source": "analysis/founder_timing.py (D-46)", "statistics": R}, indent=1, default=str))
    print("wrote", out, len(R))


# --------------------------------------------------------------------------------------------- release time
def release(dirpath):
    """8-K acceptance times from EDGAR (data.sec.gov submissions; User-Agent per D-46) -> DIR/eightk.csv and the
    release class per event -> DIR/release.csv. Run from DIR (it caches EDGAR responses in DIR/edgar/)."""
    import os

    os.chdir(dirpath)
    pathlib.Path("edgar").mkdir(exist_ok=True)
    import time
    import urllib.error
    import urllib.request

    UA = os.environ["SEC_USER_AGENT"]  # the SEC asks for a name and contact address; set it in the environment
    C = pathlib.Path("edgar")
    last = [0.0]

    def get(url, path):
        p = C / path
        if p.exists():
            return json.loads(p.read_text())
        for k in range(5):
            dt = time.time() - last[0]
            if dt < 0.15:
                time.sleep(0.15 - dt)
            last[0] = time.time()
            try:
                req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
                with urllib.request.urlopen(req, timeout=30) as r:  # nosec B310 - fixed https URL
                    b = r.read()
                p.write_bytes(b)
                return json.loads(b)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    p.write_text("{}")
                    return {}
                time.sleep(2**k)
            except Exception:
                time.sleep(2**k)
        return None

    ev = pd.read_csv("events.csv")
    ciks = sorted({int(c) for c in ev.cik.dropna()})
    rows = []
    for n, cik in enumerate(ciks):
        j = get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json", f"CIK{cik:010d}.json")
        if not j:
            continue
        blocks = [j.get("filings", {}).get("recent", {})]
        for f in j.get("filings", {}).get("files", []):
            jj = get("https://data.sec.gov/submissions/" + f["name"], f["name"])
            if jj:
                blocks.append(jj)
        for b in blocks:
            if not b or "form" not in b:
                continue
            for i, form in enumerate(b["form"]):
                if form.startswith("8-K"):
                    rows.append(
                        dict(  # noqa: C408
                            cik=cik,
                            form=form,
                            filingDate=b["filingDate"][i],
                            accept=b["acceptanceDateTime"][i],
                            items=b.get("items", [""] * len(b["form"]))[i],
                            acc=b["accessionNumber"][i],
                            doc=b.get("primaryDocument", [""] * len(b["form"]))[i],
                        )
                    )
        if n % 50 == 0:
            print(n, len(rows), flush=True)
    pd.DataFrame(rows).to_csv("eightk.csv", index=False)
    print("done", len(ciks), len(rows))
    ev = pd.read_csv("events.csv", parse_dates=["day0", "date_departure_announced"])
    k = pd.read_csv("eightk.csv", dtype={"items": str})
    k["filingDate"] = pd.to_datetime(k["filingDate"])
    k["accept"] = (
        pd.to_datetime(k["accept"], utc=True, errors="coerce").dt.tz_convert("America/New_York").dt.tz_localize(None)
    )
    k = k.dropna(subset=["accept"])
    # EDGAR acceptanceDateTime is UTC: the hour distribution peaks at 11-13 and 20-22 UTC, i.e. 6-8 am and 4-6 pm New York
    rows = []
    for e in ev.itertuples():
        D = e.date_departure_announced if pd.notna(e.date_departure_announced) else e.day0
        c = k[
            (k.cik == int(e.cik))
            & (k.accept.dt.normalize() >= D - pd.Timedelta(days=3))
            & (k.accept.dt.normalize() <= D + pd.Timedelta(days=1))
        ]
        if len(c) == 0:
            rows.append(dict(event_id=e.event_id, cls="unknown", accept=None, items=None, n8k=0))  # noqa: C408
            continue
        c = c.sort_values("accept")
        # the earliest 8-K accepted from the evening of the day before D to the end of D
        d0 = D.normalize()
        win = c[
            ((c.accept.dt.normalize() == d0 - pd.Timedelta(days=1)) & (c.accept.dt.hour >= 16))
            | (
                (c.accept.dt.normalize() < d0)
                & (c.accept.dt.normalize() >= d0 - pd.Timedelta(days=3))
                & (c.accept.dt.dayofweek >= 4)
                & (c.accept.dt.hour >= 16)
            )
            | (c.accept.dt.normalize() == d0)
        ]
        if len(win) == 0:
            # no 8-K on day D, but one before the open of the next weekday: the news first traded at that open
            nxt = c[
                (c.accept.dt.normalize() > d0)
                & (c.accept.dt.normalize() <= d0 + pd.Timedelta(days=3))
                & (c.accept.dt.hour + c.accept.dt.minute / 60 < 9.5)
            ]
            if len(nxt) and d0 == e.day0.normalize():
                rows.append(
                    dict(  # noqa: C408
                        event_id=e.event_id,
                        cls="after_close",
                        accept=str(nxt.accept.iloc[0]),
                        items=nxt["items"].iloc[0],
                        n8k=len(c),
                        rule="next_premarket",
                    )
                )
                continue
            rows.append(
                dict(  # noqa: C408
                    event_id=e.event_id,
                    cls="unknown",
                    accept=str(c.accept.iloc[0]),
                    items=c["items"].iloc[0],
                    n8k=len(c),
                )
            )
            continue
        a = win.accept.iloc[0]
        hm = a.hour + a.minute / 60
        if d0 < e.day0.normalize():
            cls = "before_open"  # announced on a non-trading day: first trades at the open of day 0
        elif a.normalize() < d0:
            cls = "before_open"  # filed after the previous close: the news first trades at the open of day 0
        elif hm < 9.5:
            cls = "before_open"
        elif hm < 16:
            cls = "during"
        else:
            cls = "after_close"
        rows.append(
            dict(event_id=e.event_id, cls=cls, accept=str(a), items=win["items"].iloc[0], n8k=len(c))  # noqa: C408
        )  # noqa: C408
    r = pd.DataFrame(rows)
    r.to_csv("release.csv", index=False)
    m = ev.merge(r, on="event_id")
    print(m.groupby(["group", "who"])["cls"].value_counts().unstack(fill_value=0))


# --------------------------------------------------------------------------------------------- minute bars
def minute(dirpath):
    """Alpha Vantage 1-minute bars (ALPHA_VANTAGE_API_KEY from the environment) on the first tradeable day for every
    event with a known release time: firm minus SPY from the first trade after release to +5, +30, +60 minutes and to
    the close -> DIR/minute.csv. Run from DIR (cache in DIR/av/)."""
    import os

    os.chdir(dirpath)
    pathlib.Path("av").mkdir(exist_ok=True)

    import time
    import urllib.request

    KEY = os.environ["ALPHA_VANTAGE_API_KEY"]
    C = pathlib.Path("av")
    last = [0.0]

    def bars(sym, month):
        p = C / f"{sym}_{month}.json"
        if p.exists():
            return json.loads(p.read_text())
        dt = time.time() - last[0]
        if dt < 0.85:
            time.sleep(0.85 - dt)
        last[0] = time.time()
        url = (
            f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={sym}&interval=1min&month={month}"
            f"&outputsize=full&extended_hours=false&adjusted=true&apikey={KEY}"
        )
        try:
            with urllib.request.urlopen(url, timeout=60) as r:  # nosec B310 - fixed https URL
                j = json.loads(r.read())
        except Exception:
            return {}
        if "Time Series (1min)" in j or "Error Message" in j:
            p.write_text(json.dumps(j))
        return j

    def series(sym, day):
        j = bars(sym, day.strftime("%Y-%m"))
        ts = j.get("Time Series (1min)") or {}
        rows = [
            (pd.Timestamp(k), float(v["4. close"]), float(v["1. open"]))
            for k, v in ts.items()
            if k.startswith(day.strftime("%Y-%m-%d"))
        ]
        if not rows:
            return None
        s = pd.DataFrame(rows, columns=["t", "close", "open"]).set_index("t").sort_index()
        return s

    ev = pd.read_csv("events.csv", parse_dates=["day0"])
    rel = pd.read_csv("release.csv", parse_dates=["accept"])
    cal = pd.read_csv("ff.csv.gz", parse_dates=["date"])["date"]
    cal = pd.DatetimeIndex(cal)
    d = ev.merge(rel, on="event_id")
    d = d[d.cls.isin(["before_open", "during", "after_close"])]
    out = []
    for e in d.itertuples():
        p0 = cal.searchsorted(e.day0)
        if p0 >= len(cal):
            continue
        tstar = cal[p0 + (1 if e.cls == "after_close" else 0)] if p0 + 1 < len(cal) else None
        if tstar is None:
            continue
        f = series(e.ticker, tstar)
        s = series("SPY", tstar)
        if f is None or s is None or len(f) < 30:
            out.append(dict(event_id=e.event_id, have=0))  # noqa: C408
            continue
        # first trade after release: the open for before_open/after_close; the first bar after acceptance for during
        if e.cls == "during" and pd.notna(e.accept):
            start = pd.Timestamp(tstar.date()) + (e.accept - e.accept.normalize())
        else:
            start = pd.Timestamp(tstar.date()) + pd.Timedelta(hours=9, minutes=31)
        day_open, day_close = f["open"].iloc[0], f["close"].iloc[-1]  # whole session, to check the series is this firm
        f = f[f.index >= start - pd.Timedelta(minutes=1)]
        s = s.reindex(f.index).ffill()
        if len(f) < 5 or s["close"].isna().all():
            out.append(dict(event_id=e.event_id, have=0))  # noqa: C408
            continue
        f0, s0 = f["open"].iloc[0], s["open"].iloc[0] if np.isfinite(s["open"].iloc[0]) else s["close"].iloc[0]
        r = {
            "event_id": e.event_id,
            "have": 1,
            "start": str(f.index[0]),
            "av_open": day_open,
            "av_close": day_close,
            "tstar": str(tstar.date()),
        }
        for m in (5, 30, 60):
            j = min(m - 1, len(f) - 1)
            r[f"m{m}"] = (f["close"].iloc[j] / f0 - 1) - (s["close"].iloc[j] / s0 - 1)
        r["close"] = (f["close"].iloc[-1] / f0 - 1) - (s["close"].iloc[-1] / s0 - 1)
        out.append(r)
    pd.DataFrame(out).to_csv("minute.csv", index=False)
    print(pd.DataFrame(out).have.value_counts())


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "extract":
        sys.path.insert(0, str(HERE))
        extract(sys.argv[2], sys.argv[3])
    elif cmd == "release":
        release(sys.argv[2])
    elif cmd == "minute":
        minute(sys.argv[2])
    else:
        analyse(sys.argv[2])
