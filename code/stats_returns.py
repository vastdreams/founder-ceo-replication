"""Statistics for the return results (sections A, B, C, D, E, F of the paper).

Input : analysis/out/returns.parquet (event_study.py)
Output: outputs/returns_stats.json, a flat dict of named statistics, each with value, n, and test
        fields, consumed by combine_results.py. No number in the paper is typed by hand.
Tests :
  mean CAR       cross-sectional t, and Boehmer-Musumeci-Poulsen (1991) standardized t
  median         Wilcoxon signed-rank (one group) or Mann-Whitney U (two groups)
  difference     Welch t
  long-run BHAR  skewness-adjusted t (Lyon, Barber, Tsai 1999) and bootstrap 95% CI of the mean
  regression     OLS of CAR on group dummies with event-year fixed effects, SE clustered by year
"""

import json
import pathlib

import numpy as np
import pandas as pd
import sample
import statsmodels.formula.api as smf
from scipy import stats

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "outputs"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(20261119)
R = {}
# Date sources precise enough for a three-day window (D-15). The 8-K dates agree with the database's within three
# days only 58% of the time and their firings show a much weaker reaction, so they are a robustness row, not the main
# sample.
PRECISE = {"database", "hand-checked"}


def put(key, value, **kw):
    R[key] = {"value": None if value is None or (isinstance(value, float) and np.isnan(value)) else float(value), **kw}


def one_group(prefix, x):
    x = pd.Series(x).dropna().astype(float)
    if len(x) < 5:
        put(prefix + ".count", len(x))
        return
    t = stats.ttest_1samp(x, 0.0)
    w = stats.wilcoxon(x) if len(x) >= 10 else None
    put(prefix + ".mean", x.mean(), n=len(x), t=t.statistic, p=t.pvalue)
    put(prefix + ".median", x.median(), n=len(x), p=None if w is None else w.pvalue)
    put(prefix + ".share_negative", (x < 0).mean(), n=len(x))
    put(prefix + ".count", len(x))


def bmp(prefix, scar):
    s = pd.Series(scar).dropna().astype(float)
    if len(s) < 5:
        return
    z = s.mean() / (s.std(ddof=1) / np.sqrt(len(s)))
    put(prefix + ".bmp_t", z, n=len(s), p=2 * (1 - stats.norm.cdf(abs(z))))


def two_group(prefix, a, b):
    a, b = pd.Series(a).dropna().astype(float), pd.Series(b).dropna().astype(float)
    if len(a) < 5 or len(b) < 5:
        return
    t = stats.ttest_ind(a, b, equal_var=False)
    u = stats.mannwhitneyu(a, b)
    put(prefix + ".diff_mean", a.mean() - b.mean(), n=len(a) + len(b), t=t.statistic, p=t.pvalue)
    put(prefix + ".diff_median", a.median() - b.median(), n=len(a) + len(b), p=u.pvalue)


def skew_adj(prefix, x):
    x = pd.Series(x).dropna().astype(float)
    n = len(x)
    if n < 10:
        return
    s = x.mean() / x.std(ddof=1)
    g = ((x - x.mean()) ** 3).sum() / (n * x.std(ddof=1) ** 3)
    t = np.sqrt(n) * (s + g * s**2 / 3 + g / (6 * n))
    boots = [rng.choice(x.values, n, replace=True).mean() for _ in range(2000)]
    put(
        prefix + ".skewadj_t",
        t,
        n=n,
        p=2 * (1 - stats.norm.cdf(abs(t))),
        ci_low=np.percentile(boots, 2.5),
        ci_high=np.percentile(boots, 97.5),
    )


