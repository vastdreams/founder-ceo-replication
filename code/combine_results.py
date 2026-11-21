"""Assemble outputs/combined_results.json.

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
    "alpha_stats.json",
    "scandal_stats.json",
    "referee_stats.json",
)
SRC = {k: (json.loads((OUT / k).read_text()) if (OUT / k).exists() else {}) for k in FILES}
RS, OS, BS, CS, PS, DS, AS, SS, RF = FILES
TITLE = "Sacked: Sex, Fraud, Founders, and the Fate of Firms That Fire Their CEO"
REPO_URL = "https://github.com/vastdreams/founder-ceo-replication"

# One label per coded reason, shared with figures.py (Figure IA.2)
REASON_LABELS = {
    "merger_or_restructuring": "Merger or restructuring",
    "new_opportunity": "Left for a new job",
    "strategy_or_power_dispute": "Strategy or power dispute",
    "retirement_or_health": "Pushed out, described as retirement or health",
    "unclear": "Reason unclear",
    "performance": "Performance",
    "activist_or_shareholder_pressure": "Activist or shareholder pressure",
    "other_personal_conduct": "Other personal conduct",
    "relationship_with_employee": "Relationship with an employee",
    "other_sexual_misconduct": "Sexual misconduct",
}
GROUP_NAMES = {
    "forced": "CEOs fired",
    "retired": "CEOs who retired",
    "forced_founder": "Founder fired",
    "forced_nonfounder": "Hired CEO fired",
    "conduct": "Fired over a personal scandal",
    "performance": "Fired for another reason",
    "criminal": "Fired for fraud or other legal violation (comparison)",
    "relationship": "Relationship with an employee",
    "sex_or_relationship": "Sex or relationship scandal",
    "financial_misconduct": "Financial misconduct (comparison)",
    "forced_strict": "Fired, evidence agrees",
    "forced_strict_founder": "Founder fired, evidence agrees",
    "forced_strict_nonfounder": "Hired CEO fired, evidence agrees",
}
POP = {
    "forced": "CEO firings for any reason but fraud or other legal violation (database codes 3 and 4)",
    "retired": "Voluntary CEO retirements (database code 5)",
    "forced_founder": "Forced exits of founder-CEOs (hand-checked)",
    "forced_nonfounder": "Forced exits of CEOs who did not found the firm",
    "conduct": "Firings over a personal scandal: sex, a relationship or other personal conduct (hand-checked)",
    "performance": "Firings for every reason but a personal scandal or fraud: performance, strategy, power, activists, restructuring",
    "criminal": "Firings over fraud or other legal violation (comparison; not in the main sample)",
    "relationship": "Forced exits after a relationship with an employee (hand-checked)",
    "sex_or_relationship": "Forced exits after sexual misconduct or a relationship with an employee (hand-checked)",
    "financial_misconduct": "Firings for financial misconduct (comparison; not in the main sample)",
    "forced_strict": "Forced exits the evidence-based coding also reads as forced",
    "scandal_gap": "Firings over a personal scandal against other firings, well-dated",
    "founder_gap": "Fired founders against fired hired CEOs, well-dated",
    "llm_yes": "Firings the evidence-based coding also reads as forced, well-dated",
    "llm_unclear": "Firings the evidence-based coding reads as unclear, well-dated",
    "llm_no": "Firings the evidence-based coding reads as not forced, well-dated",
    "all_firings": "Every firing, those over fraud or other legal violation included",
    "ipw": "Well-dated firings, reweighted by the inverse chance of being well dated",
    "same_sample": "Well-dated firings with every control, unweighted",
    "founder": "Fired founders (hand-checked)",
    "hired": "Fired CEOs who did not found the firm",
}
BASE_POP = "S&P 1500 firms, announcements 1998-2023"


def horizon(key: str) -> str:
    """Pure: how long after (or around) the announcement the statistic is measured, read from its key."""
    k = key
    if k.startswith("cox."):
        return "Up to 60 months (1,826 days) from the announcement, censored at the end of the price file"
    if k.startswith(("strict.reg.", "fraud.reg.")):
        return "60 months (1,260 trading days) from day +2 after the announcement"
    if k.startswith("code."):
        return "Sample definition: CEO departures announced 1998 to 2023"
    if k.startswith("dsel.") and "m1p1" not in k and "m5p5" not in k:
        if ".prior_ret" in k:
            return "Trading days -252 to -31 before the announcement (day 0)"
        if any(x in k for x in (".mcap_m1.", ".roa_m1.", ".leverage_w.")):
            return "Before the departure: fiscal year -1 (market value at that fiscal year-end)"
        if ".gone." in k:
            return "60 months (1,260 trading days) from day +2 after the announcement"
        return "Sample definition: CEO departures announced 1998 to 2023"
    m = re.match(r"alpha(?:diff)?\.[^.]+\.(?:ew|vw)\.(\d+)m$", k)
    if m:
        return f"Calendar months 1 to {m.group(1)} after the announcement month, portfolios formed each month"
    if k.startswith("scandal.") and "first_report" in k:
        return "Trading days -1 to +1 around the first New York Times report of the scandal (day 0)"
    if k.startswith("scandal.n_"):
        return "Sample definition: scandals first reported 1998 to 2023; departure within 12 months of the first report"
    if k.endswith("early_bankruptcy_n"):
        return "A bankruptcy recorded within 180 days after the announcement (day 0)"
    if k.startswith(("a.", "b.", "rob.n_", "flow.")) or k.startswith("g.events"):
        return "Sample definition: CEO departures announced 1998 to 2023"
    if k == "hook.nvda.day_ret":
        return "12 November 2026 against the 11 November close"
    if k == "hook.nvda.since_board_statement":
        return "From the 6 November 2026 close, before the board's 8 November statement, to 18 November 2026"
    if k.startswith(("desc.", "descdiff.")):
        return "Before the departure: fiscal year -1 (market value at that fiscal year-end)"
    if k.startswith("pre."):
        return "Three fiscal years from the event year, departures announced 1992 to 1997"
    if k.startswith(("board.", "boarddiff.")):
        return "About two years: the last proxy before the departure against the first proxy filed 600 or more days after it"
    if "pre_m30m2" in k:
        return "Trading days -30 to -2 before the announcement (day 0)"
    if "post_p2p60" in k:
        return "Trading days +2 to +60 after the announcement (day 0), about three months"
    if "m30p30" in k:
        return "Trading days -30 to +30 around the announcement (day 0)"
    if "0p1" in k and "m1p1" not in k:
        return "Trading days 0 to +1 from the announcement (day 0)"
    if k.startswith("reg.exit5"):
        return "60 months (1,260 trading days) from day +2 after the announcement"
    if "m5p5" in k:
        return "Trading days -5 to +5 around the announcement (day 0)"
    if "m1p1" in k or ".car_m1p1" in k or k.startswith("reg.car"):
        return "Trading days -1 to +1 around the announcement (day 0)"
    m = re.search(r"abn_d_(\d)", k)
    if m:
        year = "0 (the year of the departure)" if m.group(1) == "0" else "+" + m.group(1)
        return f"Fiscal year {year} against fiscal year -1, relative to the matched firm"
    m = re.search(r"(?:\.|_)(\d)y\b|_(\d)y$|\.n(\d)$|bhar_(\d)y", k)
    if m:
        h = int(next(g for g in m.groups() if g))
        return f"{12 * h} months ({252 * h:,} trading days) from day +2 after the announcement"
    if k.startswith("reg.mbhar"):
        return "36 months (756 trading days) from day +2 after the announcement"
    if k.startswith(("h.", "case.n")):
        return "Sample definition: CEO departures announced 1998 to 2023"
    if k.startswith("case.") and k.endswith("mcap_bn"):
        return "At the fiscal year-end before the departure"
    raise ValueError(f"no horizon for {key}")


def population(key: str) -> str:
    parts = key.split(".")
    g = parts[1] if len(parts) > 1 else ""
    if (
        parts[0] in ("strict", "cox", "code", "dsel", "fraud")
        and g in ("exit", "mbhar", "reg", "gone", "bankrupt", "ipw", "same_sample", "all_firings")
        or parts[0] in ("cox", "code", "dsel")
    ):
        return {
            "strict": "Firings by how the evidence-based coding reads them (forced, unclear), against retirements",
            "cox": "CEO firings against voluntary retirements, every month of follow-up to 60 months",
            "code": "Model codes checked by hand: founders, fraud, sex or relationship, other personal conduct",
            "dsel": "CEO firings: well-dated (database or hand) against dated only by a filing or the day the CEO left",
            "fraud": "Every firing, those over fraud or other legal violation included, against retirements",
        }[parts[0]] + f"; {BASE_POP}"
    if "_vs_" in g:
        a, b = g.split("_vs_")
        return f"{POP.get(a, GROUP_NAMES.get(a, a))} against {POP.get(b, GROUP_NAMES.get(b, b)).lower()}; {BASE_POP}"
    if g == "reason" and len(parts) > 2:
        return f"Forced exits whose coded primary reason is '{parts[2].replace('_', ' ')}'; {BASE_POP}"
    return f"{POP.get(g, 'CEO departures')}; {BASE_POP}"


def basket(key: str) -> str:
    """Pure: what the statistic measures, for the claim-scope gate."""
    if key.startswith("scandal."):
        return "New York Times reports of personal misconduct by sitting CEOs, and share returns"
    if key.startswith(("alpha.", "alphadiff.")):
        return "monthly portfolio returns net of the Fama-French five factors and momentum"
    if key.startswith(("cox.", "strict.exit", "strict.reg", "fraud.reg", "dsel.gone")) or key in (
        "fraud.all_firings.delisted_5y",
        "fraud.all_firings.bankruptcy_5y",
    ):
        return "whether the stock still trades, and how it left the market"
    if key.startswith("code.") or key.startswith(
        ("dsel.founder", "dsel.conduct", "dsel.strict", "dsel.n_", "dsel.year")
    ):
        return "CEO departures and their coding"
    if key.startswith(("dsel.mcap", "dsel.roa", "dsel.leverage")):
        return "as-reported annual financial statements"
    if key.startswith(("exit.", "exitdiff.", "reg.exit5")):
        return "whether the stock still trades, and how it left the market"
    if key.startswith(("roa.", "roadiff.", "desc.", "descdiff.", "h.")):
        return "as-reported annual financial statements"
    if key.startswith(("board.", "boarddiff.", "g.")):
        return "board composition in proxy statements"
    if key.startswith("pre."):
        return "total shareholder return from proxy performance graphs"
    if key.startswith(("a.", "b.", "rob.n_", "case.n", "flow.")):
        return "CEO departures and their coding"
    return "stock returns"


def calendar(key: str) -> str:
    if key.startswith("hook."):
        return "Nvidia, November 2026"
    return "departures announced 1992-1997" if key.startswith("pre.") else "departures announced 1998-2023"


def fmt(v, unit):
    if v is None:
        return "n/a"
    if unit == "pct":
        return "0.0%" if abs(v) < 0.0005 else f"{v * 100:.1f}%"  # never "-0.0%"
    if unit == "pct2":  # monthly alphas: a tenth of a percent a month is about 1.2% a year
        return f"{v * 100:.2f}%"
    if unit == "pp":
        return f"{v * 100:.1f} percentage points"
    if unit == "pps":
        return "0.0" if abs(v) < 0.0005 else f"{v * 100:.1f}"
    if unit == "count":
        return f"{int(round(v)):,}"
    if unit == "bn":
        return f"{v:.1f}"
    if unit == "year":
        return f"{int(round(v))}"
    if unit == "p3":
        return "<0.001" if v < 0.001 else f"{v:.3f}"
    if unit == "coef":
        return f"{v:.2f}"
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
        "unit": {
            "pct": "share",
            "pct2": "return a month",
            "pp": "difference",
            "count": "count",
            "coef": "coefficient",
            "bn": "USD billion",
        }.get(unit, ""),
        "test": test,
        "source_file": f"outputs/{file}",
        "source_key": key,
        "group": group,
        "population": population(key),
        "geography": "United States (S&P 1500 firms)",
        "basket": basket(key),
        "period": f"{calendar(key)}; {horizon(key)}",
    }
    for f in ("n", "t", "p", "se", "ci_low", "ci_high"):
        if r.get(f) is not None:
            s[f] = int(r[f]) if f == "n" else float(r[f])
    if "n" not in s and unit == "count" and r.get("value") is not None:
        s["n"] = int(round(r["value"]))  # a count is its own N
    return s


def ci_stats(file, key, label, unit):
    """Two statistics, key.ci_low and key.ci_high: the 95% interval from the estimate and its t (or the z implied by
    its two-sided p), with the base statistic's N and horizon."""
    from statistics import NormalDist

    base = stat(file, key, label, unit)
    r = SRC[file].get(key) or {}
    val, tt, pp = r.get("value"), r.get("t"), r.get("p")
    if base is None or val is None:
        return []
    z = abs(tt) if tt else (NormalDist().inv_cdf(1 - pp / 2) if pp and 0 < pp < 1 else None)
    if not z:
        return []
    se = abs(val) / z
    out = []
    for side, x in (("ci_low", val - 1.96 * se), ("ci_high", val + 1.96 * se)):
        s = dict(base)
        s.update(
            {
                "stat_id": f"{base['stat_id']}.{side}",
                "label": f"{label}, 95% interval, {side[3:]} end",
                "value": x,
                "formatted": fmt(x, "pps" if (unit == "pp" and side == "ci_low") else unit),
                "test": "95% interval",
            }
        )  # "from -0.8 to 2.6 percentage points"
        for f in ("t", "p", "se"):
            s.pop(f, None)
        out.append(s)
    return out


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
        ("roa", "Return on assets, year -1 (EBITDA / assets)", "pct"),
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
            ("a.n_forced", "CEOs fired, announcement sample", "count", "count"),
            ("a.n_retired", "Voluntary retirements", "count", "count"),
            ("a.n_forced_founder", "Founders fired", "count", "count"),
            ("a.n_forced_nonfounder", "Hired CEOs fired", "count", "count"),
            ("a.n_conduct", "Fired over a personal scandal", "count", "count"),
            ("a.n_performance", "Fired for another reason", "count", "count"),
            ("a.n_relationship", "Relationship with an employee", "count", "count"),
            ("a.n_sex_or_relationship", "Sex or relationship scandal", "count", "count"),
            (
                "a.n_criminal_all_dates",
                "Fired for fraud or other legal violation, all dates (comparison)",
                "count",
                "count",
            ),
            ("a.n_criminal_dated", "Fired for fraud or other legal violation, dated (comparison)", "count", "count"),
            ("a.n_lr_conduct", "Fired over a personal scandal, all dates", "count", "count"),
            ("a.n_lr_founder_personal", "Founders fired over a personal scandal, all dates", "count", "count"),
            ("a.n_lr_forced_founder", "Founders fired, all dates (long run)", "count", "count"),
            ("a.n_forced_strict", "Forced exits the evidence also reads as forced", "count", "count"),
            ("a.n_lr_forced", "CEOs fired with returns, all dates (long run)", "count", "count"),
            ("a.n_lr_retired", "Retirements with returns, all dates (long run)", "count", "count"),
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
                "Table IA.2. Who gets fired: the firm in the year before the departure",
                [
                    "Fiscal year -1, medians",
                    "Firings",
                    "Retirements",
                    "Founders fired",
                    "p, firings vs retirements",
                    "N firings",
                ],
                rows,
                ids,
                "Medians in the fiscal year before the departure, from as-reported annual statements; market value at that fiscal year-end. "
                "Return on assets is earnings before interest, taxes, depreciation and amortization (EBITDA) over total assets. "
                "p is from a Mann-Whitney U test of firings against retirements. "
                "N firings is the number of firings with the item.",
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
    # the well-dated sex-or-relationship cases and the fraud comparison, on the same well-dated sample (review r1, item 2)
    for g in ("sex_or_relationship", "criminal"):
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
        ids.append(f"{k}.mean")
    # The tests the abstract and conclusion state, in the main table (a body table must carry every number they use).
    gaps = (
        (
            "Founder minus hired CEO (below zero: larger fall after a founder)",
            "cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean",
        ),
        (
            "Personal scandal minus other firings (above zero: smaller fall after a scandal)",
            "cardiff.conduct_vs_performance.mm_m1p1.diff_mean",
        ),
        (
            "Personal scandal minus fraud (above zero: smaller fall after a scandal)",
            "cardiff.conduct_vs_criminal.mm_m1p1.diff_mean",
        ),
    )
    # Panel B: the differences only; their intervals and the equivalence tests are in the text of Section 4
    prows = [[name, v(RS, key, "pps"), "", tv(RS, key), pv(RS, key), nv(RS, key)] for name, key in gaps]
    # Panel C: who counts as fired and which firings are dated (the referee's two measurement questions)
    crows_ = []
    for name, f_, key in (
        ("Fired, the evidence-based coding agrees", RF, "strict.llm_yes.mm_m1p1"),
        ("Fired, the evidence-based coding is unclear", RF, "strict.llm_unclear.mm_m1p1"),
        ("Fired, the evidence-based coding reads not forced", RF, "strict.llm_no.mm_m1p1"),
        ("Well-dated firings reweighted to resemble every firing", RF, "dsel.ipw.mm_m1p1"),
        ("Every firing, any date (many days 0 misplaced)", RS, "rob.all_dates.forced.mm_m1p1"),
        ("Well-dated firings, fraud and legal violation included", RF, "fraud.all_firings.mm_m1p1"),
        ("CEOs fired, five-factor model", RS, "car.forced.ff5_m1p1"),
    ):
        crows_.append(
            [
                name,
                v(f_, f"{key}.mean", "pct"),
                v(f_, f"{key}.median", "pct") if f"{key}.median" in SRC[f_] else "",
                tv(f_, f"{key}.mean"),
                pv(f_, f"{key}.mean"),
                nv(f_, f"{key}.mean"),
            ]
        )
        ids.append(f"{key}.mean")
    rows = (
        [["Panel A. By group", "", "", "", "", ""]]
        + rows
        + [["Panel B. Differences in the mean, percentage points", "", "", "", "", ""]]
        + prows
        + [["Panel C. Who counts as fired, and which dates", "", "", "", "", ""]]
        + crows_
    )
    ids += [key for _, key in gaps]
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
            REASON_LABELS.get(r, r.replace("_", " ").capitalize()),
            v(RS, f"car.reason.{r}.mm_m1p1.mean", "pct"),
            tv(RS, f"car.reason.{r}.mm_m1p1.mean"),
            pv(RS, f"car.reason.{r}.mm_m1p1.mean"),
            v(RS, f"car.reason.{r}.mm_m1p1.holm_p", "p3"),
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
                c["dismissal"].replace("legal or conduct", "legal or personal conduct").capitalize(),
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
                (
                    "car.criminal.mm_m1p1.mean",
                    "Mean CAR[-1,+1], fraud or other legal violation (comparison)",
                    "pct",
                    "one-sample t",
                ),
                (
                    "car.sex_or_relationship.mm_m1p1.mean",
                    "Mean CAR[-1,+1], sex or relationship scandal",
                    "pct",
                    "one-sample t",
                ),
                (
                    "exitdiff.conduct_vs_performance.delisted_5y",
                    "Personal scandal minus other firings, delisted within 60 months",
                    "pp",
                    "chi-square",
                ),
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
                    "Personal scandal minus other reasons, CAR[-1,+1]",
                    "pp",
                    "Welch t",
                ),
                (
                    "cardiff.conduct_vs_criminal.mm_m1p1.diff_mean",
                    "Personal scandal minus fraud or crime, CAR[-1,+1]",
                    "pp",
                    "Welch t",
                ),
                (
                    "rob.all_dates.conduct_vs_criminal.mm_m1p1.diff_mean",
                    "Personal scandal minus fraud or crime, CAR[-1,+1], all dates",
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
                    "Personal scandal minus other reasons, days -30 to -2",
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
        + [
            stat(
                RS,
                f"car.reason.{r}.mm_m1p1.holm_p",
                f"Holm-adjusted p, reason: {r.replace('_', ' ')}",
                "p3",
                "Holm",
                "reason",
            )
            for r in reasons
        ]
        + cstats
        + many(DS, [("case.n_listed", "Founder cases listed", "count", "count")], "case")
        + many(
            SS,
            [
                ("scandal.n_events", "Personal scandals of sitting CEOs found in the New York Times", "count", "count"),
                ("scandal.n_departed", "Scandals after which the CEO left within 12 months", "count", "count"),
                ("scandal.n_kept", "Scandals after which the CEO stayed for 12 months", "count", "count"),
                (
                    "scandal.n_known_firings_found",
                    "Database firings over a personal scandal the search finds",
                    "count",
                    "count",
                ),
                (
                    "scandal.all.first_report.car_m1p1.mean",
                    "Market-adjusted return around the first report, all scandals",
                    "pct",
                    "one-sample t",
                ),
                (
                    "scandal.departed.first_report.car_m1p1.mean",
                    "Market-adjusted return around the first report, CEO later left",
                    "pct",
                    "one-sample t",
                ),
                (
                    "scandal.kept.first_report.car_m1p1.mean",
                    "Market-adjusted return around the first report, CEO stayed",
                    "pct",
                    "one-sample t",
                ),
            ],
            "scandal",
        )
        + many(
            DS,
            [
                ("hook.nvda.day_ret", "Nvidia share price change, 12 November 2026", "pct", "event return"),
                (
                    "hook.nvda.since_board_statement",
                    "Nvidia share price change, 6 to 18 November 2026",
                    "pct",
                    "event return",
                ),
            ],
            "case",
        )
    )
    stats = stats + many(
        RF,
        [
            ("equiv.scandal_gap.mm_m1p1.diff", "Personal scandal minus other firings, CAR[-1,+1]", "pp", "Welch t"),
            (
                "equiv.scandal_gap.mm_m1p1.ci95_low",
                "Personal-scandal gap, 95% interval, low end",
                "pps",
                "95% interval",
            ),
            (
                "equiv.scandal_gap.mm_m1p1.ci95_high",
                "Personal-scandal gap, 95% interval, high end",
                "pp",
                "95% interval",
            ),
            (
                "equiv.scandal_gap.mm_m1p1.ci90_low",
                "Personal-scandal gap, one-sided 95% bound on a larger fall",
                "pp",
                "90% interval",
            ),
            ("equiv.scandal_gap.mm_m1p1.mde", "Personal-scandal gap the test detects with 80% power", "pp", "power"),
            (
                "equiv.scandal_gap.mm_m1p1.margin",
                "Equivalence margin: the average firing's three-day fall",
                "pp",
                "margin",
            ),
            (
                "equiv.scandal_gap.mm_m1p1.tost_p",
                "Personal-scandal gap within the margin, two one-sided tests",
                "p3",
                "TOST",
            ),
            (
                "equiv.scandal_gap.mm_m1p1.tost_p_larger_fall",
                "Scandal fall larger by the margin or more, one-sided test",
                "p3",
                "one-sided t",
            ),
            ("equiv.founder_gap.mm_m1p1.diff", "Founder minus hired CEO, CAR[-1,+1]", "pp", "Welch t"),
            ("equiv.founder_gap.mm_m1p1.ci95_low", "Founder gap, 95% interval, low end", "pps", "95% interval"),
            ("equiv.founder_gap.mm_m1p1.ci95_high", "Founder gap, 95% interval, high end", "pp", "95% interval"),
            ("equiv.founder_gap.mm_m1p1.mde", "Founder gap the test detects with 80% power", "pp", "power"),
            ("equiv.founder_gap.mm_m1p1.tost_p", "Founder gap within the margin, two one-sided tests", "p3", "TOST"),
            (
                "strict.llm_yes.mm_m1p1.mean",
                "Mean CAR[-1,+1], fired, the evidence-based coding agrees",
                "pct",
                "one-sample t",
            ),
            (
                "strict.llm_yes.mm_m1p1.median",
                "Median CAR[-1,+1], fired, the evidence-based coding agrees",
                "pct",
                "Wilcoxon",
            ),
            (
                "strict.llm_unclear.mm_m1p1.mean",
                "Mean CAR[-1,+1], fired, the evidence-based coding is unclear",
                "pct",
                "one-sample t",
            ),
            (
                "strict.llm_unclear.mm_m1p1.median",
                "Median CAR[-1,+1], fired, the evidence-based coding is unclear",
                "pct",
                "Wilcoxon",
            ),
            (
                "strict.llm_no.mm_m1p1.mean",
                "Mean CAR[-1,+1], fired, the evidence-based coding reads not forced",
                "pct",
                "one-sample t",
            ),
            (
                "strict.llm_yes_vs_unclear.mm_m1p1.diff_mean",
                "Evidence agrees minus evidence unclear, CAR[-1,+1]",
                "pp",
                "Welch t",
            ),
            (
                "dsel.ipw.mm_m1p1.mean",
                "Mean CAR[-1,+1], well-dated firings reweighted to resemble every firing",
                "pct",
                "weighted t (HC1)",
            ),
            (
                "dsel.same_sample.mm_m1p1.mean",
                "Mean CAR[-1,+1], the same well-dated firings unweighted",
                "pct",
                "one-sample t",
            ),
            ("fraud.all_firings.mm_m1p1.mean", "Mean CAR[-1,+1], every firing, fraud included", "pct", "one-sample t"),
            ("fraud.all_firings.mm_m1p1.median", "Median CAR[-1,+1], every firing, fraud included", "pct", "Wilcoxon"),
        ],
        "referee",
    )
    return section(
        "C",
        "Announcement returns",
        "How does the stock react when the board fires the CEO, and does it matter who and why?",
        f"Over trading days -1 to +1, forced exits earn {v(RS, 'car.forced.mm_m1p1.mean', 'pct')} (t = {tv(RS, 'car.forced.mm_m1p1.mean')}, N = {nv(RS, 'car.forced.mm_m1p1.mean')}) "
        f"and retirements {v(RS, 'car.retired.mm_m1p1.mean', 'pct')}. Fired founders earn {v(RS, 'car.forced_founder.mm_m1p1.mean', 'pct')} against "
        f"{v(RS, 'car.forced_nonfounder.mm_m1p1.mean', 'pct')} (gap p {pv(RS, 'cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean')}). "
        f"Firings over a personal scandal earn {v(RS, 'car.conduct.mm_m1p1.mean', 'pct')}, other firings {v(RS, 'car.performance.mm_m1p1.mean', 'pct')} "
        f"(gap p {pv(RS, 'cardiff.conduct_vs_performance.mm_m1p1.diff_mean')}). Prices fall {v(RS, 'drift.forced.pre_m30m2.mean', 'pct')} over days -30 to -2 "
        f"and are flat over days +2 to +60 ({v(RS, 'drift.forced.post_p2p60.mean', 'pct')}).",
        {
            "test": "Cross-sectional t, Boehmer-Musumeci-Poulsen standardized t, Wilcoxon signed-rank; Welch t and Mann-Whitney U for differences",
            "data": "Daily total returns; market model estimated over trading days -250 to -30 for days -1 to +1; market-adjusted returns for longer windows",
            "library_call": "analysis/event_study.py; analysis/paths.py; analysis/stats_returns.py; analysis/describe.py",
            "caveat": "Day 0 is the first trading day on or after the announcement that the CEO is leaving. Firings for fraud or crime are not in the sample. Reasons other than the hand-checked conduct labels are model codes.",
        },
        stats,
        [
            table(
                "Table 2. The announcement: abnormal returns over trading days −1 to +1",
                ["Group", "Mean", "Median", "t", "p", "N"],
                rows,
                ids,
                "Market-model abnormal return over trading days -1 to +1 around the announcement (day 0), on well-dated firings (dated by the "
                "database or by hand), fraud and legal violations excluded unless stated. N counts each row's firings. t: the t of the mean, "
                "or the Welch t of a difference; p is two-sided. Panel B: the first group's mean minus the second's; a positive number means a "
                "smaller fall in the first group. Founder, scandal and fraud labels are hand-checked. The sex or relationship row "
                f"(n = {nv(RS, 'car.sex_or_relationship.mm_m1p1.mean')}) is too small for a test. Panel C reweights by size, prior return, "
                "profitability, leverage, founder and scandal flags and year (Table IA.5).",
            ),
            table(
                "Table IA.6. Before, at and after the announcement, by group",
                ["Group", "Days -30 to -2", "p", "Days -1 to +1", "p", "Days +2 to +60", "p", "N"],
                drows,
                dids,
                "Days -30 to -2 and +2 to +60 are cumulative market-adjusted returns (firm minus market), used because a firing firm's alpha before the event "
                "is strongly negative and a market model would project it forward. Days -1 to +1 is the market-model return of Table 2. Events need every day of "
                "a window. N is the number of departures in the days -1 to +1 window; the outer windows differ by at most a few percent.",
            ),
            table(
                "Table IA.7. Why the board acted: abnormal returns over trading days −1 to +1 by coded reason",
                ["Coded primary reason", "Mean", "t", "p", "Holm p", "N"],
                rrows,
                [f"car.reason.{r}.mm_m1p1.mean" for r in reasons],
                "Firings for any reason but fraud or other legal violation, by the primary reason coded from the database notes, the 8-K filed within 10 days, cited press releases, Wikipedia and matched "
                "New York Times articles. Reasons with fewer than 10 cases are not shown. Holm p adjusts each p for the number of reasons "
                "tested. Financial-misconduct, sexual-conduct and relationship labels are hand-checked; the others are model codes.",
            ),
            table(
                "Table IA.8. Personal scandals of sitting CEOs in the New York Times, 1998 to 2023",
                ["Company", "CEO", "First report", "Scandal", "Days -1 to +1"],
                scandal_rows(),
                [f"scandal.{g}.first_report.car_m1p1.mean" for g in ("all", "kept", "departed")],
                "Reports of personal misconduct by a sitting CEO of a sample firm, found by searching the New York Times Archive and checked by hand. "
                "Panel B: the CEO departed within 12 months of the first report (CEO dismissal database, or a reported departure the "
                "database misses). Days -1 to +1: market-adjusted return around the first report. The table lists the "
                f"{len(SRC[SS].get('_cases', []))} of the {v(SS, 'scandal.n_events', 'count')} scandals found whose shares traded around the first report. "
                "The search finds only a few of the database's firings over "
                "a personal scandal, mostly at the largest firms, so the table describes prominent cases, not a sample.",
            ),
            table(
                "Table IA.9. The largest founders fired, among firings both codings read as forced",
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
                "Founder-CEOs fired, among exits the evidence-based coding also reads as forced, ranked by market value at the fiscal year-end before the departure. "
                "Database reason is the CEO dismissal database's code (performance = 3, legal or personal conduct = 4). Days -1 to +1 is the market-model abnormal return; "
                "36 months is the buy-and-hold return minus the market from day +2; it can fall below -100% when the stock lost most of its value while the "
                "market rose. After 60 months reports whether the stock still traded, and if not, how it left.",
            ),
        ],
    )


