"""Assemble outputs/combined_results.json (LetteredReportPayload, backend/schemas/lettered_report.py).

Every statistic is read from a results file written by code and carries source_file and source_key. Each one also
carries its horizon (``period``: how long after, or around, the announcement it is measured), the population it is
measured on, and N. The build stops if any statistic lacks N or a horizon, or any table lacks an N column: a reader
must always see how many forced exits a number rests on and over what horizon.

Sections follow the founder_ceo_jfe rule set: A sample and B coding -> Section 2; C announcement -> 3; D long-run
returns and E operating performance -> 4; F survival -> 5; G board -> 6; H robustness -> Internet Appendix.
"""

import datetime
import hashlib
import json
import pathlib
import re

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "outputs"
FILES = (
    "returns_stats.json",
    "ops_stats.json",
    "board_stats.json",
    "coding_stats.json",
    "pre1998_stats.json",
    "describe_stats.json",
)
SRC = {k: (json.loads((OUT / k).read_text()) if (OUT / k).exists() else {}) for k in FILES}
RS, OS, BS, CS, PS, DS = FILES
TITLE = "Sacked: Sex, Fraud, Founders, and the Fate of Firms That Fire Their CEO"
REPO_URL = "https://github.com/vastdreams/founder-ceo-replication"

GROUP_NAMES = {
    "forced": "Forced exits",
    "retired": "Voluntary retirements",
    "forced_founder": "Founder fired",
    "forced_nonfounder": "Hired CEO fired",
    "conduct": "Fired for conduct",
    "performance": "Fired for performance",
    "relationship": "Relationship with an employee",
    "sex_or_relationship": "Sex or relationship scandal",
    "financial_misconduct": "Financial misconduct",
    "forced_strict": "Forced, evidence agrees",
    "forced_strict_founder": "Founder fired, evidence agrees",
    "forced_strict_nonfounder": "Hired CEO fired, evidence agrees",
}
POP = {
    "forced": "Forced CEO exits (database codes 3 and 4)",
    "retired": "Voluntary CEO retirements (database code 5)",
    "forced_founder": "Forced exits of founder-CEOs (hand-checked)",
    "forced_nonfounder": "Forced exits of CEOs who did not found the firm",
    "conduct": "Forced exits for legal violations or personal conduct (code 4)",
    "performance": "Forced exits for job performance (code 3)",
    "relationship": "Forced exits after a relationship with an employee (hand-checked)",
    "sex_or_relationship": "Forced exits after sexual misconduct or a relationship with an employee (hand-checked)",
    "financial_misconduct": "Forced exits coded as financial misconduct",
    "forced_strict": "Forced exits the evidence-based coding also reads as forced",
}
BASE_POP = "S&P 1500 firms, announcements 1998-2023"


def horizon(key: str) -> str:
    """Pure: how long after (or around) the announcement the statistic is measured, read from its key."""
    k = key
    if k.startswith(("a.", "b.", "rob.n_")) or k.startswith("g.events"):
        return "Sample definition: CEO departures announced 1998 to 2023"
    if k.startswith(("desc.", "descdiff.")):
        return "Before the departure: fiscal year -1, market value one month before the announcement"
    if k.startswith("pre."):
        return "Three fiscal years from the event year, departures announced 1992 to 1997"
    if k.startswith(("board.", "boarddiff.")):
        return "About two years: the last proxy before the departure against the first proxy filed 600 or more days after it"
    if "pre_m30m2" in k:
        return "Trading days -30 to -2 before the announcement (day 0)"
    if "post_p2p60" in k:
        return "Trading days +2 to +60 after the announcement (day 0), about three months"
    if "m5p5" in k:
        return "Trading days -5 to +5 around the announcement (day 0)"
    if "m1p1" in k or ".car_m1p1" in k or k.startswith("reg.car"):
        return "Trading days -1 to +1 around the announcement (day 0)"
    m = re.search(r"abn_d_(\d)", k)
    if m:
        return f"Fiscal year +{m.group(1)} against fiscal year -1, relative to the matched firm"
    m = re.search(r"(?:\.|_)(\d)y\b|_(\d)y$|\.n(\d)$|bhar_(\d)y", k)
    if m:
        h = int(next(g for g in m.groups() if g))
        return f"{12 * h} months ({252 * h:,} trading days) from day +2 after the announcement"
    if k.startswith("reg.mbhar"):
        return "36 months (756 trading days) from day +2 after the announcement"
    if k.startswith(("h.", "case.n")):
        return "Sample definition: CEO departures announced 1998 to 2023"
    if k.startswith("case.") and k.endswith("mcap_bn"):
        return "One month before the announcement"
    raise ValueError(f"no horizon for {key}")


def population(key: str) -> str:
    parts = key.split(".")
    g = parts[1] if len(parts) > 1 else ""
    if "_vs_" in g:
        a, b = g.split("_vs_")
        return f"{POP.get(a, GROUP_NAMES.get(a, a))} against {POP.get(b, GROUP_NAMES.get(b, b)).lower()}; {BASE_POP}"
    if g == "reason" and len(parts) > 2:
        return f"Forced exits whose coded primary reason is '{parts[2].replace('_', ' ')}'; {BASE_POP}"
    return f"{POP.get(g, 'CEO departures')}; {BASE_POP}"


def fmt(v, unit):
    if v is None:
        return "n/a"
    if unit == "pct":
        return f"{v * 100:.1f}%"
    if unit == "pp":
        return f"{v * 100:.1f} percentage points"
    if unit == "pps":
        return "0.0" if abs(v) < 0.0005 else f"{v * 100:.1f}"
    if unit == "count":
        return f"{int(round(v)):,}"
    if unit == "bn":
        return f"{v:.1f}"
    if unit == "coef":
        return f"{v:.3f}"
    return f"{v:.2f}"


def stat(file, key, label, unit, test="", group=""):
    r = SRC[file].get(key)
    if r is None:
        return None
    s = {
        "stat_id": key.replace("_v0", ""),
        "label": label,
        "value": r.get("value"),
        "formatted": fmt(r.get("value"), unit),
        "unit": {"pct": "share", "pp": "difference", "count": "count", "coef": "coefficient", "bn": "USD billion"}.get(
            unit, ""
        ),
        "test": test,
        "source_file": f"outputs/{file}",
        "source_key": key,
        "group": group,
        "population": population(key),
        "period": horizon(key),
    }
    for f in ("n", "t", "p", "se", "ci_low", "ci_high"):
        if r.get(f) is not None:
            s[f] = int(r[f]) if f == "n" else float(r[f])
    if "n" not in s and unit == "count" and r.get("value") is not None:
        s["n"] = int(round(r["value"]))  # a count is its own N
    return s


