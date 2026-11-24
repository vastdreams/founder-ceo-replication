"""Long-run growth after a founder or scandal dismissal, against the competitor (paper/DECISIONS.md D-40).

H4: after a founder dismissal the firm grows more slowly than its competitor over the next five years, and by more
than after a hired-CEO dismissal. H5: the same for dismissals over a personal scandal against other dismissals (and
the sex-or-relationship subset, named when under MIN_CELL). Two-sided tests; a null is reported as a null.

Sample and competitor: the corrected sample (D-37, D-38) and the D-37 competitor, read from
analysis/out/founder_value.parquet (pr_ticker). Fundamentals are Sharadar SF1 as-reported annual rows (dimension ARY,
one row per firm and calendar year, as ops_matched.py). Year 0 is the calendar year of the announcement; fiscal years
-3 to +5 around it.

Outcomes (D-40)
  rev     revenue growth: the log change from year -1 to year +3 (or +5), a year
  assets  asset growth, the same way
  mcap    market value (SF1, at the filing date), the same way
  rnd     R&D to sales, for firms that report R&D in year -1
  capex   capital spending to assets
  roa     EBITDA to assets (the pack's return on assets)
  gm      gross profit to sales
  Employees are not held in the data.

Benchmark: difference-in-differences. For a growth outcome, (the firm's growth a year after year -1) minus (its
growth a year over years -3 to -1), less the same for the competitor. For a ratio, (its value in year +3 or +5) minus
(its mean over years -3 to -1), less the same for the competitor. So a firm that was already shrinking, or already
spending less, is not counted as a new loss. Robustness benchmark "ind": the median of the same change across every
other SF1 firm in the Fama-French industry (at least MIN_IND firms).

Attrition (D-40). A firm that goes bankrupt or is delisted for cause (a regulatory delisting) stays in: with no
filing in a year at or after its exit, its growth from year -1 is -100% (the *_att outcomes: simple growth a year,
(X_k / X_-1) ** (1 / (k + 1)) - 1, which is -100% at zero). The same rule is applied to the competitor. A firm that
is taken over leaves at the takeover and is counted; so does a pair whose competitor is taken over. Ratios cannot be
imputed and use firms still filing. The attrition table counts, year by year, firms filing, bankrupt, delisted for
cause, taken over, delisted for another reason, not yet reached by the data and without a filing.

Implementation choices fixed before any result (D-40 leaves them open): the base year is -1, the last full year
before the dismissal; the earlier year is -3, or -2 where year -3 has no filing; the exit kind is read from the
corporate actions dated from 10 days before to 60 days after the last price, as event_study.delist_return.

Tests: each cell's difference-in-differences against zero (t, Wilcoxon signed-rank); founder minus hired and scandal
minus other by Welch t and Mann-Whitney U; Holm across the seven outcomes at +3 and +5 (14 tests a family); and a
regression of the firm-minus-competitor change after year -1 on the flag with log market value, the firm's prior
revenue growth, the prior 12-month return, leverage, industry and year, standard errors clustered by firm. A cell
under MIN_CELL gets N and its cases, no mean. Share returns against the competitor at 36 and 60 months
(founder_value.py) are repeated beside the growth results.

Inputs : analysis/out/founder_value.parquet, datasource.* (SF1 ARY, tickers, corporate actions)
Outputs: outputs/founder_growth_stats.json; analysis/out/founder_growth.parquet (one row per departure)
"""

import json
import pathlib

import datasource
import founder_value as fv
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from event_study import DELIST_BANKRUPT, DELIST_ZERO

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "outputs"
R = fv.R
put = fv.put
MIN_CELL = fv.MIN_CELL
MIN_IND = 5
YEARS = tuple(range(-3, 6))
HOR = {"y3": 3, "y5": 5}
GROWTH = ("rev", "assets", "mcap")
RATIO = ("rnd", "capex", "roa", "gm")
OUTCOMES = ("rev", "rnd", "capex", "assets", "roa", "gm", "mcap")  # the Holm family of D-40, at +3 and +5
ATT = ("rev_att", "assets_att", "mcap_att")
SEX = ("relationship_with_employee", "other_sexual_misconduct", "relationship_other")
DELIST_CAUSE = {"regulatorydelisting"}
SHR = {"y3": "pr_m36", "y5": "pr_m60"}


