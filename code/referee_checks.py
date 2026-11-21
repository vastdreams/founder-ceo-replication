"""Checks the platform referee asked for (reviews of 21 Nov 2026), each answered with a test, not a sentence.

  equiv.*    how large a gap the data allow: the 90% and 95% intervals of the personal-scandal and founder gaps at
             the announcement, the minimum detectable gap (80% power, 5% two-sided) and two one-sided tests (TOST)
             against a margin fixed before looking: the average firing's own three-day fall
  strict.*   the firings the evidence-based coding also reads as forced (D-09) and those it reads as unclear,
             at the announcement, in delisting within 60 months (raw and with the full controls) and against
             matched firms
  dsel.*     who gets a precise announcement date: well-dated against other firings on size, prior return,
             profitability, leverage, founder and scandal shares and later delisting; and the announcement return
             of the well-dated firings reweighted (inverse probability of being well dated) to look like all firings
  cox.*      delisting and bankruptcy as durations: Cox proportional hazards with every month of follow-up up to
             60 months, censored at the end of the price file, strata by Fama-French industry
  fraud.*    the firings over fraud or other legal violation put back: the announcement return of all firings and
             the 60-month delisting gap with a fraud indicator
  board.*    fired founders against fired hired CEOs on the board two years later, with tests
  code.*     how often the hand review changed each model code (founder, fraud, sexual conduct, other conduct)

Inputs : analysis/out/{returns,ops_matched,controls,delist_dates,board_outcomes,founder_final}.parquet,
         out/event_coding_final.jsonl, paper/*_review.csv
Output : outputs/referee_stats.json (flat dict of named statistics, as stats_returns.py), read by combine_results.py
"""

import json
import pathlib

import numpy as np
import pandas as pd
import sample
import stats_returns as sr
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.duration.hazard_regression import PHReg

HERE = pathlib.Path(__file__).parent
PACK = HERE.parent
OUT = PACK / "outputs"
R = sr.R
R.clear()
put, one_group, two_group = sr.put, sr.one_group, sr.two_group
HORIZON_DAYS = 1826  # 60 months
CTRL = "log_mcap + roa_m1 + prior_ret_12m_w + leverage_w + btm_w + distress + loss"


def wins(s, lo=0.01, hi=0.99):
    s = pd.to_numeric(s, errors="coerce")
    return s.clip(*s.quantile([lo, hi]))


def welch(a, b):
    a, b = pd.Series(a).dropna().astype(float), pd.Series(b).dropna().astype(float)
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    se = float(np.sqrt(va + vb))
    df = (va + vb) ** 2 / (va**2 / (len(a) - 1) + vb**2 / (len(b) - 1))
    return a.mean() - b.mean(), se, df, len(a) + len(b)


def equivalence(prefix, a, b, margin):
    diff, se, df, n = welch(a, b)
    q90, q95 = stats.t.ppf(0.95, df), stats.t.ppf(0.975, df)
    put(prefix + ".diff", diff, n=n, se=se, p=2 * (1 - stats.t.cdf(abs(diff) / se, df)))
    put(prefix + ".ci90_low", diff - q90 * se, n=n)
    put(prefix + ".ci90_high", diff + q90 * se, n=n)
    put(prefix + ".ci95_low", diff - q95 * se, n=n)
    put(prefix + ".ci95_high", diff + q95 * se, n=n)
    put(prefix + ".mde", 2.8 * se, n=n)
    p_low = 1 - stats.t.cdf((diff + margin) / se, df)  # H0: the gap is -margin or below
    p_high = stats.t.cdf((diff - margin) / se, df)  # H0: the gap is +margin or above
    put(prefix + ".tost_p", max(p_low, p_high), n=n, p=max(p_low, p_high))
    put(prefix + ".tost_p_larger_fall", p_low, n=n, p=p_low)
    put(prefix + ".margin", margin, n=n)


