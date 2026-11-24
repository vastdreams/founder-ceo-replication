"""The founder CEO in dollars, against competitors that were doing equally badly (paper/DECISIONS.md D-34).

Main hypothesis (H1): when a board fires a founder CEO, shareholders lose more than when it fires a hired CEO,
measured against competitors that were doing equally badly before. Two-sided; a null is reported as a null.

Competitor benchmarks
  pr   (primary, D-37 item 4) one matched firm in the same 4-digit SIC code, else the same 3-digit SIC code, else the
       same Sharadar industry, market value within 50% at the fiscal year-end before, no CEO change recorded in the
       three years up to the firing, and among those the nearest buy-and-hold return over trading days -282 to -31.
       The level used is recorded per firm (pr_level). With no candidate at any level the firing has no competitor.
  pr34 (robustness, the D-34 match) one matched firm: same Fama-French industry, market value within 30% (fiscal year-end before the
       firing, as ops_matched.py), no CEO change recorded in the three years up to the firing, and among those the
       nearest buy-and-hold return over trading days -282 to -31. Where no firm is inside the 30% band the band is
       widened to a factor of two and the match is flagged (pr_relaxed); with none there either the firing has no
       competitor and is counted as unmatched.
  roa  the paper's existing matched firm (ops_matched.py: same industry and size band, nearest return on assets).
  ind  the equal-weighted mean of every other firm in the same industry that is in the dismissal database's
       universe (S&P 1500 firms), with a price on the first day of the window.
  pr3  (robustness added after review, D-41) the mean return of the three nearest firms on the prior return, chosen
       by the pr rule at the same industry level; a firing with fewer than three candidates has no pr3 number.
  sp   the S&P 500 total return: the SPDR S&P 500 ETF (SPY), dividend-adjusted close (D-34 addendum). It does not
       correct for how the firm was doing before, so it is reported beside the competitor, never in its place. The
       series ends in July 2026; a window that runs past its last day has no S&P 500 number.

Also from the addendum: $100 put in the firm at day -31, against $100 in the competitor and $100 in the S&P 500,
valued at day +1 and at 12, 36 and 60 months from day +2 (inv_*), and the returns of the three over days -282 to -31.

Windows (trading days on the factor calendar; day 0 as event_study.py)
  slide     -30 to -2                       every firing (D-34); slide_wd repeats it on well-dated firings (addendum)
  ann       -1 to +1                        well-dated firings only
  slideann  -30 to +1                       every firing; slideann_wd on well-dated firings (addendum)
  m12, m36, m60  buy-and-hold from day +2 for 252, 756, 1260 trading days, for firings whose horizon is complete
            in returns.parquet. A stock that leaves the price file gets event_study.delist_return and the proceeds
            are held in the market to the end of the window; the same rule is applied to every competitor.

Dollar loss: (firm return - competitor return) x the firm's market value at day -31, in millions of 2023 dollars.
Market value at day -31 is the market value in the latest annual filing dated on or before day -31 (Sharadar SF1,
as reported, measured at the filing date), moved to day -31 by the split-adjusted price. CPI-U (FRED CPIAUCSL)
converts to 2023 dollars. Reported: mean, median and the total across firms, with the percentage return beside each;
means winsorised at 1% and 99% are a robustness row.

Tests: founder minus hired by Welch t (returns and dollars), Mann-Whitney U on the medians, Holm across the six
windows, and a regression of the return and of the signed log dollar change, sign(x) * log(1 + |x|) with x in
millions of dollars, on a founder flag with log market value, the prior 12-month return, return on assets, leverage,
industry and year, standard errors clustered by firm. A cell under MIN_CELL firings gets N and its cases, no mean.

Inputs : analysis/out/{returns,ops_matched,founder_final}.parquet, the reason codes, datasource.*, cpi_u.csv
Outputs: outputs/founder_value_stats.json; analysis/out/founder_value.parquet (one row per firing or retirement);
         analysis/out/founder_value_path.parquet (daily and monthly paths for the figure)
"""

import json
import os
import pathlib

import datasource
import numpy as np
import pandas as pd
import stats_returns as sr
import statsmodels.formula.api as smf
from event_study import DELIST_BANKRUPT, DELIST_ZERO
from scipy import stats

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "outputs"
R = sr.R
R.clear()
put = sr.put
MIN_CELL = 10
COUP = "strategy_or_power_dispute"
HORIZONS = {"m12": 252, "m36": 756, "m60": 1260}
BHR_COL = {"m12": "bhr_1y", "m36": "bhr_3y", "m60": "bhr_5y"}
MAIN_WINDOWS = ("slide", "ann", "slideann", "m12", "m36", "m60")  # the Holm family of D-34
ADDENDUM = ("slide_wd", "slideann_wd")
WINDOWS = MAIN_WINDOWS + ADDENDUM
BENCH = ("pr", "pr34", "roa", "ind", "sp", "pr3", "pr2", "pr4", "pr5")  # pr2/pr4/pr5: review addendum, D-47
LEVELS = ("sic4", "sic3", "industry")  # D-37 item 4: the narrowest industry level with a candidate
NEW_BAND = (0.5, 1.5)  # D-37: market value within 50%
STATS_FILE = os.environ.get("FV_STATS_FILE", "founder_value_stats.json")
# a variant run (another stats file) writes its event rows beside the main ones instead of over them
TAG = (
    ""
    if STATS_FILE == "founder_value_stats.json"
    else "_" + STATS_FILE.replace("founder_value_stats_", "").replace(".json", "")
)
INVEST = {"d1": 0, "m12": 252, "m36": 756, "m60": 1260}  # $100 at day -31, valued at day +1 and after each horizon
PRIOR = (-283, -31)  # price at day -283 to price at day -31: the returns of days -282 to -31