def num(s):
    return pd.to_numeric(s, errors="coerce")


def fundamentals():
    if datasource.backend() == "files":
        sf = datasource.fundamentals()
        sf["gp"] = np.nan
    else:
        sf = datasource._sql(
            """select ticker, calendardate, datekey, revenue, assets, ebitda, rnd, capex, gp, marketcap
               from sharadar.sf1 where dimension = 'ARY'"""
        )
        for c in ("calendardate", "datekey"):
            sf[c] = pd.to_datetime(sf[c])
    for c in ("revenue", "assets", "ebitda", "rnd", "capex", "gp", "marketcap"):
        sf[c] = num(sf[c])
    sf["year"] = pd.to_datetime(sf["calendardate"]).dt.year
    sf = sf.sort_values(
        ["ticker", "year", "calendardate", "datekey"], ascending=[True, True, False, True], kind="stable"
    )
    sf = sf.drop_duplicates(["ticker", "year"], keep="first")
    pos = sf["revenue"].where(sf["revenue"] > 0)
    at = sf["assets"].where(sf["assets"] > 0)
    sf["rev"] = pos
    sf["at"] = at
    sf["mc"] = sf["marketcap"].where(sf["marketcap"] > 0)
    sf["rnd_s"] = sf["rnd"].fillna(0) / pos
    sf["capex_a"] = sf["capex"].abs() / at
    sf["roa"] = sf["ebitda"] / at
    sf["gm"] = sf["gp"] / pos
    sf["filed"] = 1.0
    return sf


def exits():
    """ticker -> (kind, year): how and when the stock left the price file, as event_study.delist_return."""
    tk = datasource.securities("SF1").sort_values(["ticker", "permaticker"], kind="stable").drop_duplicates("ticker")
    tk = tk[tk["isdelisted"].astype(str).str.upper().str[0] == "Y"].dropna(subset=["lastpricedate"])
    last = pd.to_datetime(tk.set_index("ticker")["lastpricedate"])
    if datasource.backend() == "files":
        act = datasource.actions(list(last.index))
    else:
        act = datasource._sql("select ticker, date::date as date, action from sharadar.actions")
    act["date"] = pd.to_datetime(act["date"])
    act["action"] = act["action"].str.lower()
    act = act[act["ticker"].isin(last.index)]
    act["last"] = act["ticker"].map(last)
    act = act[
        (act["date"] >= act["last"] - pd.Timedelta(days=10)) & (act["date"] <= act["last"] + pd.Timedelta(days=60))
    ]
    kinds = act.groupby("ticker")["action"].apply(set).to_dict()
    out = {}
    for t, d in last.items():
        k = kinds.get(t, set())
        if k & DELIST_BANKRUPT:
            kind = "bankrupt"
        elif k & DELIST_ZERO:
            kind = "acquired"
        elif k & DELIST_CAUSE:
            kind = "cause"
        else:
            kind = "other"
        out[t] = (kind, d.year)
    return out


class Panel:
    def __init__(self, sf):
        self.p = {c: sf.pivot(index="ticker", columns="year", values=c) for c in COLS.values()}
        self.p["filed"] = sf.pivot(index="ticker", columns="year", values="filed")
        self.last_year = int(sf["year"].max())

    def look(self, col, tick, yrs):
        piv = self.p[col]
        ti = piv.index.get_indexer(pd.Index(tick))
        yi = piv.columns.get_indexer(pd.Index(yrs))
        a = piv.values
        ok = (ti >= 0) & (yi >= 0)
        return np.where(ok, a[np.clip(ti, 0, None), np.clip(yi, 0, None)], np.nan)


COLS = {"rev": "rev", "assets": "at", "mcap": "mc", "rnd": "rnd_s", "capex": "capex_a", "roa": "roa", "gm": "gm"}


