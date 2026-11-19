"""Assemble outputs/combined_results.json (LetteredReportPayload, backend/schemas/lettered_report.py).

Every statistic is read from a results file written by code (stats_returns.py, stats_ops.py, board_outcomes.py)
and carries source_file and source_key. Interpretation sentences insert the formatted values; no number is typed.
Sections: A sample, B announcement returns, C founders, D why the board acted, E long-run returns,
F what happened to the firm, G the board afterwards, H operating performance.
"""

import datetime
import hashlib
import json
import pathlib

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "outputs"
SRC = {"returns_stats.json": None, "ops_stats.json": None, "board_stats.json": None, "coding_stats.json": None}
for k in SRC:
    p = OUT / k
    SRC[k] = json.loads(p.read_text()) if p.exists() else {}


def fmt(v, unit):
    if v is None:
        return "n/a"
    if unit == "pct":
        return f"{v * 100:.1f}%"
    if unit == "pp":
        return f"{v * 100:.1f} percentage points"
    if unit == "pps":
        return f"{v * 100:.1f} pp"
    if unit == "count":
        return f"{int(round(v)):,}"
    if unit == "coef":
        return f"{v:.3f}"
    return f"{v:.2f}"


def stat(file, key, label, unit, test="", group="", population="US public firms, S&P 1500, CEO departures 1998-2023"):
    r = SRC[file].get(key)
    if r is None:
        return None
    s = {
        "stat_id": key.replace("_v0", ""),
        "label": label,
        "value": r.get("value"),
        "formatted": fmt(r.get("value"), unit),
        "unit": {"pct": "share", "pp": "difference", "count": "count", "coef": "coefficient"}.get(unit, ""),
        "test": test,
        "source_file": f"outputs/{file}",
        "source_key": key,
        "group": group,
        "population": population,
        "period": "1998-2023",
    }
    for f in ("n", "t", "p", "se", "ci_low", "ci_high"):
        if r.get(f) is not None:
            s[f] = int(r[f]) if f == "n" else float(r[f])
    return s


def v(file, key, unit):
    r = SRC[file].get(key)
    return fmt(None if r is None else r.get("value"), unit)


def pv(file, key):
    r = SRC[file].get(key) or {}
    p = r.get("p")
    return "n/a" if p is None else ("<0.001" if p < 0.001 else f"{p:.3f}")


def section(sid, title, question, interpretation, method, stats, tables=(), warnings=()):
    return {
        "section_id": sid,
        "title": title,
        "question": question,
        "interpretation": interpretation,
        "methodology": method,
        "statistics": [s for s in stats if s],
        "tables": list(tables),
        "warnings": list(warnings),
        "source_files": sorted({s["source_file"] for s in stats if s}),
    }


def table(title, columns, rows, stat_ids, notes):
    return {"title": title, "columns": columns, "rows": rows, "stat_ids": stat_ids, "notes": notes}


RS, OS, BS, CS = "returns_stats.json", "ops_stats.json", "board_stats.json", "coding_stats.json"
GROUPS = [
    ("forced", "Forced exits"),
    ("retired", "Voluntary retirements"),
    ("forced_founder", "Founder forced out"),
    ("forced_nonfounder", "Non-founder forced out"),
    ("conduct", "Dismissed for conduct"),
    ("performance", "Dismissed for performance"),
    ("relationship", "Relationship with an employee"),
]


def car_rows():
    rows, ids = [], []
    for g, name in GROUPS:
        k = f"car.{g}.mm_m1p1"
        rows.append(
            [
                name,
                v(RS, f"{k}.mean", "pct"),
                v(RS, f"{k}.median", "pct"),
                f"{(SRC[RS].get(k + '.mean') or {}).get('t', float('nan')):.2f}",
                pv(RS, f"{k}.mean"),
                v(RS, f"{k}.count", "count"),
            ]
        )
        ids += [f"{k}.mean", f"{k}.median"]
    return rows, ids


