"""Founders and hired CEOs, by why the board acted (paper/DECISIONS.md D-29; operator, 23 Nov 2026).

Every firing is placed in one cell: who was fired (founder, hired CEO) by why the board acted. No event is recoded:
the reason is the final code (sample.final_reasons, after the three hand reviews) and the founder flag is the
hand-checked one (founder_final.py).

  fraud    sample.CRIMINAL: financial misconduct, a legal or regulatory breach, criminal charges (comparison group;
           outside the paper's main sample, D-18)
  scandal  sample.PERSONAL: sexual misconduct, a relationship, other personal conduct
  coup     the code "strategy or power dispute"
  event    scandal or coup
  other    every remaining firing (performance, activists, restructuring, pushed retirements, unclear ...)
  main     every firing but fraud: the paper's main sample
  all      every firing, fraud included

Per cell: N (all firings with share prices; well-dated), the market-model abnormal return over trading days -1 to +1
and the return minus the market over days -30 to -2 (both on well-dated firings), and the shares delisted and
bankrupt within 60 months (firings followed for the full 60 months). Tests: Welch t for the returns; for the shares
the chi-square test the paper uses, or Fisher's exact test when an expected count is under 5, with the Newcombe
(Wilson score) interval. A cell under MIN_CELL events on a measure gets N only; a difference needs MIN_CELL in both
cells.

Inputs : analysis/out/{returns,drift,founder_final}.parquet, out/event_coding_final.jsonl, paper/*_review.csv
Output : outputs/founder_reason_stats.json (flat dict of named statistics, as stats_returns.py), read by
         combine_results.py
"""

import json
import pathlib

import numpy as np
import pandas as pd
import stats_returns as sr
from scipy import stats

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "outputs"
R = sr.R
R.clear()
put = sr.put
MIN_CELL = 10  # the paper's existing threshold for a reason group (min_reason_cases)
COUP = "strategy_or_power_dispute"
WHO = ("founder", "hired")
WHY = ("fraud", "event", "scandal", "coup", "other", "main", "all")
PARTITION = (
    "fraud",
    "event",
    "other",
)  # the three groups that partition every firing: the Holm family
RETURNS = (("mm_m1p1", "car_mm_m1p1"), ("pre_m30m2", "pre"))
SHARES = (("delisted_5y", "gone"), ("bankruptcy_5y", "bankrupt"))


def load():
    """Every firing with share prices, fraud firings kept, with its cell labels and the four measures."""
    d = sr.load_labelled(include_criminal=True)
    f = d[d["forced"] == 1].copy()
    f = f.merge(
        pd.read_parquet(HERE / "out" / "drift.parquet")[["event_id", "pre"]],
        on="event_id",
        how="left",
    )
    f["who"] = np.where(f["founder_v0"] == 1, "founder", "hired")
    f["why"] = np.select(
        [f["criminal"] == 1, f["conduct"] == 1, f["reason"] == COUP],
        ["fraud", "scandal", "coup"],
        default="other",
    )
    # returns on well-dated firings only (D-17); survival on every firing followed for the full 60 months
    for col in ("car_mm_m1p1", "pre"):
        f[col] = f[col].where(f["dated"] == 1)
    followed = f["bhar_5y"].notna()
    f["gone"] = f["delisted_5y"].astype(float).where(followed)
    f["bankrupt"] = (f["delist_kind_5y"] == "bankruptcy").astype(float).where(followed)
    return f


def cell(f, who, why):
    x = f[f["who"] == who]
    if why == "event":
        return x[x["why"].isin(["scandal", "coup"])]
    if why == "main":
        return x[x["why"] != "fraud"]
    if why == "all":
        return x
    return x[x["why"] == why]


def welch(prefix, a, b):
    """a minus b with the Welch t, its p and 95% interval; nothing unless both groups reach MIN_CELL."""
    a, b = a.dropna().astype(float), b.dropna().astype(float)
    put(prefix + ".n_a", len(a))
    put(prefix + ".n_b", len(b))
    if len(a) < MIN_CELL or len(b) < MIN_CELL:
        return None
    va, vb = a.var(ddof=1) / len(a), b.var(ddof=1) / len(b)
    se = float(np.sqrt(va + vb))
    df = (va + vb) ** 2 / (va**2 / (len(a) - 1) + vb**2 / (len(b) - 1))
    diff = a.mean() - b.mean()
    q = stats.t.ppf(0.975, df)
    n = len(a) + len(b)
    put(
        prefix + ".diff",
        diff,
        n=n,
        se=se,
        t=diff / se,
        p=2 * (1 - stats.t.cdf(abs(diff) / se, df)),
    )
    put(prefix + ".diff.ci_low", diff - q * se, n=n)
    put(prefix + ".diff.ci_high", diff + q * se, n=n)
    return diff, se