def status(pan, ex, tick, y0, k):
    """Per ticker and year y0 + k: filing, bankrupt, cause, acquired, other, not_reached, no_filing."""
    yrs = np.asarray(y0) + k
    filed = ~np.isnan(pan.look("rev", tick, yrs))
    out = []
    for t, y, f in zip(tick, yrs, filed):
        if f:
            out.append("filing")
            continue
        kind, ey = ex.get(t, (None, None))
        if kind is not None and ey <= y:
            out.append(kind)
        elif y > pan.last_year:
            out.append("not_reached")
        else:
            out.append("no_filing")
    return np.array(out, dtype=object)


def changes(pan, ex, tick, y0):
    """Per ticker: every outcome's change after year -1 less its change (or level) before, and the parts."""
    tick = np.asarray(tick, dtype=object)
    y0 = np.asarray(y0)
    out = {}
    for o in GROWTH:
        col = COLS[o]
        x = {k: pan.look(col, tick, y0 + k) for k in (-3, -2, -1, 3, 5)}
        early = np.where(~np.isnan(x[-3]), x[-3], x[-2])
        span = np.where(~np.isnan(x[-3]), 2.0, 1.0)
        out[f"{o}.pre"] = np.log(x[-1] / early) / span
        pre_s = (x[-1] / early) ** (1 / span) - 1
        out[f"{o}_att.pre"] = pre_s
        for h, k in HOR.items():
            post = np.log(x[k] / x[-1]) / (k + 1)
            out[f"{o}.{h}.post"] = post
            out[f"{o}.{h}"] = post - out[f"{o}.pre"]
            st = status(pan, ex, tick, y0, k)
            sim = (x[k] / x[-1]) ** (1 / (k + 1)) - 1
            failed = np.isin(st, ["bankrupt", "cause"]) & ~np.isnan(x[-1])
            sim = np.where(failed, -1.0, sim)
            out[f"{o}_att.{h}.post"] = sim
            out[f"{o}_att.{h}"] = sim - pre_s
    for o in RATIO:
        col = COLS[o]
        pre = np.nanmean(np.vstack([pan.look(col, tick, y0 + k) for k in (-3, -2, -1)]), axis=0)
        out[f"{o}.pre"] = pre
        for h, k in HOR.items():
            post = pan.look(col, tick, y0 + k)
            out[f"{o}.{h}.post"] = post
            out[f"{o}.{h}"] = post - pre
    return out