def load_events():
    d = sr.load_labelled(include_criminal=True)
    d = d[d["forced"].isin([0, 1])].copy()
    d["who"] = np.where(d["founder_v0"] == 1, "founder", "hired")
    d["why"] = np.select(
        [d["criminal"] == 1, d["conduct"] == 1, d["reason"] == COUP],
        ["fraud", "scandal", "coup"],
        default="other",
    )
    d["day0"] = pd.to_datetime(d["day0"])
    if os.environ.get("FV_SCREEN") == "1":  # D-38 item 2: drop firings the planned-succession screen flags
        s = pd.read_parquet(HERE / "out" / "screen.parquet")[["event_id", "flag"]]
        flagged = set(s.loc[s["flag"] == 1, "event_id"])
        d = d[~((d["forced"] == 1) & d["event_id"].isin(flagged))].copy()
    return d


def price_matrix(tickers, cal, col="closeadj"):
    """Prices on the factor calendar, one column per ticker, gaps inside a listing carried forward."""
    cache = HERE / "out" / f"fv_px_{col}.parquet"
    tickers = sorted(set(tickers))
    asked = HERE / "out" / f"fv_px_{col}.tickers.json"
    if cache.exists() and asked.exists() and set(tickers) <= set(json.loads(asked.read_text())):
        return pd.read_parquet(cache)  # a ticker asked for and absent from the columns has no prices
    parts = []
    for i in range(0, len(tickers), 400):
        chunk = tuple(tickers[i : i + 400])
        q = f"select ticker, date, {col} as px from sharadar.sep where ticker in %(t)s and {col} > 0"
        d = datasource._sql(q, {"t": chunk})
        d["date"] = pd.to_datetime(d["date"])
        w = d.pivot_table(index="date", columns="ticker", values="px", aggfunc="last").reindex(cal)
        last = w.apply(lambda s: s.last_valid_index())
        w = w.ffill()
        for t, lv in last.items():  # nothing after the last price
            if lv is not None:
                w.loc[w.index > lv, t] = np.nan
        parts.append(w.astype("float32"))
        print("prices", col, i + len(chunk), "/", len(tickers), flush=True)
    m = pd.concat(parts, axis=1)
    m.to_parquet(cache)
    asked.write_text(json.dumps(tickers))
    return m


class Book:
    """Buy-and-hold returns from the price matrix, with the paper's delisting rule."""

    def __init__(self, px, mkt_index, dl):
        self.P = px.values.astype("float64")
        self.col = {t: j for j, t in enumerate(px.columns)}
        self.M = mkt_index
        valid = ~np.isnan(self.P)
        self.last = np.where(valid.any(axis=0), self.P.shape[0] - 1 - np.argmax(valid[::-1], axis=0), -1)
        self.dl = np.array([dl.get(t, -0.30) for t in px.columns])

    def ret(self, cols, i0, i1):
        """Return from the close of row i0 to the close of row i1 for the columns `cols` (array of ints)."""
        cols = np.asarray(cols, dtype=int)
        out = np.full(len(cols), np.nan)
        if i0 < 0 or i1 >= self.P.shape[0] or not len(cols):
            return out
        p0 = self.P[i0, cols]
        last = self.last[cols]
        alive = last >= i1
        with np.errstate(invalid="ignore", divide="ignore"):
            out[alive] = self.P[i1, cols[alive]] / p0[alive] - 1
            gone = (~alive) & (last >= i0)
            lg = last[gone]
            out[gone] = self.P[lg, cols[gone]] / p0[gone] * (1 + self.dl[cols[gone]]) * (self.M[i1] / self.M[lg]) - 1
        return out


def delist_table(act, px):
    """ticker -> the return after the last price, as event_study.delist_return: from the corporate actions dated
    from 10 days before to 60 days after the last price."""
    out = {}
    act = act.copy()
    act["action"] = act["action"].str.lower()
    last = px.apply(lambda s: s.last_valid_index())
    for t, g in act.groupby("ticker"):
        lv = last.get(t)
        if lv is None or pd.isna(lv):
            continue
        g = g[(g["date"] >= lv - pd.Timedelta(days=10)) & (g["date"] <= lv + pd.Timedelta(days=60))]
        kinds = set(g["action"])
        if kinds & DELIST_BANKRUPT:
            out[t] = -1.0
        elif kinds & DELIST_ZERO:
            out[t] = 0.0
    return out


def window_rows(pos, dated, complete):
    """(i0, i1) rows of each window for an event at calendar row `pos`; None where the window does not apply."""
    w = {
        "slide": (pos - 31, pos - 2),
        "slideann": (pos - 31, pos + 1),
        "ann": (pos - 2, pos + 1) if dated else None,
        "slide_wd": (pos - 31, pos - 2) if dated else None,
        "slideann_wd": (pos - 31, pos + 1) if dated else None,
    }
    for name, n in HORIZONS.items():
        w[name] = (pos + 1, pos + 1 + n) if complete[name] else None
    return w