def wilson(k, n, z=1.959964):
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return c - h, c + h


def shares(prefix, a, b):
    """Share in a minus share in b: chi-square (Fisher's exact test when an expected count is under 5) and the
    Newcombe 95% interval; nothing unless both groups reach MIN_CELL."""
    a, b = a.dropna(), b.dropna()
    put(prefix + ".n_a", len(a))
    put(prefix + ".n_b", len(b))
    if len(a) < MIN_CELL or len(b) < MIN_CELL:
        return
    ka, kb, na, nb = int(a.sum()), int(b.sum()), len(a), len(b)
    tab = np.array([[ka, na - ka], [kb, nb - kb]])
    pa, pb = ka / na, kb / nb
    if tab.sum(axis=0).min() == 0:  # no firm (or every firm) in both cells: nothing to test
        p, test = 1.0, "none"
    else:
        expected = stats.contingency.expected_freq(tab)
        if expected.min() < 5:
            p, test = stats.fisher_exact(tab)[1], "fisher"
        else:
            p, test = stats.chi2_contingency(tab).pvalue, "chi2"
    (la, ua), (lb, ub) = wilson(ka, na), wilson(kb, nb)
    diff = pa - pb
    n = na + nb
    put(prefix + ".diff", diff, n=n, p=p, test=test)
    put(prefix + ".diff.ci_low", diff - np.sqrt((pa - la) ** 2 + (ub - pb) ** 2), n=n)
    put(prefix + ".diff.ci_high", diff + np.sqrt((ua - pa) ** 2 + (pb - lb) ** 2), n=n)


def holm(keys):
    """Holm-adjusted p across the tests in `keys` that were run."""
    ps = sorted((R[k]["p"], k) for k in keys if k in R and R[k].get("p") is not None)
    running = 0.0
    for i, (p, k) in enumerate(ps):
        running = max(running, min(1.0, (len(ps) - i) * p))
        put(k.replace(".diff", ".holm_p"), running, n=R[k]["n"], p=running)