def v(file, key, unit):
    r = SRC[file].get(key)
    return fmt(None if r is None else r.get("value"), unit)


def pv(file, key):
    p = (SRC[file].get(key) or {}).get("p")
    return "n/a" if p is None else ("<0.001" if p < 0.001 else f"{p:.3f}")


def tv(file, key):
    t = (SRC[file].get(key) or {}).get("t")
    return "n/a" if t is None else f"{t:.2f}"


def nv(file, key):
    n = (SRC[file].get(key) or {}).get("n")
    return "n/a" if n is None else f"{int(n):,}"


def section(sid, title, question, interpretation, method, stats, tables=()):
    stats = [s for s in stats if s]
    return {
        "section_id": sid,
        "title": title,
        "question": question,
        "interpretation": interpretation,
        "methodology": method,
        "statistics": stats,
        "tables": list(tables),
        "warnings": [],
        "source_files": sorted({s["source_file"] for s in stats}),
    }


def table(title, columns, rows, stat_ids, notes):
    return {"title": title, "columns": columns, "rows": rows, "stat_ids": stat_ids, "notes": notes}


def many(file, items, group=""):
    return [stat(file, k, lbl, u, tst, group) for k, lbl, u, tst in items]


# ---------------------------------------------------------------------------------------------------------------
def sec_a():
    groups = ("forced", "retired", "forced_founder")
    rows, ids = [], []
    for var, name, unit in (
        ("mcap", "Market value, USD billion", "bn"),
        ("roa", "Return on assets (EBITDA / assets)", "pct"),
        ("salesg", "Sales growth", "pct"),
        ("capex", "Capital spending / assets", "pct"),
    ):
        row = [name]
        for g in groups:
            k = f"desc.{g}.{var}.median"
            val = (SRC[DS].get(k) or {}).get("value")
            row.append("n/a" if val is None else (f"{val / 1e9:.1f}" if unit == "bn" else fmt(val, "pct")))
            ids.append(k)
        row.append(pv(DS, f"descdiff.forced_vs_retired.{var}.diff_median"))
        row.append(nv(DS, f"desc.forced.{var}.median"))
        rows.append(row)
    stats = many(
        RS,
        [
            ("a.events_with_returns", "Departures with returns", "count", "count"),
            ("a.n_forced", "Forced exits", "count", "count"),
            ("a.n_retired", "Voluntary retirements", "count", "count"),
            ("a.n_forced_founder", "Founders fired", "count", "count"),
            ("a.n_forced_nonfounder", "Hired CEOs fired", "count", "count"),
            ("a.n_conduct", "Fired for conduct", "count", "count"),
            ("a.n_performance", "Fired for performance", "count", "count"),
            ("a.n_relationship", "Relationship with an employee", "count", "count"),
            ("a.n_sex_or_relationship", "Sex or relationship scandal", "count", "count"),
            ("a.n_financial_misconduct", "Financial misconduct", "count", "count"),
            ("a.n_forced_strict", "Forced exits the evidence also reads as forced", "count", "count"),
        ],
        "sample",
    ) + many(
        DS,
        [
            ("desc.forced.mcap.median", "Median market value, forced", "num", "median"),
            ("desc.retired.mcap.median", "Median market value, retired", "num", "median"),
            ("desc.forced.roa.median", "Median ROA year -1, forced", "pct", "median"),
            ("desc.retired.roa.median", "Median ROA year -1, retired", "pct", "median"),
            ("descdiff.forced_vs_retired.roa.diff_median", "Forced minus retired, median ROA", "pp", "Mann-Whitney U"),
            (
                "descdiff.forced_vs_retired.mcap.diff_median",
                "Forced minus retired, median market value",
                "num",
                "Mann-Whitney U",
            ),
            ("desc.forced.salesg.median", "Median sales growth year -1, forced", "pct", "median"),
            ("desc.retired.salesg.median", "Median sales growth year -1, retired", "pct", "median"),
        ],
        "sample",
    )
    for s in stats:
        if s and s["stat_id"].endswith("mcap.median") or s and s["stat_id"].endswith("mcap.diff_median"):
            s["value"] = s["value"] / 1e9
            s["formatted"] = fmt(s["value"], "bn")
            s["unit"] = "USD billion"
    return section(
        "A",
        "Sample",
        "Which CEO departures are studied, how many have usable stock returns, and what were the firms like before?",
        f"The sample holds {v(RS, 'a.events_with_returns', 'count')} departures with returns: {v(RS, 'a.n_forced', 'count')} forced exits and "
        f"{v(RS, 'a.n_retired', 'count')} voluntary retirements. Firms that fire their CEO are smaller and less profitable the year before: median ROA "
        f"{v(DS, 'desc.forced.roa.median', 'pct')} against {v(DS, 'desc.retired.roa.median', 'pct')} (p {pv(DS, 'descdiff.forced_vs_retired.roa.diff_median')}).",
        {
            "test": "counts; medians with Mann-Whitney U",
            "data": "Gentry et al. (2021) CEO dismissal database v10Oct2024 linked to daily prices and as-reported annual statements by SEC CIK",
            "library_call": "analysis/build_events.py; analysis/event_study.py; analysis/describe.py",
            "caveat": "Founder status and reasons are coded from filings, press releases and news, then checked by hand.",
        },
        stats,
        [
            table(
                "Table 2. Who gets fired: the firm in the year before the departure",
                [
                    "Fiscal year -1, medians",
                    "Forced exits",
                    "Retirements",
                    "Founders fired",
                    "p, forced vs retired",
                    "N forced",
                ],
                rows,
                ids,
                "Medians in the fiscal year before the departure, from as-reported annual statements; market value one month before the announcement. "
                "p is from a Mann-Whitney U test of forced exits against retirements. N forced is the number of forced exits with the item.",
            )
        ],
    )