def build(d):
    ff = datasource.factors()
    ff["date"] = pd.to_datetime(ff["date"])
    ff = ff.set_index("date").sort_index()
    cal = ff.index
    mkt = (ff["mkt_rf"].astype(float) + ff["rf"].astype(float)) / 100.0
    M = np.cumprod(1 + mkt.values)

    sf = datasource.fundamentals()
    for c in ("assets", "ebitda", "marketcap", "liabilities"):
        sf[c] = pd.to_numeric(sf[c], errors="coerce")
    sf["year"] = pd.to_datetime(sf["calendardate"]).dt.year
    filings = sf.dropna(subset=["marketcap", "datekey"])[["ticker", "datekey", "marketcap"]].sort_values("datekey")
    sf = sf.sort_values(
        ["ticker", "year", "calendardate", "datekey"], ascending=[True, True, False, True], kind="stable"
    )
    sf = sf.drop_duplicates(["ticker", "year"], keep="first")
    sf["roa"] = sf["ebitda"] / sf["assets"].where(sf["assets"] > 0)
    sf["lev"] = sf["liabilities"] / sf["assets"].where(sf["assets"] > 0)
    tk = datasource.securities("SF1").sort_values(["ticker", "permaticker"], kind="stable")
    tk = tk[["ticker", "famaindustry", "cik"]].drop_duplicates("ticker")
    sf = sf.merge(tk, on="ticker", how="left")
    sic = datasource.sic_codes()
    sic["sic4"] = pd.to_numeric(sic["siccode"], errors="coerce")
    sic["sic3"] = sic["sic4"] // 10
    sf = sf.merge(sic[["ticker", "sic4", "sic3", "industry", "sicindustry"]], on="ticker", how="left")
    gt = datasource.gentry()
    code = pd.to_numeric(gt["departure_code"], errors="coerce")
    link = datasource.gvkey_cik()[["gvkey", "cik"]]
    universe = set(link["cik"].dropna().astype(int))  # firms in the dismissal database: S&P 1500 firms
    turn = gt[code.notna() & (code != 9)].merge(link, on="gvkey")[["cik", "fyear"]]
    turn_years = turn.groupby("cik")["fyear"].apply(set).to_dict()
    base = sf.dropna(subset=["marketcap"])
    base = base[base["marketcap"] > 0]
    by_year = dict(list(base.groupby("year")))
    me_row = base.set_index(["ticker", "year"])

    years = set(d["day0"].dt.year - 1)
    pool_tickers = set(base[base["year"].isin(years) & base["famaindustry"].notna()]["ticker"]) | set(d["ticker"])
    px = price_matrix(pool_tickers, cal)
    act = datasource._sql("select ticker, date::date as date, action from sharadar.actions")
    act["date"] = pd.to_datetime(act["date"])
    book = Book(px, M, delist_table(act, px))
    close = price_matrix(set(d["ticker"]), cal, col="close")
    cpi = pd.read_csv(HERE / "cpi_u.csv", parse_dates=["date"]).set_index("date")["cpi"]
    cpi_2023 = cpi[cpi.index.year == 2023].mean()
    fil = dict(list(filings.groupby("ticker")))
    spx = datasource.sp500().set_index("date")["closeadj"].astype(float)
    spx = spx[~spx.index.duplicated()].reindex(cal)
    sp_last = spx.last_valid_index()
    SP = spx.ffill().where(cal <= sp_last).values

    def sp_ret(i0, i1):
        if i0 < 0 or i1 >= len(SP) or np.isnan(SP[i0]) or np.isnan(SP[i1]):
            return np.nan
        return SP[i1] / SP[i0] - 1

    roa_ctrl = pd.read_parquet(HERE / "out" / "ops_matched.parquet").set_index("event_id")["ctrl_ticker"].to_dict()

    rows, paths = [], []
    for e in d.itertuples():
        if e.ticker not in book.col or e.day0 not in cal:
            continue
        pos = cal.get_loc(e.day0)
        y0 = e.day0.year
        me = book.col[e.ticker]
        complete = {k: pd.notna(getattr(e, BHR_COL[k])) and pos + 1 + n < len(cal) for k, n in HORIZONS.items()}
        win = window_rows(pos, e.dated == 1, complete)
        r = {"event_id": e.event_id}
        # the firm before the firing
        r["prior12"] = book.ret([me], pos + PRIOR[0], pos + PRIOR[1])[0]
        r["sp_prior12"] = sp_ret(pos + PRIOR[0], pos + PRIOR[1])
        fr = me_row.loc[(e.ticker, y0 - 1)] if (e.ticker, y0 - 1) in me_row.index else None
        if fr is not None:
            r.update(
                mcap_fy=fr["marketcap"],
                roa=fr["roa"],
                lev=fr["lev"],
                industry=fr["famaindustry"],
                sic4=fr["sic4"],
                sicindustry=fr["sicindustry"],
            )
        # market value at day -31, in millions of 2023 dollars
        i31 = pos - 31
        f = fil.get(e.ticker)
        if f is not None and i31 >= 0:
            f = f[f["datekey"] <= cal[i31]]
            if len(f) and (cal[i31] - f["datekey"].iloc[-1]).days <= 550 and e.ticker in close.columns:
                c = close[e.ticker]
                c0 = c[: cal[i31]].dropna()
                ck = c[: f["datekey"].iloc[-1]].dropna()
                if len(c0) and len(ck) and c0.index[-1] == cal[i31]:
                    mv = f["marketcap"].iloc[-1] * c0.iloc[-1] / ck.iloc[-1]
                    month = cal[i31].to_period("M").to_timestamp()
                    r["mv31"] = mv * cpi_2023 / cpi.get(month, np.nan) / 1e6
        # competitors
        comp = {
            "pr": None,
            "pr34": None,
            "roa": None,
            "ind": None,
            "sp": "index",
            "pr3": None,
            "pr2": None,
            "pr4": None,
            "pr5": None,
        }
        if fr is not None and pd.notna(r["prior12"]) and pos >= 31:
            # D-37 item 4: same 4-digit SIC, else 3-digit SIC, else Sharadar industry; size within 50%
            year = by_year.get(y0 - 1)
            year = year[(year["ticker"] != e.ticker) & year["ticker"].isin(book.col)]
            for level in LEVELS:
                if pd.isna(fr[level]):
                    continue
                cand = year[year[level] == fr[level]]
                ratio = cand["marketcap"].values / fr["marketcap"]
                cand = cand[(ratio >= NEW_BAND[0]) & (ratio <= NEW_BAND[1])]
                cand = cand[[not any(y0 - 3 <= y <= y0 for y in turn_years.get(c, ())) for c in cand["cik"]]]
                if cand.empty:
                    continue
                cols = np.array([book.col[t] for t in cand["ticker"]], dtype=int)
                pr12 = book.ret(cols, pos + PRIOR[0], pos + PRIOR[1])
                ok = ~np.isnan(pr12) & ~np.isnan(book.P[pos - 31, cols])
                if not ok.any():
                    continue
                pick = pd.DataFrame(
                    {"t": cand["ticker"].values[ok], "gap": np.abs(pr12[ok] - r["prior12"]), "c": cols[ok]}
                ).sort_values(["gap", "t"], kind="stable")
                best = pick.iloc[0]
                row = cand[cand["ticker"] == best["t"]].iloc[0]
                comp["pr"] = int(best["c"])
                for kk in (2, 4, 5):  # D-47: the k nearest at the same level, k = 2, 4, 5
                    if len(pick) >= kk:
                        comp[f"pr{kk}"] = pick["c"].values[:kk].astype(int)
                if len(pick) >= 3:  # D-41: the three nearest at the same level
                    comp["pr3"] = pick["c"].values[:3].astype(int)
                    # D-42 addendum: the balance of the three-competitor mean before the firing
                    three = cand.set_index("ticker").loc[list(pick["t"].values[:3])]
                    r.update(
                        pr3_ticker=";".join(pick["t"].values[:3]),
                        pr3_relaxed=0,
                        pr3_prior12=float(np.mean(book.ret(comp["pr3"], pos + PRIOR[0], pos + PRIOR[1]))),
                        pr3_mcap_fy=float(three["marketcap"].mean()),
                        pr3_roa=(
                            float(np.nanmean(three["roa"].astype(float).values))
                            if three["roa"].notna().any()
                            else np.nan
                        ),
                    )
                r.update(
                    pr_ticker=best["t"],
                    pr_level=level,
                    pr_relaxed=0,
                    pr_sic4=row["sic4"],
                    pr_sicindustry=row["sicindustry"],
                    pr_prior12=book.ret([comp["pr"]], pos + PRIOR[0], pos + PRIOR[1])[0],
                    pr_mcap_fy=row["marketcap"],
                    pr_roa=row["roa"],
                )
                break
        if fr is not None and pd.notna(fr["famaindustry"]):
            pool = by_year.get(y0 - 1)
            pool = pool[(pool["famaindustry"] == fr["famaindustry"]) & (pool["ticker"] != e.ticker)]
            pool = pool[pool["ticker"].isin(book.col)]
            ind = pool[pool["cik"].isin(universe)]
            comp["ind"] = np.array([book.col[t] for t in ind["ticker"]], dtype=int)
            calm = pool[[not any(y0 - 3 <= y <= y0 for y in turn_years.get(c, ())) for c in pool["cik"]]]
            cols = np.array([book.col[t] for t in calm["ticker"]], dtype=int)
            pr12 = book.ret(cols, pos + PRIOR[0], pos + PRIOR[1])
            ratio = calm["marketcap"].values / fr["marketcap"]
            ok = ~np.isnan(pr12) & ~np.isnan(book.P[pos - 31, cols] if pos >= 31 else np.nan)
            if pd.notna(r["prior12"]):
                for relaxed, band in ((0, (0.7, 1.3)), (1, (0.5, 2.0))):
                    m = ok & (ratio >= band[0]) & (ratio <= band[1])
                    if m.any():
                        cand = pd.DataFrame(
                            {"t": calm["ticker"].values[m], "gap": np.abs(pr12[m] - r["prior12"]), "c": cols[m]}
                        ).sort_values(["gap", "t"], kind="stable")
                        best = cand.iloc[0]
                        comp["pr34"] = int(best["c"])
                        row = calm[calm["ticker"] == best["t"]].iloc[0]
                        r.update(
                            pr34_ticker=best["t"],
                            pr34_relaxed=relaxed,
                            pr34_prior12=book.ret([comp["pr34"]], pos + PRIOR[0], pos + PRIOR[1])[0],
                            pr34_mcap_fy=row["marketcap"],
                            pr34_roa=row["roa"],
                        )
                        break
        t = roa_ctrl.get(e.event_id)
        if t in book.col:
            comp["roa"] = book.col[t]
            r["roa_prior12"] = book.ret([comp["roa"]], pos + PRIOR[0], pos + PRIOR[1])[0]
        for name, w in win.items():
            if w is None:
                continue
            firm = book.ret([me], *w)[0]
            r[f"firm_{name}"] = firm
            for b in BENCH:
                if comp[b] is None:
                    continue
                if b == "sp":
                    other = sp_ret(*w)
                elif b == "ind":
                    x = book.ret(comp[b], *w)
                    x = x[~np.isnan(x)]
                    other = x.mean() if len(x) >= 3 else np.nan
                elif b in ("pr3", "pr2", "pr4", "pr5"):
                    x = book.ret(comp[b], *w)
                    other = x.mean() if not np.isnan(x).any() else np.nan
                else:
                    other = book.ret([comp[b]], *w)[0]
                r[f"{b}_{name}"] = firm - other
        # $100 at day -31 in the firm, its competitor and the S&P 500 (addendum)
        for name, n in INVEST.items():
            if name != "d1" and not complete[name]:
                continue
            i0, i1 = pos - 31, pos + 1 + n
            r[f"inv_firm_{name}"] = 100 * (1 + book.ret([me], i0, i1)[0])
            for b in ("pr", "pr34"):
                if comp[b] is not None:
                    r[f"inv_{b}_{name}"] = 100 * (1 + book.ret([comp[b]], i0, i1)[0])
            r[f"inv_sp_{name}"] = 100 * (1 + sp_ret(i0, i1))
            # D-42 addendum: the same $100 in the industry mean and in the mean of the three nearest competitors
            # (descriptive values only; their tests are the return-gap tests already computed)
            if comp["ind"] is not None:
                x = book.ret(comp["ind"], i0, i1)
                x = x[~np.isnan(x)]
                if len(x) >= 3:
                    r[f"inv_ind_{name}"] = 100 * (1 + x.mean())
            if comp["pr3"] is not None:
                x = book.ret(comp["pr3"], i0, i1)
                if not np.isnan(x).any():
                    r[f"inv_pr3_{name}"] = 100 * (1 + x.mean())
        rows.append(r)
        # paths for the figure, against the primary competitor: cumulative from day -31, then monthly from day +2
        if comp["pr"] is not None and e.forced == 1 and e.criminal == 0:
            for day in range(-30, 61):
                if e.dated != 1:
                    break
                a = book.ret([me], pos - 31, pos + day)[0]
                b = book.ret([comp["pr"]], pos - 31, pos + day)[0]
                paths.append((e.event_id, "day", day, a - b))
            for mth in range(1, 61):
                i1 = pos + 1 + 21 * mth
                if not complete["m60"] or i1 >= len(cal):
                    break
                a = book.ret([me], pos + 1, i1)[0]
                b = book.ret([comp["pr"]], pos + 1, i1)[0]
                paths.append((e.event_id, "month", mth, a - b))
    v = d.merge(pd.DataFrame(rows), on="event_id", how="inner")
    for b in BENCH:
        for name in WINDOWS:
            if f"{b}_{name}" in v:
                v[f"{b}_{name}_usd"] = v[f"{b}_{name}"] * v["mv31"]
    v.to_parquet(HERE / "out" / f"founder_value{TAG}.parquet", index=False)
    pd.DataFrame(paths, columns=["event_id", "unit", "t", "gap"]).to_parquet(
        HERE / "out" / f"founder_value_path{TAG}.parquet", index=False
    )
    return v