def main():
    f = load()
    cases = {}
    for who in WHO:
        for why in WHY:
            x = cell(f, who, why)
            k = f"fr.{who}_{why}"
            put(k + ".n_all", len(x))
            put(k + ".n_dated", int((x["dated"] == 1).sum()))
            put(k + ".n5", int(x["gone"].notna().sum()))
            for name, col in RETURNS:
                y = x[col].dropna().astype(float)
                put(f"{k}.{name}.count", len(y))
                if len(y) >= MIN_CELL:
                    t = stats.ttest_1samp(y, 0.0)
                    put(
                        f"{k}.{name}.mean",
                        y.mean(),
                        n=len(y),
                        t=t.statistic,
                        p=t.pvalue,
                    )
                    put(
                        f"{k}.{name}.median",
                        y.median(),
                        n=len(y),
                        p=stats.wilcoxon(y).pvalue,
                    )
            for name, col in SHARES:
                y = x[col].dropna()
                if len(y) >= MIN_CELL:
                    put(f"{k}.{name}", y.mean(), n=len(y))
                if len(y):  # the count is printed even for a small cell; a share is not
                    put(f"{k}.{name}.count", int(y.sum()), n=len(y))
            # the cases behind a cell too small for a mean or a share: named in the text, never averaged
            if why in ("fraud", "scandal", "coup") and (
                x["car_mm_m1p1"].notna().sum() < MIN_CELL or x["gone"].notna().sum() < MIN_CELL
            ):
                cases[f"{who}_{why}"] = [
                    {
                        "event_id": int(r.event_id),
                        "company": r.coname,
                        "ceo": r.exec_fullname,
                        "year": int(r.year),
                        "reason": r.reason,
                        "well_dated": int(r.dated),
                        "car_m1p1": None if pd.isna(r.car_mm_m1p1) else float(r.car_mm_m1p1),
                        "pre_m30m2": None if pd.isna(r.pre) else float(r.pre),
                        "followed_60m": int(not pd.isna(r.gone)),
                        "after_60m": None if pd.isna(r.gone) else (r.delist_kind_5y if r.gone == 1 else "listed"),
                    }
                    for r in x.itertuples()
                ]
                for r in x.itertuples():
                    if not pd.isna(r.car_mm_m1p1):
                        put(
                            f"frcase.{int(r.event_id)}.car_m1p1",
                            float(r.car_mm_m1p1),
                            n=1,
                        )
                    if not pd.isna(r.pre):
                        put(f"frcase.{int(r.event_id)}.pre_m30m2", float(r.pre), n=1)

    # founder minus hired CEO within each reason
    for why in WHY:
        a, b = cell(f, "founder", why), cell(f, "hired", why)
        for name, col in RETURNS:
            welch(f"frdiff.{why}.founder_vs_hired.{name}", a[col], b[col])
        for name, col in SHARES:
            shares(f"frdiff.{why}.founder_vs_hired.{name}", a[col], b[col])
    for name in ("mm_m1p1", "pre_m30m2", "delisted_5y", "bankruptcy_5y"):
        holm([f"frdiff.{why}.founder_vs_hired.{name}.diff" for why in PARTITION])

    # fraud minus event within founders and within hired CEOs, and the difference between the two differences
    for name, col in RETURNS:
        got = {}
        for who in WHO:
            got[who] = welch(
                f"frdiff.{who}.fraud_vs_event.{name}",
                cell(f, who, "fraud")[col],
                cell(f, who, "event")[col],
            )
        if got["founder"] and got["hired"]:
            dd = got["founder"][0] - got["hired"][0]
            se = float(np.sqrt(got["founder"][1] ** 2 + got["hired"][1] ** 2))
            n = sum(int(cell(f, who, why)[col].notna().sum()) for who in WHO for why in ("fraud", "event"))
            put(
                f"frdiff.interaction.fraud_vs_event.{name}.diff",
                dd,
                n=n,
                se=se,
                t=dd / se,
                p=2 * (1 - stats.norm.cdf(abs(dd) / se)),
            )
            put(
                f"frdiff.interaction.fraud_vs_event.{name}.diff.ci_low",
                dd - 1.959964 * se,
                n=n,
            )
            put(
                f"frdiff.interaction.fraud_vs_event.{name}.diff.ci_high",
                dd + 1.959964 * se,
                n=n,
            )
    for name, col in SHARES:
        for who in WHO:
            shares(
                f"frdiff.{who}.fraud_vs_event.{name}",
                cell(f, who, "fraud")[col],
                cell(f, who, "event")[col],
            )
    # the same within the reasons: scandal against coup among founders, where both reach MIN_CELL
    for who in WHO:
        for name, col in RETURNS:
            welch(
                f"frdiff.{who}.scandal_vs_coup.{name}",
                cell(f, who, "scandal")[col],
                cell(f, who, "coup")[col],
            )

    # The mix of reasons: what share of founder firings, and of hired CEOs' firings, falls in each group, on every
    # firing with share prices. Added after the cell counts were seen (D-29, addendum), so it is labelled as such.
    for why in PARTITION + ("scandal", "coup", "main"):
        sel = {"event": ["scandal", "coup"], "main": ["scandal", "coup", "other"]}.get(why, [why])
        ind = {who: cell(f, who, "all")["why"].isin(sel).astype(float) for who in WHO}
        for who in WHO:
            put(f"frmix.{who}_{why}.share", ind[who].mean(), n=len(ind[who]))
        if why in PARTITION:
            shares(f"frmix.{why}.founder_vs_hired.share", ind["founder"], ind["hired"])
    tab = np.array([[len(cell(f, who, why)) for why in PARTITION] for who in WHO])
    chi = stats.chi2_contingency(tab)
    put("frmix.partition.chi2", chi.statistic, n=int(tab.sum()), p=chi.pvalue)

    R["_cases"] = cases
    (OUT / "founder_reason_stats.json").write_text(json.dumps(R, indent=1))
    for who in WHO:
        for why in WHY:
            k = f"fr.{who}_{why}"
            g = lambda s: R.get(s, {}).get("value")  # noqa: E731
            print(
                f"{who:8s}{why:8s} N={g(k + '.n_all'):5.0f} dated={g(k + '.n_dated'):4.0f} "
                f"car={g(k + '.mm_m1p1.mean')} (n={g(k + '.mm_m1p1.count')}) pre={g(k + '.pre_m30m2.mean')} "
                f"gone={g(k + '.delisted_5y')} bk={g(k + '.bankruptcy_5y')} n5={g(k + '.n5')}"
            )
    for k, r in R.items():
        if k.startswith("frdiff.") and k.endswith(".diff"):
            print(f"{k:58s} {r['value']:+.4f} p={r.get('p'):.4f} n={r['n']} {r.get('test', '')}")


if __name__ == "__main__":
    main()
