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
import statsmodels.formula.api as smf
from scipy import stats

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "outputs"
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(20261119)
R = {}


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


def main():
    d = pd.read_parquet(HERE / "out" / "returns.parquet")
    coding = HERE / "out" / "event_coding_v1.jsonl"
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
        d["relationship_v0"] = (d["primary_reason"] == "relationship_with_employee").astype(int)
        d["pushed_retirement"] = ((d["code"] == 5) & (d["forced_llm"] == "yes")).astype(int)
    d["year"] = pd.to_datetime(d["event_date"]).dt.year
    f, r = d[d["forced"] == 1], d[d["forced"] == 0]
    groups = {
        "forced": f,
        "retired": r,
        "forced_founder": f[f["founder_v0"] == 1],
        "forced_nonfounder": f[f["founder_v0"] == 0],
        "conduct": f[f["conduct"] == 1],
        "performance": f[f["conduct"] == 0],
        "relationship": f[f["relationship_v0"] == 1],
        "retired_founder": r[r["founder_v0"] == 1],
    }

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
        for w in ("m1p1", "0p1", "m5p5", "m30p30"):
            one_group(f"car.{g}.mm_{w}", x[f"car_mm_{w}"])
            one_group(f"car.{g}.ff5_{w}", x[f"car_ff5_{w}"])
        bmp(f"car.{g}.mm_m1p1", x["scar_mm_m1p1"])
    for a, b in [
        ("forced", "retired"),
        ("forced_founder", "forced_nonfounder"),
        ("conduct", "performance"),
        ("forced_founder", "retired_founder"),
    ]:
        for w in ("m1p1", "m5p5"):
            two_group(f"cardiff.{a}_vs_{b}.mm_{w}", groups[a][f"car_mm_{w}"], groups[b][f"car_mm_{w}"])

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

    # E: long-run
    for g, x in groups.items():
        for h in (1, 3, 5):
            one_group(f"bhar.{g}.{h}y", x[f"bhar_{h}y"])
            skew_adj(f"bhar.{g}.{h}y", x[f"bhar_{h}y"])
    for a, b in [("forced", "retired"), ("forced_founder", "forced_nonfounder"), ("conduct", "performance")]:
        for h in (1, 3, 5):
            two_group(f"bhardiff.{a}_vs_{b}.{h}y", groups[a][f"bhar_{h}y"], groups[b][f"bhar_{h}y"])

    # F: what happened to the firm within five years
    for g, x in groups.items():
        x5 = x.dropna(subset=["bhar_5y"])
        put(f"exit.{g}.n5", len(x5))
        put(f"exit.{g}.delisted_5y", x5["delisted_5y"].mean() if len(x5) else None, n=len(x5))
        for k in ("acquired", "bankruptcy", "delisted_other", "unknown"):
            put(f"exit.{g}.{k}_5y", (x5["delist_kind_5y"] == k).mean() if len(x5) else None, n=len(x5))
    for a, b in [("forced", "retired"), ("forced_founder", "forced_nonfounder")]:
        xa, xb = groups[a].dropna(subset=["bhar_5y"]), groups[b].dropna(subset=["bhar_5y"])
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