def sec_b():
    return section(
        "B",
        "Founder and reason coding",
        "How reliable are the founder and reason codes?",
        f"The model coded {v(CS, 'b.model_founder_codes', 'count')} forced exits as founder removals. A hand review confirmed "
        f"{v(CS, 'b.founders_confirmed', 'count')}, rejected {v(CS, 'b.founders_rejected', 'count')} (an error rate of {v(CS, 'b.model_error_rate', 'pct')}) and added "
        f"{v(CS, 'b.founders_added', 'count')}. The reviewed codes are used throughout.",
        {
            "test": "hand review",
            "data": "paper/founder_review.csv; paper/conduct_review.csv",
            "library_call": "analysis/code_events.py; analysis/coding_final.py; analysis/founder_final.py",
            "caveat": "Founder means founded or co-founded the firm or its direct predecessor; heirs are excluded.",
        },
        many(
            CS,
            [
                ("b.model_founder_codes", "Forced exits coded founder by the model", "count", "count"),
                ("b.founders_reviewed", "Founder codes reviewed by hand", "count", "count"),
                ("b.founders_confirmed", "Founders confirmed", "count", "count"),
                ("b.founders_rejected", "Model founder codes rejected", "count", "count"),
                ("b.founders_added", "Founders added where the model was unclear", "count", "count"),
                ("b.model_error_rate", "Model error rate on founder codes", "pct", "share"),
            ],
            "coding",
        ),
    )


ANN_GROUPS = (
    "forced",
    "retired",
    "forced_founder",
    "forced_nonfounder",
    "conduct",
    "performance",
    "financial_misconduct",
    "sex_or_relationship",
)