def scandal_rows():
    """The NYT scandal cases in two panels, the board kept its CEO or the CEO left within a year,
    each closed by its mean return around the first report."""
    cases = SRC[SS].get("_cases", [])
    rows = []
    for departed, head, key in (
        (False, "Panel A. The board kept the CEO", "kept"),
        (True, "Panel B. The CEO left within a year", "departed"),
    ):
        rows.append([head, "", "", "", ""])
        for c in (c for c in cases if bool(c["departed"]) == departed):
            rows.append(
                [
                    c["company"],
                    c["ceo_name"],
                    str(c["first_report_date"])[:10],
                    str(c["scandal_type"]).replace("_", " ").capitalize(),
                    "n/a" if c.get("car") is None else f"{c['car'] * 100:.1f}%",
                ]
            )
        stat_key = f"scandal.{key}.first_report.car_m1p1.mean"
        rows.append([f"Mean, {nv(SS, stat_key)} cases", "", "", "", v(SS, stat_key, "pct")])
    return rows


LR_GROUPS = ("forced", "retired", "forced_founder", "forced_nonfounder", "conduct", "performance")


def sec_d():
    # Two panels with the p-values in their own columns: (A) against the market, (B) against a matched firm.
    rows, ids = [["Panel A. Median return minus the market", "", "", "", "", "", "", ""]], []
    for g in LR_GROUPS:
        keys = [f"bhar.{g}.{h}y.median" for h in (1, 3, 5)]
        rows.append([GROUP_NAMES[g]] + [v(RS, k, "pct") for k in keys] + [pv(RS, k) for k in keys] + [nv(RS, keys[1])])
    rows.append(["Panel B. Median return minus a matched firm", "", "", "", "", "", "", ""])
    for g in LR_GROUPS:
        keys = [f"mbhar.{g}.{h}y.median" for h in (1, 3, 5)]
        rows.append([GROUP_NAMES[g]] + [v(OS, k, "pct") for k in keys] + [pv(OS, k) for k in keys] + [nv(OS, keys[1])])
        ids += keys
    # long-run returns are skewed: the mean row shows how far means and medians part
    keys = [f"mbhar.forced.{h}y.mean" for h in (1, 3, 5)]
    rows.append(["CEOs fired, mean"] + [v(OS, k, "pct") for k in keys] + [pv(OS, k) for k in keys] + [nv(OS, keys[1])])
    stats = []
    for h in (1, 3, 5):
        stats.append(
            stat(
                RS,
                f"bhar.forced.{h}y.mean",
                f"Mean {12 * h}-month BHAR vs market, forced exits",
                "pct",
                "one-sample t",
                "forced",
            )
        )
        stats.append(
            stat(
                OS,
                f"mbhar.forced.{h}y.mean",
                f"Mean {12 * h}-month BHAR vs matched firm, forced exits",
                "pct",
                "one-sample t",
                "forced",
            )
        )
        if h == 3:  # 36-month skewness-adjusted t: already in section D; not repeated
            pass
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
            ("mbhar.forced.5y.skewadj_t", "Skewness-adjusted t, 60-month matched BHAR, forced", "coef", "LBT 1999"),
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
                "bhar.criminal.3y.median",
                "Median 36-month BHAR vs market, fraud or crime (comparison)",
                "pct",
                "Wilcoxon",
            ),
        ],
    )
    arows, aids = [], []
    for h in (12, 36):
        for g, name in (
            ("forced", "CEOs fired"),
            ("retired", "CEOs who retired"),
            ("forced_founder", "Founder fired"),
            ("conduct", "Fired over a personal scandal"),
        ):
            ke, kv = f"alpha.{g}.ew.{h}m", f"alpha.{g}.vw.{h}m"
            if SRC[AS].get(ke) is None:
                continue
            arows.append(
                [
                    f"{name}, {h} months",
                    v(AS, ke, "pct2"),
                    tv(AS, ke),
                    v(AS, kv, "pct2"),
                    tv(AS, kv),
                    nv(AS, ke),
                    f"{SRC[AS][ke].get('firms', 0):.0f}",
                ]
            )
            aids += [ke, kv]
            stats += many(
                AS,
                [
                    (ke, f"Calendar-time alpha, equal-weighted, {name.lower()}, {h} months", "pct2", "OLS, Newey-West"),
                    (kv, f"Calendar-time alpha, value-weighted, {name.lower()}, {h} months", "pct2", "OLS, Newey-West"),
                ],
            )
        kd, kdv = f"alphadiff.forced_vs_retired.ew.{h}m", f"alphadiff.forced_vs_retired.vw.{h}m"
        arows.append(
            [
                f"Firings minus retirements, {h} months",
                v(AS, kd, "pct2"),
                tv(AS, kd),
                v(AS, kdv, "pct2"),
                tv(AS, kdv),
                nv(AS, kd),
                "",
            ]
        )
        aids += [kd, kdv]
        stats += many(
            AS,
            [
                (
                    kd,
                    f"Calendar-time alpha, firings minus retirements, equal-weighted, {h} months",
                    "pct2",
                    "OLS, Newey-West",
                ),
                (
                    kdv,
                    f"Calendar-time alpha, firings minus retirements, value-weighted, {h} months",
                    "pct2",
                    "OLS, Newey-West",
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
                "Table IA.12. Long-run returns at 12, 36 and 60 months",
                ["Group", "12m", "36m", "60m", "p, 12m", "p, 36m", "p, 60m", "N, 36m"],
                rows,
                ids,
                "Medians of buy-and-hold returns from day +2 over 12, 36 and 60 months, all firings, with the Wilcoxon p. Panel A subtracts "
                "the market's buy-and-hold return; Panel B subtracts a matched firm in the same industry, with market value within 30 percent "
                "and the nearest return on assets. The last row gives means with t-test p; skewed returns can give means and medians of "
                "opposite sign. Delisted firms take their delisting return and then hold the market. N, 36m counts events at 36 months.",
            ),
            table(
                "Table IA.11. Calendar-time alpha after the announcement",
                [
                    "Portfolio",
                    "Equal-weighted, % a month",
                    "t",
                    "Value-weighted, % a month",
                    "t",
                    "N months",
                    "Firms a month",
                ],
                arows,
                aids,
                "Each calendar month the portfolio holds every firm whose announcement fell 1 to H months before. Its return minus the risk-free rate "
                "is regressed on the Fama-French five factors and momentum; alpha is the intercept, with Newey-West t (6 lags). Value weights are market "
                "values at the fiscal year-end before the event. Months with fewer than 10 firms are dropped. The difference rows regress the firing "
                "portfolio's return minus the retirement portfolio's. Delisted firms take their delisting return in their last month.",
            ),
        ],
    )


