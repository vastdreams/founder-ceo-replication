"""Statistics for matched-firm long-run returns and operating performance (sections E and H).

Input : analysis/out/ops_matched.parquet (ops_matched.py), analysis/out/event_coding_final.jsonl
Output: outputs/ops_stats.json
Operating ROA changes are winsorized at the 1st and 99th percentiles of the pooled sample before testing
(Barber and Lyon 1996 recommend median tests; both are reported). Matched BHARs are tested with the
skewness-adjusted t and a bootstrap CI of the mean, plus the Wilcoxon signed-rank test of the median.
"""

import json
import pathlib

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from stats_returns import R, one_group, put, skew_adj, two_group  # shared helpers and result dict

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "outputs"


def wins(s, lo=0.01, hi=0.99):
    a, b = s.quantile(lo), s.quantile(hi)
    return s.clip(a, b)


def main():
    R.clear()
    d = pd.read_parquet(HERE / "out" / "ops_matched.parquet")
    c = pd.DataFrame([json.loads(x) for x in open(HERE / "out" / "event_coding_final.jsonl")]).rename(
        columns={"forced": "forced_llm"}
    )
    d = d.merge(c[["event_id", "ceo_is_founder", "primary_reason"]], on="event_id", how="left")
    d["founder"] = (d["ceo_is_founder"] == "yes").astype(int)
    ff = HERE / "out" / "founder_final.parquet"
    if ff.exists():  # hand-reviewed founder flag
        d = d.drop(columns=["founder"]).merge(pd.read_parquet(ff)[["event_id", "founder"]], on="event_id", how="left")
        d["founder"] = d["founder"].fillna(0).astype(int)
    for k in (0, 1, 2, 3):
        if f"abn_d_roa_{k}" in d:
            d[f"abn_d_roa_{k}_w"] = wins(d[f"abn_d_roa_{k}"])
    f, r = d[d["forced"] == 1], d[d["forced"] == 0]
    groups = {
        "forced": f,
        "retired": r,
        "forced_founder": f[f["founder"] == 1],
        "forced_nonfounder": f[f["founder"] == 0],
        "conduct": f[f["conduct"] == 1],
        "performance": f[f["conduct"] == 0],
    }
    put("h.matched_events", len(d))
    put("h.relaxed_matches", int(d["match_relaxed"].sum()))
    for g, x in groups.items():
        put(f"h.n_{g}", len(x))
        for k in (1, 2, 3):
            one_group(f"roa.{g}.abn_d_{k}", x[f"abn_d_roa_{k}_w"])
        for h in (1, 3, 5):
            one_group(f"mbhar.{g}.{h}y", x[f"mbhar_{h}y"])
            skew_adj(f"mbhar.{g}.{h}y", x[f"mbhar_{h}y"])
    for a, b in [("forced", "retired"), ("forced_founder", "forced_nonfounder"), ("conduct", "performance")]:
        for k in (1, 3):
            two_group(f"roadiff.{a}_vs_{b}.abn_d_{k}", groups[a][f"abn_d_roa_{k}_w"], groups[b][f"abn_d_roa_{k}_w"])
        for h in (1, 3, 5):
            two_group(f"mbhardiff.{a}_vs_{b}.{h}y", groups[a][f"mbhar_{h}y"], groups[b][f"mbhar_{h}y"])
    strict = f[f["match_relaxed"] == 0]
    one_group("rob.mbhar_strict_matches.3y", strict["mbhar_3y"])
    two_group("rob.mbhar_strict.forced_vs_retired.3y", strict["mbhar_3y"], r[r["match_relaxed"] == 0]["mbhar_3y"])
    ff = f.dropna(subset=["mbhar_3y"]).copy()
    ff["mbhar_3y"] = wins(ff["mbhar_3y"])  # winsorized for the regression; extreme returns drive the raw mean
    if "log_mcap_m1" in ff:  # public replication files carry log size, not the vendor's market value
        ff["log_mcap"] = ff["log_mcap_m1"]
    else:
        ff["log_mcap"] = np.log(ff["mcap_m1"].clip(lower=1))
    ff["year"] = pd.to_datetime(ff["event_date"]).dt.year
    m = smf.ols("mbhar_3y ~ founder + conduct + log_mcap + C(year)", data=ff).fit(
        cov_type="cluster", cov_kwds={"groups": ff["year"]}
    )
    for k in ("founder", "conduct", "log_mcap"):
        put(f"reg.mbhar_3y.{k}", m.params[k], se=m.bse[k], t=m.tvalues[k], p=m.pvalues[k], n=int(m.nobs))
    (OUT / "ops_stats.json").write_text(json.dumps(R, indent=1))
    for k in [
        "h.matched_events",
        "roa.forced.abn_d_1.median",
        "roa.retired.abn_d_1.median",
        "roa.forced_founder.abn_d_3.median",
        "roa.forced_nonfounder.abn_d_3.median",
        "roadiff.forced_vs_retired.abn_d_3.diff_median",
        "mbhar.forced.3y.median",
        "mbhar.retired.3y.median",
        "mbhar.forced_founder.3y.median",
        "mbhar.forced_founder.5y.median",
        "mbhardiff.forced_founder_vs_forced_nonfounder.3y.diff_median",
        "mbhardiff.forced_vs_retired.3y.diff_median",
        "reg.mbhar_3y.founder",
        "reg.mbhar_3y.conduct",
    ]:
        v = R.get(k, {})
        print(f"{k:58s} {v.get('value')!s:>22} n={v.get('n')} t={v.get('t')} p={v.get('p')}")


if __name__ == "__main__":
    main()