def sec_c():
    rows, ids = [], []
    for g in ANN_GROUPS:
        k = f"car.{g}.mm_m1p1"
        rows.append(
            [
                GROUP_NAMES[g],
                v(RS, f"{k}.mean", "pct"),
                v(RS, f"{k}.median", "pct"),
                tv(RS, f"{k}.mean"),
                pv(RS, f"{k}.mean"),
                nv(RS, f"{k}.mean"),
            ]
        )
        ids += [f"{k}.mean", f"{k}.median"]
    drows, dids = [], []
    for g in ("forced", "retired", "forced_founder", "conduct", "performance"):
        pre, ann, post = f"drift.{g}.pre_m30m2.mean", f"car.{g}.mm_m1p1.mean", f"drift.{g}.post_p2p60.mean"
        drows.append(
            [
                GROUP_NAMES[g],
                v(RS, pre, "pct"),
                pv(RS, pre),
                v(RS, ann, "pct"),
                pv(RS, ann),
                v(RS, post, "pct"),
                pv(RS, post),
                nv(RS, ann),
            ]
        )
        dids += [pre, ann, post]
    reasons = sorted(
        {k.split(".")[2] for k in SRC[RS] if k.startswith("car.reason.") and k.endswith(".mm_m1p1.mean")},
        key=lambda r: SRC[RS][f"car.reason.{r}.mm_m1p1.mean"]["value"],
    )
    rrows = [
        [
            r.replace("_", " ")
            .capitalize()
            .replace("Retirement or health", "Pushed out, described as retirement or health"),
            v(RS, f"car.reason.{r}.mm_m1p1.mean", "pct"),
            tv(RS, f"car.reason.{r}.mm_m1p1.mean"),
            pv(RS, f"car.reason.{r}.mm_m1p1.mean"),
            nv(RS, f"car.reason.{r}.mm_m1p1.mean"),
        ]
        for r in reasons
    ]
    cases = SRC[DS].get("_cases", [])
    crows, cstats = [], []
    for c in cases:
        eid = c["event_id"]
        SRC[DS][f"case.{eid}.mcap_bn"] = {"value": c["mcap_m1"] / 1e9, "n": 1}
        crows.append(
            [
                c["company"],
                c["ceo"],
                str(c["year"]),
                c["dismissal"].capitalize(),
                v(DS, f"case.{eid}.mcap_bn", "bn"),
                v(DS, f"case.{eid}.car_m1p1", "pct"),
                v(DS, f"case.{eid}.bhar_3y", "pct"),
                c["fate_5y"],
            ]
        )
        cstats += many(
            DS,
            [
                (f"case.{eid}.car_m1p1", f"CAR[-1,+1], {c['company']} {c['year']}", "pct", "event return"),
                (f"case.{eid}.bhar_3y", f"3-year BHAR, {c['company']} {c['year']}", "pct", "event return"),
                (f"case.{eid}.mcap_bn", f"Market value, {c['company']} {c['year']}", "bn", "level"),
            ],
            "case",
        )
    stats = (
        [
            stat(RS, f"car.{g}.mm_m1p1.mean", f"Mean CAR[-1,+1], {GROUP_NAMES[g].lower()}", "pct", "one-sample t", g)
            for g in ANN_GROUPS
        ]
        + [
            stat(RS, f"car.{g}.mm_m1p1.median", f"Median CAR[-1,+1], {GROUP_NAMES[g].lower()}", "pct", "Wilcoxon", g)
            for g in ANN_GROUPS
        ]
        + many(
            RS,
            [
                ("car.forced.mm_m1p1.bmp_t", "BMP standardized t, forced exits", "coef", "BMP 1991"),
                ("car.forced.ff5_m1p1.mean", "Mean five-factor CAR[-1,+1], forced exits", "pct", "one-sample t"),
                ("car.forced.mm_m5p5.mean", "Mean CAR[-5,+5], forced exits", "pct", "one-sample t"),
                (
                    "cardiff.forced_vs_retired.mm_m1p1.diff_mean",
                    "Forced minus retired, mean CAR[-1,+1]",
                    "pp",
                    "Welch t",
                ),
                (
                    "cardiff.forced_vs_retired.mm_m1p1.diff_median",
                    "Forced minus retired, median CAR[-1,+1]",
                    "pp",
                    "Mann-Whitney U",
                ),
                (
                    "cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean",
                    "Founder minus hired CEO, CAR[-1,+1]",
                    "pp",
                    "Welch t",
                ),
                (
                    "reg.car_m1p1.forced_x_founder_v0",
                    "Regression: forced x founder",
                    "pp",
                    "OLS, year effects, clustered by year",
                ),
                (
                    "cardiff.conduct_vs_performance.mm_m1p1.diff_mean",
                    "Conduct minus performance, CAR[-1,+1]",
                    "pp",
                    "Welch t",
                ),
                (
                    "cardiff.sex_or_relationship_vs_financial_misconduct.mm_m1p1.diff_mean",
                    "Sex or relationship minus financial misconduct, CAR[-1,+1]",
                    "pp",
                    "Welch t",
                ),
                (
                    "cardiff.sex_or_relationship_vs_financial_misconduct.mm_m1p1.diff_median",
                    "Sex or relationship minus financial misconduct, median CAR[-1,+1]",
                    "pp",
                    "Mann-Whitney U",
                ),
                (
                    "car.relationship.mm_m1p1.mean",
                    "Mean CAR[-1,+1], relationship with an employee",
                    "pct",
                    "one-sample t",
                ),
                ("car.relationship.mm_m1p1.count", "Relationship cases with returns", "count", "count"),
            ],
        )
        + [
            stat(RS, k, lbl, "pct", "one-sample t", "drift")
            for k, lbl in [
                (
                    f"drift.{g}.{w}.mean",
                    f"Mean market-adjusted CAR, {'days -30 to -2' if w == 'pre_m30m2' else 'days +2 to +60'}, {GROUP_NAMES[g].lower()}",
                )
                for g in ("forced", "retired", "forced_founder", "conduct", "performance")
                for w in ("pre_m30m2", "post_p2p60")
            ]
        ]
        + many(
            RS,
            [
                (
                    "driftdiff.forced_vs_retired.pre_m30m2.diff_mean",
                    "Forced minus retired, days -30 to -2",
                    "pp",
                    "Welch t",
                ),
                (
                    "driftdiff.forced_vs_retired.post_p2p60.diff_mean",
                    "Forced minus retired, days +2 to +60",
                    "pp",
                    "Welch t",
                ),
                (
                    "driftdiff.conduct_vs_performance.pre_m30m2.diff_mean",
                    "Conduct minus performance, days -30 to -2",
                    "pp",
                    "Welch t",
                ),
            ],
            "drift",
        )
        + [
            stat(
                RS,
                f"car.reason.{r}.mm_m1p1.mean",
                f"Mean CAR[-1,+1], reason: {r.replace('_', ' ')}",
                "pct",
                "one-sample t",
                "reason",
            )
            for r in reasons
        ]
        + cstats
        + many(DS, [("case.n_listed", "Founder cases listed", "count", "count")], "case")
    )
    return section(
        "C",
        "Announcement returns",
        "How does the stock react when the board fires the CEO, and does it matter who and why?",
        f"Over trading days -1 to +1, forced exits earn {v(RS, 'car.forced.mm_m1p1.mean', 'pct')} (t = {tv(RS, 'car.forced.mm_m1p1.mean')}, N = {nv(RS, 'car.forced.mm_m1p1.mean')}) "
        f"and retirements {v(RS, 'car.retired.mm_m1p1.mean', 'pct')}. Fired founders earn {v(RS, 'car.forced_founder.mm_m1p1.mean', 'pct')} against "
        f"{v(RS, 'car.forced_nonfounder.mm_m1p1.mean', 'pct')} (gap p {pv(RS, 'cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean')}). "
        f"Financial misconduct costs {v(RS, 'car.financial_misconduct.mm_m1p1.mean', 'pct')}, sex or relationship scandals {v(RS, 'car.sex_or_relationship.mm_m1p1.mean', 'pct')} "
        f"(gap p {pv(RS, 'cardiff.sex_or_relationship_vs_financial_misconduct.mm_m1p1.diff_mean')}). Prices fall {v(RS, 'drift.forced.pre_m30m2.mean', 'pct')} over days -30 to -2 "
        f"and are flat over days +2 to +60 ({v(RS, 'drift.forced.post_p2p60.mean', 'pct')}).",
        {
            "test": "Cross-sectional t, Boehmer-Musumeci-Poulsen standardized t, Wilcoxon signed-rank; Welch t and Mann-Whitney U for differences",
            "data": "Daily total returns; market model estimated over trading days -250 to -30 for days -1 to +1; market-adjusted returns for longer windows",
            "library_call": "analysis/event_study.py; analysis/paths.py; analysis/stats_returns.py; analysis/describe.py",
            "caveat": "Day 0 is the first trading day on or after the announcement. Reasons other than the hand-checked conduct labels are model codes.",
        },
        stats,
        [
            table(
                "Table 4. The market's verdict: abnormal returns over trading days -1 to +1",
                ["Group", "Mean", "Median", "t", "p", "N"],
                rows,
                ids,
                "Cumulative market-model abnormal return from trading day -1 to day +1 around the announcement (day 0), with the model estimated over days -250 to -30 "
                "(at least 120 days). t is the cross-sectional t of the mean; p is two-sided. N is the number of departures with returns over the window. "
                "Forced exits are database codes 3 and 4; founder status, sexual-conduct and relationship labels are hand-checked; financial misconduct is a model code.",
            ),
            table(
                "Table 3. Before, at and after the announcement",
                ["Group", "Days -30 to -2", "p", "Days -1 to +1", "p", "Days +2 to +60", "p", "N"],
                drows,
                dids,
                "Days -30 to -2 and +2 to +60 are cumulative market-adjusted returns (firm minus market), used because a forced-exit firm's alpha before the event "
                "is strongly negative and a market model would project it forward. Days -1 to +1 is the market-model return of Table 4. Events need every day of "
                "a window. N is the number of departures in the days -1 to +1 window; the outer windows differ by at most a few percent.",
            ),
            table(
                "Table 5. Why the board acted: abnormal returns over trading days -1 to +1 by coded reason",
                ["Coded primary reason", "Mean", "t", "p", "N"],
                rrows,
                [f"car.reason.{r}.mm_m1p1.mean" for r in reasons],
                "Forced exits only, by the primary reason coded from the database notes, the 8-K filed within 10 days, cited press releases, Wikipedia and matched "
                "New York Times articles. Reasons with fewer than 10 cases are not shown. Sexual-conduct and relationship labels are hand-checked; the others are model codes.",
            ),
            table(
                "Table 6. The largest founders fired",
                [
                    "Company",
                    "Founder",
                    "Year",
                    "Database reason",
                    "Value, USD bn",
                    "Days -1 to +1",
                    "36 months",
                    "After 60 months",
                ],
                crows,
                [s["stat_id"] for s in cstats if s],
                "Founder-CEOs fired, among exits the evidence-based coding also reads as forced, ranked by market value one month before the announcement. "
                "Database reason is the CEO dismissal database's code (performance = 3, legal or conduct = 4). Days -1 to +1 is the market-model abnormal return; "
                "36 months is the buy-and-hold return minus the market from day +2; it can fall below -100% when the stock lost most of its value while the "
                "market rose. After 60 months reports whether the stock still traded, and if not, how it left.",
            ),
        ],
    )