def load_labelled(include_criminal: bool = False):
    """returns.parquet with the final labels: model codes, the hand founder review and the hand conduct review.
    Firings for crimes (financial misconduct, legal or regulatory violations) are dropped unless asked for, and
    `conduct` marks a firing over a personal scandal (sample.py, D-18)."""
    d = pd.read_parquet(HERE / "out" / "returns.parquet")
    coding = HERE / "out" / "event_coding_final.jsonl"
    if coding.exists():  # v1 labels replace the regex flags (hand validation pending, see paper/DECISIONS.md)
        c = pd.DataFrame([json.loads(x) for x in open(coding)]).rename(columns={"forced": "forced_llm"})
        d = d.merge(
            c[["event_id", "ceo_is_founder", "founder_family", "forced_llm", "primary_reason", "confidence"]],
            on="event_id",
            how="left",
        )
        d["founder_v0"] = (d["ceo_is_founder"] == "yes").astype(int)
        ff = HERE / "out" / "founder_final.parquet"
        if ff.exists():  # hand-reviewed founder flag (paper/founder_review.csv)
            d = d.drop(columns=["founder_v0"]).merge(
                pd.read_parquet(ff)[["event_id", "founder"]].rename(columns={"founder": "founder_v0"}),
                on="event_id",
                how="left",
            )
            d["founder_v0"] = d["founder_v0"].fillna(0).astype(int)
        fr = HERE.parent / "paper" / "fraud_review.csv"
        if fr.exists():  # hand review of every financial-misconduct label (paper/fraud_review.csv)
            rv = pd.read_csv(fr)[["event_id", "decision"]]
            d = d.merge(rv, on="event_id", how="left")
            d["primary_reason"] = d["decision"].fillna(d["primary_reason"])
            d = d.drop(columns=["decision"])
        cr = HERE.parent / "paper" / "conduct_review.csv"
        if cr.exists():  # hand review of every sexual-conduct and relationship label (paper/conduct_review.csv)
            rv = pd.read_csv(cr)[["event_id", "decision"]]
            d = d.merge(rv, on="event_id", how="left")
            d["primary_reason"] = d["decision"].fillna(d["primary_reason"])
            d = d.drop(columns=["decision"])
        d["relationship_v0"] = (d["primary_reason"] == "relationship_with_employee").astype(int)
        d["pushed_retirement"] = ((d["code"] == 5) & (d["forced_llm"] == "yes")).astype(int)
    d["year"] = pd.to_datetime(d["event_date"]).dt.year
    # Precisely dated: the announcement date comes from the database, a hand check or the firm's own 8-K (redate.py),
    # not from the day the CEO left office. Announcement-window results use these; long-run results use every
    # departure, which a few days of dating error cannot move (D-15).
    d["dated"] = d["date_source"].isin(PRECISE).astype(int) if "date_source" in d else 1
    return sample.apply(d, include_criminal=include_criminal)


def make_groups(d, with_crimes=None):
    """The comparison groups on the paper's sample `d`. Firings for crimes are not in `d`; the discussion's fraud and
    crime groups come from `with_crimes` (the same departures with them kept), when given."""
    f, r = d[d["forced"] == 1], d[d["forced"] == 0]
    fc = with_crimes[with_crimes["forced"] == 1] if with_crimes is not None else f.iloc[0:0]
    return {
        "forced": f,
        "retired": r,
        "forced_founder": f[f["founder_v0"] == 1],
        "forced_nonfounder": f[f["founder_v0"] == 0],
        "conduct": f[f["conduct"] == 1],
        "performance": f[f["conduct"] == 0],
        "relationship": f[f["relationship_v0"] == 1],
        "retired_founder": r[r["founder_v0"] == 1],
        # sex vs money: sexual misconduct or a relationship with an employee, against financial misconduct
        "sex_or_relationship": f[
            f["primary_reason"].isin(["relationship_with_employee", "relationship_other", "other_sexual_misconduct"])
        ],
        "financial_misconduct": fc[fc["primary_reason"] == "financial_misconduct"],
        "criminal": fc[fc["criminal"] == 1],
        "founder_personal": f[(f["founder_v0"] == 1) & (f["conduct"] == 1)],
        # strict: the database codes the exit forced and the evidence-based coding agrees (D-09)
        "forced_strict": f[f["forced_llm"] == "yes"],
        "forced_strict_founder": f[(f["forced_llm"] == "yes") & (f["founder_v0"] == 1)],
        "forced_strict_nonfounder": f[(f["forced_llm"] == "yes") & (f["founder_v0"] == 0)],
    }