def cells(v):
    f, r = v[v["forced"] == 1], v[v["forced"] == 0]
    main = f[f["why"] != "fraud"]
    fraud = f[f["why"] == "fraud"]
    r = r[r["criminal"] == 0]
    c = {
        "founder": main[main["who"] == "founder"],
        "hired": main[main["who"] == "hired"],
        "forced": main,
        "retired": r,
        "fraud": fraud,
        "founder_fraud": fraud[fraud["who"] == "founder"],
        "hired_fraud": fraud[fraud["who"] == "hired"],
        "scandal": main[main["why"] == "scandal"],
        "founder_scandal": main[(main["why"] == "scandal") & (main["who"] == "founder")],
        "hired_scandal": main[(main["why"] == "scandal") & (main["who"] == "hired")],
        "coup": main[main["why"] == "coup"],
        "founder_coup": main[(main["why"] == "coup") & (main["who"] == "founder")],
        "hired_coup": main[(main["why"] == "coup") & (main["who"] == "hired")],
        "other": main[main["why"] == "other"],
        "founder_other": main[(main["why"] == "other") & (main["who"] == "founder")],
        "hired_other": main[(main["why"] == "other") & (main["who"] == "hired")],
    }
    return c


def winsor(x):
    lo, hi = np.percentile(x, [1, 99])
    return np.clip(x, lo, hi)