def build(v):
    sf = fundamentals()
    pan = Panel(sf)
    ex = exits()
    tk = datasource.securities("SF1").sort_values(["ticker", "permaticker"], kind="stable")
    ind_of = tk.drop_duplicates("ticker").set_index("ticker")["famaindustry"]
    d = v.copy()
    d["y0"] = pd.to_datetime(d["day0"]).dt.year
    firm = changes(pan, ex, d["ticker"].values, d["y0"].values)
    comp = changes(pan, ex, d["pr_ticker"].fillna("").values, d["y0"].values)
    keys = [f"{o}.{h}" for o in OUTCOMES + ATT for h in HOR]
    for k in keys:
        d[f"firm.{k}"] = firm[k]
        d[f"comp.{k}"] = comp[k]
        d[f"pr.{k}"] = firm[k] - comp[k]
        d[f"firm.{k}.post"] = firm[k + ".post"]
        d[f"comp.{k}.post"] = comp[k + ".post"]
        d[f"gap.{k}"] = firm[k + ".post"] - comp[k + ".post"]  # the regression's outcome: no differencing
    for o in OUTCOMES + ATT:
        d[f"firm.{o}.pre"] = firm[f"{o}.pre"]
        d[f"comp.{o}.pre"] = comp[f"{o}.pre"]
    # a pair leaves when the firm or its competitor is taken over (or delisted for another reason) before the year
    for h, k in HOR.items():
        sf_ = status(pan, ex, d["ticker"].values, d["y0"].values, k)
        sc_ = status(pan, ex, d["pr_ticker"].fillna("").values, d["y0"].values, k)
        d[f"st_firm.{h}"] = sf_
        d[f"st_comp.{h}"] = sc_
        out_ = np.isin(sf_, ["acquired", "other"]) | np.isin(sc_, ["acquired", "other"])
        for o in ATT:
            d.loc[out_, [f"pr.{o}.{h}", f"gap.{o}.{h}"]] = np.nan
    # R&D only where the firm reports R&D in year -1
    rnd1 = pan.look("rnd_s", d["ticker"].values, d["y0"].values - 1)
    for h in HOR:
        d.loc[~(rnd1 > 0), [f"pr.rnd.{h}", f"gap.rnd.{h}", f"firm.rnd.{h}", f"comp.rnd.{h}"]] = np.nan
    # industry-median benchmark: the same change across every other SF1 firm of the Fama-French industry
    everyone = np.array(sorted(set(pan.p["rev"].index) & set(ind_of.dropna().index)), dtype=object)
    inds = ind_of.reindex(everyone).values
    for k in [f"{o}.{h}" for o in OUTCOMES for h in HOR]:
        d[f"ind.{k}"] = np.nan
    for y in sorted(d["y0"].unique()):
        allc = changes(pan, ex, everyone, np.full(len(everyone), y))
        rows = d.index[d["y0"] == y]
        for k in [f"{o}.{h}" for o in OUTCOMES for h in HOR]:
            s = pd.DataFrame({"t": everyone, "ind": inds, "x": allc[k]}).dropna()
            for i in rows:
                g = s[(s["ind"] == d.at[i, "industry"]) & (s["t"] != d.at[i, "ticker"])]["x"]
                if len(g) >= MIN_IND and not np.isnan(d.at[i, f"firm.{k}"]):
                    d.at[i, f"ind.{k}"] = d.at[i, f"firm.{k}"] - g.median()
    d["rev_pre_firm"] = firm["rev.pre"]
    # the revenue path: year -1 = 100, for pairs with revenue for firm and competitor in that year
    base_f = pan.look("rev", d["ticker"].values, d["y0"].values - 1)
    base_c = pan.look("rev", d["pr_ticker"].fillna("").values, d["y0"].values - 1)
    for k in YEARS:
        d[f"idx_firm.{k}"] = 100 * pan.look("rev", d["ticker"].values, d["y0"].values + k) / base_f
        d[f"idx_comp.{k}"] = 100 * pan.look("rev", d["pr_ticker"].fillna("").values, d["y0"].values + k) / base_c
    for k in range(0, 6):
        d[f"att.{k}"] = status(pan, ex, d["ticker"].values, d["y0"].values, k)
        d[f"att_comp.{k}"] = status(pan, ex, d["pr_ticker"].fillna("").values, d["y0"].values, k)
    d["base_rev"] = ~np.isnan(base_f)
    return d, pan.last_year


def cells(d):
    c = fv.cells(d)
    main = c["forced"]
    c["nonscandal"] = main[main["why"] != "scandal"]
    c["sexrel"] = main[(main["why"] == "scandal") & main["reason"].isin(SEX)]
    return {k: c[k] for k in ("founder", "hired", "forced", "retired", "scandal", "nonscandal", "sexrel", "fraud")}


def describe(prefix, x):
    x = pd.Series(x).replace([np.inf, -np.inf], np.nan).dropna().astype(float)
    if len(x) >= MIN_CELL and (x != 0).sum() == 0:
        put(prefix + ".count", len(x), n=len(x))
        return
    fv.describe(prefix, x, "ret")


def clean(x):
    return pd.Series(x).replace([np.inf, -np.inf], np.nan).dropna().astype(float)


def holm_family(keys, suffix, tag):
    ps = sorted((R[k]["p"], k) for k in keys if k in R and R[k].get("p") is not None)
    running = 0.0
    for i, (p, k) in enumerate(ps):
        running = max(running, min(1.0, (len(ps) - i) * p))
        put(k[: -len(suffix)] + tag, running, n=R[k]["n"], p=running)