def sec_e():
    rows, ids = [], []
    for g in LR_GROUPS:
        row = [GROUP_NAMES[g]]
        for y in (0, 1, 2, 3):
            row.append(f"{v(OS, f'roa.{g}.abn_d_{y}.median', 'pps')} ({pv(OS, f'roa.{g}.abn_d_{y}.median')})")
            ids.append(f"roa.{g}.abn_d_{y}.median")
        row += [nv(OS, f"roa.{g}.abn_d_1.median"), nv(OS, f"roa.{g}.abn_d_3.median")]
        rows.append(row)
    stats = []
    for g in LR_GROUPS:
        for y in (0, 1, 2, 3):
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
                "Table IA.13. Profitability against the matched firm, fiscal years 0 to +3",
                ["Group", "Year 0", "Year +1", "Year +2", "Year +3", "N, year +1", "N, year +3"],
                rows,
                ids,
                "Median change in return on assets (ROA) from fiscal year -1 to year 0 (the year of the departure), +1, +2 and +3, minus the same change at the matched firm, in percentage "
                "points, with the Wilcoxon p in parentheses. ROA is earnings before interest, taxes, depreciation and amortization (EBITDA) over "
                "total assets, winsorized at the 1st and 99th percentiles. N falls with the horizon because firms stop filing "
                "after a sale or bankruptcy.",
            )
        ],
    )