def describe(prefix, x, unit):
    """One cell, window and benchmark: N always; mean, median (and total for dollars) from MIN_CELL firings up."""
    x = pd.Series(x).dropna().astype(float)
    put(prefix + ".count", len(x), n=len(x))
    if len(x) < MIN_CELL:
        return
    t = stats.ttest_1samp(x, 0.0)
    se = x.std(ddof=1) / np.sqrt(len(x))
    q = stats.t.ppf(0.975, len(x) - 1)
    put(prefix + ".mean", x.mean(), n=len(x), t=t.statistic, p=t.pvalue, se=se)
    put(prefix + ".mean.ci_low", x.mean() - q * se, n=len(x))
    put(prefix + ".mean.ci_high", x.mean() + q * se, n=len(x))
    put(prefix + ".median", x.median(), n=len(x), p=stats.wilcoxon(x).pvalue)
    w = winsor(x.values)
    tw = stats.ttest_1samp(w, 0.0)
    put(prefix + ".wmean", w.mean(), n=len(x), t=tw.statistic, p=tw.pvalue)
    put(prefix + ".share_negative", (x < 0).mean(), n=len(x))
    if unit == "usd":
        put(prefix + ".total", x.sum(), n=len(x))
        worst = x.nsmallest(1)
        put(prefix + ".largest_loss", worst.iloc[0], n=1)
        put(prefix + ".largest_loss_share", worst.iloc[0] / x.sum() if x.sum() else np.nan, n=len(x))


def welch(prefix, a, b):
    a, b = pd.Series(a).dropna().astype(float), pd.Series(b).dropna().astype(float)
    put(prefix + ".n_a", len(a), n=len(a))
    put(prefix + ".n_b", len(b), n=len(b))
    if len(a) < MIN_CELL or len(b) < MIN_CELL:
        return
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    se = float(np.sqrt(va + vb))
    df = (va + vb) ** 2 / (va**2 / (len(a) - 1) + vb**2 / (len(b) - 1))
    diff = a.mean() - b.mean()
    q = stats.t.ppf(0.975, df)
    n = len(a) + len(b)
    put(prefix + ".diff", diff, n=n, se=se, t=diff / se, p=2 * (1 - stats.t.cdf(abs(diff) / se, df)))
    put(prefix + ".diff.ci_low", diff - q * se, n=n)
    put(prefix + ".diff.ci_high", diff + q * se, n=n)
    put(prefix + ".diff_median", a.median() - b.median(), n=n, p=stats.mannwhitneyu(a, b).pvalue)
    wa, wb = winsor(a.values), winsor(b.values)
    tw = stats.ttest_ind(wa, wb, equal_var=False)
    put(prefix + ".wdiff", wa.mean() - wb.mean(), n=n, t=tw.statistic, p=tw.pvalue)
    # the smallest gap a two-sided 5% test with 80% power would detect
    put(prefix + ".mde", (1.959964 + 0.841621) * se, n=n)


def exact(prefix, a, b, reps=20000):
    """Addendum (operator, 23 Nov 2026): small-sample tests beside the standard ones. A two-sided permutation test of
    the difference in means (founder and hired labels shuffled, seeded), and an exact sign test of the founders' own
    median against zero."""
    a, b = pd.Series(a).dropna().astype(float).values, pd.Series(b).dropna().astype(float).values
    if len(a) < MIN_CELL or len(b) < MIN_CELL:
        return
    rng = np.random.default_rng(20261123)
    pool = np.concatenate([a, b])
    obs = a.mean() - b.mean()
    hits = 0
    for _ in range(reps):
        rng.shuffle(pool)
        hits += abs(pool[: len(a)].mean() - pool[len(a) :].mean()) >= abs(obs) - 1e-12
    p = (hits + 1) / (reps + 1)
    put(prefix + ".perm_p", p, n=len(a) + len(b), p=p)
    k = int((a < 0).sum())
    nz = int((a != 0).sum())
    sp = stats.binomtest(k, nz, 0.5).pvalue if nz else np.nan
    put(prefix + ".sign_p_a", sp, n=nz, p=sp)
    put(prefix + ".share_negative_a", k / nz if nz else np.nan, n=nz)