def regress(prefix, data, y, flag):
    cols = [y, flag, "mv31", "rev_pre_firm", "prior12", "lev", "industry", "year", "cik"]
    x = data[cols].replace([np.inf, -np.inf], np.nan).dropna().copy()
    put(prefix + ".n", len(x), n=len(x))
    if x[flag].sum() < MIN_CELL or (1 - x[flag]).sum() < MIN_CELL:
        return
    x = x.rename(columns={y: "y"})
    x["lmv"] = np.log(x["mv31"])
    for c in ("y", "rev_pre_firm", "prior12", "lev"):
        x[c] = np.clip(x[c], *np.percentile(x[c], [1, 99]))
    m = smf.ols(f"y ~ {flag} + lmv + rev_pre_firm + prior12 + lev + C(industry) + C(year)", data=x).fit(
        cov_type="cluster", cov_kwds={"groups": x["cik"].astype(int)}
    )
    n = int(m.nobs)
    ci = m.conf_int().loc[flag]
    put(prefix + ".coef", m.params[flag], n=n, se=m.bse[flag], t=m.tvalues[flag], p=m.pvalues[flag])
    put(prefix + ".coef.ci_low", ci[0], n=n)
    put(prefix + ".coef.ci_high", ci[1], n=n)
    put(prefix + ".n_flag", int(x[flag].sum()), n=n)