def load_ops(include_criminal=False):
    """ops_matched.parquet with the final labels, as stats_ops.py reads it, plus the controls and bankruptcy dates."""
    d = pd.read_parquet(HERE / "out" / "ops_matched.parquet")
    c = pd.DataFrame([json.loads(x) for x in open(HERE / "out" / "event_coding_final.jsonl")]).rename(
        columns={"forced": "forced_llm"}
    )
    d = d.merge(c[["event_id", "ceo_is_founder", "primary_reason", "forced_llm"]], on="event_id", how="left")
    d = d.merge(
        pd.read_parquet(HERE / "out" / "founder_final.parquet")[["event_id", "founder"]], on="event_id", how="left"
    )
    d["founder"] = d["founder"].fillna(0).astype(int)
    d = sample.apply(d, include_criminal=include_criminal)
    d = d.merge(pd.read_parquet(HERE / "out" / "controls.parquet"), on="event_id", how="left")
    d = d.merge(pd.read_parquet(HERE / "out" / "delist_dates.parquet"), on="event_id", how="left")
    d["log_mcap"] = np.log(pd.to_numeric(d["mcap_m1"], errors="coerce").clip(lower=1))
    d["roa_m1"] = wins(d["roa_-1"])
    for k in ("prior_ret_12m", "leverage", "btm"):
        d[k + "_w"] = wins(d[k])
    d["year"] = pd.to_datetime(d["event_date"]).dt.year
    d["gone"] = d["delisted_5y"]
    d["bankrupt"] = np.where(d["delisted_5y"].notna(), (d["delist_kind_5y"] == "bankruptcy").astype(float), np.nan)
    d["strict"] = ((d["forced"] == 1) & (d["forced_llm"] == "yes")).astype(int)
    d["unclear"] = ((d["forced"] == 1) & (d["forced_llm"] == "unclear")).astype(int)
    return d


def lpm(prefix, df, y, terms, key="forced", ctrl=CTRL):
    x = df.dropna(subset=[y, "log_mcap", "roa_m1", "prior_ret_12m_w", "leverage_w", "btm_w", "distress", "loss"])
    m = smf.ols(f"{y} ~ {terms} + {ctrl} + C(year) + C(famaindustry)", data=x).fit(
        cov_type="cluster", cov_kwds={"groups": x["year"]}
    )
    put(prefix, m.params[key], se=m.bse[key], t=m.tvalues[key], p=m.pvalues[key], n=int(m.nobs))
    return m


def equivalence_checks(d):
    """d: the well-dated departures of the paper's sample (stats_returns.load_labelled)."""
    f = d[d["forced"] == 1]
    margin = abs(f["car_mm_m1p1"].dropna().mean())
    equivalence(
        "equiv.scandal_gap.mm_m1p1", f[f["conduct"] == 1]["car_mm_m1p1"], f[f["conduct"] == 0]["car_mm_m1p1"], margin
    )
    equivalence(
        "equiv.founder_gap.mm_m1p1",
        f[f["founder_v0"] == 1]["car_mm_m1p1"],
        f[f["founder_v0"] == 0]["car_mm_m1p1"],
        margin,
    )


def strict_checks(d, ops):
    f = d[d["forced"] == 1]
    r = d[d["forced"] == 0]
    for k in ("yes", "unclear", "no"):
        one_group(f"strict.llm_{k}.mm_m1p1", f[f["forced_llm"] == k]["car_mm_m1p1"])
    two_group(
        "strict.llm_yes_vs_unclear.mm_m1p1",
        f[f["forced_llm"] == "yes"]["car_mm_m1p1"],
        f[f["forced_llm"] == "unclear"]["car_mm_m1p1"],
    )
    two_group("strict.llm_yes_vs_retired.mm_m1p1", f[f["forced_llm"] == "yes"]["car_mm_m1p1"], r["car_mm_m1p1"])
    of, orr = ops[ops["forced"] == 1], ops[ops["forced"] == 0]
    for name, g in (("yes", of[of["strict"] == 1]), ("unclear", of[of["unclear"] == 1]), ("retired", orr)):
        x5 = g.dropna(subset=["gone"])
        put(f"strict.exit.{name}.delisted_5y", x5["gone"].mean(), n=len(x5))
        put(f"strict.exit.{name}.bankruptcy_5y", x5["bankrupt"].mean(), n=len(x5))
        for h in (1, 3, 5):
            one_group(f"strict.mbhar.{name}.{h}y", g[f"mbhar_{h}y"])
    # delisting with the full controls: only the strict firings (or only the unclear ones) against retirements
    for name, flag in (("yes", "strict"), ("unclear", "unclear")):
        sub = ops[(ops["forced"] == 0) | (ops[flag] == 1)].copy()
        lpm(f"strict.reg.gone.{name}", sub, "gone", "forced")
        lpm(f"strict.reg.bankrupt.{name}", sub, "bankrupt", "forced")