def holm(keys, suffix=".diff"):
    ps = sorted((R[k]["p"], k) for k in keys if k in R and R[k].get("p") is not None)
    running = 0.0
    for i, (p, k) in enumerate(ps):
        running = max(running, min(1.0, (len(ps) - i) * p))
        put(k[: -len(suffix)] + ".holm_p", running, n=R[k]["n"], p=running)


def slog(x):
    return np.sign(x) * np.log1p(np.abs(x))


def regress(prefix, data, y, flag):
    """y on the flag with log market value, the prior 12-month return, return on assets, leverage, industry and year;
    standard errors clustered by firm."""
    cols = [y, flag, "mv31", "prior12", "roa", "lev", "industry", "year", "cik"]
    x = data[cols].replace([np.inf, -np.inf], np.nan).dropna().copy()
    put(prefix + ".n", len(x), n=len(x))
    if x[flag].sum() < MIN_CELL or (1 - x[flag]).sum() < MIN_CELL:
        return
    x["lmv"] = np.log(x["mv31"])
    for c in ("prior12", "roa", "lev"):
        x[c] = np.clip(x[c], *np.percentile(x[c], [1, 99]))
    m = smf.ols(f"{y} ~ {flag} + lmv + prior12 + roa + lev + C(industry) + C(year)", data=x).fit(
        cov_type="cluster", cov_kwds={"groups": x["cik"].astype(int)}
    )
    n = int(m.nobs)
    ci = m.conf_int().loc[flag]
    put(prefix + ".coef", m.params[flag], n=n, se=m.bse[flag], t=m.tvalues[flag], p=m.pvalues[flag])
    put(prefix + ".coef.ci_low", ci[0], n=n)
    put(prefix + ".coef.ci_high", ci[1], n=n)
    put(prefix + ".prior12", m.params["prior12"], n=n, t=m.tvalues["prior12"], p=m.pvalues["prior12"])
    put(prefix + ".n_flag", int(x[flag].sum()), n=n)


def balance(prefix, x, m="pr"):
    """How close a competitor is to the firm before the firing: prior return, market value, ROA."""
    x = x[x[f"{m}_ticker"].notna()]
    put(prefix + ".n", len(x), n=len(x))
    if len(x) < MIN_CELL:
        return
    for name, a, b, logs in (
        ("prior12", "prior12", f"{m}_prior12", False),
        ("mcap", "mcap_fy", f"{m}_mcap_fy", True),
        ("roa", "roa", f"{m}_roa", False),
    ):
        y = x[[a, b]].replace([np.inf, -np.inf], np.nan).dropna()
        n = len(y)
        put(f"{prefix}.{name}.firm.mean", y[a].mean(), n=n)
        put(f"{prefix}.{name}.comp.mean", y[b].mean(), n=n)
        put(f"{prefix}.{name}.firm.median", y[a].median(), n=n)
        put(f"{prefix}.{name}.comp.median", y[b].median(), n=n)
        fa, fb = (np.log(y[a]), np.log(y[b])) if logs else (y[a], y[b])
        gap = fa - fb
        t = stats.ttest_1samp(gap, 0.0)
        pooled = np.sqrt((fa.var(ddof=1) + fb.var(ddof=1)) / 2)
        put(f"{prefix}.{name}.gap", gap.mean(), n=n, t=t.statistic, p=t.pvalue)
        put(f"{prefix}.{name}.gap_median", gap.median(), n=n, p=stats.wilcoxon(gap).pvalue)
        put(f"{prefix}.{name}.std_diff", gap.mean() / pooled if pooled else np.nan, n=n)
    put(prefix + ".relaxed", int(x[f"{m}_relaxed"].sum()), n=len(x))
    if m == "pr":
        for level in LEVELS:
            put(f"{prefix}.level.{level}", int((x["pr_level"] == level).sum()), n=len(x))