def main():
    v = pd.read_parquet(HERE / "out" / "founder_value.parquet")
    d, last_year = build(v)
    d.to_parquet(HERE / "out" / "founder_growth.parquet", index=False)
    C = cells(d)
    put("fg.last_year", last_year, n=len(d))
    every = [(o, h) for o in OUTCOMES + ATT for h in HOR]
    for name, g in C.items():
        put(f"fg.{name}.n_all", len(g), n=len(g))
        put(f"fg.{name}.n_base", int(g["base_rev"].sum()), n=len(g))
        for o, h in every:
            k = f"{o}.{h}"
            describe(f"fg.{name}.pr.{k}", g[f"pr.{k}"])
            if o in OUTCOMES:
                describe(f"fg.{name}.ind.{k}", g[f"ind.{k}"])
            pair = g[[f"firm.{k}.post", f"comp.{k}.post", f"pr.{k}"]].replace([np.inf, -np.inf], np.nan).dropna()
            if len(pair) >= MIN_CELL:
                put(f"fg.{name}.firm.{k}.post.median", pair[f"firm.{k}.post"].median(), n=len(pair))
                put(f"fg.{name}.comp.{k}.post.median", pair[f"comp.{k}.post"].median(), n=len(pair))
                put(f"fg.{name}.firm.{k}.post.mean", pair[f"firm.{k}.post"].mean(), n=len(pair))
                put(f"fg.{name}.comp.{k}.post.mean", pair[f"comp.{k}.post"].mean(), n=len(pair))
                pre = g.loc[pair.index, [f"firm.{o}.pre", f"comp.{o}.pre"]]
                put(f"fg.{name}.firm.{k}.pre.median", pre[f"firm.{o}.pre"].median(), n=len(pair))
                put(f"fg.{name}.comp.{k}.pre.median", pre[f"comp.{o}.pre"].median(), n=len(pair))
        for h, col in SHR.items():
            describe(f"fg.{name}.pr.shr.{h}", g[col])
        # the revenue path, pairs with both in the year
        for k in YEARS:
            pair = g[[f"idx_firm.{k}", f"idx_comp.{k}"]].replace([np.inf, -np.inf], np.nan).dropna()
            put(f"fgpath.{name}.count.{'m' if k < 0 else 'p'}{abs(k)}", len(pair), n=len(pair))
            if len(pair) >= MIN_CELL:
                put(
                    f"fgpath.{name}.firm.{'m' if k < 0 else 'p'}{abs(k)}.median",
                    pair[f"idx_firm.{k}"].median(),
                    n=len(pair),
                )
                put(
                    f"fgpath.{name}.comp.{'m' if k < 0 else 'p'}{abs(k)}.median",
                    pair[f"idx_comp.{k}"].median(),
                    n=len(pair),
                )
        # attrition, among firms with revenue in year -1
        b = g[g["base_rev"]]
        for k in range(0, 6):
            for st in ("filing", "bankrupt", "cause", "acquired", "other", "not_reached", "no_filing"):
                put(f"fgatt.{name}.p{k}.{st}", int((b[f"att.{k}"] == st).sum()), n=len(b))
            both = (b[f"att.{k}"] == "filing") & (b[f"att_comp.{k}"] == "filing")
            put(f"fgatt.{name}.p{k}.pairs", int(both.sum()), n=len(b))
    PAIRS = (("founder_vs_hired", "founder", "hired"), ("scandal_vs_nonscandal", "scandal", "nonscandal"))
    for label, a, b in PAIRS:
        for o, h in every:
            k = f"{o}.{h}"
            fv.welch(f"fgdiff.{label}.pr.{k}", clean(C[a][f"pr.{k}"]), clean(C[b][f"pr.{k}"]))
            if o in OUTCOMES:
                fv.welch(f"fgdiff.{label}.ind.{k}", clean(C[a][f"ind.{k}"]), clean(C[b][f"ind.{k}"]))
        for h, col in SHR.items():
            fv.welch(f"fgdiff.{label}.pr.shr.{h}", clean(C[a][col]), clean(C[b][col]))
        fam = [f"fgdiff.{label}.pr.{o}.{h}" for o in OUTCOMES for h in HOR]
        holm_family([k + ".diff" for k in fam], ".diff", ".holm_p")
        holm_family([k + ".diff_median" for k in fam], ".diff_median", ".holm_p_median")
    for name in ("founder", "hired", "scandal", "nonscandal", "forced"):
        fam = [f"fg.{name}.pr.{o}.{h}" for o in OUTCOMES for h in HOR]
        holm_family([k + ".mean" for k in fam], ".mean", ".holm_p")
        holm_family([k + ".median" for k in fam], ".median", ".holm_p_median")
    main_ = C["forced"].copy()
    main_["founder"] = (main_["who"] == "founder").astype(int)
    main_["scandal"] = (main_["why"] == "scandal").astype(int)
    for flag in ("founder", "scandal"):
        for o, h in every:
            regress(f"fgreg.{flag}.{o}.{h}", main_, f"gap.{o}.{h}", flag)
    cases = {}
    for name in ("sexrel", "scandal", "founder"):
        g = C[name]
        cases[name] = [
            {
                "event_id": int(r["event_id"]),
                "coname": r["coname"],
                "year": int(r["y0"]),
                "competitor": r["pr_ticker"],
                **{
                    f"{o}.{h}": (None if pd.isna(r[f"pr.{o}.{h}"]) else float(r[f"pr.{o}.{h}"]))
                    for o in ("rev", "rev_att")
                    for h in HOR
                },
                "status_y3": r["st_firm.y3"],
                "status_y5": r["st_firm.y5"],
            }
            for _, r in g.iterrows()
        ]
    R["_cases"] = cases
    (OUT / "founder_growth_stats.json").write_text(json.dumps(R, indent=1, default=str))
    for name in ("founder", "hired", "scandal", "nonscandal", "sexrel"):
        for h in HOR:
            a = R.get(f"fg.{name}.pr.rev.{h}.median") or {}
            c = R.get(f"fg.{name}.pr.rev.{h}.count") or {}
            print(name, h, "rev DiD median", a.get("value"), "p", a.get("p"), "n", c.get("value"))
    for label, _, _ in PAIRS:
        for h in HOR:
            k = R.get(f"fgdiff.{label}.pr.rev.{h}.diff") or {}
            print(label, h, "rev diff", k.get("value"), "p", k.get("p"))
    print("wrote founder_growth_stats.json", len(R), "keys")


if __name__ == "__main__":
    main()