LR_GROUPS = ("forced", "retired", "forced_founder", "forced_nonfounder", "conduct", "performance")


def sec_d():
    rows, ids = [], []
    for g in LR_GROUPS:
        row = [GROUP_NAMES[g]]
        for h in (1, 3, 5):
            row.append(v(RS, f"bhar.{g}.{h}y.median", "pct"))
        for h in (1, 3, 5):
            row.append(v(OS, f"mbhar.{g}.{h}y.median", "pct"))
            ids.append(f"mbhar.{g}.{h}y.median")
        row.append(nv(OS, f"mbhar.{g}.3y.median"))
        rows.append(row)
    stats = []
    for g in LR_GROUPS:
        for h in (1, 3, 5):
            stats.append(
                stat(
                    RS,
                    f"bhar.{g}.{h}y.median",
                    f"Median {12 * h}-month BHAR vs market, {GROUP_NAMES[g].lower()}",
                    "pct",
                    "Wilcoxon",
                    g,
                )
            )
            stats.append(
                stat(
                    OS,
                    f"mbhar.{g}.{h}y.median",
                    f"Median {12 * h}-month BHAR vs matched firm, {GROUP_NAMES[g].lower()}",
                    "pct",
                    "Wilcoxon",
                    g,
                )
            )
    stats += many(
        OS,
        [
            ("mbhar.forced.3y.skewadj_t", "Skewness-adjusted t, 36-month matched BHAR, forced", "coef", "LBT 1999"),
            (
                "mbhardiff.forced_vs_retired.3y.diff_median",
                "Forced minus retired, median 36-month matched BHAR",
                "pp",
                "Mann-Whitney U",
            ),
            (
                "mbhardiff.forced_founder_vs_forced_nonfounder.3y.diff_median",
                "Founder minus hired CEO, median 36-month matched BHAR",
                "pp",
                "Mann-Whitney U",
            ),
        ],
    ) + many(
        RS,
        [
            (
                "bhardiff.forced_founder_vs_forced_nonfounder.3y.diff_median",
                "Founder minus hired CEO, median 36-month BHAR vs market",
                "pp",
                "Mann-Whitney U",
            ),
            (
                "bhar.sex_or_relationship.3y.median",
                "Median 36-month BHAR vs market, sex or relationship",
                "pct",
                "Wilcoxon",
            ),
            (
                "bhar.financial_misconduct.3y.median",
                "Median 36-month BHAR vs market, financial misconduct",
                "pct",
                "Wilcoxon",
            ),
        ],
    )
    return section(
        "D",
        "Long-run returns",
        "Does the firm do better or worse in the 12, 36 and 60 months after the firing?",
        f"Against the market, the median forced-exit firm returns {v(RS, 'bhar.forced.1y.median', 'pct')} over 12 months, {v(RS, 'bhar.forced.3y.median', 'pct')} over 36 and "
        f"{v(RS, 'bhar.forced.5y.median', 'pct')} over 60. Against a matched firm the medians are {v(OS, 'mbhar.forced.1y.median', 'pct')}, {v(OS, 'mbhar.forced.3y.median', 'pct')} "
        f"and {v(OS, 'mbhar.forced.5y.median', 'pct')}.",
        {
            "test": "Wilcoxon signed-rank; skewness-adjusted t with bootstrap CI (Lyon, Barber and Tsai 1999)",
            "data": "Buy-and-hold returns from day +2, delisting returns per Shumway (1997), matched control per Barber and Lyon (1996)",
            "library_call": "analysis/event_study.py; analysis/ops_matched.py; analysis/stats_ops.py",
            "caveat": "Market-adjusted BHARs are skewed and negative for the typical stock; matched-firm BHARs are the main test.",
        },
        stats,
        [
            table(
                "Table 7. Long-run returns at 12, 36 and 60 months",
                [
                    "Group",
                    "Market, 12m",
                    "Market, 36m",
                    "Market, 60m",
                    "Matched, 12m",
                    "Matched, 36m",
                    "Matched, 60m",
                    "N, 36m",
                ],
                rows,
                ids,
                "Medians of buy-and-hold returns from trading day +2 after the announcement, over 12, 36 and 60 months (252, 756 and 1,260 trading days). Market "
                "subtracts the buy-and-hold market return; Matched subtracts a control firm in the same Fama-French industry with market value within 30 percent "
                "and the closest ROA, with no CEO turnover within three years. A delisted firm keeps its final return, with Shumway delisting returns. N, 36m "
                "is the number of matched events at 36 months; Figure 4 reports N at each horizon.",
            )
        ],
    )