def sec_f():
    rows, ids = [], []
    for g in LR_GROUPS + ("forced_strict", "criminal"):
        rows.append(
            [
                GROUP_NAMES[g],
                v(RS, f"exit.{g}.delisted_1y", "pct"),
                v(RS, f"exit.{g}.delisted_3y", "pct"),
                v(RS, f"exit.{g}.delisted_5y", "pct"),
                v(RS, f"exit.{g}.acquired_5y", "pct"),
                v(RS, f"exit.{g}.bankruptcy_5y", "pct"),
                "" if g == "retired" else pv(RS, f"exitdiff.{g}_vs_retired.delisted_5y"),
                v(RS, f"exit.{g}.n5", "count"),
            ]
        )
        ids += [f"exit.{g}.delisted_{h}y" for h in (1, 3, 5)]
    # The firing gap without and with controls (Table IA.10 has the full set), in the main table: the abstract's key
    # number with controls must be printed in a body table.
    gap = "exitdiff.forced_vs_retired.delisted_5y"
    rows = (
        [["Panel A. Share of firms", "", "", "", "", "", "", ""]]
        + rows
        + [["Panel B. Differences in the 60-month share, percentage points", "", "", "", "", "", "", ""]]
        + [["Firings minus retirements", "", "", v(RS, gap, "pps"), "", "", pv(RS, gap), nv(RS, gap)]]
        + [
            [
                name,
                "",
                "",
                v(OS, f"{reg}.gone.forced", "pps"),
                v(OS, f"{reg}.acquired.forced", "pps"),
                v(OS, f"{reg}.bankrupt.forced", "pps"),
                pv(OS, f"{reg}.gone.forced"),
                nv(OS, f"{reg}.gone.forced"),
            ]
            for name, reg in (
                ("Firings minus retirements, size and profitability", "reg.exit5"),
                (
                    "Firings minus retirements, every control",
                    "reg.exit5c",
                ),
            )
        ]
    )
    for name, key in (
        ("Founder minus hired CEO", "exitdiff.forced_founder_vs_forced_nonfounder.delisted_5y"),
        ("Personal scandal minus other firings", "exitdiff.conduct_vs_performance.delisted_5y"),
    ):
        rows.append([name, "", "", v(RS, key, "pps"), "", "", pv(RS, key), nv(RS, key)])
    ids += [gap, "reg.exit5.gone.forced", "reg.exit5c.gone.forced"]
    stats_rf = many(
        RF,
        [
            (
                f"strict.reg.{y}.{a}",
                f"{'Delisted' if y == 'gone' else 'Bankrupt'} within 60 months, {lbl} minus retirements, every control",
                "pp",
                "linear probability model",
            )
            for y in ("gone", "bankrupt")
            for a, lbl in (("yes", "fired, evidence agrees,"), ("unclear", "fired, evidence unclear,"))
        ]
        + [
            (
                f"fraud.reg.{y}.{k}",
                f"{'Delisted' if y == 'gone' else 'Bankrupt'} within 60 months, {lbl}, every control",
                "pp",
                "linear probability model",
            )
            for y in ("gone", "bankrupt")
            for k, lbl in (
                ("criminal", "fraud or legal violation beyond other firings"),
                ("forced", "other firings minus retirements, fraud firings in the model"),
            )
        ]
        + [
            (
                f"cox.{e}.{sp}.forced_hr",
                f"Hazard ratio of {'delisting' if e == 'gone' else 'bankruptcy'}, firings against retirements, {lbl}",
                "coef",
                "Cox proportional hazards",
            )
            for e in ("gone", "bankrupt")
            for sp, lbl in (
                ("base", "size and profitability"),
                ("full", "every control"),
                ("strict", "evidence agrees, every control"),
            )
        ]
        + [
            (
                "fraud.all_firings.delisted_5y",
                "Delisted within 60 months, every firing, fraud included",
                "pct",
                "proportion",
            ),
            (
                "fraud.all_firings.bankruptcy_5y",
                "Bankrupt within 60 months, every firing, fraud included",
                "pct",
                "proportion",
            ),
            (
                "cox.n_incomplete_horizon",
                "Departures followed for less than 60 months, in the Cox model only",
                "count",
                "count",
            ),
        ],
        "referee",
    )
    stats = []
    for g in LR_GROUPS + ("forced_strict", "criminal"):
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
    stats += (
        many(
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
                (
                    "exit.forced.delisted_other_5y",
                    "Delisted for another reason within 60 months, forced",
                    "pct",
                    "proportion",
                ),
                (
                    "exitdiff.forced_strict_vs_retired.delisted_5y",
                    "Evidence agrees minus retired, stopped trading within 60 months",
                    "pp",
                    "chi-square",
                ),
            ],
        )
        + stats_rf
    )
    bands = [
        ("small", "Under $0.3 billion"),
        ("mid", "$0.3 to 1 billion"),
        ("large", "$1 to 5 billion"),
        ("mega", "Over $5 billion"),
    ]
    srows, sids = [], []
    for b, name in bands:
        srows.append(
            [
                name,
                v(RS, f"exit.forced.size_{b}.delisted_5y", "pct"),
                v(RS, f"exit.retired.size_{b}.delisted_5y", "pct"),
                pv(RS, f"exitdiff.forced_vs_retired.size_{b}.delisted_5y"),
                v(RS, f"exit.forced.size_{b}.bankruptcy_5y", "pct"),
                v(RS, f"exit.retired.size_{b}.bankruptcy_5y", "pct"),
                v(RS, f"exit.forced.size_{b}.n5", "count"),
                v(RS, f"exit.retired.size_{b}.n5", "count"),
            ]
        )
        sids += [f"exit.forced.size_{b}.delisted_5y", f"exit.retired.size_{b}.delisted_5y"]
        for g, gl in (("forced", "firings"), ("retired", "retirements")):
            stats += many(
                RS,
                [
                    (
                        f"exit.{g}.size_{b}.delisted_5y",
                        f"Stopped trading within 60 months, {gl}, market value {name.lower()}",
                        "pct",
                        "proportion",
                    ),
                    (
                        f"exit.{g}.size_{b}.bankruptcy_5y",
                        f"Bankrupt within 60 months, {gl}, market value {name.lower()}",
                        "pct",
                        "proportion",
                    ),
                    (
                        f"exit.{g}.size_{b}.acquired_5y",
                        f"Acquired within 60 months, {gl}, market value {name.lower()}",
                        "pct",
                        "proportion",
                    ),
                ],
            )
        stats += many(
            RS,
            [
                (
                    f"exitdiff.forced_vs_retired.size_{b}.delisted_5y",
                    f"Firings minus retirements, stopped trading within 60 months, market value {name.lower()}",
                    "pp",
                    "chi-square",
                )
            ],
        )
    srows.append(
        [
            "All, bankruptcies within 180 days of the announcement set aside",
            v(RS, "exit.forced.after.delisted_5y", "pct"),
            v(RS, "exit.retired.after.delisted_5y", "pct"),
            "",
            v(RS, "exit.forced.after.bankruptcy_5y", "pct"),
            v(RS, "exit.retired.after.bankruptcy_5y", "pct"),
            nv(RS, "exit.forced.after.delisted_5y"),
            nv(RS, "exit.retired.after.delisted_5y"),
        ]
    )
    stats += many(
        RS,
        [
            (
                "exit.forced.after.delisted_5y",
                "Stopped trading within 60 months, firings, early bankruptcies set aside",
                "pct",
                "proportion",
            ),
            (
                "exit.retired.after.delisted_5y",
                "Stopped trading within 60 months, retirements, early bankruptcies set aside",
                "pct",
                "proportion",
            ),
            (
                "exit.forced.after.bankruptcy_5y",
                "Bankrupt within 60 months, firings, early bankruptcies set aside",
                "pct",
                "proportion",
            ),
            (
                "exit.retired.after.bankruptcy_5y",
                "Bankrupt within 60 months, retirements, early bankruptcies set aside",
                "pct",
                "proportion",
            ),
            (
                "exit.forced.early_bankruptcy_n",
                "Firings with a bankruptcy within 180 days of the announcement",
                "count",
                "count",
            ),
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
                "Table 4. Firms delisted within 12, 36 and 60 months, by group",
                [
                    "Group",
                    "Delisted by 12 months",
                    "Delisted by 36 months",
                    "Delisted by 60 months",
                    "Taken over by 60 months",
                    "Bankrupt by 60 months",
                    "p vs retired",
                    "N, 60 months",
                ],
                rows,
                ids,
                "Firms whose stock left the price file within 12, 36 and 60 months of the announcement, among firms followed that long. Taken "
                "over and Bankrupt classify the corporate action within 60 days of the final price. p vs retired: chi-square test of the 60-month "
                "share. Panel B: the 60-month gap, raw or as a linear probability coefficient with year and industry effects; N counts firings "
                "and retirements. Size and profitability: log market value and return on assets. Every control adds the prior return, "
                "leverage, book-to-market, distress and loss. Table IA.10 adds the checks.",
            ),
            table(
                "Table 3. Firms delisted within 60 months, by market value before the firing",
                [
                    "Market value",
                    "Delisted, firings",
                    "Delisted, retirements",
                    "p",
                    "Bankrupt, firings",
                    "Bankrupt, retirements",
                    "N firings",
                    "N retirements",
                ],
                srows,
                sids,
                "Market value at the fiscal year-end before the departure, in US dollars. Delisted: the stock left the price file (taken over, bankrupt or other) within 60 months of the "
                "announcement. Bankrupt: the corporate action within 60 days of the final price was a bankruptcy or liquidation. p is a chi-square test of "
                "the share gone, firings against retirements. The last row sets aside firms whose bankruptcy was recorded within 180 days after the "
                "announcement, which were already failing when the CEO left. Only events with a complete 60-month horizon enter.",
            ),
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
                nv(BS, f"board.{g}.director_turnover.mean"),
                v(BS, f"board.{g}.split_before.mean", "pct"),
                v(BS, f"board.{g}.split_after.mean", "pct"),
                nv(BS, f"board.{g}.split_after.mean"),
                v(BS, f"board.{g}.{stays}.mean", "pct"),
            ]
        )
    rows.append(
        [
            "p, firings against retirements",
            pv(BS, "boarddiff.forced_vs_retired.director_turnover.diff_mean"),
            nv(BS, "boarddiff.forced_vs_retired.director_turnover.diff_mean"),
            "",
            "",
            "",
            "",
        ]
    )
    rows.append(
        [
            "p, founder against hired CEO",
            pv(RF, "board.founder_vs_hired.director_turnover.diff_mean"),
            nv(RF, "board.founder_vs_hired.director_turnover.diff_mean"),
            "",
            "",
            "",
            pv(RF, "board.founder_vs_hired.ceo_stays_director.diff"),
        ]
    )
    stats = many(
        RF,
        [
            (
                "board.founder_vs_hired.director_turnover.diff_mean",
                "Founder minus hired CEO, earlier directors gone",
                "pp",
                "Welch t",
            ),
            (
                "board.founder_vs_hired.ceo_stays_director.diff",
                "Founder minus hired CEO, departing CEO still a director",
                "pp",
                "Fisher exact",
            ),
            ("board.founder_vs_hired.ceo_stays_director.founder", "Fired founder still a director", "pct", "mean"),
            ("board.founder_vs_hired.ceo_stays_director.hired", "Fired hired CEO still a director", "pct", "mean"),
        ],
        "board",
    ) + many(
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
            ("board.forced.split_before.mean", "Chair and CEO split before, forced", "pct", "mean"),
            ("board.retired.split_before.mean", "Chair and CEO split before, retired", "pct", "mean"),
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
                "Table IA.14. The board about two years after the departure",
                [
                    "Group",
                    "Earlier directors gone",
                    "N",
                    "Split before",
                    "Split after",
                    "N, split",
                    "Departing CEO still a director",
                ],
                rows,
                [],
                "Directors in the last proxy before the departure and the first one at least 600 days after it, matched on surname and first "
                "initial. Earlier directors gone: the share no longer named; a proxy does not say why. Split: the chair and CEO roles held by "
                "different people, where the later proxy names a chair (N, split). Last column: the founder for fired founders, otherwise the "
                "departing CEO. The p rows: Welch t for directors gone, Fisher exact test for the last column.",
            )
        ],
    )