def main():
    d = load_events()
    v = build(d)
    v["founder"] = (v["who"] == "founder").astype(int)
    C = cells(v)
    put("fv.n_events", len(v), n=len(v))
    for name, x in C.items():
        put(f"fv.{name}.n_all", len(x), n=len(x))
        put(f"fv.{name}.n_matched", int(x["pr_ticker"].notna().sum()), n=len(x))
        put(f"fv.{name}.n_mv", int(x["mv31"].notna().sum()), n=len(x))
        mv = x["mv31"].dropna()
        if len(mv) >= MIN_CELL:
            put(f"fv.{name}.mv31.median", mv.median(), n=len(mv))
            put(f"fv.{name}.mv31.mean", mv.mean(), n=len(mv))
            put(f"fv.{name}.mv31.total", mv.sum(), n=len(mv))
        for w in WINDOWS:
            if f"firm_{w}" in x:
                describe(f"fv.{name}.firm.{w}.ret", x[f"firm_{w}"], "ret")
            for b in BENCH:
                if f"{b}_{w}" not in x:
                    continue
                describe(f"fv.{name}.{b}.{w}.ret", x[f"{b}_{w}"], "ret")
                describe(f"fv.{name}.{b}.{w}.usd", x[f"{b}_{w}_usd"], "usd")
        balance(f"fvbal.{name}", x)
        balance(f"fvbal34.{name}", x, "pr34")
        if "pr3_ticker" in x:
            balance(f"fvbal3.{name}", x, "pr3")
        put(f"fv.{name}.n_matched34", int(x["pr34_ticker"].notna().sum()), n=len(x))
        # addendum: $100 at day -31, on the firings that have the firm, the competitor and the S&P 500
        for h in INVEST:
            cols = [f"inv_{a}_{h}" for a in ("firm", "pr", "sp")]
            if not all(c in x for c in cols):
                continue
            y = x[cols].dropna()
            put(f"fvinv.{name}.{h}.count", len(y), n=len(y))
            if len(y) < MIN_CELL:
                continue
            for a, c in zip(("firm", "pr", "sp"), cols):
                put(f"fvinv.{name}.{a}.{h}.mean", y[c].mean(), n=len(y))
                put(f"fvinv.{name}.{a}.{h}.median", y[c].median(), n=len(y))
            for a, c in (("pr", cols[1]), ("sp", cols[2])):
                gap = y[cols[0]] - y[c]
                t = stats.ttest_1samp(gap, 0.0)
                put(f"fvinv.{name}.firm_minus_{a}.{h}.mean", gap.mean(), n=len(y), t=t.statistic, p=t.pvalue)
                put(f"fvinv.{name}.firm_minus_{a}.{h}.median", gap.median(), n=len(y), p=stats.wilcoxon(gap).pvalue)
        # D-42 addendum: $100 in the firm against the industry mean and the three nearest competitors (values only)
        for h in INVEST:
            for a in ("ind", "pr3"):
                cols = [f"inv_firm_{h}", f"inv_{a}_{h}"]
                if not all(c in x for c in cols):
                    continue
                y = x[cols].dropna()
                put(f"fvinv.{name}.{a}.{h}.count", len(y), n=len(y))
                if len(y) < MIN_CELL:
                    continue
                for side, c in ((f"firm_{a}", cols[0]), (a, cols[1])):
                    put(f"fvinv.{name}.{side}.{h}.mean", y[c].mean(), n=len(y))
                    put(f"fvinv.{name}.{side}.{h}.median", y[c].median(), n=len(y))
        # the same $100 line against the D-34 competitor (D-37 robustness)
        for h in INVEST:
            cols = [f"inv_firm_{h}", f"inv_pr34_{h}"]
            if not all(c in x for c in cols):
                continue
            y = x[cols].dropna()
            put(f"fvinv.{name}.pr34.{h}.count", len(y), n=len(y))
            if len(y) < MIN_CELL:
                continue
            for a, c in (("firm34", cols[0]), ("pr34", cols[1])):
                put(f"fvinv.{name}.{a}.{h}.mean", y[c].mean(), n=len(y))
                put(f"fvinv.{name}.{a}.{h}.median", y[c].median(), n=len(y))
            gap = y[cols[0]] - y[cols[1]]
            t = stats.ttest_1samp(gap, 0.0)
            put(f"fvinv.{name}.firm_minus_pr34.{h}.mean", gap.mean(), n=len(y), t=t.statistic, p=t.pvalue)
            put(f"fvinv.{name}.firm_minus_pr34.{h}.median", gap.median(), n=len(y), p=stats.wilcoxon(gap).pvalue)
        # addendum: the decline before, for the firm, its competitor and the S&P 500
        y = x[["prior12", "pr_prior12", "sp_prior12"]].dropna()
        put(f"fvprior.{name}.count", len(y), n=len(y))
        if len(y) >= MIN_CELL:
            for a, c in (("firm", "prior12"), ("pr", "pr_prior12"), ("sp", "sp_prior12")):
                put(f"fvprior.{name}.{a}.mean", y[c].mean(), n=len(y))
                put(f"fvprior.{name}.{a}.median", y[c].median(), n=len(y))
            for a, c in (("pr", "pr_prior12"), ("sp", "sp_prior12")):
                gap = y["prior12"] - y[c]
                t = stats.ttest_1samp(gap, 0.0)
                put(f"fvprior.{name}.firm_minus_{a}.mean", gap.mean(), n=len(y), t=t.statistic, p=t.pvalue)

    # D-42 addendum: Holm across the five benchmarks of the founder question, per window (means and medians)
    for w in MAIN_WINDOWS:
        for stat_ in ("mean", "median"):
            keys = [f"fv.founder.{bb}.{w}.ret.{stat_}" for bb in ("sp", "ind", "pr3", "roa", "pr")]
            ps = sorted((R[k]["p"], k) for k in keys if k in R and R[k].get("p") is not None)
            running = 0.0
            for i, (pp, k) in enumerate(ps):
                running = max(running, min(1.0, (len(ps) - i) * pp))
                put(k + ".holm5_p", running, n=R[k]["n"], p=running)

    pairs = (
        ("main.founder_vs_hired", "founder", "hired"),
        ("forced_vs_retired", "forced", "retired"),
        ("fraud.founder_vs_hired", "founder_fraud", "hired_fraud"),
        ("other.founder_vs_hired", "founder_other", "hired_other"),
        ("scandal_vs_fraud", "scandal", "fraud"),
        ("scandal_vs_other", "scandal", "other"),
        ("coup_vs_other", "coup", "other"),
        ("fraud_vs_forced", "fraud", "forced"),
    )
    for label, a, b in pairs:
        for bench in BENCH:
            for w in WINDOWS:
                for unit, col in (("ret", f"{bench}_{w}"), ("usd", f"{bench}_{w}_usd")):
                    if col in v:
                        welch(f"fvdiff.{label}.{bench}.{w}.{unit}", C[a][col], C[b][col])
            for unit in ("ret", "usd"):
                holm([f"fvdiff.{label}.{bench}.{w}.{unit}.diff" for w in MAIN_WINDOWS])

    # D-41, checks added after review: H1 on the founders the case check found clearly forced out, and H1 on pairs
    # matched within the same 4-digit SIC code only (both against the primary competitor)
    cases_csv = HERE.parent / "paper" / "founder_cases" / "founder_cases.csv"
    pushed = set()
    if cases_csv.exists():
        fc = pd.read_csv(cases_csv)
        pushed = set(fc.loc[fc["push_class"] == "pushed", "event_id"].astype(int))
    fo, hi = C["founder"], C["hired"]
    subsets = {
        "pushed": (fo[fo["event_id"].isin(pushed)], hi),
        "sic4": (fo[fo["pr_level"] == "sic4"], hi[hi["pr_level"] == "sic4"]),
    }
    for sname, (a, b) in subsets.items():
        for w in ("slideann", "ann", "slide"):
            col = f"pr_{w}"
            describe(f"fvrob.{sname}.founder.pr.{w}.ret", a[col], "ret")
            describe(f"fvrob.{sname}.hired.pr.{w}.ret", b[col], "ret")
            welch(f"fvrob.{sname}.founder_vs_hired.pr.{w}.ret", a[col], b[col])

    for w in WINDOWS:  # addendum: exact small-sample tests for H1 against the primary competitor
        if f"pr_{w}" in v:
            exact(f"fvdiff.main.founder_vs_hired.pr.{w}.ret", C["founder"][f"pr_{w}"], C["hired"][f"pr_{w}"])
            exact(f"fvdiff.main.founder_vs_hired.pr.{w}.usd", C["founder"][f"pr_{w}_usd"], C["hired"][f"pr_{w}_usd"])

    for h in INVEST:
        for a in ("firm", "pr", "sp"):
            col = f"inv_{a}_{h}"
            if col in v:
                need = [f"inv_{b}_{h}" for b in ("firm", "pr", "sp")]
                fa, fb = C["founder"].dropna(subset=need), C["hired"].dropna(subset=need)
                welch(f"fvinvdiff.main.founder_vs_hired.{a}.{h}", fa[col], fb[col])

    # regressions: founder flag among the main-sample firings; firing flag among firings and retirements
    main_f = C["forced"].copy()
    both = pd.concat([C["forced"], C["retired"]]).copy()
    both["fired"] = (both["forced"] == 1).astype(int)
    for bench in BENCH:
        for w in WINDOWS:
            col = f"{bench}_{w}"
            if col not in v:
                continue
            for data, flag, label in ((main_f, "founder", "founder"), (both, "fired", "fired")):
                data = data.copy()
                data["y"] = data[col]
                data["ylog"] = slog(data[f"{col}_usd"])
                regress(f"fvreg.{label}.{bench}.{w}.ret", data, "y", flag)
                regress(f"fvreg.{label}.{bench}.{w}.logusd", data, "ylog", flag)
        for unit in ("ret", "logusd"):
            holm([f"fvreg.founder.{bench}.{w}.{unit}.coef" for w in MAIN_WINDOWS], suffix=".coef")

    # the cases behind the cells too small for a mean
    cases = {}
    for name in ("founder_scandal", "founder_coup"):
        x = C[name]
        cases[name] = []
        for r in x.itertuples():
            row = {"event_id": int(r.event_id), "company": r.coname, "ceo": r.exec_fullname, "year": int(r.year)}
            for w in MAIN_WINDOWS:
                for unit, col in (("ret", f"pr_{w}"), ("usd", f"pr_{w}_usd")):
                    val = getattr(r, col, np.nan)
                    row[f"{w}_{unit}"] = None if pd.isna(val) else float(val)
                    if not pd.isna(val):
                        put(f"fvcase.{int(r.event_id)}.{w}.{unit}", float(val), n=1)
            cases[name].append(row)
    # the five largest dollar losses and gains behind the founder total, so a reader sees what drives it
    top = {}
    for name in ("founder", "hired"):
        for w in ("slideann", "m12", "m60"):
            x = C[name][["event_id", "coname", "year", f"pr_{w}_usd", f"pr_{w}"]].dropna()
            top[f"{name}.{w}"] = x.sort_values(f"pr_{w}_usd").head(5).to_dict("records") + x.sort_values(
                f"pr_{w}_usd"
            ).tail(3).to_dict("records")
    # figure series: mean and median gap against the primary competitor, founders and hired CEOs
    p = pd.read_parquet(HERE / "out" / f"founder_value_path{TAG}.parquet").merge(
        v[["event_id", "who"]], on="event_id", how="left"
    )
    series = {}
    for (unit, who), g in p.groupby(["unit", "who"]):
        s = g.groupby("t")["gap"].agg(["mean", "median", "count"])
        series[f"{unit}.{who}"] = {
            "t": [int(i) for i in s.index],
            "mean": [float(x) for x in s["mean"]],
            "median": [float(x) for x in s["median"]],
            "n": [int(x) for x in s["count"]],
        }
    R["_cases"] = cases
    R["_top"] = top
    R["_series"] = series
    (OUT / STATS_FILE).write_text(json.dumps(R, indent=1, default=str))

    g = lambda k: R.get(k, {}).get("value")  # noqa: E731
    for name in C:
        print(f"== {name} N={g(f'fv.{name}.n_all')} matched={g(f'fv.{name}.n_matched')} mv={g(f'fv.{name}.n_mv')}")
        for w in WINDOWS:
            k = f"fv.{name}.pr.{w}"
            if g(k + ".ret.mean") is not None:
                print(
                    f"   {w:12s} n={g(k + '.ret.count'):5.0f} ret mean={g(k + '.ret.mean'):+.4f} "
                    f"med={g(k + '.ret.median'):+.4f} usd mean={g(k + '.usd.mean'):+.0f} "
                    f"med={g(k + '.usd.median'):+.0f} total={g(k + '.usd.total'):+.0f}"
                )
    for k, r in R.items():
        if k.startswith("fvdiff.main") and k.endswith(".diff") and ".pr." in k:
            print(f"{k:60s} {r['value']:+.4f} p={r['p']:.4f} n={r['n']}")
        if k.startswith("fvreg.founder.pr") and k.endswith(".coef"):
            print(f"{k:60s} {r['value']:+.4f} p={r['p']:.4f} n={r['n']}")
        if k.startswith("fvbal.founder.") or k.startswith("fvbal.forced."):
            print(f"{k:60s} {r['value']}")


if __name__ == "__main__":
    main()