def sec_e():
    rows, ids = [], []
    for g in LR_GROUPS:
        row = [GROUP_NAMES[g]]
        for y in (1, 2, 3):
            row.append(v(OS, f"roa.{g}.abn_d_{y}.median", "pps"))
            ids.append(f"roa.{g}.abn_d_{y}.median")
        row += [nv(OS, f"roa.{g}.abn_d_1.median"), nv(OS, f"roa.{g}.abn_d_3.median")]
        rows.append(row)
    stats = []
    for g in LR_GROUPS:
        for y in (1, 2, 3):
            stats.append(
                stat(
                    OS,
                    f"roa.{g}.abn_d_{y}.median",
                    f"Median abnormal change in ROA, year {y}, {GROUP_NAMES[g].lower()}",
                    "pps",
                    "Wilcoxon",
                    g,
                )
            )
    stats += many(
        OS,
        [
            (
                "roadiff.forced_vs_retired.abn_d_1.diff_median",
                "Forced minus retired, ROA change year 1",
                "pp",
                "Mann-Whitney U",
            ),
            (
                "roadiff.forced_vs_retired.abn_d_3.diff_median",
                "Forced minus retired, ROA change year 3",
                "pp",
                "Mann-Whitney U",
            ),
            ("h.matched_events", "Events with a matched control", "count", "count"),
        ],
    )
    return section(
        "E",
        "Operating performance",
        "Does profitability recover after the firing?",
        f"Against its matched firm, the median forced-exit firm's ROA changes by {v(OS, 'roa.forced.abn_d_1.median', 'pps')} percentage points in fiscal year +1 "
        f"(p {pv(OS, 'roa.forced.abn_d_1.median')}) and {v(OS, 'roa.forced.abn_d_3.median', 'pps')} in year +3 (p {pv(OS, 'roa.forced.abn_d_3.median')}).",
        {
            "test": "Wilcoxon signed-rank; Mann-Whitney U",
            "data": "As-reported annual statements; EBITDA over total assets, winsorized at the 1st and 99th percentiles",
            "library_call": "analysis/ops_matched.py; analysis/stats_ops.py",
            "caveat": "Firms that stop filing drop out, so later years cover fewer firms.",
        },
        stats,
        [
            table(
                "Table 8. Profitability against the matched firm, fiscal years +1 to +3",
                ["Group", "Year +1", "Year +2", "Year +3", "N, year +1", "N, year +3"],
                rows,
                ids,
                "Median change in ROA (EBITDA over total assets) from fiscal year -1 to year +1, +2 and +3, minus the same change at the matched firm, in percentage "
                "points. ROA winsorized at the 1st and 99th percentiles. N falls with the horizon because firms stop filing after a sale or bankruptcy.",
            )
        ],
    )


def sec_f():
    rows, ids = [], []
    for g in LR_GROUPS + ("financial_misconduct", "sex_or_relationship"):
        rows.append(
            [
                GROUP_NAMES[g],
                v(RS, f"exit.{g}.delisted_1y", "pct"),
                v(RS, f"exit.{g}.delisted_3y", "pct"),
                v(RS, f"exit.{g}.delisted_5y", "pct"),
                v(RS, f"exit.{g}.acquired_5y", "pct"),
                v(RS, f"exit.{g}.bankruptcy_5y", "pct"),
                v(RS, f"exit.{g}.n5", "count"),
            ]
        )
        ids += [f"exit.{g}.delisted_{h}y" for h in (1, 3, 5)]
    stats = []
    for g in LR_GROUPS + ("financial_misconduct", "sex_or_relationship"):
        for h in (1, 3, 5):
            stats.append(
                stat(
                    RS,
                    f"exit.{g}.delisted_{h}y",
                    f"Stopped trading within {12 * h} months, {GROUP_NAMES[g].lower()}",
                    "pct",
                    "proportion",
                    g,
                )
            )
        for k in ("acquired", "bankruptcy"):
            stats.append(
                stat(
                    RS,
                    f"exit.{g}.{k}_5y",
                    f"{k.capitalize()} within 60 months, {GROUP_NAMES[g].lower()}",
                    "pct",
                    "proportion",
                    g,
                )
            )
        stats.append(
            stat(
                RS,
                f"exit.{g}.n5",
                f"Events with a complete 60-month horizon, {GROUP_NAMES[g].lower()}",
                "count",
                "count",
                g,
            )
        )
    stats += many(
        RS,
        [
            (
                "exitdiff.forced_vs_retired.delisted_5y",
                "Forced minus retired, stopped trading within 60 months",
                "pp",
                "chi-square",
            ),
            (
                "exitdiff.forced_founder_vs_forced_nonfounder.delisted_5y",
                "Founder minus hired CEO, stopped trading within 60 months",
                "pp",
                "chi-square",
            ),
            ("exit.forced.acquired_1y", "Acquired within 12 months, forced", "pct", "proportion"),
            ("exit.forced.bankruptcy_1y", "Bankruptcy within 12 months, forced", "pct", "proportion"),
            ("exit.forced.acquired_3y", "Acquired within 36 months, forced", "pct", "proportion"),
            ("exit.forced.bankruptcy_3y", "Bankruptcy within 36 months, forced", "pct", "proportion"),
        ],
    )
    return section(
        "F",
        "What happened to the firm",
        "How often does the firm stop trading within 12, 36 and 60 months, and why?",
        f"Within 12, 36 and 60 months, {v(RS, 'exit.forced.delisted_1y', 'pct')}, {v(RS, 'exit.forced.delisted_3y', 'pct')} and {v(RS, 'exit.forced.delisted_5y', 'pct')} "
        f"of forced-exit firms stop trading, against {v(RS, 'exit.retired.delisted_1y', 'pct')}, {v(RS, 'exit.retired.delisted_3y', 'pct')} and {v(RS, 'exit.retired.delisted_5y', 'pct')} "
        f"after retirements (60-month p {pv(RS, 'exitdiff.forced_vs_retired.delisted_5y')}).",
        {
            "test": "Chi-square test of proportions",
            "data": "Last trading date and corporate actions in the price file",
            "library_call": "analysis/event_study.py; analysis/stats_returns.py",
            "caveat": "Delisting type is the corporate action within 60 days of the last price; delistings with no action are counted as other.",
        },
        stats,
        [
            table(
                "Table 9. Firms that stop trading within 12, 36 and 60 months",
                ["Group", "Gone, 12m", "Gone, 36m", "Gone, 60m", "Acquired, 60m", "Bankrupt, 60m", "N, 60m"],
                rows,
                ids,
                "Share of firms whose stock left the price file within 12, 36 and 60 months of the announcement. Each horizon uses the events whose horizon "
                "is complete in the data; N, 60m counts those for 60 months (the 12- and 36-month counts are larger). Acquired and Bankrupt classify the "
                "corporate action within 60 days of the final price.",
            )
        ],
    )