def sec_h():
    flow = [
        ("Firings in the database, departures 1998 to 2023", "flow.forced_db"),
        ("with an SEC company identifier", "flow.forced_cik"),
        ("with a price history covering the announcement", "flow.forced_priced"),
        ("with announcement returns", "flow.forced_returns_all"),
        ("less firings for fraud or other legal violation (comparison only)", "flow.forced_criminal"),
        ("firings for any other reason (the paper's sample)", "flow.forced_returns"),
        ("well-dated: by the database or by hand (announcement sample)", "flow.forced_dated"),
        ("Founder codes from the model, all firings", "flow.founder_model"),
        ("founders confirmed by hand", "flow.founder_confirmed"),
        ("of which departures 1998 to 2023", "flow.founder_in_years"),
        ("of which with returns, firings over fraud or other legal violation excluded", "flow.founder_returns"),
        ("of which well-dated (announcement sample)", "flow.founder_dated"),
    ]
    flow_rows = [["Panel A. From the database to the samples", ""]] + [[name, v(DS, k, "count")] for name, k in flow]
    code_rows = []
    for c, lbl in (
        ("founder", "Founder codes checked by hand"),
        ("fraud", "Fraud and legal-violation codes checked by hand"),
        ("sex", "Sex and relationship codes checked by hand"),
        ("personal", "Other personal-conduct codes checked by hand"),
    ):
        code_rows += [
            [lbl, v(RF, f"code.{c}.n_reviewed", "count")],
            ["of which the model's code was kept", v(RF, f"code.{c}.n_kept", "count")],
        ]
    flow_rows += [["Panel B. The hand review of the model's codes", ""]] + code_rows
    code_ids = [f"code.{c}.{x}" for c in ("founder", "fraud", "sex", "personal") for x in ("n_reviewed", "n_kept")]
    windows = [
        ("Days 0 to +1", "0p1"),
        ("Days -1 to +1", "m1p1"),
        ("Days -5 to +5", "m5p5"),
    ]
    win_rows = [
        [
            name,
            v(RS, f"car.forced_founder.mm_{w}.mean", "pct"),
            v(RS, f"car.forced_nonfounder.mm_{w}.mean", "pct"),
            v(RS, f"cardiff.forced_founder_vs_forced_nonfounder.mm_{w}.diff_mean", "pps"),
            pv(RS, f"cardiff.forced_founder_vs_forced_nonfounder.mm_{w}.diff_mean"),
            v(RS, f"mde.founder_gap.mm_{w}", "pps"),
            nv(RS, f"car.forced_founder.mm_{w}.mean"),
        ]
        for name, w in windows
    ]
    exit_rows = [
        [
            name,
            v(RS, f"exit.forced.{k}_5y", "pct"),
            v(RS, f"exit.retired.{k}_5y", "pct"),
            v(OS, f"reg.exit5.{y}.forced", "pps"),
            pv(OS, f"reg.exit5.{y}.forced"),
            nv(OS, f"reg.exit5.{y}.forced"),
        ]
        for name, k, y in (
            ("Delisted", "delisted", "gone"),
            ("Acquired", "acquired", "acquired"),
            ("Bankrupt", "bankruptcy", "bankrupt"),
        )
    ]
    exit_rows.append(
        [
            "Delisted, against the matched firm",
            v(OS, "exit.paired_forced.delisted_5y", "pct"),
            v(OS, "exit.ctrl_of_forced.delisted_5y", "pct") + " (matched)",
            v(OS, "exitdiff.forced_vs_ctrl.delisted_5y", "pps"),
            pv(OS, "exitdiff.forced_vs_ctrl.delisted_5y"),
            nv(OS, "exitdiff.forced_vs_ctrl.delisted_5y"),
        ]
    )
    for name, key in (
        ("Delisted, adding prior return, leverage, book-to-market, distress and loss", "reg.exit5c.gone.forced"),
        ("Acquired, same controls", "reg.exit5c.acquired.forced"),
        ("Bankrupt, same controls", "reg.exit5c.bankrupt.forced"),
        ("Founder, within firings, same controls", "reg.exit5c.gone.founder"),
        ("Personal scandal, within firings, same controls", "reg.exit5c.gone.conduct"),
        ("Leverage (debt over assets), coefficient in the same model", "reg.exit5c.gone.leverage_w"),
    ):
        exit_rows.append([name, "", "", v(OS, key, "pps"), pv(OS, key), nv(OS, key)])
    # the referee's checks (referee_checks.py): evidence-forced and unclear firings, fraud put back, Cox hazards
    for name, key in (
        ("Delisted, fired with the evidence agreeing, every control", "strict.reg.gone.yes"),
        ("Bankrupt, fired with the evidence agreeing, every control", "strict.reg.bankrupt.yes"),
        ("Delisted, fired with the evidence unclear, every control", "strict.reg.gone.unclear"),
        ("Delisted, fraud firings beyond other firings, every control", "fraud.reg.gone.criminal"),
    ):
        exit_rows.append([name, "", "", v(RF, key, "pps"), pv(RF, key), nv(RF, key)])
    for name, key in (
        ("Delisting hazard ratio (Cox), size and profitability", "cox.gone.base.forced_hr"),
        ("Delisting hazard ratio (Cox), every control", "cox.gone.full.forced_hr"),
        ("Bankruptcy hazard ratio (Cox), every control", "cox.bankrupt.full.forced_hr"),
        ("Delisting hazard ratio (Cox), evidence agreeing, every control", "cox.gone.strict.forced_hr"),
    ):
        exit_rows.append([name, "", "", v(RF, key, "coef"), pv(RF, key), nv(RF, key)])
    extra = (
        many(
            OS,
            [
                (
                    "reg.exit5c.gone.forced",
                    "Firing effect on stopping trading within 60 months, full controls",
                    "pp",
                    "OLS, year and industry effects, clustered by year",
                ),
                (
                    "reg.exit5c.acquired.forced",
                    "Firing effect on takeover within 60 months, full controls",
                    "pp",
                    "OLS, year and industry effects, clustered by year",
                ),
                (
                    "reg.exit5c.bankrupt.forced",
                    "Firing effect on bankruptcy within 60 months, full controls",
                    "pp",
                    "OLS, year and industry effects, clustered by year",
                ),
                (
                    "reg.exit5c.gone.founder",
                    "Founder against hired CEO, stopping trading within 60 months, within firings, full controls",
                    "pp",
                    "OLS, year and industry effects, clustered by year",
                ),
                (
                    "reg.exit5c.gone.conduct",
                    "Personal scandal against other firings, stopping trading within 60 months, full controls",
                    "pp",
                    "OLS, year and industry effects, clustered by year",
                ),
                (
                    "reg.exit5c.gone.leverage_w",
                    "Leverage coefficient, stopping trading within 60 months",
                    "pp",
                    "OLS, year and industry effects, clustered by year",
                ),
            ],
            "robustness",
        )
        + [stat(DS, k, name, "count", "count", "sample") for name, k in flow]
        + [
            stat(
                RS,
                f"car.forced_founder.mm_{w}.mean",
                f"Mean CAR, founder fired, {name}",
                "pct",
                "one-sample t",
                "founder",
            )
            for name, w in windows
        ]
        + [
            stat(
                RS,
                f"car.forced_nonfounder.mm_{w}.mean",
                f"Mean CAR, hired CEO fired, {name}",
                "pct",
                "one-sample t",
                "founder",
            )
            for name, w in windows
        ]
        + [
            stat(
                RS,
                f"cardiff.forced_founder_vs_forced_nonfounder.mm_{w}.diff_mean",
                f"Founder minus hired CEO, {name}",
                "pp",
                "Welch t",
                "founder",
            )
            for name, w in windows
        ]
        + [
            stat(
                RS,
                f"mde.founder_gap.mm_{w}",
                f"Minimum detectable founder gap, {name}",
                "pp",
                "80% power, 5% test",
                "founder",
            )
            for name, w in windows
        ]
        + [
            stat(
                OS,
                f"reg.exit5.{y}.forced",
                f"Firing coefficient, {y} within 60 months, with controls",
                "pp",
                "OLS, year and industry effects, clustered by year",
                "exit",
            )
            for y in ("gone", "acquired", "bankrupt")
        ]
        + many(
            OS,
            [
                (
                    "exit.ctrl_of_forced.delisted_5y",
                    "Matched firms of firings stopped trading within 60 months",
                    "pct",
                    "proportion",
                ),
                (
                    "exit.ctrl_of_retired.delisted_5y",
                    "Matched firms of retirements stopped trading within 60 months",
                    "pct",
                    "proportion",
                ),
                (
                    "exitdiff.forced_vs_ctrl.delisted_5y",
                    "Firings minus their matched firms, stopped trading within 60 months",
                    "pp",
                    "paired t",
                ),
                (
                    "exit.paired_forced.delisted_5y",
                    "Firing firms with a matched firm, stopped trading within 60 months",
                    "pct",
                    "proportion",
                ),
                (
                    "exitdiff.retired_vs_ctrl.delisted_5y",
                    "Retirements minus their matched firms, stopped trading within 60 months",
                    "pp",
                    "paired t",
                ),
                ("h.relaxed_matches", "Matches that relax the size rule", "count", "count"),
            ],
            "exit",
        )
        + many(
            RS,
            [
                ("a.n_forced_all_dates", "Firings with returns, all dates", "count", "count"),
                ("a.n_forced_undated", "Firings dated only by leaving office", "count", "count"),
                ("a.n_forced_dated_database", "Firings dated by the database", "count", "count"),
                ("a.n_forced_dated_8k", "Firings dated by an 8-K", "count", "count"),
                ("a.n_forced_dated_nyt", "Firings dated by the NYT", "count", "count"),
                ("a.n_llm_yes", "Firings the evidence reads as forced", "count", "count"),
                ("a.n_llm_unclear", "Firings the evidence leaves unclear", "count", "count"),
                ("a.n_llm_no", "Firings the evidence reads as not forced", "count", "count"),
                (
                    "driftdiff.forced_founder_vs_forced_nonfounder.pre_m30m2.diff_mean",
                    "Founder minus hired CEO, days -30 to -2",
                    "pp",
                    "Welch t",
                ),
                (
                    "drift.criminal.pre_m30m2.mean",
                    "Mean market-adjusted CAR, days -30 to -2, fraud or crime (comparison)",
                    "pct",
                    "one-sample t",
                ),
                (
                    "drift.conduct.pre_m30m2.mean",
                    "Mean market-adjusted CAR, days -30 to -2, personal scandal",
                    "pct",
                    "one-sample t",
                ),
                (
                    "roadiff.forced_vs_retired.abn_d_1.diff_median",
                    "Forced minus retired, ROA change year 1",
                    "pp",
                    "Mann-Whitney U",
                ),
                (
                    "car.forced_founder.mm_m1p1.ci_high",
                    "Upper end of the 95% interval, founder fired, CAR[-1,+1]",
                    "pct",
                    "t interval",
                ),
                (
                    "rob.all_dates.forced_founder.mm_m1p1.mean",
                    "Mean CAR[-1,+1], founder fired, all dates",
                    "pct",
                    "one-sample t",
                ),
                (
                    "rob.all_dates.forced_nonfounder.mm_m1p1.mean",
                    "Mean CAR[-1,+1], hired CEO fired, all dates",
                    "pct",
                    "one-sample t",
                ),
                (
                    "rob.all_dates.conduct.mm_m1p1.mean",
                    "Mean CAR[-1,+1], personal scandal, all dates",
                    "pct",
                    "one-sample t",
                ),
                (
                    "rob.all_dates.performance.mm_m1p1.mean",
                    "Mean CAR[-1,+1], other reasons, all dates",
                    "pct",
                    "one-sample t",
                ),
                (
                    "rob.all_dates.criminal.mm_m1p1.mean",
                    "Mean CAR[-1,+1], fraud or crime (comparison), all dates",
                    "pct",
                    "one-sample t",
                ),
                (
                    "rob.all_dates.sex_or_relationship.mm_m1p1.mean",
                    "Mean CAR[-1,+1], sex or relationship, all dates",
                    "pct",
                    "one-sample t",
                ),
                ("rob.datesrc_database.mm_m1p1.mean", "Mean CAR[-1,+1], dated by the database", "pct", "one-sample t"),
            ]
            + [
                (
                    f"exitdiff.{g}_vs_retired.delisted_5y",
                    f"{GROUP_NAMES[g]} minus retirements, stopped trading within 60 months",
                    "pp",
                    "chi-square",
                )
                for g in (
                    "forced_founder",
                    "forced_nonfounder",
                    "conduct",
                    "performance",
                    "criminal",
                )
            ],
            "robustness",
        )
    )
    specs = [
        (
            "Founder minus hired CEO, controlling for size, prior 12-month return and year",
            RS,
            "regc.car_m1p1.founder_v0",
            "pp",
        ),
        (
            "Personal scandal minus other firings, same controls",
            RS,
            "regc.car_m1p1.conduct",
            "pp",
        ),
        (
            "Five-factor plus momentum: founder minus hired CEO",
            RS,
            "rob.founder_vs_nonfounder_ff5.m1p1.diff_mean",
            "pp",
        ),
        (
            "Five-factor plus momentum: personal scandal minus other reasons",
            RS,
            "rob.conduct_vs_performance_ff5.m1p1.diff_mean",
            "pp",
        ),
        ("Return minus the market instead of the market model", RS, "rob.forced.ma_m1p1.mean", "pct"),
        ("Evidence agrees: return minus a matched firm, 36 months, median", RF, "strict.mbhar.yes.3y.median", "pct"),
        (
            "Evidence agrees: founder minus hired CEO",
            RS,
            "cardiff.forced_strict_founder_vs_forced_strict_nonfounder.mm_m1p1.diff_mean",
            "pp",
        ),
        ("Adding retirements the evidence reads as pushed", RS, "rob.forced_plus_pushed.mm_m1p1.mean", "pct"),
        ("Pushed retirements alone", RS, "rob.pushed.mm_m1p1.mean", "pct"),
        ("Excluding 2008 and 2009", RS, "rob.forced_excl_crisis.mm_m1p1.mean", "pct"),
        (
            "Return minus a matched firm, 36 months, matches within the size band only",
            OS,
            "rob.mbhar_strict_matches.3y.median",
            "pct",
        ),
        ("Evidence agrees: return minus the market, 36 months", RS, "bhar.forced_strict.3y.median", "pct"),
        (
            "All dates, every firing with returns",
            RS,
            "rob.all_dates.forced.mm_m1p1.mean",
            "pct",
        ),
        ("Not precisely dated (8-K, news report or leaving office)", RS, "rob.undated.forced.mm_m1p1.mean", "pct"),
        ("Dated by an 8-K only", RS, "rob.datesrc_8k.mm_m1p1.mean", "pct"),
        ("Every firing, any date, wider window", RF, "dsel.window.all.mm_m5p5.mean", "pct"),
        ("Not precisely dated, wider window", RF, "dsel.window.undated.mm_m5p5.mean", "pct"),
        ("Well-dated, wider window", RF, "dsel.window.dated.mm_m5p5.mean", "pct"),
        ("All dates: sex or relationship minus fraud", RS, "rob.all_dates.sex_vs_fraud.mm_m1p1.diff_mean", "pp"),
        (
            "All dates: personal scandal minus other firings",
            RS,
            "rob.all_dates.conduct_vs_performance.mm_m1p1.diff_mean",
            "pp",
        ),
        ("All dates: founder minus hired CEO", RS, "rob.all_dates.founder_vs_nonfounder.mm_m1p1.diff_mean", "pp"),
        ("Excluding firings coded as leaving for a new job", RS, "rob.forced_excl_newopp.mm_m1p1.mean", "pct"),
        ("Return minus the market, 36 months, every delisting return 0", RS, "rob.bhar_dl0.forced.3y.median", "pct"),
        (
            "Return minus the market, 36 months, non-takeover delistings -100%",
            RS,
            "rob.bhar_dlworst.forced.3y.median",
            "pct",
        ),
        (
            "Pre-1998: 3-year return minus reported index, firings minus retirements",
            PS,
            "pre.forced_vs_retired.abn_tsr_3y.diff_median",
            "pp",
        ),
    ]
    # Three panels, each row one change against the main tables; rows on fewer than 15 firings are left out (review r1)
    panels = {
        "Panel A. The announcement return": (
            "rob.forced.ma_m1p1.mean",
            "rob.forced_plus_pushed.mm_m1p1.mean",
            "rob.forced_excl_crisis.mm_m1p1.mean",
            "rob.forced_excl_newopp.mm_m1p1.mean",
            "rob.undated.forced.mm_m1p1.mean",
            "rob.datesrc_8k.mm_m1p1.mean",
            "dsel.window.dated.mm_m5p5.mean",
            "dsel.window.all.mm_m5p5.mean",
            "dsel.window.undated.mm_m5p5.mean",
        ),
        "Panel B. Gaps between groups at the announcement": (
            "regc.car_m1p1.founder_v0",
            "regc.car_m1p1.conduct",
            "rob.founder_vs_nonfounder_ff5.m1p1.diff_mean",
            "rob.conduct_vs_performance_ff5.m1p1.diff_mean",
            "cardiff.forced_strict_founder_vs_forced_strict_nonfounder.mm_m1p1.diff_mean",
            "rob.all_dates.sex_vs_fraud.mm_m1p1.diff_mean",
            "rob.all_dates.conduct_vs_performance.mm_m1p1.diff_mean",
            "rob.all_dates.founder_vs_nonfounder.mm_m1p1.diff_mean",
        ),
        "Panel C. The long run": (
            "rob.mbhar_strict_matches.3y.median",
            "bhar.forced_strict.3y.median",
            "strict.mbhar.yes.3y.median",
            "rob.bhar_dl0.forced.3y.median",
            "rob.bhar_dlworst.forced.3y.median",
            "pre.forced_vs_retired.abn_tsr_3y.diff_median",
        ),
    }
    by_key = {k: (name, f, k, u) for name, f, k, u in specs}
    rows = []
    for head, keys in panels.items():
        rows.append([head, "", "", "", ""])
        for key in keys:
            name, f, k, u = by_key[key]
            rows.append(
                [
                    name,
                    v(f, k, u).replace(" percentage points", " pp"),
                    pv(f, k),
                    nv(f, k),
                    horizon(k).split(" after")[0].split(" around")[0],
                ]
            )
    specs = [s for s in specs if s[2] != "rob.pushed.mm_m1p1.mean"]
    stats = (
        [stat(f, k, name, u, "as in the main tables", "robustness") for name, f, k, u in specs]
        + many(
            RS,
            [
                ("rob.n_pushed_retirements", "Retirements the evidence reads as pushed", "count", "count"),
                ("car.forced_strict.mm_m1p1.mean", "Mean CAR[-1,+1], fired, evidence agrees", "pct", "one-sample t"),
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
    # 95% intervals for the tests the paper reads as nulls (review r1, items 5 and R3), from each estimate and its test
    # statistic (t where reported, else the z implied by the two-sided p): the reader sees what the data rule out.
    for f, k, label, unit in (
        (
            RS,
            "cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean",
            "founder minus hired CEO, CAR[-1,+1]",
            "pp",
        ),
        (
            RS,
            "cardiff.conduct_vs_performance.mm_m1p1.diff_mean",
            "personal scandal minus other firings, CAR[-1,+1]",
            "pp",
        ),
        (
            RS,
            "exitdiff.conduct_vs_performance.delisted_5y",
            "personal scandal minus other firings, delisted in 60 months",
            "pp",
        ),
        (
            RS,
            "exitdiff.forced_founder_vs_forced_nonfounder.delisted_5y",
            "founder minus hired CEO, delisted in 60 months",
            "pp",
        ),
        (AS, "alpha.forced.ew.36m", "36-month calendar-time alpha, firings, equal-weighted", "pct2"),
    ):
        extra += ci_stats(f, k, label, unit)
    dsel_rows, dsel_ids = [], []
    for lbl, key, unit in (
        ("Market value, USD billion, median", "mcap_m1", "bn"),
        ("Return over the prior year, median", "prior_ret_12m_w", "pct"),
        ("Return on assets, year -1, median", "roa_m1", "pct"),
        ("Liabilities over assets, median", "leverage_w", "pct"),
        ("Founder fired, share", "founder", "pct"),
        ("Fired over a personal scandal, share", "conduct", "pct"),
        ("Evidence-based coding agrees it was forced, share", "strict", "pct"),
        ("Delisted within 60 months, share", "gone", "pct"),
        ("Year of the announcement, median", "year", "year"),
    ):
        a_, b_ = f"dsel.{key}.dated", f"dsel.{key}.undated"
        dsel_rows.append(
            [lbl, v(RF, a_, unit), v(RF, b_, unit), pv(RF, a_) if key != "year" else "", nv(RF, a_), nv(RF, b_)]
        )
        dsel_ids += [a_, b_]
        extra += [
            stat(RF, a_, f"{lbl}, well-dated firings", unit, "Mann-Whitney U or chi-square", "dating"),
            stat(RF, b_, f"{lbl}, other firings", unit, "Mann-Whitney U or chi-square", "dating"),
        ]
    extra += many(
        RF,
        [
            ("dsel.n_dated", "Well-dated firings", "count", "count"),
            *[
                (f"code.{c}.{x}", f"{lbl}: {xl}", unit, "count")
                for c, lbl in (
                    ("founder", "Founder codes"),
                    ("fraud", "Fraud and legal-violation codes"),
                    ("sex", "Sex and relationship codes"),
                    ("personal", "Other personal-conduct codes"),
                )
                for x, xl, unit in (
                    ("n_reviewed", "checked by hand", "count"),
                    ("n_kept", "model code kept", "count"),
                    ("n_changed", "model code changed", "count"),
                    ("share_kept", "share of model codes kept", "pct"),
                )
            ],
            ("dsel.n_undated", "Firings dated only by a filing or by the day the CEO left office", "count", "count"),
            ("dsel.logit.pseudo_r2", "Pseudo R-squared of the logit of being well dated", "coef", "logit"),
            (
                "strict.mbhar.yes.5y.median",
                "Median 60-month return minus a matched firm, fired, evidence agrees",
                "pct",
                "Wilcoxon",
            ),
            (
                "strict.mbhar.yes.1y.median",
                "Median 12-month return minus a matched firm, fired, evidence agrees",
                "pct",
                "Wilcoxon",
            ),
        ],
        "dating",
    )
    stats = stats + extra
    return section(
        "H",
        "Robustness",
        "Do the results survive other models, samples and definitions?",
        f"With five factors plus momentum the founder gap is {v(RS, 'rob.founder_vs_nonfounder_ff5.m1p1.diff_mean', 'pp')} (p {pv(RS, 'rob.founder_vs_nonfounder_ff5.m1p1.diff_mean')}) "
        f"and the personal-scandal gap {v(RS, 'rob.conduct_vs_performance_ff5.m1p1.diff_mean', 'pp')} (p {pv(RS, 'rob.conduct_vs_performance_ff5.m1p1.diff_mean')}). "
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
                "Table IA.4. Robustness",
                ["Specification", "Estimate", "p", "N", "Horizon"],
                rows,
                [k for _, _, k, _ in specs],
                "Each row changes one thing against the main tables. Evidence agrees: the CEO dismissal database codes the exit forced and the evidence-based coding "
                "(8-K, press releases, Wikipedia, New York Times) also reads it as forced. Pushed retirements: the database codes a retirement and the evidence reads it as forced. "
                "Pre-1998: departures announced 1992 to 1997, three-year return minus the index the firm itself reports in its proxy performance graph.",
            ),
            table(
                "Table IA.5. Well-dated and other firings",
                ["Characteristic", "Well-dated", "Other firings", "p", "N, well-dated", "N, other"],
                dsel_rows,
                dsel_ids,
                "Firings at S&P 1500 firms, 1998 to 2023, fraud and legal violations excluded. Well-dated: the announcement date comes from the "
                "database or a hand check of a dated source; the other firings are dated only by an 8-K or the day the CEO left office. Medians "
                "use a Mann-Whitney test and shares a chi-square test. Founder and scandal firings were dated by hand, so more of them are "
                "well-dated. Table 2's reweighted return weights each well-dated firing by the inverse of its chance of being well-dated, from a "
                "logit on these traits and the year.",
            ),
            table(
                "Table IA.1. From the database to the main sample",
                ["Step", "N"],
                flow_rows,
                [k for _, k in flow] + code_ids,
                "Firings are database codes 3 and 4; firings over fraud or other legal violation leave the sample after the hand review of their codes. A price history covers the announcement when the security trades from 60 days before day 0. Founder codes "
                "come from the evidence-based model coding; every one on a firing was checked by hand, which also added founders the model had left unclear. "
                "Panel B: one coder; a code not kept was changed to another reason or to not a founder.",
            ),
            table(
                "Table IA.3. The founder gap in every window",
                [
                    "Window (trading days)",
                    "Founder fired",
                    "Hired CEO fired",
                    "Gap, pp",
                    "p",
                    "Detectable gap, pp",
                    "N founders",
                ],
                win_rows,
                [f"cardiff.forced_founder_vs_forced_nonfounder.mm_{w}.diff_mean" for _, w in windows],
                "Mean market-model abnormal returns of fired founders and fired hired CEOs over each window, the gap with its Welch p, and the smallest gap the test "
                "would detect with 80% power at the 5% level. The paper's main window is days -1 to +1.",
            ),
            table(
                "Table IA.10. Delisting within 60 months, with controls and against matched firms",
                ["Outcome", "Firings", "Retirements", "Firing effect with controls, pp", "p", "N"],
                exit_rows,
                [f"reg.exit5.{y}.forced" for y in ("gone", "acquired", "bankrupt")],
                "Firing effect with controls: the coefficient on the firing dummy in a linear probability model with log market value, return on assets (ROA) in "
                "fiscal year -1, event-year and Fama-French industry effects, standard errors clustered by year. The matched row compares each firing firm "
                "with its own matched firm (paired t). The rows marked same controls add the prior 12-month return, leverage, book-to-market, an Altman Z "
                "distress flag and a loss flag, on the firms with every item; the founder and personal-scandal rows estimate that model within firings. "
                "Evidence agreeing or unclear: firings as the evidence-based coding reads them, against retirements. Hazard ratios: Cox model, "
                "every month of follow-up to 60 months, industry strata; above one, firing firms leave sooner.",
            ),
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
    for k in ("a.n_sex_or_relationship", "a.n_forced_strict"):
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
            {"name": "nvda_intraday_low_pct", "value": 14, "source": "CNBC, 12 November 2026 (cnbc2026nvidia)"},
            # Published benchmarks, each read in full (literature/LITERATURE_NOTES.md)
            {
                "name": "lit_cline_car_pct",
                "value": 1.79,
                "source": "cline2018: three-day CAR after executive indiscretions",
            },
            {
                "name": "lit_metoo_car_pct",
                "value": 1.5,
                "source": "borellikjaer2021: two-day abnormal return after sexual-harassment scandals",
            },
            {
                "name": "lit_death_founder_pct",
                "value": 1.03,
                "source": "jenter2023: average CAR after a founder-CEO's sudden death",
            },
            {
                "name": "lit_death_other_pct",
                "value": 1.01,
                "source": "jenter2023: average CAR after a non-founder CEO's sudden death",
            },
            {
                "name": "lit_chen_strong_pct",
                "value": 3.4,
                "source": "chen2026: dismissal CAR when directors' interlock benchmarking is strong",
            },
            {"name": "lit_chen_weak_pct", "value": 1.0, "source": "chen2026: dismissal CAR when it is weak"},
            {
                "name": "lit_karpoff_multiple",
                "value": 7.5,
                "source": "karpoff2008jfqa: reputational penalty as a multiple of legal penalties",
            },
            {
                "name": "lit_gentry_agreement_pct",
                "value": 87,
                "source": "gentry2021: share of events an independent recoding matched",
            },
            {"name": "pre_window_start", "value": -30, "source": "paths.py"},
            {"name": "post_window_end", "value": 60, "source": "paths.py"},
            {
                "name": "lit_cline_ceo_pct",
                "value": 3.84,
                "source": "cline2018 Table 5: CAR(-1,+1) when the CEO is the offender",
            },
            {
                "name": "lit_larcker_reveal_pct",
                "value": 3.1,
                "source": "larcker2016: three-day reaction to the first report of CEO misbehaviour",
            },
            {
                "name": "lit_larcker_fire_pct",
                "value": 0.8,
                "source": "larcker2016: mean reaction to the termination itself",
            },
            {
                "name": "redate_agree_3d_pct",
                "value": 58,
                "source": "redate.py validation: 8-K date within 3 days of the database date",
            },
            {
                "name": "redate_agree_10d_pct",
                "value": 73,
                "source": "redate.py validation: 8-K date within 10 days of the database date",
            },
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