def date_selection(d_all, ops):
    """Well-dated firings against firings dated only by a filing or by the day the CEO left office."""
    f = d_all[d_all["forced"] == 1].merge(
        ops[["event_id", "log_mcap", "mcap_m1", "roa_m1", "prior_ret_12m_w", "leverage_w", "gone", "strict"]],
        on="event_id",
        how="left",
    )
    a, b = f[f["dated"] == 1], f[f["dated"] == 0]
    put("dsel.n_dated", len(a))
    put("dsel.n_undated", len(b))
    for v, scale in (("mcap_m1", 1e-9), ("prior_ret_12m_w", 1.0), ("roa_m1", 1.0), ("leverage_w", 1.0)):
        x, y = a[v].dropna() * scale, b[v].dropna() * scale
        u = stats.mannwhitneyu(x, y)
        put(f"dsel.{v}.dated", x.median(), n=len(x), p=u.pvalue)
        put(f"dsel.{v}.undated", y.median(), n=len(y), p=u.pvalue)
    for v, col in (("founder", "founder_v0"), ("conduct", "conduct"), ("strict", "strict"), ("gone", "gone")):
        x, y = a[col].dropna(), b[col].dropna()
        tab = np.array([[x.sum(), len(x) - x.sum()], [y.sum(), len(y) - y.sum()]])
        p = stats.chi2_contingency(tab)[1]
        put(f"dsel.{v}.dated", x.mean(), n=len(x), p=p)
        put(f"dsel.{v}.undated", y.mean(), n=len(y), p=p)
    yr = pd.to_datetime(f["event_date"]).dt.year
    put("dsel.year.dated", yr[f["dated"] == 1].median(), n=int((f["dated"] == 1).sum()))
    put("dsel.year.undated", yr[f["dated"] == 0].median(), n=int((f["dated"] == 0).sum()))
    # Inverse-probability weights: the chance a firing is well dated, from its observable traits; each well-dated
    # firing then counts for the firings like it that were not dated (weights trimmed at the 1st and 99th pct).
    z = f.dropna(subset=["log_mcap", "roa_m1", "prior_ret_12m_w", "leverage_w"]).copy()
    z["strict"] = z["strict"].fillna(0)
    z["yb"] = (pd.to_datetime(z["event_date"]).dt.year // 3).astype(str)
    lg = smf.logit(
        "dated ~ log_mcap + roa_m1 + prior_ret_12m_w + leverage_w + founder_v0 + conduct + strict + C(yb)", data=z
    ).fit(disp=0)
    z["ps"] = lg.predict(z)
    w = z[z["dated"] == 1].dropna(subset=["car_mm_m1p1"]).copy()
    w["w"] = (1 / w["ps"]).clip(*(1 / w["ps"]).quantile([0.01, 0.99]))
    m = sm.WLS(w["car_mm_m1p1"], np.ones(len(w)), weights=w["w"]).fit(cov_type="HC1")
    put("dsel.ipw.mm_m1p1.mean", m.params.iloc[0], n=len(w), t=m.tvalues.iloc[0], p=m.pvalues.iloc[0])
    one_group("dsel.same_sample.mm_m1p1", w["car_mm_m1p1"])
    # A late day 0 moves the news outside a three-day window but not outside a wider one: every firing, whatever its
    # date source, over trading days -5 to +5 (review round 2: "rerun with a wider window").
    for name, g in (("all", f), ("dated", f[f["dated"] == 1]), ("undated", f[f["dated"] == 0])):
        one_group(f"dsel.window.{name}.mm_m5p5", g["car_mm_m5p5"])
    put("dsel.logit.pseudo_r2", lg.prsquared, n=int(lg.nobs))


def cox_checks(ops):
    end = pd.to_datetime(ops["lastpricedate"]).max()
    d = ops.copy()
    day0 = pd.to_datetime(d["day0"])
    last = pd.to_datetime(d["lastpricedate"])
    t_all = np.where(d["isdelisted"] == "Y", (last - day0).dt.days, (end - day0).dt.days).astype(float)
    d["time"] = np.minimum(t_all, HORIZON_DAYS).clip(min=1)
    d["ev_gone"] = ((d["isdelisted"] == "Y") & (t_all <= HORIZON_DAYS)).astype(int)
    d["ev_bankrupt"] = (d["days_to_bankruptcy"].notna() & (d["days_to_bankruptcy"] <= HORIZON_DAYS)).astype(int)
    d["yb"] = (d["year"] // 3).astype(str)
    covs_full = ["forced", "log_mcap", "roa_m1", "prior_ret_12m_w", "leverage_w", "btm_w", "distress", "loss"]
    covs_base = ["forced", "log_mcap", "roa_m1"]
    for spec, covs in (("base", covs_base), ("full", covs_full)):
        x = d.dropna(subset=covs + ["famaindustry"]).copy()
        yb = pd.get_dummies(x["yb"], prefix="yb", drop_first=True, dtype=float)
        X = pd.concat([x[covs].astype(float), yb], axis=1)
        for ev in ("gone", "bankrupt"):
            m = PHReg(x["time"].values, X.values, status=x[f"ev_{ev}"].values, strata=x["famaindustry"].values).fit()
            i = 0  # forced is the first column
            put(
                f"cox.{ev}.{spec}.forced_hr",
                float(np.exp(m.params[i])),
                n=int(len(x)),
                p=float(m.pvalues[i]),
                t=float(m.tvalues[i]),
                ci_low=float(np.exp(m.params[i] - 1.96 * m.bse[i])),
                ci_high=float(np.exp(m.params[i] + 1.96 * m.bse[i])),
                events=int(x[f"ev_{ev}"].sum()),
            )
            put(f"cox.{ev}.{spec}.events", int(x[f"ev_{ev}"].sum()), n=int(len(x)))
    # the strict firings only, against retirements, full controls
    x = d[(d["forced"] == 0) | (d["strict"] == 1)].dropna(subset=covs_full + ["famaindustry"]).copy()
    yb = pd.get_dummies(x["yb"], prefix="yb", drop_first=True, dtype=float)
    X = pd.concat([x[covs_full].astype(float), yb], axis=1)
    for ev in ("gone", "bankrupt"):
        m = PHReg(x["time"].values, X.values, status=x[f"ev_{ev}"].values, strata=x["famaindustry"].values).fit()
        put(
            f"cox.{ev}.strict.forced_hr",
            float(np.exp(m.params[0])),
            n=int(len(x)),
            p=float(m.pvalues[0]),
            t=float(m.tvalues[0]),
            ci_low=float(np.exp(m.params[0] - 1.96 * m.bse[0])),
            ci_high=float(np.exp(m.params[0] + 1.96 * m.bse[0])),
            events=int(x[f"ev_{ev}"].sum()),
        )
    put("cox.n_incomplete_horizon", int(d["delisted_5y"].isna().sum()), n=len(d))


def fraud_checks(d_c):
    """d_c: well-dated departures with the fraud and legal-violation firings kept."""
    f = d_c[d_c["forced"] == 1]
    one_group("fraud.all_firings.mm_m1p1", f["car_mm_m1p1"])
    ops_c = load_ops(include_criminal=True)
    of = ops_c[ops_c["forced"] == 1].dropna(subset=["gone"])
    put("fraud.all_firings.delisted_5y", of["gone"].mean(), n=len(of))
    put("fraud.all_firings.bankruptcy_5y", of["bankrupt"].mean(), n=len(of))
    for y in ("gone", "bankrupt"):
        m = lpm(f"fraud.reg.{y}.forced", ops_c, y, "forced + criminal")
        put(
            f"fraud.reg.{y}.criminal",
            m.params["criminal"],
            se=m.bse["criminal"],
            t=m.tvalues["criminal"],
            p=m.pvalues["criminal"],
            n=int(m.nobs),
        )


def board_checks():
    b = pd.read_parquet(HERE / "out" / "board_outcomes.parquet").drop(columns=["founder", "conduct"], errors="ignore")
    b = b.merge(
        pd.read_parquet(HERE / "out" / "founder_final.parquet")[["event_id", "founder"]], on="event_id", how="left"
    )
    b["founder"] = b["founder"].fillna(0).astype(int)
    ret = pd.read_parquet(HERE / "out" / "returns.parquet")[["event_id", "event_date"]]
    b = b.merge(ret, on="event_id", how="left")
    b = sample.apply(b)
    f = b[b["forced"] == 1]
    fo, hi = f[f["founder"] == 1], f[f["founder"] == 0]
    two_group("board.founder_vs_hired.director_turnover", fo["director_turnover"], hi["director_turnover"])
    for v in ("ceo_stays_director", "outside_chair_after"):
        x, y = fo[v].dropna(), hi[v].dropna()
        if len(x) >= 5 and len(y) >= 5:
            p = stats.fisher_exact([[x.sum(), len(x) - x.sum()], [y.sum(), len(y) - y.sum()]])[1]
            put(f"board.founder_vs_hired.{v}.diff", x.mean() - y.mean(), n=len(x) + len(y), p=p)
            put(f"board.founder_vs_hired.{v}.founder", x.mean(), n=len(x))
            put(f"board.founder_vs_hired.{v}.hired", y.mean(), n=len(y))


def coding_checks():
    """How often the one coder's hand review changed the model's code, by kind of code."""
    specs = (
        ("founder", "founder_review.csv", "model_code", "decision"),
        ("fraud", "fraud_review.csv", "model_code", "decision"),
        ("sex", "conduct_review.csv", "model_label", "decision"),
        ("personal", "personal_conduct_review.csv", "model_label", "decision"),
    )
    for name, fn, mcol, dcol in specs:
        rv = pd.read_csv(PACK / "paper" / fn)
        same = rv[mcol].astype(str).str.strip() == rv[dcol].astype(str).str.strip()
        put(f"code.{name}.n_reviewed", len(rv))
        put(f"code.{name}.n_kept", int(same.sum()), n=len(rv))
        put(f"code.{name}.share_kept", same.mean(), n=len(rv))
        put(f"code.{name}.n_changed", int((~same).sum()), n=len(rv))


def main():
    d_all = sr.load_labelled()
    d = d_all[d_all["dated"] == 1].copy()
    d_all_c = sr.load_labelled(include_criminal=True)
    d_c = d_all_c[d_all_c["dated"] == 1].copy()
    ops = load_ops()
    equivalence_checks(d)
    strict_checks(d, ops)
    date_selection(d_all, ops)
    cox_checks(ops)
    fraud_checks(d_c)
    board_checks()
    coding_checks()
    (OUT / "referee_stats.json").write_text(json.dumps(R, indent=1, default=float))
    for k, v in R.items():
        print(f"{k:52s} {v.get('value')!s:>22} n={v.get('n')} p={v.get('p')}")


if __name__ == "__main__":
    main()