def sec_g():
    rows = []
    for g in ("forced", "retired", "forced_founder", "forced_nonfounder", "conduct"):
        stays = "founder_stays" if g == "forced_founder" else "ceo_stays_director"
        rows.append(
            [
                GROUP_NAMES[g],
                v(BS, f"board.{g}.director_turnover.mean", "pct"),
                v(BS, f"board.{g}.split_after.mean", "pct"),
                v(BS, f"board.{g}.{stays}.mean", "pct"),
                nv(BS, f"board.{g}.director_turnover.mean"),
            ]
        )
    stats = many(
        BS,
        [
            ("board.forced.director_turnover.mean", "Share of pre-departure directors gone, forced", "pct", "mean"),
            ("board.retired.director_turnover.mean", "Share of pre-departure directors gone, retired", "pct", "mean"),
            (
                "boarddiff.forced_vs_retired.director_turnover.diff_mean",
                "Forced minus retired, director turnover",
                "pp",
                "Welch t",
            ),
            ("board.forced.split_after.mean", "Chair and CEO split after, forced", "pct", "mean"),
            ("board.retired.split_after.mean", "Chair and CEO split after, retired", "pct", "mean"),
            ("board.forced_founder.founder_stays.mean", "Founder still on the board", "pct", "mean"),
            ("board.forced_nonfounder.ceo_stays_director.mean", "Fired hired CEO still a director", "pct", "mean"),
            ("board.retired.ceo_stays_director.mean", "Retired CEO still a director", "pct", "mean"),
            ("board.conduct.director_turnover.mean", "Share of pre-departure directors gone, conduct", "pct", "mean"),
            (
                "board.forced_founder.director_turnover.mean",
                "Share of pre-departure directors gone, founder fired",
                "pct",
                "mean",
            ),
            ("g.events_with_board_data", "Departures with board data before and after", "count", "count"),
        ],
        "board",
    )
    return section(
        "G",
        "The board afterwards",
        "What happens to the board about two years after the firing?",
        f"About two years after a forced exit, {v(BS, 'board.forced.director_turnover.mean', 'pct')} of the earlier directors are gone, against "
        f"{v(BS, 'board.retired.director_turnover.mean', 'pct')} after a retirement (p {pv(BS, 'boarddiff.forced_vs_retired.director_turnover.diff_mean')}).",
        {
            "test": "Means; Welch t",
            "data": "Director lists extracted from DEF 14A proxy statements",
            "library_call": "analysis/extract_board.py; analysis/board_outcomes.py",
            "caveat": "Firms without both proxies, including most firms sold or delisted in between, are excluded.",
        },
        stats,
        [
            table(
                "Table 10. The board about two years after the departure",
                ["Group", "Earlier directors gone", "Chair and CEO split", "Departing CEO still a director", "N"],
                rows,
                [],
                "Director lists from the last proxy filed before the departure and the first proxy filed at least 600 days after it. Directors match on surname and first "
                "initial. For fired founders the third column is the founder; otherwise the departing CEO. N is the number of departures with both proxies.",
            )
        ],
    )


def sec_h():
    specs = [
        (
            "Five-factor plus momentum: founder minus hired CEO",
            RS,
            "rob.founder_vs_nonfounder_ff5.m1p1.diff_mean",
            "pp",
        ),
        (
            "Five-factor plus momentum: conduct minus performance",
            RS,
            "rob.conduct_vs_performance_ff5.m1p1.diff_mean",
            "pp",
        ),
        ("Market-adjusted, forced exits", RS, "rob.forced.ma_m1p1.mean", "pct"),
        ("Evidence agrees the exit was forced", RS, "car.forced_strict.mm_m1p1.mean", "pct"),
        (
            "Evidence agrees: founder minus hired CEO",
            RS,
            "cardiff.forced_strict_founder_vs_forced_strict_nonfounder.mm_m1p1.diff_mean",
            "pp",
        ),
        ("Adding retirements the evidence reads as pushed", RS, "rob.forced_plus_pushed.mm_m1p1.mean", "pct"),
        ("Pushed retirements alone", RS, "rob.pushed.mm_m1p1.mean", "pct"),
        ("Excluding 2008 and 2009", RS, "rob.forced_excl_crisis.mm_m1p1.mean", "pct"),
        ("Matched BHAR, 36 months, strict size matches", OS, "rob.mbhar_strict_matches.3y.median", "pct"),
        ("Evidence agrees: BHAR vs market, 36 months", RS, "bhar.forced_strict.3y.median", "pct"),
        (
            "Pre-1998: 3-year return minus reported index, forced minus retired",
            PS,
            "pre.forced_vs_retired.abn_tsr_3y.diff_median",
            "pp",
        ),
    ]
    rows = [
        [
            name,
            v(f, k, u).replace(" percentage points", " pp"),
            pv(f, k),
            nv(f, k),
            horizon(k).split(" after")[0].split(" around")[0],
        ]
        for name, f, k, u in specs
    ]
    stats = (
        [stat(f, k, name, u, "as in the main tables", "robustness") for name, f, k, u in specs]
        + many(
            RS,
            [
                ("rob.n_pushed_retirements", "Retirements the evidence reads as pushed", "count", "count"),
                (
                    "car.forced_strict_founder.mm_m1p1.mean",
                    "Mean CAR[-1,+1], founder fired, evidence agrees",
                    "pct",
                    "one-sample t",
                ),
                (
                    "car.forced_strict_nonfounder.mm_m1p1.mean",
                    "Mean CAR[-1,+1], hired CEO fired, evidence agrees",
                    "pct",
                    "one-sample t",
                ),
                (
                    "bhar.forced_strict_founder.5y.median",
                    "Median 60-month BHAR vs market, founder fired, evidence agrees",
                    "pct",
                    "Wilcoxon",
                ),
                (
                    "exit.forced_strict.delisted_5y",
                    "Stopped trading within 60 months, evidence agrees",
                    "pct",
                    "proportion",
                ),
            ],
            "robustness",
        )
        + many(
            PS,
            [
                ("pre.events_with_tsr", "Pre-1998 departures with a proxy return graph", "count", "count"),
                ("pre.n_forced", "Pre-1998 forced exits with a proxy return graph", "count", "count"),
                (
                    "pre.forced.abn_tsr_3y.median",
                    "Median 3-year TSR minus reported index, forced, 1992-1997",
                    "pct",
                    "Wilcoxon",
                ),
                (
                    "pre.retired.abn_tsr_3y.median",
                    "Median 3-year TSR minus reported index, retired, 1992-1997",
                    "pct",
                    "Wilcoxon",
                ),
            ],
            "robustness",
        )
    )
    return section(
        "H",
        "Robustness",
        "Do the results survive other models, samples and definitions?",
        f"With five factors plus momentum the founder gap is {v(RS, 'rob.founder_vs_nonfounder_ff5.m1p1.diff_mean', 'pp')} (p {pv(RS, 'rob.founder_vs_nonfounder_ff5.m1p1.diff_mean')}) "
        f"and the conduct gap {v(RS, 'rob.conduct_vs_performance_ff5.m1p1.diff_mean', 'pp')} (p {pv(RS, 'rob.conduct_vs_performance_ff5.m1p1.diff_mean')}). "
        f"On the {v(RS, 'a.n_forced_strict', 'count')} exits the evidence also reads as forced, the return is {v(RS, 'car.forced_strict.mm_m1p1.mean', 'pct')}.",
        {
            "test": "as in the main tables",
            "data": "as in the main tables; pre-1998 returns from proxy performance graphs",
            "library_call": "analysis/stats_returns.py; analysis/stats_ops.py; analysis/pre1998_tsr.py",
            "caveat": "Pushed retirements and the strict sample rest on the evidence-based model coding, not on a hand check.",
        },
        stats,
        [
            table(
                "Table IA.1. Robustness",
                ["Specification", "Estimate", "p", "N", "Horizon"],
                rows,
                [k for _, _, k, _ in specs],
                "Each row changes one thing against the main tables. Evidence agrees: the CEO dismissal database codes the exit forced and the evidence-based coding "
                "(8-K, press releases, Wikipedia, NYT) also reads it as forced. Pushed retirements: the database codes a retirement and the evidence reads it as forced. "
                "Pre-1998: departures announced 1992 to 1997, three-year return minus the index the firm itself reports in its proxy performance graph.",
            )
        ],
    )