def main():
    sections = []
    sections.append(
        section(
            "A",
            "Sample",
            "Which CEO departures are studied and how many have usable stock returns?",
            f"The sample holds {v(RS, 'a.events_with_returns', 'count')} departures with returns: {v(RS, 'a.n_forced', 'count')} forced exits "
            f"and {v(RS, 'a.n_retired', 'count')} voluntary retirements. Of the forced exits, {v(RS, 'a.n_forced_founder', 'count')} removed a founder, "
            f"{v(RS, 'a.n_conduct', 'count')} were dismissals for conduct and {v(RS, 'a.n_relationship', 'count')} followed a relationship with an employee.",
            {
                "test": "counts",
                "data": "Gentry et al. (2021) CEO dismissal database v10Oct2024 linked to daily prices by SEC CIK",
                "library_call": "analysis/build_events.py; analysis/event_study.py",
                "caveat": "Founder status and reasons are coded from the dataset's notes and sources, then checked by hand (paper/FOUNDER_REVIEW.md).",
            },
            [
                stat(RS, k, lbl, "count", group="sample")
                for k, lbl in [
                    ("a.events_with_returns", "Departures with returns"),
                    ("a.n_forced", "Forced exits"),
                    ("a.n_retired", "Voluntary retirements"),
                    ("a.n_forced_founder", "Founder forced out"),
                    ("a.n_forced_nonfounder", "Non-founder forced out"),
                    ("a.n_conduct", "Dismissed for conduct"),
                    ("a.n_performance", "Dismissed for performance"),
                    ("a.n_relationship", "Relationship with an employee"),
                    ("a.first_year", "First event year"),
                    ("a.last_year", "Last event year"),
                ]
            ],
        )
    )

    rows, ids = car_rows()
    sections.append(
        section(
            "B",
            "Announcement returns",
            "How does the stock react when the board removes the CEO?",
            f"Over the three trading days around the announcement, forced exits earn a market-model abnormal return of {v(RS, 'car.forced.mm_m1p1.mean', 'pct')} "
            f"(p {pv(RS, 'car.forced.mm_m1p1.mean')}), while voluntary retirements earn {v(RS, 'car.retired.mm_m1p1.mean', 'pct')} "
            f"(p {pv(RS, 'car.retired.mm_m1p1.mean')}). The gap is {v(RS, 'cardiff.forced_vs_retired.mm_m1p1.diff_mean', 'pp')} (p {pv(RS, 'cardiff.forced_vs_retired.mm_m1p1.diff_mean')}).",
            {
                "test": "Cross-sectional t, Boehmer-Musumeci-Poulsen standardized t, Wilcoxon signed-rank; Welch t for differences",
                "data": "Daily total returns (Sharadar closeadj), market model estimated over days -250 to -30",
                "library_call": "analysis/event_study.py; analysis/stats_returns.py",
                "caveat": "Day 0 is the first trading day on or after the announcement.",
            },
            [
                stat(RS, f"car.{g}.mm_m1p1.mean", f"Mean CAR[-1,+1], {n}", "pct", "one-sample t", g)
                for g, n in GROUPS[:2]
            ]
            + [
                stat(RS, "car.forced.mm_m1p1.bmp_t", "BMP standardized t, forced exits", "coef", "BMP 1991", "forced"),
                stat(RS, "car.forced.mm_m1p1.median", "Median CAR[-1,+1], forced exits", "pct", "Wilcoxon", "forced"),
                stat(
                    RS,
                    "car.forced.ff5_m1p1.mean",
                    "Mean five-factor CAR[-1,+1], forced exits",
                    "pct",
                    "one-sample t",
                    "forced",
                ),
                stat(RS, "car.forced.mm_m5p5.mean", "Mean CAR[-5,+5], forced exits", "pct", "one-sample t", "forced"),
                stat(
                    RS,
                    "cardiff.forced_vs_retired.mm_m1p1.diff_mean",
                    "Forced minus retired, mean CAR[-1,+1]",
                    "pp",
                    "Welch t",
                ),
                stat(
                    RS,
                    "cardiff.forced_vs_retired.mm_m1p1.diff_median",
                    "Forced minus retired, median CAR[-1,+1]",
                    "pp",
                    "Mann-Whitney U",
                ),
            ],
            [
                table(
                    "Table 1. Abnormal returns around the announcement, days -1 to +1",
                    ["Group", "Mean CAR", "Median CAR", "t", "p", "N"],
                    rows,
                    ids,
                    "CAR is the cumulative market-model abnormal return from day -1 to day +1, with the model estimated over days -250 to -30. "
                    "t is the cross-sectional t of the mean; p is two-sided. Forced exits are Gentry et al. codes 3 and 4. Founder status and reasons are hand-checked codes.",
                )
            ],
        )
    )

    sections.append(
        section(
            "C",
            "Founders",
            "Is removing a founder different from removing a hired CEO?",
            f"When the CEO removed is the founder, the three-day abnormal return is {v(RS, 'car.forced_founder.mm_m1p1.mean', 'pct')}, against "
            f"{v(RS, 'car.forced_nonfounder.mm_m1p1.mean', 'pct')} for non-founders, a gap of {v(RS, 'cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean', 'pp')} "
            f"(p {pv(RS, 'cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean')}). In a regression with event-year effects the founder interaction is "
            f"{v(RS, 'reg.car_m1p1.forced_x_founder_v0', 'pp')} (p {pv(RS, 'reg.car_m1p1.forced_x_founder_v0')}).",
            {
                "test": "Welch t; OLS with event-year fixed effects, SE clustered by year",
                "data": "Forced exits and retirements with returns",
                "library_call": "analysis/stats_returns.py",
                "caveat": "Founder means founded or co-founded the firm; heirs of founders are not founders.",
            },
            [
                stat(RS, k, lbl, u, tst, "founder")
                for k, lbl, u, tst in [
                    ("car.forced_founder.mm_m1p1.mean", "Mean CAR[-1,+1], founder forced out", "pct", "one-sample t"),
                    (
                        "car.forced_nonfounder.mm_m1p1.mean",
                        "Mean CAR[-1,+1], non-founder forced out",
                        "pct",
                        "one-sample t",
                    ),
                    (
                        "cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean",
                        "Founder minus non-founder, CAR[-1,+1]",
                        "pp",
                        "Welch t",
                    ),
                    (
                        "reg.car_m1p1.forced_x_founder_v0",
                        "Regression: forced x founder",
                        "pp",
                        "OLS, clustered by year",
                    ),
                    ("bhar.forced_founder.3y.median", "Median 3-year BHAR, founder forced out", "pct", "Wilcoxon"),
                    (
                        "exit.forced_founder.delisted_5y",
                        "Share delisted within 5 years, founder forced out",
                        "pct",
                        "proportion",
                    ),
                ]
            ],
        )
    )

    sections.append(
        section(
            "D",
            "Why the board acted",
            "Does the reason for the removal change the market's reaction?",
            f"Dismissals for conduct earn {v(RS, 'car.conduct.mm_m1p1.mean', 'pct')} against {v(RS, 'car.performance.mm_m1p1.mean', 'pct')} for performance "
            f"dismissals, a gap of {v(RS, 'cardiff.conduct_vs_performance.mm_m1p1.diff_mean', 'pp')} (p {pv(RS, 'cardiff.conduct_vs_performance.mm_m1p1.diff_mean')}). "
            f"The {v(RS, 'a.n_relationship', 'count')} removals that followed a relationship with an employee average {v(RS, 'car.relationship.mm_m1p1.mean', 'pct')} "
            f"(p {pv(RS, 'car.relationship.mm_m1p1.mean')}).",
            {
                "test": "Welch t",
                "data": "Forced exits by coded primary reason",
                "library_call": "analysis/code_events.py; analysis/stats_returns.py",
                "caveat": "Relationship cases are few, so their mean is reported with its uncertainty rather than as a test result.",
            },
            [
                stat(RS, k, lbl, u, tst, "reason")
                for k, lbl, u, tst in [
                    ("car.conduct.mm_m1p1.mean", "Mean CAR[-1,+1], conduct", "pct", "one-sample t"),
                    ("car.performance.mm_m1p1.mean", "Mean CAR[-1,+1], performance", "pct", "one-sample t"),
                    ("cardiff.conduct_vs_performance.mm_m1p1.diff_mean", "Conduct minus performance", "pp", "Welch t"),
                    (
                        "car.relationship.mm_m1p1.mean",
                        "Mean CAR[-1,+1], relationship with an employee",
                        "pct",
                        "one-sample t",
                    ),
                    ("car.relationship.mm_m1p1.count", "Relationship cases with returns", "count", "count"),
                ]
            ],
        )
    )

    sections.append(
        section(
            "E",
            "Long-run returns",
            "Does the firm do better or worse in the years after the removal?",
            f"Against the market, the median forced-exit firm's three-year buy-and-hold abnormal return is {v(RS, 'bhar.forced.3y.median', 'pct')}. Against a matched firm in the same "
            f"industry with similar size and profitability, the median is {v(OS, 'mbhar.forced.3y.median', 'pct')} (p {pv(OS, 'mbhar.forced.3y.median')}), "
            f"and the forced-minus-retired difference is {v(OS, 'mbhardiff.forced_vs_retired.3y.diff_median', 'pp')} (p {pv(OS, 'mbhardiff.forced_vs_retired.3y.diff_median')}).",
            {
                "test": "Wilcoxon signed-rank; skewness-adjusted t with bootstrap CI (Lyon, Barber and Tsai 1999)",
                "data": "Buy-and-hold returns from day +2, delisting returns per Shumway (1997)",
                "library_call": "analysis/ops_matched.py; analysis/stats_ops.py",
                "caveat": "Market-adjusted BHARs are right-skewed; matched-firm BHARs are the main test.",
            },
            [
                stat(
                    RS,
                    "bhar.forced.3y.median",
                    "Median 3-year market-adjusted BHAR, forced",
                    "pct",
                    "Wilcoxon",
                    "forced",
                ),
                stat(
                    RS,
                    "bhar.retired.3y.median",
                    "Median 3-year market-adjusted BHAR, retired",
                    "pct",
                    "Wilcoxon",
                    "retired",
                ),
                stat(
                    OS, "mbhar.forced.3y.median", "Median 3-year matched-firm BHAR, forced", "pct", "Wilcoxon", "forced"
                ),
                stat(
                    OS,
                    "mbhar.retired.3y.median",
                    "Median 3-year matched-firm BHAR, retired",
                    "pct",
                    "Wilcoxon",
                    "retired",
                ),
                stat(
                    OS, "mbhar.forced.5y.median", "Median 5-year matched-firm BHAR, forced", "pct", "Wilcoxon", "forced"
                ),
                stat(
                    OS,
                    "mbhar.forced.3y.skewadj_t",
                    "Skewness-adjusted t, 3-year matched BHAR, forced",
                    "coef",
                    "LBT 1999",
                    "forced",
                ),
                stat(
                    OS,
                    "mbhardiff.forced_vs_retired.3y.diff_median",
                    "Forced minus retired, median 3-year matched BHAR",
                    "pp",
                    "Mann-Whitney U",
                ),
                stat(
                    OS,
                    "mbhardiff.forced_founder_vs_forced_nonfounder.3y.diff_median",
                    "Founder minus non-founder, median 3-year matched BHAR",
                    "pp",
                    "Mann-Whitney U",
                ),
            ],
        )
    )

    sections.append(
        section(
            "F",
            "What happened to the firm",
            "How often does the firm stop trading after the removal, and why?",
            f"Within five years, {v(RS, 'exit.forced.delisted_5y', 'pct')} of forced-exit firms leave the price file against {v(RS, 'exit.retired.delisted_5y', 'pct')} "
            f"after retirements (p {pv(RS, 'exitdiff.forced_vs_retired.delisted_5y')}). Acquisitions account for {v(RS, 'exit.forced.acquired_5y', 'pct')} of forced-exit firms.",
            {
                "test": "Chi-square test of proportions",
                "data": "Sharadar delisting dates and corporate actions",
                "library_call": "analysis/event_study.py; analysis/stats_returns.py",
                "caveat": "Delisting type comes from Sharadar actions within 60 days of the last price; unmatched delistings are treated as performance delistings.",
            },
            [
                stat(RS, k, lbl, u, tst, g)
                for k, lbl, u, tst, g in [
                    ("exit.forced.delisted_5y", "Delisted within 5 years, forced", "pct", "proportion", "forced"),
                    ("exit.retired.delisted_5y", "Delisted within 5 years, retired", "pct", "proportion", "retired"),
                    (
                        "exitdiff.forced_vs_retired.delisted_5y",
                        "Forced minus retired, delisted within 5 years",
                        "pp",
                        "chi-square",
                        "",
                    ),
                    ("exit.forced.acquired_5y", "Acquired within 5 years, forced", "pct", "proportion", "forced"),
                    ("exit.forced.bankruptcy_5y", "Bankruptcy within 5 years, forced", "pct", "proportion", "forced"),
                    (
                        "exit.forced_founder.delisted_5y",
                        "Delisted within 5 years, founder forced out",
                        "pct",
                        "proportion",
                        "founder",
                    ),
                ]
            ],
        )
    )

    if SRC[BS]:
        sections.append(
            section(
                "G",
                "The board afterwards",
                "Does the board change after it removes the CEO?",
                f"Two years after a forced exit, {v(BS, 'board.forced.director_turnover.mean', 'pct')} of the pre-departure directors have left, against "
                f"{v(BS, 'board.retired.director_turnover.mean', 'pct')} after retirements (p {pv(BS, 'boarddiff.forced_vs_retired.director_turnover.diff_mean')}).",
                {
                    "test": "Welch t; chi-square for proportions",
                    "data": "Director lists from the last proxy before and the first proxy at least 600 days after the departure",
                    "library_call": "analysis/extract_board.py; analysis/board_outcomes.py",
                    "caveat": "Director names are matched by surname and first initial.",
                },
                [
                    stat(BS, k, lbl, u, tst, g)
                    for k, lbl, u, tst, g in [
                        (
                            "board.forced.director_turnover.mean",
                            "Share of pre-departure directors gone by year two, forced",
                            "pct",
                            "mean",
                            "forced",
                        ),
                        (
                            "board.retired.director_turnover.mean",
                            "Share of pre-departure directors gone by year two, retired",
                            "pct",
                            "mean",
                            "retired",
                        ),
                        (
                            "boarddiff.forced_vs_retired.director_turnover.diff_mean",
                            "Forced minus retired, director turnover",
                            "pp",
                            "Welch t",
                            "",
                        ),
                        (
                            "board.forced.split_after.mean",
                            "Chair and CEO split after, forced",
                            "pct",
                            "proportion",
                            "forced",
                        ),
                        (
                            "board.forced_founder.founder_stays.mean",
                            "Founder still on the board in year two",
                            "pct",
                            "proportion",
                            "founder",
                        ),
                        (
                            "board.forced_nonfounder.ceo_stays_director.mean",
                            "Removed hired CEO still a director in year two",
                            "pct",
                            "proportion",
                            "forced",
                        ),
                        (
                            "board.retired.ceo_stays_director.mean",
                            "Retired CEO still a director in year two",
                            "pct",
                            "proportion",
                            "retired",
                        ),
                        (
                            "board.retired.split_after.mean",
                            "Chair and CEO split after, retired",
                            "pct",
                            "proportion",
                            "retired",
                        ),
                        (
                            "g.events_with_board_data",
                            "Departures with board data before and after",
                            "count",
                            "count",
                            "sample",
                        ),
                    ]
                ],
            )
        )

    sections.append(
        section(
            "H",
            "Operating performance",
            "Does profitability change after the removal, relative to a matched firm?",
            f"In the first year after a forced exit, the median change in operating return on assets relative to the matched firm is "
            f"{v(OS, 'roa.forced.abn_d_1.median', 'pp')} (p {pv(OS, 'roa.forced.abn_d_1.median')}); by year three it is "
            f"{v(OS, 'roa.forced.abn_d_3.median', 'pp')} (p {pv(OS, 'roa.forced.abn_d_3.median')}).",
            {
                "test": "Wilcoxon signed-rank on winsorized changes (Barber and Lyon 1996)",
                "data": "Sharadar as-reported annual statements, EBITDA over total assets",
                "library_call": "analysis/ops_matched.py; analysis/stats_ops.py",
                "caveat": "Matched on industry, size within 70-130%, and pre-event ROA; no CEO turnover at the control within three years.",
            },
            [
                stat(OS, k, lbl, u, tst, g)
                for k, lbl, u, tst, g in [
                    ("h.matched_events", "Events with a matched control", "count", "count", "sample"),
                    (
                        "roa.forced.abn_d_1.median",
                        "Median abnormal change in ROA, year 1, forced",
                        "pp",
                        "Wilcoxon",
                        "forced",
                    ),
                    (
                        "roa.forced.abn_d_3.median",
                        "Median abnormal change in ROA, year 3, forced",
                        "pp",
                        "Wilcoxon",
                        "forced",
                    ),
                    (
                        "roa.retired.abn_d_1.median",
                        "Median abnormal change in ROA, year 1, retired",
                        "pp",
                        "Wilcoxon",
                        "retired",
                    ),
                    (
                        "roadiff.forced_vs_retired.abn_d_3.diff_median",
                        "Forced minus retired, ROA change year 3",
                        "pp",
                        "Mann-Whitney U",
                        "",
                    ),
                ]
            ],
        )
    )

    sections.append(
        section(
            "H",
            "Robustness",
            "Do the main results survive other models, samples and definitions?",
            f"With the five-factor model, the founder gap is {v(RS, 'rob.founder_vs_nonfounder_ff5.m1p1.diff_mean', 'pp')} (p {pv(RS, 'rob.founder_vs_nonfounder_ff5.m1p1.diff_mean')}) "
            f"and the conduct gap is {v(RS, 'rob.conduct_vs_performance_ff5.m1p1.diff_mean', 'pp')} (p {pv(RS, 'rob.conduct_vs_performance_ff5.m1p1.diff_mean')}). "
            f"Adding the {v(RS, 'rob.n_pushed_retirements', 'count')} retirements our coding identifies as pushed out gives a forced-exit return of "
            f"{v(RS, 'rob.forced_plus_pushed.mm_m1p1.mean', 'pct')}. Excluding 2008 and 2009 gives {v(RS, 'rob.forced_excl_crisis.mm_m1p1.mean', 'pct')}. "
            f"Using only strict matches, the median three-year matched return is {v(OS, 'rob.mbhar_strict_matches.3y.median', 'pct')}.",
            {
                "test": "as in sections C and D",
                "data": "as in sections C and D",
                "library_call": "analysis/stats_returns.py; analysis/stats_ops.py",
                "caveat": "Pushed retirements come from the model coding of the dataset notes and are not hand-checked.",
            },
            [
                stat(
                    RS,
                    "rob.founder_vs_nonfounder_ff5.m1p1.diff_mean",
                    "Founder minus non-founder, five-factor CAR[-1,+1]",
                    "pp",
                    "Welch t",
                    "robustness",
                ),
                stat(
                    RS,
                    "rob.conduct_vs_performance_ff5.m1p1.diff_mean",
                    "Conduct minus performance, five-factor CAR[-1,+1]",
                    "pp",
                    "Welch t",
                    "robustness",
                ),
                stat(RS, "rob.n_pushed_retirements", "Retirements coded as pushed out", "count", "count", "robustness"),
                stat(
                    RS,
                    "rob.pushed.mm_m1p1.mean",
                    "Mean CAR[-1,+1], pushed retirements",
                    "pct",
                    "one-sample t",
                    "robustness",
                ),
                stat(
                    RS,
                    "rob.forced_plus_pushed.mm_m1p1.mean",
                    "Mean CAR[-1,+1], forced plus pushed",
                    "pct",
                    "one-sample t",
                    "robustness",
                ),
                stat(
                    RS,
                    "rob.forced_excl_crisis.mm_m1p1.mean",
                    "Mean CAR[-1,+1], forced, excluding 2008-2009",
                    "pct",
                    "one-sample t",
                    "robustness",
                ),
                stat(
                    OS,
                    "rob.mbhar_strict_matches.3y.median",
                    "Median 3-year matched BHAR, strict matches only",
                    "pct",
                    "Wilcoxon",
                    "robustness",
                ),
            ],
        )
    )

    def cell(file, key, unit):
        return v(file, key, unit)

    lr_rows, lr_ids = [], []
    for g, name in [
        ("forced", "Forced exits"),
        ("retired", "Voluntary retirements"),
        ("forced_founder", "Founder forced out"),
        ("forced_nonfounder", "Non-founder forced out"),
        ("conduct", "Dismissed for conduct"),
        ("performance", "Dismissed for performance"),
    ]:
        lr_rows.append(
            [
                name,
                cell(RS, f"bhar.{g}.3y.median", "pct"),
                cell(OS, f"mbhar.{g}.1y.median", "pct"),
                cell(OS, f"mbhar.{g}.3y.median", "pct"),
                cell(OS, f"mbhar.{g}.5y.median", "pct"),
                cell(OS, f"roa.{g}.abn_d_1.median", "pps"),
                cell(OS, f"roa.{g}.abn_d_3.median", "pps"),
            ]
        )
        lr_ids += [f"mbhar.{g}.3y.median"]
    ex_rows = []
    for g, name in [
        ("forced", "Forced exits"),
        ("retired", "Voluntary retirements"),
        ("forced_founder", "Founder forced out"),
        ("forced_nonfounder", "Non-founder forced out"),
        ("conduct", "Dismissed for conduct"),
        ("performance", "Dismissed for performance"),
    ]:
        ex_rows.append(
            [
                name,
                cell(RS, f"exit.{g}.delisted_5y", "pct"),
                cell(RS, f"exit.{g}.acquired_5y", "pct"),
                cell(RS, f"exit.{g}.bankruptcy_5y", "pct"),
                cell(RS, f"exit.{g}.delisted_other_5y", "pct"),
                cell(RS, f"exit.{g}.n5", "count"),
            ]
        )
    bd_rows = []
    for g, name in [
        ("forced", "Forced exits"),
        ("retired", "Voluntary retirements"),
        ("forced_founder", "Founder forced out"),
        ("forced_nonfounder", "Non-founder forced out"),
    ]:
        bd_rows.append(
            [
                name,
                cell(BS, f"board.{g}.director_turnover.mean", "pct"),
                cell(BS, f"board.{g}.split_after.mean", "pct"),
                cell(BS, f"board.{g}.ceo_stays_director.mean", "pct"),
                cell(BS, f"g.n_{g}", "count"),
            ]
        )
    for x in sections:
        if x["title"] == "Long-run returns":
            x["tables"].append(
                table(
                    "Table 2. Long-run returns and operating performance (medians)",
                    [
                        "Group",
                        "BHAR vs market, 3y",
                        "Matched BHAR, 1y",
                        "Matched BHAR, 3y",
                        "Matched BHAR, 5y",
                        "Abnormal ROA change, y1 (pp)",
                        "Abnormal ROA change, y3 (pp)",
                    ],
                    lr_rows,
                    lr_ids,
                    "Medians. BHAR vs market compounds from day +2 against the value-weighted market. Matched BHAR subtracts the buy-and-hold return of a control firm in the same "
                    "Fama-French industry with market value within 30 percent and the closest operating ROA in the prior year. ROA is EBITDA over total assets from as-reported "
                    "statements, winsorized at the 1st and 99th percentiles; changes are from year -1, measured against the control, in percentage points (pp). Delisted firms keep their final return.",
                )
            )
        if x["title"] == "What happened to the firm":
            x["tables"].append(
                table(
                    "Table 3. Firms that stop trading within five years",
                    ["Group", "Stopped trading", "Acquired", "Bankruptcy", "Other delisting", "N"],
                    ex_rows,
                    [],
                    "Share of firms whose stock leaves the price file within five years of the announcement, by the type of the last corporate action within 60 days of "
                    "the final price. N counts events with a full five-year window.",
                )
            )
        if x["title"] == "The board afterwards":
            x["tables"].append(
                table(
                    "Table 4. The board two years after the departure",
                    [
                        "Group",
                        "Pre-departure directors gone",
                        "Chair and CEO split",
                        "Departing CEO still a director",
                        "N",
                    ],
                    bd_rows,
                    [],
                    "Director lists come from the last proxy before the departure and the first proxy filed at least 600 days after it. Directors match on surname and "
                    "first initial. Firms without both proxies, including most firms sold or delisted in between, are excluded.",
                )
            )

    # re-letter to the founder_ceo_jfe rule set: A,B -> Section 2; C -> 3; D,E -> 4; F -> 5; G -> 6; H -> appendix
    letter = {
        "Sample": "A",
        "Announcement returns": "C",
        "Founders": "C2",
        "Why the board acted": "C3",
        "Long-run returns": "D",
        "Operating performance": "E",
        "What happened to the firm": "F",
        "The board afterwards": "G",
        "Robustness": "H",
    }
    for x in sections:
        x["section_id"] = letter[x["title"]]
    c = next(x for x in sections if x["section_id"] == "C")
    for sub in [x for x in sections if x["section_id"] in ("C2", "C3")]:
        c["interpretation"] += " " + sub["interpretation"]
        c["statistics"] += [
            st for st in sub["statistics"] if st["stat_id"] not in {y["stat_id"] for y in c["statistics"]}
        ]
        c["source_files"] = sorted(set(c["source_files"]) | set(sub["source_files"]))
    sections = [x for x in sections if x["section_id"] not in ("C2", "C3")]
    sections.insert(
        1,
        section(
            "B",
            "Founder and reason coding",
            "How reliable are the founder and reason codes?",
            f"The model coded {v(CS, 'b.model_founder_codes', 'count')} forced exits as founder removals. A hand review of "
            f"{v(CS, 'b.founders_reviewed', 'count')} cases confirmed {v(CS, 'b.founders_confirmed', 'count')} founders and rejected "
            f"{v(CS, 'b.founders_rejected', 'count')} model codes, an error rate of {v(CS, 'b.model_error_rate', 'pct')}. The reviewed codes are used throughout.",
            {
                "test": "hand review",
                "data": "paper/founder_review.csv",
                "library_call": "analysis/code_events.py; analysis/founder_final.py",
                "caveat": "Founder means founded or co-founded the firm or its direct predecessor; heirs are excluded.",
            },
            [
                stat(CS, k, lbl, u, "count", "coding")
                for k, lbl, u in [
                    ("b.model_founder_codes", "Forced exits coded founder by the model", "count"),
                    ("b.founders_reviewed", "Founder codes reviewed by hand", "count"),
                    ("b.founders_confirmed", "Founders confirmed", "count"),
                    ("b.founders_rejected", "Model founder codes rejected", "count"),
                    ("b.model_error_rate", "Model error rate on founder codes", "pct"),
                ]
            ],
        ),
    )
    sections.sort(key=lambda x: x["section_id"])
    files = sorted(p.name for p in OUT.glob("*_stats.json"))
    payload = {
        "label": "What happens after the board removes the CEO",
        "engine_version": "founder_ceo_exits 1.0",
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
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
        ],
        "sections": sections,
    }
    (OUT / "combined_results.json").write_text(json.dumps(payload, indent=1))
    print("sections", [s["section_id"] for s in sections], "stats", sum(len(s["statistics"]) for s in sections))


if __name__ == "__main__":
    main()