def main():
    d_all = load_labelled()
    d = d_all[d_all["dated"] == 1].copy()
    d_all_c = load_labelled(include_criminal=True)  # the discussion's comparison: firings for crimes kept
    d_c = d_all_c[d_all_c["dated"] == 1].copy()
    f_all = d_all[d_all["forced"] == 1]
    fc_all = d_all_c[(d_all_c["forced"] == 1) & (d_all_c["criminal"] == 1)]
    put("a.n_criminal_all_dates", len(fc_all))
    put("a.n_criminal_dated", int((fc_all["dated"] == 1).sum()))
    put("a.n_criminal_founder_all_dates", int((fc_all["founder_v0"] == 1).sum()))
    put("a.n_forced_with_crimes_all_dates", int((d_all_c["forced"] == 1).sum()))
    put("a.n_forced_all_dates", len(f_all))
    put("a.n_forced_undated", int((f_all["dated"] == 0).sum()))
    for src in ("database", "8-K", "NYT"):
        put(f"a.n_forced_dated_{src.lower().replace('-', '')}", int((f_all.get("date_source") == src).sum()))
    one_group("rob.all_dates.forced.mm_m1p1", f_all["car_mm_m1p1"])
    two_group(
        "rob.all_dates.founder_vs_nonfounder.mm_m1p1",
        f_all[f_all["founder_v0"] == 1]["car_mm_m1p1"],
        f_all[f_all["founder_v0"] == 0]["car_mm_m1p1"],
    )
    one_group("rob.undated.forced.mm_m1p1", f_all[f_all["dated"] == 0]["car_mm_m1p1"])
    ga = make_groups(d_all, d_all_c)  # the splits on every firing, whatever its date source
    for g in (
        "forced_founder",
        "forced_nonfounder",
        "conduct",
        "performance",
        "financial_misconduct",
        "criminal",
        "sex_or_relationship",
        "founder_personal",
    ):
        one_group(f"rob.all_dates.{g}.mm_m1p1", ga[g]["car_mm_m1p1"])
    two_group(
        "rob.all_dates.conduct_vs_performance.mm_m1p1", ga["conduct"]["car_mm_m1p1"], ga["performance"]["car_mm_m1p1"]
    )
    two_group("rob.all_dates.conduct_vs_criminal.mm_m1p1", ga["conduct"]["car_mm_m1p1"], ga["criminal"]["car_mm_m1p1"])
    two_group(
        "rob.all_dates.sex_vs_fraud.mm_m1p1",
        ga["sex_or_relationship"]["car_mm_m1p1"],
        ga["financial_misconduct"]["car_mm_m1p1"],
    )
    one_group("rob.datesrc_8k.mm_m1p1", f_all[f_all["date_source"] == "8-K"]["car_mm_m1p1"])
    f, r = d[d["forced"] == 1], d[d["forced"] == 0]
    if "forced_llm" in f:
        for k in ("yes", "unclear", "no"):
            put(f"a.n_llm_{k}", int((f["forced_llm"] == k).sum()))
    one_group("rob.forced_excl_newopp.mm_m1p1", f[f["primary_reason"] != "new_opportunity"]["car_mm_m1p1"])
    for src in ("database", "8-K", "hand-checked"):  # the announcement return by where its date comes from
        one_group(f"rob.datesrc_{src.lower().replace('-', '')}.mm_m1p1", f[f["date_source"] == src]["car_mm_m1p1"])
    ff_ = d[(d["forced"] == 1) & (d["founder_v0"] == 1)]["car_mm_m1p1"].dropna()
    if len(ff_) > 5:
        se_ = ff_.std(ddof=1) / np.sqrt(len(ff_))
        put("car.forced_founder.mm_m1p1.ci_high", ff_.mean() + 1.96 * se_, n=len(ff_))
        put("car.forced_founder.mm_m1p1.ci_low", ff_.mean() - 1.96 * se_, n=len(ff_))
    groups = make_groups(d, d_c)  # announcement windows: precisely dated departures
    groups_lr = make_groups(d_all, d_all_c)  # long run: every departure
    for g, x in groups_lr.items():
        put(f"a.n_lr_{g}", len(x))

    # H: robustness
    if "pushed_retirement" in d:
        pushed = r[r["pushed_retirement"] == 1]
        wide = pd.concat([f, pushed])
        put("rob.n_pushed_retirements", len(pushed))
        one_group("rob.pushed.mm_m1p1", pushed["car_mm_m1p1"])
        one_group("rob.forced_plus_pushed.mm_m1p1", wide["car_mm_m1p1"])
        two_group(
            "rob.forced_plus_pushed_vs_retired_rest.mm_m1p1",
            wide["car_mm_m1p1"],
            r[r["pushed_retirement"] == 0]["car_mm_m1p1"],
        )
    nocrisis = d[~d["year"].isin([2008, 2009])]
    one_group("rob.forced_excl_crisis.mm_m1p1", nocrisis[nocrisis["forced"] == 1]["car_mm_m1p1"])
    two_group(
        "rob.founder_vs_nonfounder_ff5.m1p1",
        f[f["founder_v0"] == 1]["car_ff5_m1p1"],
        f[f["founder_v0"] == 0]["car_ff5_m1p1"],
    )
    two_group(
        "rob.conduct_vs_performance_ff5.m1p1",
        f[f["conduct"] == 1]["car_ff5_m1p1"],
        f[f["conduct"] == 0]["car_ff5_m1p1"],
    )

    # A: sample
    put("a.events_with_returns", len(d))
    for g, x in groups.items():
        put(f"a.n_{g}", len(x))
    put("a.first_year", d["year"].min())
    put("a.last_year", d["year"].max())

    # B-D: announcement returns
    for g, x in groups.items():
        if len(x) < 2:  # founder_personal: three firings in all, too few for a test; reported as cases
            continue
        for w in ("m1p1", "0p1", "m5p5", "m30p30"):
            one_group(f"car.{g}.mm_{w}", x[f"car_mm_{w}"])
            one_group(f"car.{g}.ff5_{w}", x[f"car_ff5_{w}"])
        bmp(f"car.{g}.mm_m1p1", x["scar_mm_m1p1"])
    for a, b in [
        ("forced", "retired"),
        ("forced_founder", "forced_nonfounder"),
        ("conduct", "performance"),
        ("forced_founder", "retired_founder"),
        ("sex_or_relationship", "financial_misconduct"),
        ("conduct", "criminal"),
        ("forced_strict", "retired"),
        ("forced_strict_founder", "forced_strict_nonfounder"),
    ]:
        for w in ("m1p1", "m5p5"):
            two_group(f"cardiff.{a}_vs_{b}.mm_{w}", groups[a][f"car_mm_{w}"], groups[b][f"car_mm_{w}"])

    # The founder gap in every window, with the minimum detectable effect (80% power, 5% two-sided test)
    for w in ("0p1", "m1p1", "m5p5", "m30p30"):
        a = groups["forced_founder"][f"car_mm_{w}"].dropna()
        b = groups["forced_nonfounder"][f"car_mm_{w}"].dropna()
        two_group(f"cardiff.forced_founder_vs_forced_nonfounder.mm_{w}", a, b)
        se = float(np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b)))
        put(f"mde.founder_gap.mm_{w}", 2.8 * se, n=len(a) + len(b))
        one_group(f"car.forced_founder.mm_{w}", a)
    m = smf.ols(
        "car_mm_m1p1 ~ forced + forced:founder_v0 + founder_v0 + conduct + C(year)",
        data=d.dropna(subset=["car_mm_m1p1"]),
    ).fit(cov_type="cluster", cov_kwds={"groups": d.dropna(subset=["car_mm_m1p1"])["year"]})
    for k in ("forced", "forced:founder_v0", "founder_v0", "conduct"):
        put(
            f"reg.car_m1p1.{k.replace(':', '_x_')}",
            m.params[k],
            se=m.bse[k],
            t=m.tvalues[k],
            p=m.pvalues[k],
            n=int(m.nobs),
        )
    put("reg.car_m1p1.r2", m.rsquared, n=int(m.nobs))
    # Within firings, the founder and personal-scandal gaps with size, the prior 12-month return and year effects
    # (controls.py), since founder and scandal firms may differ in both.
    cp, opp = HERE / "out" / "controls.parquet", HERE / "out" / "ops_matched.parquet"
    if cp.exists() and opp.exists():
        fc = f.merge(pd.read_parquet(cp)[["event_id", "prior_ret_12m"]], on="event_id", how="left").merge(
            pd.read_parquet(opp)[["event_id", "mcap_m1"]], on="event_id", how="left"
        )
        fc = fc.dropna(subset=["car_mm_m1p1", "prior_ret_12m", "mcap_m1"])
        fc["log_mcap"] = np.log(fc["mcap_m1"].clip(lower=1))
        fc["prior_ret_w"] = fc["prior_ret_12m"].clip(*fc["prior_ret_12m"].quantile([0.01, 0.99]))
        mc = smf.ols("car_mm_m1p1 ~ founder_v0 + conduct + log_mcap + prior_ret_w + C(year)", data=fc).fit(
            cov_type="cluster", cov_kwds={"groups": fc["year"]}
        )
        for k in ("founder_v0", "conduct"):
            put(f"regc.car_m1p1.{k}", mc.params[k], se=mc.bse[k], t=mc.tvalues[k], p=mc.pvalues[k], n=int(mc.nobs))

    # E: long-run
    for g, x in groups_lr.items():
        if len(x) < 2:
            continue
        for h in (1, 3, 5):
            one_group(f"bhar.{g}.{h}y", x[f"bhar_{h}y"])
            skew_adj(f"bhar.{g}.{h}y", x[f"bhar_{h}y"])
    for a, b in [
        ("forced", "retired"),
        ("forced_founder", "forced_nonfounder"),
        ("conduct", "performance"),
        ("forced_strict", "retired"),
    ]:
        for h in (1, 3, 5):
            two_group(f"bhardiff.{a}_vs_{b}.{h}y", groups_lr[a][f"bhar_{h}y"], groups_lr[b][f"bhar_{h}y"])

    # F: what happened to the firm within five years
    for g, x in groups_lr.items():
        x5 = x.dropna(subset=["bhar_5y"])
        put(f"exit.{g}.n5", len(x5))
        put(f"exit.{g}.delisted_5y", x5["delisted_5y"].mean() if len(x5) else None, n=len(x5))
        for k in ("acquired", "bankruptcy", "delisted_other", "unknown"):
            put(f"exit.{g}.{k}_5y", (x5["delist_kind_5y"] == k).mean() if len(x5) else None, n=len(x5))
    for a, b in [("forced", "retired"), ("forced_founder", "forced_nonfounder"), ("forced_strict", "retired")] + [
        (g, "retired")
        for g in (
            "forced_founder",
            "forced_nonfounder",
            "conduct",
            "performance",
            "financial_misconduct",
            "criminal",
            "sex_or_relationship",
        )
    ]:
        xa, xb = groups_lr[a].dropna(subset=["bhar_5y"]), groups_lr[b].dropna(subset=["bhar_5y"])
        tab = [
            [xa["delisted_5y"].sum(), len(xa) - xa["delisted_5y"].sum()],
            [xb["delisted_5y"].sum(), len(xb) - xb["delisted_5y"].sum()],
        ]
        chi = stats.chi2_contingency(tab)
        put(
            f"exitdiff.{a}_vs_{b}.delisted_5y",
            xa["delisted_5y"].mean() - xb["delisted_5y"].mean(),
            n=len(xa) + len(xb),
            p=chi.pvalue,
        )

    # F by size: most bankruptcies are among firms worth under $300 million at the fiscal year-end before the event,
    # and firing firms are smaller, so survival is also reported within size bands. A bankruptcy recorded within 180
    # days of the announcement means the firm was already failing when the CEO left (delist_dates.py); those are
    # set aside in the "after the firing" rows.
    ops_p, dd_p = HERE / "out" / "ops_matched.parquet", HERE / "out" / "delist_dates.parquet"
    if ops_p.exists():
        mc = pd.read_parquet(ops_p)[["event_id", "mcap_m1"]]
        bands = [(0, 3e8, "small"), (3e8, 1e9, "mid"), (1e9, 5e9, "large"), (5e9, float("inf"), "mega")]
        for g in ("forced", "retired"):
            x = groups_lr[g].merge(mc, on="event_id", how="left").dropna(subset=["bhar_5y"])
            if dd_p.exists():
                x = x.merge(pd.read_parquet(dd_p)[["event_id", "days_to_bankruptcy"]], on="event_id", how="left")
                early = (x["delist_kind_5y"] == "bankruptcy") & (x["days_to_bankruptcy"] <= 180)
                put(f"exit.{g}.early_bankruptcy_n", int(early.sum()))
                y = x[~early]
                put(f"exit.{g}.after.delisted_5y", y["delisted_5y"].mean(), n=len(y))
                put(f"exit.{g}.after.bankruptcy_5y", (y["delist_kind_5y"] == "bankruptcy").mean(), n=len(y))
            for lo, hi, b in bands:
                z = x[(x["mcap_m1"] >= lo) & (x["mcap_m1"] < hi)]
                put(f"exit.{g}.size_{b}.n5", len(z))
                put(f"exit.{g}.size_{b}.delisted_5y", z["delisted_5y"].mean() if len(z) else None, n=len(z))
                for k in ("acquired", "bankruptcy"):
                    put(f"exit.{g}.size_{b}.{k}_5y", (z["delist_kind_5y"] == k).mean() if len(z) else None, n=len(z))
        for lo, hi, b in bands:
            xa = groups_lr["forced"].merge(mc, on="event_id").dropna(subset=["bhar_5y"])
            xb = groups_lr["retired"].merge(mc, on="event_id").dropna(subset=["bhar_5y"])
            xa = xa[(xa["mcap_m1"] >= lo) & (xa["mcap_m1"] < hi)]
            xb = xb[(xb["mcap_m1"] >= lo) & (xb["mcap_m1"] < hi)]
            if len(xa) and len(xb):
                tab = [
                    [xa["delisted_5y"].sum(), len(xa) - xa["delisted_5y"].sum()],
                    [xb["delisted_5y"].sum(), len(xb) - xb["delisted_5y"].sum()],
                ]
                put(
                    f"exitdiff.forced_vs_retired.size_{b}.delisted_5y",
                    xa["delisted_5y"].mean() - xb["delisted_5y"].mean(),
                    n=len(xa) + len(xb),
                    p=stats.chi2_contingency(tab).pvalue,
                )

    # F by horizon: delisted within 1, 3 and 5 years, each on the events whose horizon is complete
    for g, x in groups_lr.items():
        for h in (1, 3):
            xh = x.dropna(subset=[f"bhar_{h}y"])
            put(f"exit.{g}.n{h}", len(xh))
            put(f"exit.{g}.delisted_{h}y", xh[f"delisted_{h}y"].mean() if len(xh) else None, n=len(xh))
            for k in ("acquired", "bankruptcy"):
                put(f"exit.{g}.{k}_{h}y", (xh[f"delist_kind_{h}y"] == k).mean() if len(xh) else None, n=len(xh))

    # C by detailed reason: every primary reason with at least 10 forced exits
    f2 = f.copy()
    reasons = []
    for reason, x in f2.groupby("primary_reason"):
        if len(x) >= 10:
            one_group(f"car.reason.{reason}.mm_m1p1", x["car_mm_m1p1"])
            reasons.append(reason)
    # Holm-adjusted p-values across the reasons tested (multiple comparisons)
    ps = sorted((R[f"car.reason.{x}.mm_m1p1.mean"]["p"], x) for x in reasons if R.get(f"car.reason.{x}.mm_m1p1.mean"))
    running = 0.0
    for i, (pval, x) in enumerate(ps):
        running = max(running, min(1.0, (len(ps) - i) * pval))
        put(f"car.reason.{x}.mm_m1p1.holm_p", running, n=R[f"car.reason.{x}.mm_m1p1.mean"]["n"])

    # Before and after the announcement: market-adjusted CAR over trading days [-30,-2] and [+2,+60] (paths.py)
    # ar_daily.parquet (paths.py) is built from licensed daily prices and is not published; the per-event window
    # sums it yields are, as out/drift.parquet, so the public package rebuilds these statistics without it.
    ar, dp = HERE / "out" / "ar_daily.parquet", HERE / "out" / "drift.parquet"
    if ar.exists():
        a = pd.read_parquet(ar)
        pre = a[a["day"].between(-30, -2)].groupby("event_id")["ar_ma"].agg(["sum", "count"])
        post = a[a["day"].between(2, 60)].groupby("event_id")["ar_ma"].agg(["sum", "count"])
        ma3 = a[a["day"].between(-1, 1)].groupby("event_id")["ar_ma"].agg(["sum", "count"])
        drift = pd.DataFrame(
            {
                "pre": pre["sum"].where(pre["count"] == 29),
                "post": post["sum"].where(post["count"] == 59),
                "car_ma_m1p1": ma3["sum"].where(ma3["count"] == 3),
            }
        ).reset_index()
        drift.to_parquet(dp, index=False)
    if dp.exists():
        drift = pd.read_parquet(dp)
        d = d.merge(drift[["event_id", "car_ma_m1p1"]], on="event_id", how="left")
        one_group("rob.forced.ma_m1p1", d[d["forced"] == 1]["car_ma_m1p1"])
        dd = d.merge(drift[["event_id", "pre", "post"]], on="event_id", how="left")
        ddc = d_c.merge(drift[["event_id", "pre", "post"]], on="event_id", how="left")
        dg = {
            "forced": dd[dd["forced"] == 1],
            "retired": dd[dd["forced"] == 0],
            "forced_founder": dd[(dd["forced"] == 1) & (dd["founder_v0"] == 1)],
            "conduct": dd[(dd["forced"] == 1) & (dd["conduct"] == 1)],
            "performance": dd[(dd["forced"] == 1) & (dd["conduct"] == 0)],
            "forced_nonfounder": dd[(dd["forced"] == 1) & (dd["founder_v0"] == 0)],
            "financial_misconduct": ddc[(ddc["forced"] == 1) & (ddc["primary_reason"] == "financial_misconduct")],
            "criminal": ddc[(ddc["forced"] == 1) & (ddc["criminal"] == 1)],
            "sex_or_relationship": dd[
                (dd["forced"] == 1)
                & dd["primary_reason"].isin(
                    ["relationship_with_employee", "relationship_other", "other_sexual_misconduct"]
                )
            ],
        }
        for g, x in dg.items():
            one_group(f"drift.{g}.pre_m30m2", x["pre"])
            one_group(f"drift.{g}.post_p2p60", x["post"])
        for w in ("pre", "post"):
            k = "pre_m30m2" if w == "pre" else "post_p2p60"
            two_group(f"driftdiff.forced_vs_retired.{k}", dg["forced"][w], dg["retired"][w])
            two_group(f"driftdiff.conduct_vs_performance.{k}", dg["conduct"][w], dg["performance"][w])
            two_group(
                f"driftdiff.forced_founder_vs_forced_nonfounder.{k}",
                dg["forced_founder"][w],
                dg["forced_nonfounder"][w],
            )

    # Delisting-return assumptions: 36-month BHAR with every delisting return set to 0, and with every delisting
    # that is not a takeover set to -100% (event_study.py writes both).
    for alt in ("dl0", "dlworst"):
        if f"bhar_3y_{alt}" in d:
            one_group(f"rob.bhar_{alt}.forced.3y", groups_lr["forced"][f"bhar_3y_{alt}"])
            one_group(f"rob.bhar_{alt}.retired.3y", groups_lr["retired"][f"bhar_3y_{alt}"])
    (OUT / "returns_stats.json").write_text(json.dumps(R, indent=1))
    show = [
        "a.n_forced",
        "a.n_retired",
        "a.n_forced_founder",
        "a.n_conduct",
        "a.n_relationship",
        "car.forced.mm_m1p1.mean",
        "car.retired.mm_m1p1.mean",
        "car.forced_founder.mm_m1p1.mean",
        "car.forced_nonfounder.mm_m1p1.mean",
        "car.conduct.mm_m1p1.mean",
        "car.performance.mm_m1p1.mean",
        "car.relationship.mm_m1p1.mean",
        "cardiff.forced_vs_retired.mm_m1p1.diff_mean",
        "cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean",
        "cardiff.conduct_vs_performance.mm_m1p1.diff_mean",
        "reg.car_m1p1.forced_x_founder_v0",
        "bhar.forced.3y.median",
        "bhar.retired.3y.median",
        "bhar.forced_founder.3y.median",
        "bhar.forced_nonfounder.3y.median",
        "bhar.forced.5y.skewadj_t",
        "bhardiff.forced_founder_vs_forced_nonfounder.3y.diff_median",
        "exit.forced.delisted_5y",
        "exit.retired.delisted_5y",
        "exit.forced.acquired_5y",
        "exit.forced.bankruptcy_5y",
        "exit.forced_founder.delisted_5y",
        "exitdiff.forced_vs_retired.delisted_5y",
    ]
    for k in show:
        v = R.get(k, {})
        print(f"{k:58s} {v.get('value')!s:>22} n={v.get('n')} t={v.get('t')} p={v.get('p')}")


if __name__ == "__main__":
    main()