def check(payload):
    """The horizon-and-N gate: every statistic has N and a horizon; every table has an N column and a horizon."""
    bad = []
    for sec in payload["sections"]:
        for s in sec["statistics"]:
            if not s.get("n"):
                bad.append(f"{s['stat_id']}: no N")
            if not s.get("period") or s["period"] == "1998-2023":
                bad.append(f"{s['stat_id']}: no horizon")
        for t in sec["tables"]:
            if "Company" in t["columns"]:
                continue  # one row per named event: each row is N = 1 and states its own horizons
            if not any(c == "N" or c.startswith("N,") or c.startswith("N ") for c in t["columns"]):
                bad.append(f"{t['title']}: no N column")
    if bad:
        raise SystemExit("horizon/N gate failed:\n  " + "\n  ".join(bad[:40]))


def main():
    for k in ("a.n_sex_or_relationship", "a.n_financial_misconduct", "a.n_forced_strict"):
        g = k.split("a.n_")[1]
        c = SRC[RS].get(f"car.{g}.mm_m1p1.count")
        if c:
            SRC[RS][k] = {"value": c["value"]}
    if "b.model_error_rate" in SRC[CS] and "b.model_founder_codes" in SRC[CS]:
        SRC[CS]["b.model_error_rate"]["n"] = SRC[CS]["b.model_founder_codes"][
            "value"
        ]  # the rate is over the model's codes
    sections = [sec_a(), sec_b(), sec_c(), sec_d(), sec_e(), sec_f(), sec_g(), sec_h()]
    files = sorted(p.name for p in OUT.glob("*_stats.json"))
    payload = {
        "label": TITLE,
        "engine_version": "founder_ceo_exits 2.0",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "source_files": {f"outputs/{f}": hashlib.sha256((OUT / f).read_bytes()).hexdigest()[:16] for f in files},
        "constants": [
            {"name": "paper_ruleset", "value": "founder_ceo_jfe", "source": "backend ruleset"},
            {"name": "estimation_window_start", "value": -250, "source": "event_study.py"},
            {"name": "estimation_window_end", "value": -30, "source": "event_study.py"},
            {"name": "min_estimation_days", "value": 120, "source": "event_study.py"},
            {"name": "match_size_band_low", "value": 0.7, "source": "ops_matched.py"},
            {"name": "match_size_band_high", "value": 1.3, "source": "ops_matched.py"},
            {"name": "shumway_delist_return", "value": -0.3, "source": "event_study.py"},
            {"name": "board_post_lag_days", "value": 600, "source": "extract_board.py"},
            {"name": "sample_start_year", "value": 1998, "source": "build_events.py"},
            {"name": "index_size", "value": 1500, "source": "Gentry et al. (2021): S&P 1500 firms"},
            {"name": "matching_rule_pct", "value": 30, "source": "ops_matched.py"},
            {"name": "winsor_lower_pct", "value": 1, "source": "stats_ops.py"},
            {"name": "winsor_upper_pct", "value": 99, "source": "stats_ops.py"},
            {"name": "days_1y", "value": 252, "source": "event_study.py HORIZONS"},
            {"name": "days_3y", "value": 756, "source": "event_study.py HORIZONS"},
            {"name": "days_5y", "value": 1260, "source": "event_study.py HORIZONS"},
            {"name": "months_1y", "value": 12, "source": "horizon in months"},
            {"name": "months_3y", "value": 36, "source": "horizon in months"},
            {"name": "months_5y", "value": 60, "source": "horizon in months"},
            {"name": "trading_days_per_month", "value": 21, "source": "paths.py"},
            {"name": "evidence_window_days", "value": 10, "source": "evidence_fetch.py"},
            {"name": "min_reason_cases", "value": 10, "source": "stats_returns.py"},
            {"name": "n_cases_listed", "value": 12, "source": "describe.py"},
            {"name": "ci_level", "value": 95, "source": "confidence level of every interval"},
            {"name": "pre_window_start", "value": -30, "source": "paths.py"},
            {"name": "post_window_end", "value": 60, "source": "paths.py"},
            {"name": "replication_repo_url", "value": REPO_URL, "source": "public replication archive"},
        ],
        "sections": sections,
    }
    check(payload)
    (OUT / "combined_results.json").write_text(json.dumps(payload, indent=1))
    print(
        "sections",
        [s["section_id"] for s in sections],
        "stats",
        sum(len(s["statistics"]) for s in sections),
        "tables",
        sum(len(s["tables"]) for s in sections),
    )


if __name__ == "__main__":
    main()
