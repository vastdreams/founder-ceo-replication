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
import sys as _sys  # noqa: E402

_sys.path.insert(0, str(HERE))
import constants  # noqa: E402  (analysis/constants.py: every printed constant with its source)
import provenance  # noqa: E402  (analysis/provenance.py: where each statistic comes from)

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
    "founder_reason_stats.json",
    "founder_value_stats.json",
    "founder_appendix_stats.json",
    "screen_stats.json",
    "founder_value_versions.json",
    "founder_growth_stats.json",
    "founder_alpha_stats.json",
)
# H1 under each correction (D-37, D-38): one file per run of founder_value.py, merged into founder_value_versions.json
# with keys h1v.<version>.<key>, the competitor of that version renamed "pr".
H1_VERSIONS = (
    ("d34", "founder_value_stats_d34.json", "pr", "Broad industry match, uncorrected codes"),
    ("unc", "founder_value_stats_uncorrected_newmatch.json", "pr", "Uncorrected codes, closest competitor"),
    ("d37old", "founder_value_stats_d37.json", "pr34", "Founder corrections, broad industry match"),
    ("d37", "founder_value_stats_d37.json", "pr", "Founder corrections, closest competitor"),
    ("d38", "founder_value_stats.json", "pr", "All corrections, closest competitor"),
    ("scr", "founder_value_stats_screen.json", "pr", "All corrections, with the succession screen"),
)


def build_versions():
    out = {}
    for ver, name, bench, _ in H1_VERSIONS:
        f = OUT / name
        if not f.exists():
            continue
        src = json.loads(f.read_text())
        for k, r in src.items():
            if k.startswith("_") or not isinstance(r, dict):
                continue
            if f".{bench}." not in k and not k.startswith(("fvinv.", "fv.founder.n", "fv.hired.n")):
                continue
            kk = k.replace(f".{bench}.", ".pr.") if bench != "pr" else k
            if bench != "pr" and k.startswith("fvinv."):
                kk = (
                    kk.replace(".firm34.", ".firm.")
                    .replace(".pr34.", ".pr.")
                    .replace("firm_minus_pr34", "firm_minus_pr")
                )
                if ".firm." in k or ".sp." in k or "firm_minus_pr." in k or "firm_minus_sp" in k:
                    continue  # those belong to the version's own competitor sample
            out[f"h1v.{ver}.{kk}"] = r
    (OUT / "founder_value_versions.json").write_text(json.dumps(out, indent=1))


build_versions()
SRC = {k: (json.loads((OUT / k).read_text()) if (OUT / k).exists() else {}) for k in FILES}
RS, OS, BS, CS, PS, DS, AS, SS, RF, FR, FV, FA, SC, VV, FG, FW = FILES
D44 = "d44_stats.json"  # D-44 before/after (d44_compare.py)
D44_ALPHA_ROWS = (
    ("Six-factor alpha a month, held 12 months from day +1", "fwdalpha.founder.d1.ew.ff6.12m", "pct2"),
    ("Six-factor alpha a month, held 36 months from day +1", "fwdalpha.founder.d1.ew.ff6.36m", "pct2"),
    ("Against the S&P 500 from day +1, 12 months, median", "fwd.founder.d1.sp.m12.gap.median", "pct"),
    ("Against the S&P 500 from day +1, 36 months, median", "fwd.founder.d1.sp.m36.gap.median", "pct"),
)
SRC[D44] = json.loads((OUT / D44).read_text()) if (OUT / D44).exists() else {}
FM = "founder_missed_stats.json"  # review fix: founders among dismissals coded as hired CEOs (founder_missed_check.py)
SRC[FM] = json.loads((OUT / FM).read_text()) if (OUT / FM).exists() else {}
# D-46: announcement day against the long horizon (founder_timing.py); stored as {"source", "statistics"}
FT = "founder_timing_stats.json"
_ft = json.loads((OUT / FT).read_text()) if (OUT / FT).exists() else {}
SRC[FT] = dict(_ft.get("statistics", _ft))
for _k, _r in list(SRC[FT].items()):
    if not isinstance(_r, dict):
        continue
    if _r.get("p_holm") is not None:  # Holm-adjusted p as its own statistic, so the text can cite it
        SRC[FT][_k + ".holm"] = {"value": _r["p_holm"], "n": _r.get("n")}
    if _r.get("mde") is not None:  # minimum detectable effect, 2.8 standard errors (80% power, 5% two-sided)
        SRC[FT][_k + ".mde"] = {"value": _r["mde"], "n": _r.get("n")}
    if ".ctime." in _k and _r.get("value") is not None:
        h = int(_k.split(".")[3])
        SRC[FT][_k + ".total"] = {"value": _r["value"] * h, "n": _r.get("n")}  # daily alpha times days held
        SRC[FT][_k + ".firms"] = {"value": _r.get("firms_avg"), "n": _r.get("n")}
for _k, _r in list(SRC[FW].items()):  # D-43 calendar-time alphas: Holm p as its own statistic
    if isinstance(_r, dict) and _k.startswith("fwdalpha.") and _r.get("p_holm") is not None:
        SRC[FW][_k + ".holm"] = {"value": _r["p_holm"], "n": _r.get("n")}


class _Tracked(dict):
    """A results file that records every key read, so each table cell can be traced to the statistic behind it."""

    log = []

    def __init__(self, name, d):
        super().__init__(d)
        self.name = name

    def get(self, k, default=None):
        if dict.__contains__(self, k):
            _Tracked.log.append((self.name, k))
        return dict.get(self, k, default)

    def __getitem__(self, k):
        if dict.__contains__(self, k):
            _Tracked.log.append((self.name, k))
        return dict.__getitem__(self, k)


for _f in list(SRC):
    SRC[_f] = _Tracked(_f, SRC[_f])

TITLE = "Sacked: Sex, Fraud, and the Fate of Firms That Fire Their Founder CEO"
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
    "forced_founder": "Forced exits of founder-CEOs (checked against the sources)",
    "forced_nonfounder": "Forced exits of CEOs who did not found the firm",
    "conduct": "Firings over a personal scandal: sex, a relationship or other personal conduct (checked against the sources)",
    "performance": "Firings for every reason but a personal scandal or fraud: performance, strategy, power, activists, restructuring",
    "criminal": "Firings over fraud or other legal violation (comparison; not in the main sample)",
    "relationship": "Forced exits after a relationship with an employee (checked against the sources)",
    "sex_or_relationship": "Forced exits after sexual misconduct or a relationship with an employee (checked against the sources)",
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
    "founder": "Fired founders (checked against the sources)",
    "hired": "Fired CEOs who did not found the firm",
}
BASE_POP = "S&P 1500 firms, announcements 1998-2023"


TM_WIN = {
    "runup": "trading days -30 to -2 before the announcement",
    "gap": "overnight, from the close before the first tradeable day to its open",
    "day": "the first tradeable day, open to close",
    "t0": "the first tradeable day, close to close",
    "t0cc": "the first tradeable day, close to close",
    "t1": "the trading day after the first tradeable day",
    "p2_5": "trading days +2 to +5 after the first tradeable day",
    "p6_20": "trading days +6 to +20 after the first tradeable day",
    "p21_60": "trading days +21 to +60 after the first tradeable day",
    "p6m": "126 trading days (six months) from the close of the first tradeable day",
    "day0_1": "trading days -1 to +1 around the announcement",
}
TM_GROUP = {
    "founder": "Founders dismissed for any reason but fraud or other legal violation, well-dated",
    "forced": "CEOs dismissed for any reason but fraud or other legal violation, well-dated",
}


def tm_horizon(k: str) -> str:
    """Pure: the window of a D-46 statistic. The first tradeable day is day 0 for releases before the close, day +1 after."""
    parts = k.split(".")
    if parts[2] in ("n", "cls"):
        return "Sample definition: well-dated dismissals, release time from the 8-K acceptance time"
    if parts[2] == "minute":
        m = parts[3]
        return "the first tradeable day, from the first trade after the release to " + (
            "the close" if m == "close" else f"{m.lstrip('m')} minutes later"
        )
    if parts[2] == "ctime":
        return f"calendar time, each firm held {parts[3]} trading days from the close of the first tradeable day"
    if parts[2] == "rule":
        return f"short the firm and hold the S&P 500 from the {parts[4]} of the first tradeable day for {parts[5]} trading days"
    if parts[2] == "bycls":
        return TM_WIN.get(parts[4], parts[4])
    return TM_WIN.get(parts[2], parts[2])


def tm_population(k: str) -> str:
    parts = k.split(".")
    who = TM_GROUP.get(parts[1], parts[1])
    if parts[2] == "bycls":
        who += f", release {parts[3].replace('_', ' ')}"
    if parts[2] == "rule":
        who += ", release time known" if parts[3] == "known" else ", every release class"
    return f"{who}; {BASE_POP}"


TABLE_HORIZON = {}  # keys first registered because a table cell reads them: the table states their window


def horizon(key: str) -> str:
    """Pure: how long after (or around) the announcement the statistic is measured, read from its key."""
    k = key
    if k.startswith("tm."):
        return tm_horizon(k)
    if k.startswith("fmiss."):
        return "Sample definition: CEO departures announced 1998 to 2023"
    if k.startswith("d44."):  # D-44 before/after: the horizon of the underlying statistic
        return horizon(k.split(".", 2)[2])
    if k.startswith("h1v."):
        return fv_horizon(k.split(".", 2)[2])
    if k.startswith(FG_PREFIXES):
        return fg_horizon(k)
    if k.startswith(FWD_PREFIXES):
        return fwd_horizon(k)
    if k.startswith(("fa.", "screen.")):
        if ".outcome." in k:
            return "36 months (756 trading days) from day +2 after the announcement, or delisting within 60 months"
        if ".fate." in k:
            return "From the announcement to five years after"
        return "Sample definition: CEO departures announced 1998 to 2023"
    if k.startswith(FV_PREFIXES):
        return fv_horizon(k)
    if k.startswith("frmix.") or (k.startswith("fr.") and k.endswith((".n_all", ".n_dated"))):
        return "Sample definition: CEO departures announced 1998 to 2023"
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
    if key in TABLE_HORIZON:
        return TABLE_HORIZON[key]
    raise ValueError(f"no horizon for {key}")


# Founders and hired CEOs by why the board acted (founder_reason.py, D-29)
FR_WHY = {
    "fraud": "fired over fraud or other legal violation (comparison; not in the main sample)",
    "event": "fired over an event: a personal scandal or a boardroom coup",
    "scandal": "fired over a personal scandal",
    "coup": "fired in a boardroom coup (a strategy or power dispute)",
    "other": "fired over performance or another reason (not fraud, a personal scandal or a coup)",
    "main": "fired for any reason but fraud or other legal violation (the main sample)",
    "all": "fired for any reason, fraud included",
}
FR_WHO = {"founder": "Founders", "hired": "Hired CEOs"}


def fr_population(key: str) -> str:
    parts = key.split(".")
    if parts[0] == "frcase":
        return f"One named firing (event {parts[1]}); {BASE_POP}"
    if parts[1] == "partition":
        return f"Every firing, founders and hired CEOs by fraud, event and performance or other; {BASE_POP}"
    if parts[1] == "interaction":
        return f"Fraud against event firings, founders against hired CEOs; {BASE_POP}"
    if parts[1] in FR_WHO:  # frdiff.founder.fraud_vs_event...
        a, b = parts[2].split("_vs_")
        return f"{FR_WHO[parts[1]]} {FR_WHY[a]}, against those {FR_WHY[b]}; {BASE_POP}"
    if parts[1] in FR_WHY:  # frdiff.fraud.founder_vs_hired... , frmix.fraud.founder_vs_hired...
        return f"Founders against hired CEOs, both {FR_WHY[parts[1]]}; {BASE_POP}"
    who, why = parts[1].split("_", 1)
    if parts[0] == "frmix":
        group = "founder" if who == "founder" else "hired CEO"
        return f"{FR_WHO[who]} {FR_WHY[why]}, as a share of every {group} fired; {BASE_POP}"
    return f"{FR_WHO[who]} {FR_WHY[why]}; {BASE_POP}"


def population(key: str) -> str:
    parts = key.split(".")
    if key.startswith("tm."):
        return tm_population(key)
    if key.startswith("fmiss."):
        return f"CEOs dismissed for any reason but fraud whose founder code is not yes; {BASE_POP}"
    if key.startswith(FG_PREFIXES):
        return fg_population(key)
    if key.startswith(FWD_PREFIXES):
        return fwd_population(key)
    if key.startswith("h1v."):
        label = next(lbl for ver, _, _, lbl in H1_VERSIONS if ver == parts[1])
        return f"{label}: " + fv_population(key.split(".", 2)[2])
    if key.startswith("fa.audit.hired"):
        return f"Hired CEOs fired, a random sample of 60 checked case by case; {BASE_POP}"
    if key.startswith("fa."):
        return (
            f"Founders fired, after the corrections from the case checks (every founder departure checked); {BASE_POP}"
        )
    if key.startswith("screen."):
        return f"Departures checked against the sources (103 founder, 60 hired), and every firing for the counts; {BASE_POP}"
    if key.startswith(FV_PREFIXES):
        return fv_population(key)
    if parts[0] in ("fr", "frdiff", "frmix", "frcase"):
        return fr_population(key)
    g = parts[1] if len(parts) > 1 else ""
    if (
        parts[0] in ("strict", "cox", "code", "dsel", "fraud")
        and g in ("exit", "mbhar", "reg", "gone", "bankrupt", "ipw", "same_sample", "all_firings")
        or parts[0] in ("cox", "code", "dsel")
    ):
        return {
            "strict": "Firings by how the evidence-based coding reads them (forced, unclear), against retirements",
            "cox": "CEO firings against voluntary retirements, every month of follow-up to 60 months",
            "code": "Model codes checked against the sources: founders, fraud, sex or relationship, other personal conduct",
            "dsel": "CEO firings: well-dated (database or a dated source) against dated only by a filing or the day the CEO left",
            "fraud": "Every firing, those over fraud or other legal violation included, against retirements",
        }[parts[0]] + f"; {BASE_POP}"
    if "_vs_" in g:
        a, b = g.split("_vs_")
        return f"{POP.get(a, GROUP_NAMES.get(a, a))} against {POP.get(b, GROUP_NAMES.get(b, b)).lower()}; {BASE_POP}"
    if g == "reason" and len(parts) > 2:
        return f"Forced exits whose coded primary reason is '{parts[2].replace('_', ' ')}'; {BASE_POP}"
    return f"{POP.get(g, 'CEO departures')}; {BASE_POP}"


def basket(key: str) -> str:
    """Pure: what the statistic measures, for the claim-scope gate (backend/services/gates/claim_scope.py)."""
    if key.startswith("tm.") and ".ctime." in key:
        return "daily portfolio returns net of the market or of the Fama-French five factors and momentum"
    if key.startswith("tm."):
        return "stock returns minus the S&P 500 or the industry"
    if key.startswith("fwdalpha."):
        return "monthly portfolio returns net of the market or of the Fama-French five factors and momentum"
    if key.startswith(("fwd.", "fwdcase.")):
        return "stock returns"
    if key.startswith(FG_PREFIXES):
        if ".shr." in key:
            return "stock returns"
        if key.startswith("fgatt."):
            return "whether the stock still trades, and how it left the market"
        if key.endswith((".n_all", ".n_base")):
            return "CEO departures and their coding"
        return "as-reported annual financial statements"
    if key.startswith(("fa.", "screen.")) and ".outcome." not in key:
        return "CEO departures and their coding"
    if key.startswith(("fvbal.", "fvbal3.")) and (".mcap." in key or ".roa." in key):
        return "as-reported annual financial statements"
    if key.startswith("fv.") and key.endswith((".n_all", ".n_matched", ".n_mv")):
        return "CEO departures and their coding"
    if key.startswith("frmix.") or (key.startswith("fr.") and key.endswith((".n_all", ".n_dated", ".n5"))):
        return "CEO departures and their coding"
    if key.startswith(("fr.", "frdiff.")) and ("delisted_5y" in key or "bankruptcy_5y" in key):
        return "whether the stock still trades, and how it left the market"
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
        return "0.0 percentage points" if abs(v) < 0.0005 else f"{v * 100:.1f} percentage points"  # never "-0.0"
    if unit == "pps":
        return "0.0" if abs(v) < 0.0005 else f"{v * 100:.1f}"
    if unit == "count":
        return f"{int(round(v)):,}"
    if unit == "bn":
        return f"{v:.1f}"
    if unit == "year":
        return f"{int(round(v))}"
    if unit == "idx":  # an index with its base year at 100
        return f"{v:.1f}"
    if unit == "p3":
        return "<0.001" if v < 0.001 else f"{v:.3f}"
    if unit == "coef":
        return f"{v:.2f}"
    if unit in ("usdm", "usdbn"):  # dollars of 2023: "-$42 million", "$466 billion"
        word = "million" if unit == "usdm" else "billion"
        digits = 1 if (unit == "usdbn" and abs(v) < 100) else 0
        body = f"{abs(v):,.{digits}f}"
        return f"{'-' if v < 0 and float(body.replace(',', '')) else ''}${body} {word}"
    if unit == "bpd":  # a daily alpha in basis points
        return f"{v * 10000:.1f} basis points a day"
    if unit == "usd2":  # the value of $100 invested
        return f"${v:,.2f}"
    if unit == "usdgap":
        return f"{'-' if v < 0 else ''}${abs(v):,.2f}"
    if unit == "usdm_cell":
        return "0" if abs(v) < 0.5 else f"{v:,.0f}"
    if unit == "usdbn_cell":
        return "0.0" if abs(v) < 0.05 else f"{v:,.1f}"
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
            "usdm": "USD million (2023 dollars)",
            "usdbn": "USD billion (2023 dollars)",
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
    return provenance.attach(s, file, key, unit, test)


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


# D-43: what an investor earns after the firing is public (founder_alpha.py)
# FW (founder_alpha_stats.json) is unpacked from FILES above
FWD_PREFIXES = ("fwd.", "fwdalpha.", "fwdcase.")
FWD_ENTRY = {
    "d1": "from the close of trading day +1 after the announcement (well-dated firings)",
    "d0": "from the close of the announcement day (well-dated firings)",
    "lco": "from the close of the trading day after the CEO left office (every firing)",
}
FWD_GROUP = {
    "founder": "Founders fired for any reason but fraud or other legal violation",
    "forced": "CEOs fired for any reason but fraud or other legal violation",
    "retired": "CEOs who retired voluntarily",
}
FWD_BENCH = {"sp": "the S&P 500 total return", "ind": "the industry average", "pr3": "the three closest competitors"}


def fwd_horizon(k: str) -> str:
    parts = k.split(".")
    if parts[0] == "fwdalpha":
        h = parts[-1].rstrip("m")
        return (
            f"Calendar months 1 to {h} after the month of entry ({FWD_ENTRY[parts[2]]}), portfolios formed each month"
        )
    if parts[0] == "fwdcase":
        return f"12 months (252 trading days) {FWD_ENTRY['d1']}, or {FWD_ENTRY['lco']} where the date is not precise"
    m = int(parts[4].lstrip("m"))
    return f"{m} month{'s' if m > 1 else ''} ({21 * m:,} trading days) {FWD_ENTRY[parts[2]]}"


def fwd_population(k: str) -> str:
    parts = k.split(".")
    if parts[0] == "fwdcase":
        return f"One named founder firing (event {parts[1]}); {BASE_POP}"
    what = f"{FWD_GROUP[parts[1]]}, against " + (
        "the market and the Fama-French factors" if parts[0] == "fwdalpha" else FWD_BENCH[parts[3]]
    )
    return f"{what}; {BASE_POP}"


def fwd_exhibit():
    """Statistics for the forward-looking returns (D-43); prose and tables come with the text revision."""
    S = SRC[FW]
    out = []
    for k in sorted(S):
        r = S[k]
        if not isinstance(r, dict) or r.get("value") is None or not r.get("n"):
            continue
        if k.startswith("fwdalpha."):
            unit, test = "pct2", "OLS on monthly factors, Newey-West lag 6; Holm across holding periods"
        elif k.endswith((".inv_firm.mean", ".inv_firm.median", ".inv_bench.mean", ".inv_bench.median")) or ".inv_" in k:
            unit, test = "usd2", "value of $100"
        elif k.endswith(".beat_share"):
            unit, test = "pct", "binomial test of a share of one half"
        elif k.endswith(".gap.mean"):
            unit, test = "pct", "skewness-adjusted t (Lyon, Barber and Tsai 1999); bootstrap interval"
        elif k.endswith(".gap.median"):
            unit, test = "pct", "Wilcoxon signed-rank"
        elif k.endswith(".n"):
            unit, test = "count", "count"
        else:
            continue
        out.append(stat(FW, k, k.replace("_", " "), unit, test, "founder_alpha"))
    return out


def sec_j():
    stats = fwd_exhibit()
    if not stats:
        return None
    return section(
        "J",
        "What an investor earns after the firing",
        "From the moment a founder firing is public, does the firm's stock beat or trail the stock market?",
        f"Bought at the close of the day after the announcement and held 12 months, $100 in the median founder firm is "
        f"worth {v(FW, 'fwd.founder.d1.sp.m12.inv_firm.median', 'usd2')}, against "
        f"{v(FW, 'fwd.founder.d1.sp.m12.inv_bench.median', 'usd2')} in the S&P 500 "
        f"(N = {nv(FW, 'fwd.founder.d1.sp.m12.inv_firm.median')}).",
        {
            "test": "Skewness-adjusted t and bootstrap on buy-and-hold gaps; Wilcoxon; calendar-time CAPM and five-factor plus momentum alphas with Newey-West errors, Holm across holding periods",
            "data": "Sharadar daily prices and corporate actions; SPY dividend-adjusted close; Kenneth French factors",
            "library_call": "analysis/founder_alpha.py",
            "caveat": "Founder firings are few, so the calendar-time portfolio holds few firms in most months; the number held is reported.",
        },
        stats,
        [],
    )


def tm_unit(k: str) -> str:
    if k.endswith((".holm",)):
        return "p3"
    if ".ctime." in k and not k.endswith((".total", ".firms")):
        return "bpd" if not k.endswith(".mde") else "bpd"
    if k.endswith(".firms") or k.endswith(".n") or ".cls." in k:
        return "count"
    if k.endswith(".mde"):
        return "pp"
    return "pct"


def tm_test(k: str) -> str:
    if ".ctime." in k:
        return "daily calendar-time OLS on the market or five factors plus momentum, Newey-West lag 5"
    if k.endswith(".holm"):
        return "Holm adjustment across windows or rules within the group"
    if k.endswith(".median"):
        return "Wilcoxon signed-rank"
    if k.endswith(".mean"):
        return "skewness-adjusted t (Lyon, Barber and Tsai 1999), firm-clustered t"
    return "count or share"


def sec_k():
    """D-46 and D-43: when the market prices the news, and what is left for an investor after it."""
    S = SRC[FT]
    if not S:
        return None
    stats = []
    for k in sorted(S):
        r = S[k]
        if not isinstance(r, dict) or r.get("value") is None or not r.get("n") or k.endswith("share_negative"):
            continue
        stats.append(stat(FT, k, k.replace("_", " "), tm_unit(k), tm_test(k), "founder_timing"))
    for k in sorted(SRC[FM]):
        stats.append(stat(FM, k, k.replace("_", " "), "count", "count", "founder_missed"))
    for k in sorted(SRC[FW]):
        if k.startswith("fwdalpha.") and k.endswith(".holm"):
            stats.append(
                stat(FW, k, k.replace("_", " "), "p3", "Holm adjustment across holding periods", "founder_alpha")
            )

    def cell(g, key, unit="pct"):
        r = S.get(f"tm.{g}.{key}") or {}
        return fmt(r.get("value"), unit) if r.get("value") is not None else "n/a"

    def pcell(g, key, holm=False):
        r = S.get(f"tm.{g}.{key}") or {}
        p_ = r.get("p_holm" if holm else "p")
        return "" if p_ is None else ("<0.001" if p_ < 0.001 else f"{p_:.3f}")

    def ncell(g, key):
        r = S.get(f"tm.{g}.{key}") or {}
        return "" if r.get("n") is None else f"{int(r['n']):,}"

    rows, ids = [], []

    def add(label, key, unit="pct", holm=False):
        rows.append(
            [label]
            + [x for g in ("founder", "forced") for x in (cell(g, key, unit), pcell(g, key, holm), ncell(g, key))]
        )
        ids.extend(f"tm.{g}.{key}" for g in ("founder", "forced") if f"tm.{g}.{key}" in S)

    blank = ["", "", "", "", "", ""]
    rows.append(["Panel A. Return minus the S&P 500, by window"] + blank)
    for lbl, key in (
        ("Run-up, days −30 to −2, mean", "runup.sp.mean"),
        ("Run-up, days −30 to −2, median", "runup.sp.median"),
        ("First tradeable day, overnight gap, mean", "gap.sp.mean"),
        ("First tradeable day, open to close, mean", "day.sp.mean"),
        ("First tradeable day, close to close, mean", "t0.sp.mean"),
        ("First tradeable day, close to close, median", "t0.sp.median"),
        ("Next day, mean", "t1.sp.mean"),
        ("Days +2 to +5, mean", "p2_5.sp.mean"),
        ("Days +2 to +5, median", "p2_5.sp.median"),
        ("Days +6 to +20, mean", "p6_20.sp.mean"),
        ("Days +21 to +60, mean", "p21_60.sp.mean"),
        ("Six months, mean", "p6m.sp.mean"),
        ("Six months, median", "p6m.sp.median"),
    ):
        add(lbl, key)
    rows.append(["Panel B. Release time and the overnight gap"] + blank)
    for lbl, key in (
        ("Released before the open, count", "cls.before_open"),
        ("Released during trading hours, count", "cls.during"),
        ("Released after the close, count", "cls.after_close"),
        ("Release time unknown, count", "cls.unknown"),
    ):
        add(lbl, key, "count")
    for lbl, key in (
        ("Overnight gap, released before the open, mean", "bycls.before_open.gap.sp.mean"),
        ("Overnight gap, released after the close, mean", "bycls.after_close.gap.sp.mean"),
        ("Days +2 to +5, release time unknown, mean", "bycls.unknown.p2_5.sp.mean"),
    ):
        add(lbl, key)
    rows.append(["Panel C. Short the firm, hold the S&P 500, release time known (p Holm-adjusted)"] + blank)
    for lbl, key in (
        ("From the open, 5 days, mean", "rule.known.open.5.mean"),
        ("From the open, 20 days, mean", "rule.known.open.20.mean"),
        ("From the open, 60 days, mean", "rule.known.open.60.mean"),
        ("From the open, 5 days, net of 50 bp", "rule.known.open.5.net50"),
        ("From the close, 5 days, mean", "rule.known.close.5.mean"),
        ("From the close, 126 days, mean", "rule.known.close.126.mean"),
    ):
        add(lbl, key, holm=True)
    rows.append(["Panel D. Calendar-time six-factor alpha, held from the close of the first tradeable day"] + blank)
    for lbl, key in (
        ("Held 5 days, a day", "ctime.5.ff6"),
        ("Held 20 days, a day", "ctime.20.ff6"),
        ("Held 126 days, a day", "ctime.126.ff6"),
    ):
        add(lbl, key, "bpd")
    t33 = table(
        "Table IA.33. When the market prices the news: the first tradeable day against the long horizon",
        ["Window", "Founders", "p", "N", "All dismissals", "p", "N"],
        rows,
        ids,
        "Well-dated dismissals for any reason but fraud. Release time: when the firm's 8-K was accepted by EDGAR, "
        "New York time, the latest the news could have been public. First tradeable day: the announcement day for "
        "releases before the close, else the next day. Returns are the firm's minus the S&P 500's with dividends. "
        "p: skewness-adjusted t (Panels A and B), Holm-adjusted across each group's eight rules (Panel C), Newey-West "
        "(Panel D). Panel C uses only releases with a known time; a positive return is a gain to the short seller, "
        "before borrowing costs. Panel D: daily intercept of an equal-weighted portfolio on five Fama-French factors "
        "and momentum; N counts trading days.",
    )
    return section(
        "K",
        "When the market prices the news",
        "How much of the reaction to a dismissal comes at the first trade, and does anything remain for an investor after it?",
        f"For all dismissals the overnight gap on the first tradeable day is {cell('forced', 'gap.sp.mean')}; "
        f"for founders the five-day short from the open earns {cell('founder', 'rule.known.open.5.mean')} "
        f"(Holm p {pcell('founder', 'rule.known.open.5.mean', True)}).",
        {
            "test": "Skewness-adjusted and firm-clustered t; Wilcoxon; Holm within group; calendar-time alphas with Newey-West errors",
            "data": "Sharadar daily open and close; SPY; EDGAR 8-K acceptance times; Alpha Vantage 1-minute bars; Kenneth French daily factors",
            "library_call": "analysis/founder_timing.py",
            "caveat": "The 8-K acceptance time is an upper bound on the release time; about 40% of dismissals cannot be timed.",
        },
        stats,
        [t33],
    )


UNITS = ("pct", "pp", "pps", "count", "coef", "bn", "usd2", "usdm", "usdbn", "pct2", "p3", "idx", "bpd", "year")


def _variants(r):
    """Every way a table may print a statistic's value, p, N, t or interval end."""
    out = {}
    v = r.get("value")
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        for u in UNITS:
            try:
                x = fmt(v, u)
            except Exception:  # noqa: BLE001
                continue
            for y in (x, x.lstrip("-"), x.replace(" percentage points", ""), x.replace(" basis points a day", "")):
                out.setdefault(y.replace("\u2212", "-"), "value")
    p_ = r.get("p")
    if isinstance(p_, (int, float)):
        out.setdefault("<0.001" if p_ < 0.001 else f"{p_:.3f}", "p")
    n_ = r.get("n")
    if isinstance(n_, (int, float)):
        out.setdefault(f"{int(n_):,}", "n")
        out.setdefault(str(int(n_)), "n")
    for k in ("t", "ci_low", "ci_high"):
        if isinstance(r.get(k), (int, float)):
            for u in ("pct", "pp", "pps", "coef"):
                out.setdefault(fmt(r[k], u).replace("\u2212", "-"), k)
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        if float(v).is_integer() and 1900 <= v <= 2100:
            out.setdefault(str(int(v)), "value")
        for y in (f"{v:,.1f}", f"{v:,.0f}", f"{v:.1f}", f"{v:.2f}", f"{v / 1e9:.1f}", f"{v / 1e6:,.0f}"):
            out.setdefault(y, "value")
    for k, x in r.items():  # any other numeric field (months, firms held) and any text field (dates, quotes)
        if isinstance(x, (int, float)) and not isinstance(x, bool) and k not in ("value", "p", "n", "t"):
            for y in (
                f"{int(x):,}" if float(x).is_integer() else f"{x:.2f}",
                f"{x:.0f}",
                str(int(x)) if float(x).is_integer() else "",
            ):
                if y:
                    out.setdefault(y, k)
        if isinstance(x, str):
            for tok in re.findall(r"\d{4}-\d{2}-\d{2}|\d[\d,.]*%?", x):
                out.setdefault(tok, k)
    return out


def _row_index():
    """Rows that a results file stores ready-made (case tables built by founder_appendix.py and others)."""
    idx = {}

    def walk(f, obj, path):
        if isinstance(obj, dict):
            for k, x in obj.items():
                walk(f, x, f"{path}.{k}" if path else k)
        elif isinstance(obj, list) and obj and all(isinstance(r, (list, tuple)) for r in obj):
            for i, r in enumerate(obj):
                idx.setdefault(tuple(str(c) for c in r), (f, f"{path}[{i}]"))

    for f in SRC:
        walk(f, dict(SRC[f]), "")
    return idx


ROW_INDEX = None
CONST_TOKENS = {str(v).replace("\u2212", "-"): n for n, v, _ in constants.CONSTANTS}


def match_cells(tb, keys):
    """Each numeric token printed in the table, traced to the results file, key and field it came from."""
    pool = {}

    def walk(f, obj, path):  # stored case lists and records: every number or date in them, with its path
        if isinstance(obj, dict) and "value" in obj:
            for s, field in _variants(obj).items():
                pool.setdefault(s, (f, path, field))
        elif isinstance(obj, dict):
            for kk, x in obj.items():
                walk(f, x, f"{path}.{kk}")
        elif isinstance(obj, (list, tuple)):
            for i, x in enumerate(obj):
                walk(f, x, f"{path}[{i}]")
        elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
            for y in (
                (str(obj), f"{obj:,}", f"{obj:.1f}", fmt(obj, "pps"), fmt(obj, "pct"))
                if not float(obj).is_integer()
                else (str(int(obj)), f"{int(obj):,}")
            ):
                pool.setdefault(y, (f, path, "stored"))
        elif isinstance(obj, str):
            for tok in re.findall(r"\d{4}-\d{2}-\d{2}|\d[\d,.]*%?", obj):
                pool.setdefault(tok, (f, path, "stored"))

    for f, k in keys:
        r = SRC[f].get(k) if f in SRC else None
        if r is not None:
            walk(f, r, k)
    global ROW_INDEX
    if ROW_INDEX is None:
        ROW_INDEX = _row_index()
    rows = []
    for row in tb["rows"]:
        whole = ROW_INDEX.get(tuple(str(c) for c in row))
        for ci, c in enumerate(row[1:], 1):
            for tok in re.findall(
                r"\d{4}-\d{2}-\d{2}|[-\u2212]?\$?[\d][\d,.]*%?(?: (?:million|billion))?|<0\.001", str(c)
            ):
                tok = tok.replace("\u2212", "-")
                src = pool.get(tok) or pool.get(tok.lstrip("-"))
                if not src and whole:
                    src = (whole[0], whole[1], "stored row")
                if not src and tok in CONST_TOKENS:
                    src = ("constants.py", CONST_TOKENS[tok], "constant")
                rows.append(
                    {
                        "row": str(row[0])[:80],
                        "col": tb["columns"][ci] if ci < len(tb["columns"]) else ci,
                        "printed": tok,
                        "file": src[0] if src else None,
                        "key": src[1] if src else None,
                        "field": src[2] if src else None,
                    }
                )
    return rows


def section(sid, title, question, interpretation, method, stats, tables=()):
    stats = [s for s in stats if s]
    read = sorted(set(_Tracked.log))
    _Tracked.log.clear()
    for tb in tables:
        tb["cell_keys"] = [list(x) for x in read]
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


# D-42: founders are compared with normal firms only, never with hired CEOs. Rows and statistic ids that set the two
# against each other leave every table; hired-CEO firms stay only inside results on all dismissals.
D42_DROP_ROWS = {
    "Hired CEO fired",
    "Hired CEOs fired",
    "of which hired CEOs",
    "Founder minus hired CEO",
    "Founder minus hired CEO (below zero: larger fall after a founder)",
    "p, founder against hired CEO",
    "Fired hired CEO still a director",
    "Founder minus hired CEO, controlling for size, prior 12-month return and year",
    "Five-factor plus momentum: founder minus hired CEO",
    "Evidence agrees: founder minus hired CEO",
    "All dates: founder minus hired CEO",
}
D42_DROP_IDS = re.compile(
    r"founder_vs_hired|forced_nonfounder|founder_vs_nonfounder|founder_gap|^fv\.hired\.|^fg\.hired\.|^fr\.hired|"
    r"^frmix\.hired|hired_fraud|^fvinv\.hired|^fvprior\.hired|^fvbal\.hired"
)


def table(title, columns, rows, stat_ids, notes):
    rows = [r for r in rows if not (r and str(r[0]).strip() in D42_DROP_ROWS)]
    stat_ids = [s for s in stat_ids if not D42_DROP_IDS.search(s)]
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
            "caveat": "Founder status and reasons are coded from filings, press releases and news, then checked against the sources.",
        },
        stats,
        [
            table(
                "Table 2. Dismissing firms are smaller and less profitable than retirement firms",
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
        f"The model coded {v(CS, 'b.model_founder_codes', 'count')} forced exits as founder removals. A first review confirmed "
        f"{v(CS, 'b.founders_confirmed', 'count')}, rejected {v(CS, 'b.founders_rejected', 'count')} (an error rate of {v(CS, 'b.model_error_rate', 'pct')}) and added "
        f"{v(CS, 'b.founders_added', 'count')}. The reviewed codes are used throughout.",
        {
            "test": "first review",
            "data": "paper/founder_review.csv; paper/conduct_review.csv",
            "library_call": "analysis/code_events.py; analysis/coding_final.py; analysis/founder_final.py",
            "caveat": "Founder means founded or co-founded the firm or its direct predecessor; heirs are excluded.",
        },
        many(
            CS,
            [
                ("b.model_founder_codes", "Forced exits coded founder by the model", "count", "count"),
                ("b.founders_reviewed", "Founder codes reviewed against the sources", "count", "count"),
                ("b.founders_confirmed", "Founders confirmed", "count", "count"),
                ("b.founders_rejected", "Model founder codes rejected", "count", "count"),
                ("b.founders_added", "Founders added where the model was unclear", "count", "count"),
                ("b.model_error_rate", "Model error rate on founder codes", "pct", "share"),
            ],
            "coding",
        ),
    )


FR_ROWS = (
    ("fraud", "Fraud or other legal violation (comparison group)"),
    ("event", "Event: personal scandal or boardroom coup"),
    ("scandal", "of which personal scandal"),
    ("coup", "of which boardroom coup"),
    ("other", "Performance or other"),
    ("main", "All but fraud (the main sample)"),
)
# measure key, suffix of the cell statistic, panel title, label, test of the founder-minus-hired difference
FR_MEASURES = (
    (
        "mm_m1p1",
        ".mean",
        "Panel B. Abnormal return, trading days −1 to +1 (well-dated firings)",
        "mean CAR[-1,+1]",
        "Welch t",
    ),
    (
        "pre_m30m2",
        ".mean",
        "Panel C. Return minus the market, trading days −30 to −2 (well-dated firings)",
        "mean return minus the market, days -30 to -2",
        "Welch t",
    ),
    (
        "delisted_5y",
        "",
        "Panel D. Delisted within 60 months (firings followed for 60 months)",
        "delisted within 60 months",
        "chi-square or Fisher exact",
    ),
    (
        "bankruptcy_5y",
        "",
        "Panel E. Bankrupt within 60 months (firings followed for 60 months)",
        "bankrupt within 60 months",
        "chi-square or Fisher exact",
    ),
)
FR_NOTES = (
    "Founder dismissals only, each in one row by its final reason code: fraud or other legal violation, an event "
    "(a personal scandal or a boardroom coup) or anything else. Fraud dismissals, outside the main sample, are shown for "
    "comparison. The coup rows use the code strategy or power dispute; for founders every such code was checked case by case. "
    "Each N counts the dismissals behind the number to its left. Panel A gives each reason's share of all founder dismissals. "
    "In Panels B to E a dash marks a cell with fewer than 10 dismissals, which gets no mean or share. Panels B and C are "
    "means; Panels D and E are shares of the firms followed for 60 months."
)
FR_FEW = "–"  # a cell under 10 events: N is printed, no mean, share or test


def fr_interval(key):
    lo, hi = SRC[FR].get(key + ".ci_low"), SRC[FR].get(key + ".ci_high")
    return "" if not lo or not hi else f"{fmt(lo['value'], 'pps')} to {fmt(hi['value'], 'pps')}"


def fr_exhibit():
    """Statistics and the body table for founders and hired CEOs by why the board acted (D-29)."""
    stats, rows, ids = [], [], []
    blank = ["", ""]

    def diff_stats(key, label, test):
        out = [stat(FR, key, label, "pp", test, "founder_reason")]
        out += many(
            FR,
            [
                (key + ".ci_low", f"{label}, 95% interval, low end", "pps", "95% interval"),
                (key + ".ci_high", f"{label}, 95% interval, high end", "pp", "95% interval"),
                (key.replace(".diff", ".holm_p"), f"{label}, Holm-adjusted p (fraud, event, other)", "p3", "Holm"),
            ],
            "founder_reason",
        )
        return out

    # Panel A: the mix of reasons
    rows.append(["Panel A. Share of the group's firings (all firings with share prices)"] + blank)
    for why, name in FR_ROWS:
        dk = f"frmix.{why}.founder_vs_hired.share.diff"
        has = dk in SRC[FR]
        rows.append([name, v(FR, f"frmix.founder_{why}.share", "pct"), v(FR, f"fr.founder_{why}.n_all", "count")])
        for who in ("founder", "hired"):
            lbl = f"{FR_WHO[who]} {FR_WHY[why]}"
            stats += many(
                FR,
                [
                    (f"frmix.{who}_{why}.share", f"{lbl}, share of the group's firings", "pct", "proportion"),
                    (f"fr.{who}_{why}.n_all", f"{lbl}, firings with share prices", "count", "count"),
                    (f"fr.{who}_{why}.n_dated", f"{lbl}, well-dated firings", "count", "count"),
                    (f"fr.{who}_{why}.n5", f"{lbl}, firings followed for 60 months", "count", "count"),
                ],
                "founder_reason",
            )
            ids.append(f"frmix.{who}_{why}.share")
        if has:
            stats += diff_stats(dk, f"Share of firings {FR_WHY[why]}, founders minus hired CEOs", "chi-square")
    stats += many(
        FR,
        [
            (f"fr.{who}_all.{k}", f"{FR_WHO[who]} {FR_WHY['all']}, {lbl}", "count", "count")
            for who in FR_WHO
            for k, lbl in (
                ("n_all", "firings with share prices"),
                ("n_dated", "well-dated firings"),
                ("n5", "firings followed for 60 months"),
            )
        ],
        "founder_reason",
    )
    stats += many(
        FR,
        [("frmix.partition.chi2", "Reason mix, founders against hired CEOs, chi-square", "coef", "chi-square")],
        "founder_reason",
    )

    # Panels B to E: one measure each
    for m, suffix, panel, mlabel, test in FR_MEASURES:
        rows.append([panel] + blank)
        for why, name in FR_ROWS:
            cells = []
            for who in ("founder", "hired"):
                k = f"fr.{who}_{why}.{m}"
                n_key = f"{k}.count" if suffix else f"fr.{who}_{why}.n5"
                has = (k + suffix) in SRC[FR]
                cells += [v(FR, k + suffix, "pct") if has else FR_FEW, v(FR, n_key, "count")]
                lbl = f"{FR_WHO[who]} {FR_WHY[why]}, {mlabel}"
                stats += many(
                    FR,
                    [
                        (k + suffix, lbl, "pct", "one-sample t" if suffix else "proportion"),
                        (k + ".count", f"{lbl}, {'firings measured' if suffix else 'firms'}", "count", "count"),
                    ],
                    "founder_reason",
                )
                if has:
                    ids.append(k + suffix)
            dk = f"frdiff.{why}.founder_vs_hired.{m}.diff"
            has = dk in SRC[FR]
            rows.append([name] + cells[:2])
            if has:
                stats += diff_stats(dk, f"Founders minus hired CEOs, both {FR_WHY[why]}, {mlabel}", test)
        for who in ("founder", "hired"):
            for pair in ("fraud_vs_event", "scandal_vs_coup"):
                dk = f"frdiff.{who}.{pair}.{m}.diff"
                if dk in SRC[FR]:
                    a, b = pair.split("_vs_")
                    stats += diff_stats(dk, f"{FR_WHO[who]}: {a} minus {b} firings, {mlabel}", test)
    # the named cases behind the small founder cells
    for k in sorted(SRC[FR]):
        if k.startswith("frcase."):
            what = "CAR[-1,+1]" if k.endswith("car_m1p1") else "return minus the market, days -30 to -2"
            stats.append(stat(FR, k, f"Named founder firing {k.split('.')[1]}, {what}", "pct", "event return", "case"))
    tbl = table(
        "Table 8. Founder dismissals by why the board acted",
        ["Why the board acted", "Founders", "N"],
        rows,
        ids,
        FR_NOTES,
    )
    return [x for x in stats if x], tbl


# The founder CEO in dollars, against competitors that were doing equally badly (founder_value.py, D-34)
FV_PREFIXES = ("fv.", "fvdiff.", "fvreg.", "fvbal.", "fvbal3.", "fvcase.", "fvinv.", "fvinvdiff.", "fvprior.", "fvrob.")
FV_CELL = {
    "founder": "Founders fired for any reason but fraud (the main sample)",
    "hired": "Hired CEOs fired for any reason but fraud (the main sample)",
    "forced": "CEO firings for any reason but fraud or other legal violation (the main sample)",
    "retired": "Voluntary CEO retirements",
    "fraud": "Firings over fraud or other legal violation (comparison; not in the main sample)",
    "founder_fraud": "Founders fired over fraud or other legal violation (comparison; not in the main sample)",
    "hired_fraud": "Hired CEOs fired over fraud or other legal violation (comparison; not in the main sample)",
    "scandal": "Firings over a personal scandal",
    "founder_scandal": "Founders fired over a personal scandal",
    "hired_scandal": "Hired CEOs fired over a personal scandal",
    "coup": "Firings in a boardroom coup (a strategy or power dispute)",
    "founder_coup": "Founders fired in a boardroom coup",
    "hired_coup": "Hired CEOs fired in a boardroom coup",
    "other": "Firings over performance or another reason (not fraud, a personal scandal or a coup)",
    "founder_other": "Founders fired over performance or another reason",
    "hired_other": "Hired CEOs fired over performance or another reason",
}
FV_PAIR = {
    "main.founder_vs_hired": "Fired founders against fired hired CEOs, any reason but fraud (the main sample)",
    "forced_vs_retired": "CEO firings for any reason but fraud, against voluntary retirements",
    "fraud.founder_vs_hired": "Founders against hired CEOs, both fired over fraud or other legal violation",
    "other.founder_vs_hired": "Founders against hired CEOs, both fired over performance or another reason",
    "scandal_vs_fraud": "Firings over a personal scandal against firings over fraud or other legal violation",
    "scandal_vs_other": "Firings over a personal scandal against firings over performance or another reason",
    "coup_vs_other": "Firings in a boardroom coup against firings over performance or another reason",
    "fraud_vs_forced": "Firings over fraud or other legal violation against every other firing",
}
# window key -> (table label, text label, horizon)
FV_WIN = {
    "slide": ("Days −30 to −2", "days -30 to -2", "Trading days -30 to -2 before the announcement (day 0)"),
    "ann": ("Days −1 to +1", "days -1 to +1", "Trading days -1 to +1 around the announcement (day 0)"),
    "slideann": ("Days −30 to +1", "days -30 to +1", "Trading days -30 to +1 around the announcement (day 0)"),
    "m12": ("12 months from day +2", "12 months", "12 months (252 trading days) from day +2 after the announcement"),
    "m36": ("36 months from day +2", "36 months", "36 months (756 trading days) from day +2 after the announcement"),
    "m60": ("60 months from day +2", "60 months", "60 months (1,260 trading days) from day +2 after the announcement"),
    "slide_wd": (
        "Days −30 to −2, well-dated",
        "days -30 to -2, well-dated firings",
        "Trading days -30 to -2 before the announcement (day 0), well-dated firings",
    ),
    "slideann_wd": (
        "Days −30 to +1, well-dated",
        "days -30 to +1, well-dated firings",
        "Trading days -30 to +1 around the announcement (day 0), well-dated firings",
    ),
}
FV_MAIN = ("slide", "ann", "slideann", "m12", "m36", "m60")
FV_BENCH = {
    "pr": "a competitor matched on industry, size and the prior 12-month return",
    "roa": "a competitor matched on industry, size and return on assets",
    "ind": "the mean of the other S&P 1500 firms in the industry",
    "sp": "the S&P 500 total return (SPY)",
    "pr3": "the mean of the three nearest competitors on the prior 12-month return",
    "pr2": "the mean of the two nearest competitors on the prior 12-month return",
    "pr4": "the mean of the four nearest competitors on the prior 12-month return",
    "pr5": "the mean of the five nearest competitors on the prior 12-month return",
    "firm": "the firm's own return",
}
FV_INV = {
    "d1": ("Day +1", "From trading day -31 to day +1 around the announcement (day 0)"),
    "m12": ("12 months", "From trading day -31 to 12 months (252 trading days) after day +2"),
    "m36": ("36 months", "From trading day -31 to 36 months (756 trading days) after day +2"),
    "m60": ("60 months", "From trading day -31 to 60 months (1,260 trading days) after day +2"),
}
FV_ASSET = {"firm": "the firm", "pr": "its matched competitor", "sp": "the S&P 500"}
FV_FEW = "–"


def fv_window(key: str):
    parts = key.split(".")
    return next((x for x in parts if x in FV_WIN), None)


def fv_horizon(key: str) -> str:
    if key.startswith(("fvinv.", "fvinvdiff.")):
        return FV_INV[next(x for x in key.split(".") if x in FV_INV)][1]
    if key.startswith("fvprior."):
        return "Before the departure: trading days -282 to -31 before the announcement (day 0)"
    w = fv_window(key)
    if w:
        return FV_WIN[w][2]
    if key.startswith(("fvbal.", "fvbal3.")):
        if ".prior12." in key:
            return "Before the departure: trading days -282 to -31 before the announcement (day 0)"
        return "Before the departure: fiscal year -1 (market value at that fiscal year-end)"
    if ".mv31." in key:
        return "Market value 31 trading days before the announcement (day 0), in 2023 dollars"
    return "Sample definition: CEO departures announced 1998 to 2023"


def fv_population(key: str) -> str:
    parts = key.split(".")
    if parts[0] == "fvcase":
        return f"One named firing (event {parts[1]}); {BASE_POP}"
    if parts[0] == "fvinvdiff":
        return f"{FV_PAIR['main.founder_vs_hired']}; {BASE_POP}"
    if parts[0] == "fvdiff":
        label = next((x for x in FV_PAIR if key.startswith(f"fvdiff.{x}.")), None)
        return f"{FV_PAIR[label]}; {BASE_POP}"
    if parts[0] == "fvrob":
        who = {
            "pushed": "Founders the case check found clearly forced out",
            "sic4": "Pairs matched within the same 4-digit SIC code",
        }
        return f"{who.get(parts[1], 'Check added after review')}, against hired CEOs, any reason but fraud; {BASE_POP}"
    if parts[0] == "fvreg":
        who = FV_PAIR["main.founder_vs_hired"] if parts[1] == "founder" else FV_PAIR["forced_vs_retired"]
        return f"{who}, with controls; {BASE_POP}"
    return f"{FV_CELL.get(parts[1], 'CEO departures')}; {BASE_POP}"


def fv_prepare():
    """Derived statistics in the units the paper prints: totals and market values in billions of dollars."""
    src = SRC[FV]
    for k in list(src):
        r = src[k]
        if not isinstance(r, dict) or r.get("value") is None:
            continue
        if k.endswith(".usd.total") or (".mv31." in k):
            src[k + "_bn"] = {**r, "value": r["value"] / 1000.0}
        if k.startswith(("fvbal.", "fvbal3.")) and ".mcap." in k and k.endswith((".mean", ".median")):
            src[k + "_bn"] = {**r, "value": r["value"] / 1e9}


# Long-run growth after the dismissal (founder_growth.py, D-40)
FG_PREFIXES = ("fg.", "fgdiff.", "fgreg.", "fgatt.", "fgpath.")
FG_CELL = {
    "founder": "Founders fired for any reason but fraud (the main sample)",
    "hired": "Hired CEOs fired for any reason but fraud (the main sample)",
    "forced": "CEO firings for any reason but fraud or other legal violation (the main sample)",
    "scandal": "Firings over a personal scandal",
    "nonscandal": "Firings for any reason but a personal scandal or fraud",
    "sexrel": "Firings over sexual misconduct or a relationship",
}
FG_PAIR = {
    "founder_vs_hired": "Fired founders against fired hired CEOs, any reason but fraud (the main sample)",
    "scandal_vs_nonscandal": "Firings over a personal scandal against every other firing but fraud",
}
FG_FLAG = {"founder": "founder_vs_hired", "scandal": "scandal_vs_nonscandal"}
# outcome -> (table label, text label, kind)
FG_OUT = {
    "rev": ("Revenue growth a year", "revenue growth a year", "growth"),
    "rev_att": (
        "Revenue growth a year, failed firms at −100%",
        "revenue growth a year with failed firms at -100%",
        "growth",
    ),
    "assets": ("Asset growth a year", "asset growth a year", "growth"),
    "assets_att": (
        "Asset growth a year, failed firms at −100%",
        "asset growth a year with failed firms at -100%",
        "growth",
    ),
    "mcap": ("Market value growth a year", "market value growth a year", "growth"),
    "mcap_att": (
        "Market value growth a year, failed firms at −100%",
        "market value growth a year with failed firms at -100%",
        "growth",
    ),
    "rnd": ("R&D to sales", "R&D to sales", "ratio"),
    "capex": ("Capital spending to assets", "capital spending to assets", "ratio"),
    "roa": ("Return on assets", "return on assets (EBITDA to assets)", "ratio"),
    "gm": ("Gross margin", "gross profit to sales", "ratio"),
    "shr": ("Share return against the competitor", "buy-and-hold share return minus the competitor's", "return"),
}
FG_MAIN = ("rev", "rnd", "capex", "assets", "roa", "gm", "mcap")
FG_ATT = ("rev_att", "assets_att", "mcap_att")
FG_HOR = {"y3": 3, "y5": 5}
FG_BENCH = {"pr": "its matched competitor", "ind": "the median firm of its industry"}
FG_STATUS = (
    ("filing", "still filing"),
    ("bankrupt", "bankrupt"),
    ("cause", "removed by a regulatory delisting"),
    ("acquired", "taken over"),
    ("other", "delisted for another reason"),
    ("not_reached", "not yet reached by the data"),
    ("no_filing", "without a filing that year"),
    ("pairs", "filing, with a competitor also filing"),
)


def fg_horizon(key: str) -> str:
    parts = key.split(".")
    if ".shr." in key:
        return (
            "36 months (756 trading days) from day +2 after the announcement"
            if "y3" in parts
            else "60 months (1,260 trading days) from day +2 after the announcement"
        )
    yr = next((x for x in parts if re.fullmatch(r"[mp]\d", x)), None)
    if yr:
        k = int(yr[1])
        return (
            f"Fiscal year {'-' if yr[0] == 'm' else '+'}{k} around the dismissal (year 0)"
            if k
            else "The fiscal year of the dismissal (year 0)"
        )
    h = next((x for x in parts if x in FG_HOR), None)
    if h:
        k = FG_HOR[h]
        if key.endswith(".pre.median"):
            return "Before the dismissal: fiscal years -3 to -1 (year 0 is the year of the dismissal)"
        return f"Fiscal year -1 to fiscal year +{k} after the dismissal (year 0), against fiscal years -3 to -1"
    return "Sample definition: CEO departures announced 1998 to 2023"


def fg_population(key: str) -> str:
    parts = key.split(".")
    if parts[0] == "fgdiff":
        return f"{FG_PAIR[parts[1]]}; {BASE_POP}"
    if parts[0] == "fgreg":
        return f"{FG_PAIR[FG_FLAG[parts[1]]]}, with controls; {BASE_POP}"
    return f"{FG_CELL.get(parts[1], 'CEO departures')}; {BASE_POP}"


def growth_exhibit():
    """Statistics and tables for growth after the dismissal (D-40)."""
    S = SRC[FG]
    stats, seen = [], set()

    def add(key, label, unit, test=""):
        if key in seen or key not in S or S[key].get("value") is None or not S[key].get("n"):
            return
        seen.add(key)
        stats.append(stat(FG, key, label, unit, test, "founder_growth"))

    def val(key, unit):
        return v(FG, key, unit) if key in S and S[key].get("value") is not None else FV_FEW

    def p_(key):
        return pv(FG, key) if key in S and S[key].get("p") is not None else FV_FEW

    def n_(key):
        return val(key, "count")

    cells = ("founder", "hired", "scandal", "nonscandal", "forced")
    for c in FG_CELL:
        add(f"fg.{c}.n_all", f"{FG_CELL[c]}, firings with share prices", "count", "count")
        add(f"fg.{c}.n_base", f"{FG_CELL[c]}, firings with revenue in fiscal year -1", "count", "count")
    for c in cells + ("sexrel",):
        for o, (_, name, _kind) in FG_OUT.items():
            for h, k in FG_HOR.items():
                when = "36 months" if (o == "shr" and k == 3) else ("60 months" if o == "shr" else f"to year +{k}")
                for b in ("pr", "ind"):
                    if b == "ind" and (o not in FG_MAIN):
                        continue
                    key = f"fg.{c}.{b}.{o}.{h}"
                    what = f"{FG_CELL[c]}: {name}, {when}"
                    what += "" if o == "shr" else f", change against {FG_BENCH[b]}"
                    unit = "pct" if o == "shr" else "pp"
                    add(f"{key}.count", f"{what}, firings measured", "count", "count")
                    add(f"{key}.median", f"{what}, median", unit, "Wilcoxon signed-rank")
                    if b == "pr":
                        add(f"{key}.mean", f"{what}, mean", unit, "one-sample t")
                        add(f"{key}.wmean", f"{what}, mean winsorised at 1% and 99%", unit, "one-sample t")
                        add(f"{key}.holm_p_median", f"{what}, median, Holm-adjusted p across 14 tests", "p3", "Holm")
                if o == "shr":
                    continue
                for side, who in (("firm", "the firm"), ("comp", "its competitor")):
                    lbl = f"{FG_CELL[c]}: {name} of {who}"
                    add(f"fg.{c}.{side}.{o}.{h}.post.median", f"{lbl}, after year -1 {when}, median", "pct", "median")
                    add(
                        f"fg.{c}.{side}.{o}.{h}.pre.median",
                        f"{lbl}, before (pairs measured {when}), median",
                        "pct",
                        "median",
                    )
    for label, pop in FG_PAIR.items():
        for o, (_, name, _kind) in FG_OUT.items():
            for h, k in FG_HOR.items():
                when = "36 months" if (o == "shr" and k == 3) else ("60 months" if o == "shr" else f"to year +{k}")
                key = f"fgdiff.{label}.pr.{o}.{h}"
                what = f"{pop}: {name}, {when}" + ("" if o == "shr" else ", change against the competitor")
                add(f"{key}.diff", f"{what}, difference in means", "pp", "Welch t")
                add(f"{key}.diff.ci_low", f"{what}, difference in means, 95% interval, low end", "pps", "95% interval")
                add(f"{key}.diff.ci_high", f"{what}, difference in means, 95% interval, high end", "pp", "95% interval")
                add(f"{key}.diff_median", f"{what}, difference in medians", "pp", "Mann-Whitney U")
                add(f"{key}.wdiff", f"{what}, difference in means winsorised at 1% and 99%", "pp", "Welch t")
                add(f"{key}.holm_p", f"{what}, difference in means, Holm-adjusted p across 14 tests", "p3", "Holm")
                add(
                    f"{key}.holm_p_median",
                    f"{what}, difference in medians, Holm-adjusted p across 14 tests",
                    "p3",
                    "Holm",
                )
                add(f"{key}.mde", f"{what}, smallest gap a 5% test with 80% power would detect", "pp", "power")
                if o in FG_MAIN:
                    ik = f"fgdiff.{label}.ind.{o}.{h}"
                    iw = f"{pop}: {name}, {when}, change against the industry median"
                    add(f"{ik}.diff", f"{iw}, difference in means", "pp", "Welch t")
                    add(f"{ik}.diff_median", f"{iw}, difference in medians", "pp", "Mann-Whitney U")
    for flag, label in FG_FLAG.items():
        for o, (_, name, _kind) in FG_OUT.items():
            if o == "shr":
                continue
            for h, k in FG_HOR.items():
                key = f"fgreg.{flag}.{o}.{h}"
                what = f"{FG_PAIR[label]}: {name} against the competitor, to year +{k}, coefficient with controls"
                add(f"{key}.coef", what, "pp", "OLS, standard errors clustered by firm")
                add(f"{key}.coef.ci_low", f"{what}, 95% interval, low end", "pps", "95% interval")
                add(f"{key}.coef.ci_high", f"{what}, 95% interval, high end", "pp", "95% interval")
    for c in ("founder", "hired", "scandal", "nonscandal"):
        for k in range(0, 6):
            for st, name in FG_STATUS:
                add(f"fgatt.{c}.p{k}.{st}", f"{FG_CELL[c]}: firms {name}, year +{k}", "count", "count")
        for y in ("m3", "m2", "m1", "p0", "p1", "p2", "p3", "p4", "p5"):
            yy = f"{'-' if y[0] == 'm' else '+'}{y[1]}"
            add(
                f"fgpath.{c}.count.{y}",
                f"{FG_CELL[c]}: pairs with revenue for firm and competitor, year {yy}",
                "count",
                "count",
            )
            for side, who in (("firm", "the firm"), ("comp", "its competitor")):
                add(
                    f"fgpath.{c}.{side}.{y}.median",
                    f"{FG_CELL[c]}: revenue of {who}, year {yy}, median with year -1 = 100",
                    "idx",
                    "median",
                )

    def body(a, b, label, name_a, name_b, num, title, extra):
        if a == "founder":  # D-42: founders against the competitor and the industry median only
            rows, ids = [], []
            rows.append(
                ["Panel A. Change against the matched competitor and the industry median, percentage points"] + [""] * 5
            )
            for o, hs in (
                ("rev", ("y3", "y5")),
                ("rev_att", ("y3", "y5")),
                ("rnd", ("y3",)),
                ("capex", ("y3", "y5")),
                ("roa", ("y3", "y5")),
                ("assets", ("y3", "y5")),
                ("mcap", ("y3", "y5")),
            ):
                for h in hs:
                    kp, ki = f"fg.founder.pr.{o}.{h}", f"fg.founder.ind.{o}.{h}"
                    rows.append(
                        [
                            f"{FG_OUT[o][0]}, to year +{FG_HOR[h]}",
                            val(kp + ".median", "pps"),
                            p_(kp + ".median"),
                            val(ki + ".median", "pps"),
                            p_(ki + ".median"),
                            f"{n_(kp + '.count')}; {n_(ki + '.count')}",
                        ]
                    )
                    if kp + ".median" in S:
                        ids.append(kp + ".median")
            rows.append(["Panel B. Share return minus the competitor's, from day +2"] + [""] * 5)
            for h in ("y3", "y5"):
                kp = f"fg.founder.pr.shr.{h}"
                rows.append(
                    [
                        "36 months" if h == "y3" else "60 months",
                        val(kp + ".median", "pct"),
                        p_(kp + ".median"),
                        "",
                        "",
                        n_(kp + ".count"),
                    ]
                )
            return table(
                f"Table {num}. {title}",
                [
                    "Outcome and horizon",
                    "Against the competitor, median",
                    "p",
                    "Against the industry, median",
                    "p",
                    "N",
                ],
                rows,
                ids,
                "Founder dismissals for any reason but fraud. Each cell is the firm's change from before the dismissal (fiscal "
                "years -3 to -1) to after it (year -1 to year +3 or +5). From it we subtract the same change at the matched "
                "competitor or at the industry's median firm; percentage points, growth a year. Failed firms at −100%: firms that went bankrupt, or that a "
                "regulator delisted, stay in. p: Wilcoxon signed-rank, unadjusted. N: firms against the competitor; against the "
                "industry. Holm-adjusted p are in Table IA.29.",
            )
        rows, ids = [], []

        def panel(head, bench, outs):
            rows.append([head] + [""] * 7)
            for o, hs in outs:
                for h in hs:
                    k = FG_HOR[h]
                    ka, kb, kd = f"fg.{a}.{bench}.{o}.{h}", f"fg.{b}.{bench}.{o}.{h}", f"fgdiff.{label}.{bench}.{o}.{h}"
                    unit = "pct" if o == "shr" else "pps"
                    lab = f"{FG_OUT[o][0]}, {'36 months' if (o == 'shr' and k == 3) else ('60 months' if o == 'shr' else f'to year +{k}')}"
                    rows.append(
                        [
                            lab,
                            val(ka + ".median", unit),
                            p_(ka + ".median"),
                            val(kb + ".median", unit),
                            p_(kb + ".median"),
                            val(kd + ".diff_median", "pps"),
                            p_(kd + ".diff_median"),
                            f"{n_(ka + '.count')}; {n_(kb + '.count')}",
                        ]
                    )
                    if ka + ".median" in S:
                        ids.append(ka + ".median")
            return rows

        both = ("y3", "y5")
        panel(
            "Panel A. Change against the matched competitor (difference-in-differences), percentage points",
            "pr",
            (("rev", both), ("rev_att", both), ("rnd", ("y3",)), ("capex", both), ("roa", both)),
        )
        panel(
            "Panel B. Change against the industry median, percentage points",
            "ind",
            (("rev", both), ("capex", both)),
        )
        panel("Panel C. Share return minus the competitor's, from day +2", "pr", (("shr", both),))
        return table(
            f"Table {num}. {title}",
            [
                "Outcome and horizon",
                f"{name_a}, median",
                "p",
                f"{name_b}, median",
                "p",
                "Difference in medians",
                "p, difference",
                "N",
            ],
            rows,
            ids,
            "Panels A and B: the firm's change from before the dismissal (fiscal years -3 to -1) to after it, minus the same change "
            "at its competitor or at its industry's median firm. After is year -1 to year +3 or +5; growth is a year. Failed firms "
            "at −100%: firms that went bankrupt, or that a regulator delisted, stay in. p: Wilcoxon signed-rank for a median, "
            f"Mann-Whitney U for the difference. N: {extra}. Every Holm-adjusted p in Panel A is 1.000 (Table IA.29). Panel C "
            "gives share returns from day +2. R&D to sales at year +5 has too few firings for a median.",
        )

    t_h4 = body(
        "founder",
        "hired",
        "founder_vs_hired",
        "Founders",
        "Hired CEOs",
        "IA.24",
        "Growth after a founder dismissal: every outcome, against the competitor and the industry",
        "founders; hired CEOs",
    )
    t_h5 = body(
        "scandal",
        "nonscandal",
        "scandal_vs_nonscandal",
        "Personal scandal",
        "Other dismissals",
        "IA.25",
        "Growth after the dismissal: personal scandals and other dismissals, every test",
        "scandal; other dismissals",
    )

    # Tables 9 and 10 (body): the main rows for each hypothesis
    def compact(a, b, label, num, title, name_a, name_b):
        if a == "founder":  # D-42: founders against the competitor and the industry median only
            crows, cids = [], []
            for o, h, lab in (
                ("rev", "y3", "Revenue growth a year, to year +3"),
                ("rev", "y5", "Revenue growth a year, to year +5"),
                ("rev_att", "y3", "Revenue growth, failed firms at −100%, to year +3"),
                ("capex", "y5", "Capital spending to assets, to year +5"),
                ("roa", "y5", "Return on assets, to year +5"),
            ):
                kp, ki = f"fg.founder.pr.{o}.{h}", f"fg.founder.ind.{o}.{h}"
                crows.append(
                    [
                        lab,
                        val(kp + ".median", "pps"),
                        p_(kp + ".median"),
                        val(ki + ".median", "pps"),
                        p_(ki + ".median"),
                        f"{n_(kp + '.count')}; {n_(ki + '.count')}",
                    ]
                )
                if kp + ".median" in S:
                    cids.append(kp + ".median")
            return table(
                f"Table {num}. {title}",
                [
                    "Outcome and horizon",
                    "Against the competitor, median",
                    "p",
                    "Against the industry, median",
                    "p",
                    "N",
                ],
                crows,
                cids,
                "Founder dismissals for any reason but fraud. The firm's change from before the dismissal (fiscal years -3 to -1) "
                "to after it, minus the same change at its matched competitor or at its industry's median firm, in percentage "
                "points; growth is a year. Failed firms at −100%: firms that went bankrupt, or that a regulator delisted, stay "
                "in. p: Wilcoxon signed-rank, unadjusted. N: firms against the competitor; against the industry. Table IA.24 "
                "gives every outcome and Table IA.29 the means and the Holm adjustment.",
            )
        crows, cids = [], []
        for bench, o, h, lab in (
            ("pr", "rev", "y3", "Revenue growth a year, to year +3"),
            ("pr", "rev", "y5", "Revenue growth a year, to year +5"),
            ("pr", "rev_att", "y3", "Revenue growth, failed firms at −100%, to year +3"),
            ("ind", "rev", "y3", "Revenue growth against the industry median, to year +3"),
            ("pr", "capex", "y5", "Capital spending to assets, to year +5"),
            ("pr", "roa", "y5", "Return on assets, to year +5"),
            ("pr", "shr", "y3", "Share return, 36 months from day +2"),
        ):
            ka, kb, kd = f"fg.{a}.{bench}.{o}.{h}", f"fg.{b}.{bench}.{o}.{h}", f"fgdiff.{label}.{bench}.{o}.{h}"
            unit = "pct" if o == "shr" else "pps"
            crows.append(
                [
                    lab,
                    val(ka + ".median", unit),
                    p_(ka + ".median"),
                    val(kb + ".median", unit),
                    p_(kb + ".median"),
                    f"{val(kd + '.diff_median', 'pps')} ({p_(kd + '.diff_median')})",
                    f"{n_(ka + '.count')}; {n_(kb + '.count')}",
                ]
            )
            if ka + ".median" in S:
                cids.append(ka + ".median")
        return table(
            f"Table {num}. {title}",
            [
                "Outcome and horizon",
                f"{name_a}, median",
                "p",
                f"{name_b}, median",
                "p",
                "Difference in medians (p)",
                "N",
            ],
            crows,
            cids,
            "The firm's change from before the dismissal (fiscal years -3 to -1) to after it, minus the same change at its matched "
            "competitor, in percentage points; growth is a year. One row uses the industry's median firm instead. Failed firms at "
            "−100%: firms that went bankrupt, or that a regulator delisted, stay in. The share return is the firm's minus its "
            "competitor's. p: Wilcoxon signed-rank for a median, Mann-Whitney U for a difference. Against the competitor every "
            f"Holm-adjusted p is 1.000 (Table IA.29). N: {name_a.lower()}; {name_b.lower()}. Table IA.{'24' if num == '9' else '25'} "
            "gives every outcome.",
        )

    t_body = compact(
        "founder",
        "hired",
        "founder_vs_hired",
        "9",
        "Growth after a founder dismissal: lower against the industry, not detectably different from the competitor",
        "Founders",
        "Hired CEOs",
    )
    t_body2 = compact(
        "scandal",
        "nonscandal",
        "scandal_vs_nonscandal",
        "10",
        "Growth after a scandal dismissal is not detectably weaker than after other dismissals",
        "Personal scandals",
        "Other dismissals",
    )

    # Table IA.26: before and after, the firm and its competitor
    lrows, lids = [], []
    for c, name in (("founder", "Founders fired"),):
        lrows.append([name] + [""] * 6)
        for o in FG_MAIN:
            for h, k in FG_HOR.items():
                f_, c_ = f"fg.{c}.firm.{o}.{h}", f"fg.{c}.comp.{o}.{h}"
                lrows.append(
                    [
                        f"{FG_OUT[o][0]}, to year +{k}",
                        val(f_ + ".pre.median", "pct"),
                        val(f_ + ".post.median", "pct"),
                        val(c_ + ".pre.median", "pct"),
                        val(c_ + ".post.median", "pct"),
                        val(f"fg.{c}.pr.{o}.{h}.median", "pps"),
                        n_(f"fg.{c}.pr.{o}.{h}.count"),
                    ]
                )
                if f_ + ".post.median" in S:
                    lids.append(f_ + ".post.median")
    t_levels = table(
        "Table IA.26. Growth before and after a founder dismissal: the firm and its competitor",
        [
            "Group, outcome and horizon",
            "Firm, before",
            "Firm, after",
            "Competitor, before",
            "Competitor, after",
            "Change against competitor, median",
            "N",
        ],
        lrows,
        lids,
        "Medians across pairs with every number. Before: growth a year over fiscal years -3 to -1, or the ratio's mean over those "
        "years. After: growth a year from year -1 to year +3 or +5, or the ratio in that year. The last column is the median of each "
        "pair's change at the firm minus the change at its competitor, in percentage points; it is not the difference of the "
        "medians beside it. A dash marks fewer than 10 pairs.",
    )

    # Table IA.27: the revenue path
    prow, pids = [], []
    for c, name in (
        ("founder", "Founders fired"),
        ("scandal", "Fired over a personal scandal"),
        ("nonscandal", "Other dismissals"),
    ):
        prow.append([name, "", "", ""])
        for y in ("m3", "m2", "m1", "p0", "p1", "p2", "p3", "p4", "p5"):
            yy = f"{'−' if y[0] == 'm' else '+'}{y[1]}" if y != "p0" else "0"
            prow.append(
                [
                    f"Year {yy}",
                    val(f"fgpath.{c}.firm.{y}.median", "bn"),
                    val(f"fgpath.{c}.comp.{y}.median", "bn"),
                    n_(f"fgpath.{c}.count.{y}"),
                ]
            )
            if f"fgpath.{c}.firm.{y}.median" in S:
                pids.append(f"fgpath.{c}.firm.{y}.median")
    t_path = table(
        "Table IA.27. Revenue around the dismissal, year −1 = 100",
        ["Group and fiscal year", "Firm", "Competitor", "N"],
        prow,
        pids,
        "Median revenue of the firm and of its matched competitor, each set to 100 in the fiscal year before the dismissal (year "
        "0). N counts pairs in which both filed that year, so it falls as firms and competitors leave; a later year is not the same "
        "set of pairs as an earlier one.",
    )

    # Table IA.28: attrition
    arow, aids = [], []
    for c, name in (
        ("founder", "Founders fired"),
        ("scandal", "Fired over a personal scandal"),
        ("nonscandal", "Other dismissals"),
    ):
        arow.append([name] + [""] * 7)
        for k in range(0, 6):

            def g(st, c=c, k=k):
                return S.get(f"fgatt.{c}.p{k}.{st}", {}).get("value") or 0

            arow.append(
                [
                    f"Year {'0' if k == 0 else '+' + str(k)}",
                    fmt(g("filing"), "count"),
                    fmt(g("bankrupt"), "count"),
                    fmt(g("cause"), "count"),
                    fmt(g("acquired"), "count"),
                    fmt(g("not_reached"), "count"),
                    fmt(g("other") + g("no_filing"), "count"),
                    nv(FG, f"fgatt.{c}.p{k}.filing"),
                ]
            )
            aids.append(f"fgatt.{c}.p{k}.filing")
    t_att = table(
        "Table IA.28. Attrition after the dismissal",
        [
            "Group and fiscal year",
            "Still filing",
            "Bankrupt",
            "Regulatory delisting",
            "Taken over",
            "Not yet reached",
            "No filing or other",
            "N",
        ],
        arow,
        aids,
        "Firms with revenue in the fiscal year before the dismissal (N), by where they stand in each later year. Bankruptcies and "
        "regulatory delistings are read from the corporate actions around the last share price. Those firms stay in the rows of "
        "Tables 9 and 10 that set failed firms at −100%. A firm taken over leaves at the takeover. Not yet reached: the year is "
        "after the last year of data.",
    )

    # Table IA.29: every outcome, means and controls
    erow, eids = [], []
    # D-42: founders against their competitor, with intervals and the Holm adjustment; no founder-minus-hired difference
    erow.append(["Founders: change against the competitor"] + [""] * 7)
    for o in FG_MAIN + FG_ATT:
        for h, k in FG_HOR.items():
            kf = f"fg.founder.pr.{o}.{h}"
            lo, hi = S.get(kf + ".mean.ci_low"), S.get(kf + ".mean.ci_high")
            ok = lo and hi and lo.get("value") is not None and hi.get("value") is not None
            erow.append(
                [
                    f"{FG_OUT[o][0]}, to year +{k}",
                    val(kf + ".wmean", "pps"),
                    "",
                    val(kf + ".mean", "pps"),
                    (f"{fmt(lo['value'], 'pps')} to {fmt(hi['value'], 'pps')}; " if ok else "") + p_(kf + ".mean"),
                    "",
                    "",
                    n_(kf + ".count"),
                ]
            )
            if kf + ".mean" in S and S[kf + ".mean"].get("value") is not None:
                eids.append(kf + ".mean")
    for label, a, b, name in (
        ("scandal_vs_nonscandal", "scandal", "nonscandal", "Personal scandal minus other dismissals"),
    ):
        flag = "founder" if a == "founder" else "scandal"
        erow.append([name] + [""] * 7)
        for o in FG_MAIN + FG_ATT:
            for h, k in FG_HOR.items():
                kd = f"fgdiff.{label}.pr.{o}.{h}"
                lo, hi = S.get(kd + ".diff.ci_low"), S.get(kd + ".diff.ci_high")
                kr = f"fgreg.{flag}.{o}.{h}"
                rlo, rhi = S.get(kr + ".coef.ci_low"), S.get(kr + ".coef.ci_high")
                ok = lo and hi and lo.get("value") is not None and hi.get("value") is not None
                rok = rlo and rhi and rlo.get("value") is not None and rhi.get("value") is not None
                erow.append(
                    [
                        f"{FG_OUT[o][0]}, to year +{k}",
                        val(f"fg.{a}.pr.{o}.{h}.wmean", "pps"),
                        val(f"fg.{b}.pr.{o}.{h}.wmean", "pps"),
                        val(kd + ".diff", "pps"),
                        f"{fmt(lo['value'], 'pps')} to {fmt(hi['value'], 'pps')}; {p_(kd + '.diff')}" if ok else FV_FEW,
                        val(kd + ".wdiff", "pps"),
                        (
                            f"{val(kr + '.coef', 'pps')} ({fmt(rlo['value'], 'pps')} to {fmt(rhi['value'], 'pps')})"
                            if rok
                            else FV_FEW
                        ),
                        f"{n_(kd + '.n_a')}; {n_(kd + '.n_b')}",
                    ]
                )
                if kd + ".diff" in S and S[kd + ".diff"].get("value") is not None:
                    eids.append(kd + ".diff")
    t_every = table(
        "Table IA.29. Growth after the dismissal: every outcome, means and controls",
        [
            "Outcome and horizon",
            "Group, winsorised mean",
            "Comparison group, winsorised mean",
            "Mean, or difference in means",
            "95% interval; p",
            "Winsorised difference",
            "With controls (95% interval)",
            "N",
        ],
        erow,
        eids,
        "The change against the matched competitor of Tables 9 and 10, in percentage points. Founders: the founder firm's own "
        "change against its competitor, mean with its 95% interval and one-sample t p, and the winsorised mean. Personal "
        "scandal: the difference in means against other dismissals (Welch t on the raw changes, which a few firms with tiny "
        "sales or assets can move); the winsorised columns clip at 1% and 99%. With controls: the coefficient on the scandal "
        "flag in a regression of the firm-minus-competitor change after year -1 on log market value, prior revenue growth, "
        "prior 12-month return, leverage, industry and year, clustered by firm. N: first; second group.",
    )

    # Table IA.30: sex-or-relationship dismissals, named
    crow = []
    for r in S.get("_cases", {}).get("sexrel", []):

        def one(x):
            return FV_FEW if x is None else fmt(x, "pps")

        crow.append(
            [
                r["coname"].title(),
                str(r["year"]),
                r.get("competitor") or FV_FEW,
                one(r.get("rev.y3")),
                one(r.get("rev.y5")),
                {
                    "filing": "Still filing",
                    "acquired": "Taken over",
                    "bankrupt": "Bankrupt",
                    "cause": "Regulatory delisting",
                }.get(r.get("status_y5"), "No filing"),
            ]
        )
    t_cases = table(
        "Table IA.30. Dismissals over sexual misconduct or a relationship: revenue growth against the competitor",
        [
            "Company",
            "Year",
            "Competitor (ticker)",
            "Revenue growth to year +3",
            "Revenue growth to year +5",
            "At year +5",
        ],
        crow,
        [],
        "The dismissals coded as sexual misconduct or a relationship, named because fewer than 10 have a competitor filing in "
        "year +3. Revenue growth is the firm's change in growth a year from before the dismissal to after it, minus its "
        "competitor's, in percentage points. A dash marks a firm or competitor without the filings needed.",
    )
    return stats, [t_body, t_body2], [t_h4, t_h5, t_levels, t_path, t_att, t_every, t_cases]


def sec_i():
    stats, body, appendix = growth_exhibit()
    if not stats:
        return None
    return section(
        "I",
        "Growth after the dismissal",
        "Does the firm grow more slowly than its competitor after a founder or scandal dismissal?",
        f"Against the matched competitor, the median founder firm's revenue growth changes by "
        f"{v(FG, 'fg.founder.pr.rev.y3.median', 'pp')} a year to year +3 (p {pv(FG, 'fg.founder.pr.rev.y3.median')}, "
        f"N = {nv(FG, 'fg.founder.pr.rev.y3.median')}) and the median hired-CEO firm's by "
        f"{v(FG, 'fg.hired.pr.rev.y3.median', 'pp')} (N = {nv(FG, 'fg.hired.pr.rev.y3.median')}); the difference in medians has p "
        f"{pv(FG, 'fgdiff.founder_vs_hired.pr.rev.y3.diff_median')}. After a personal scandal the median change is "
        f"{v(FG, 'fg.scandal.pr.rev.y3.median', 'pp')} (N = {nv(FG, 'fg.scandal.pr.rev.y3.median')}).",
        {
            "test": "Wilcoxon signed-rank, one-sample t, Welch t, Mann-Whitney U, Holm across 14 tests; OLS with controls, clustered by firm",
            "data": "Sharadar SF1 as-reported annual statements, fiscal years -3 to +5 around the dismissal year",
            "library_call": "analysis/founder_growth.py",
            "caveat": "Difference-in-differences against the closest competitor. Ratios use firms still filing; revenue, asset and market value growth are also "
            "reported with bankrupt firms and regulatory delistings at -100%. Employees are not in the data.",
        },
        stats,
        body + appendix,
    )


def cases_exhibits():
    """Appendix exhibits from the hand check (founder_appendix.py, screen.py) and H1 under each correction."""
    stats = []

    def add(file, key, label, unit, test=""):
        r = SRC[file].get(key)
        if r is None or r.get("value") is None or not r.get("n"):
            return
        stats.append(stat(file, key, label, unit, test, "founder_cases"))

    A, S, V = SRC[FA], SRC[SC], SRC[VV]
    for k in sorted(A):
        if k.startswith("fa."):
            add(FA, k, k.replace("fa.", "").replace("_", " ").replace(".", ": "), "count", "count")
    for k in sorted(S):
        if k.startswith("screen."):
            unit = "pct" if k.endswith(("sensitivity", "rate", "specificity", "precision")) else "count"
            add(SC, k, k.replace("screen.", "succession screen: ").replace("_", " "), unit, "hand check")
    tables = []

    # H1 under each correction
    rows, ids = [], []
    W = "slideann"
    for ver, _, _, label in H1_VERSIONS:
        p = f"h1v.{ver}"
        if f"{p}.fv.founder.pr.{W}.ret.mean" not in V:
            continue
        d = f"{p}.fvdiff.main.founder_vs_hired.pr.{W}.ret"
        fk = f"{p}.fv.founder.pr.{W}.ret.mean"
        flo, fhi = V.get(fk + ".ci_low"), V.get(fk + ".ci_high")
        rows.append(
            [
                label,
                v(VV, fk, "pct"),
                f"{fmt(flo['value'], 'pct')} to {fmt(fhi['value'], 'pct')}" if flo and fhi else "",
                pv(VV, fk),
                v(VV, f"{p}.fv.founder.pr.{W}.ret.median", "pct"),
                f"{v(VV, f'{p}.fvinv.founder.firm.d1.median', 'usd2')} / {v(VV, f'{p}.fvinv.founder.pr.d1.median', 'usd2')}",
                v(VV, f"{p}.fv.founder.pr.{W}.usd.median", "usdm_cell"),
                v(VV, f"{p}.fv.founder.pr.{W}.ret.count", "count"),
            ]
        )
        for key, lbl, unit, test in (
            (f"{p}.fv.founder.pr.{W}.ret.mean", "founders' mean return gap, days -30 to +1", "pct", "one-sample t"),
            (f"{p}.fv.founder.pr.{W}.ret.median", "founders' median return gap, days -30 to +1", "pct", "Wilcoxon"),
            (
                f"{p}.fv.founder.pr.{W}.ret.mean.ci_low",
                "founders' mean return gap, 95% interval, low end",
                "pct",
                "95% interval",
            ),
            (
                f"{p}.fv.founder.pr.{W}.ret.mean.ci_high",
                "founders' mean return gap, 95% interval, high end",
                "pct",
                "95% interval",
            ),
            (f"{p}.fv.hired.pr.{W}.ret.mean", "hired CEOs' mean return gap, days -30 to +1", "pct", "one-sample t"),
            (f"{p}.fv.hired.pr.{W}.ret.median", "hired CEOs' median return gap, days -30 to +1", "pct", "Wilcoxon"),
            (d + ".diff", "founders minus hired, mean return gap, days -30 to +1", "pp", "Welch t"),
            (d + ".diff.ci_low", "founders minus hired, 95% interval, low end", "pps", "95% interval"),
            (d + ".diff.ci_high", "founders minus hired, 95% interval, high end", "pp", "95% interval"),
            (d + ".diff_median", "founders minus hired, median return gap", "pp", "Mann-Whitney U"),
            (d + ".holm_p", "founders minus hired, Holm-adjusted p", "p3", "Holm"),
            (
                f"{p}.fvinv.founder.firm.d1.median",
                "$100 in the founder's firm at day -31, median at day +1",
                "usd2",
                "median",
            ),
            (
                f"{p}.fvinv.founder.pr.d1.median",
                "$100 in its competitor at day -31, median at day +1",
                "usd2",
                "median",
            ),
            (
                f"{p}.fvinv.hired.firm.d1.median",
                "$100 in the hired CEO's firm at day -31, median at day +1",
                "usd2",
                "median",
            ),
            (f"{p}.fvinv.hired.pr.d1.median", "$100 in its competitor at day -31, median at day +1", "usd2", "median"),
            (f"{p}.fv.founder.pr.{W}.usd.median", "founders' median dollar change, days -30 to +1", "usdm", "Wilcoxon"),
            (f"{p}.fv.hired.pr.{W}.usd.median", "hired CEOs' median dollar change, days -30 to +1", "usdm", "Wilcoxon"),
            (f"{p}.fv.founder.pr.{W}.ret.count", "founder firings measured", "count", "count"),
            (f"{p}.fv.hired.pr.{W}.ret.count", "hired-CEO firings measured", "count", "count"),
        ):
            add(VV, key, f"{label}: {lbl}", unit, test)
        ids.append(f"{p}.fv.founder.pr.{W}.ret.mean")
    if rows:
        tables.append(
            table(
                "Table IA.8. The founder firm against its competitor under each version of the codes and the competitor",
                [
                    "Codes and competitor",
                    "Mean",
                    "95% interval",
                    "p",
                    "Median",
                    "$100 at day +1, median: firm / competitor",
                    "Median $ million",
                    "N",
                ],
                rows,
                ids,
                "Founder dismissals for any reason but fraud. Mean and median: the founder firm's return minus its "
                "competitor's over trading days -30 to +1; p is a one-sample t test, unadjusted. $100: the median value "
                "at day +1 of $100 put in at day -31. Median $ million: the median dollar change against the competitor, in "
                "2023 dollars. The closest competitor shares the 4-digit, else the 3-digit SIC code, else the Sharadar "
                "industry, within 50% in market value, with the nearest prior-year return.",
            )
        )

    # hand checks and the screen
    ar = []
    for label, nkey, keys in (
        ("Founders, every departure", "fa.n_checked", ("fa.n_planned_dropped", None, None)),
        (
            "Hired CEOs, random 60",
            "fa.audit.hired.n",
            ("fa.audit.hired.planned", "fa.audit.hired.redate", "fa.audit.hired.recode"),
        ),
    ):
        ar.append(
            [label, v(FA, nkey, "count")] + [v(FA, k, "count") if k else "see notes" for k in keys] + ["", "", ""]
        )
    ar.append(
        [
            "Succession screen on the 163 checked departures",
            v(SC, "screen.validation.n_checked", "count"),
            v(SC, "screen.validation.n_planned", "count"),
            "",
            "",
            v(SC, "screen.validation.flag.sensitivity", "pct"),
            v(SC, "screen.validation.flag.false_positives", "count"),
            v(SC, "screen.validation.flag.precision", "pct"),
        ]
    )
    tables.append(
        table(
            "Table IA.1. The case checks found planned successions and wrong dates on both sides",
            [
                "Check",
                "N",
                "Planned successions",
                "Redated",
                "Recoded",
                "Screen sensitivity",
                "False positives",
                "Precision",
            ],
            ar,
            ["fa.n_checked", "fa.audit.hired.n", "screen.validation.n_checked"],
            "Founders: every founder departure, checked case by case by AI research assistants in five batches; 13 founder "
            "dates moved to the first public report and 4 reasons were recoded. Hired CEOs: 60 drawn at random from the "
            "hired-CEO dismissals and checked with the same rules. No second human coder has checked either. The "
            "screen flags a dismissal announced 90 or more days before the CEO left office, or one whose notes say the CEO "
            "stayed chairman and name the chief operating officer or the president as successor. Sensitivity: "
            "flagged among the planned successions; false positives: flagged among the other checked departures.",
        )
    )
    T = A.get("_tables", {})
    if T:
        tables.append(
            table(
                "Table IA.9. Founder dismissals, case by case",
                [
                    "Company",
                    "Founder",
                    "Reason",
                    "How",
                    "Successor",
                    "3 years vs competitor, points",
                    "Outcome",
                    "Founder's fate",
                ],
                T["cases"],
                ["fa.n_kept"],
                "Every founder dismissal kept after the case checks, by date. How: pushed or unclear on the "
                "sources read. 3 years vs competitor: the buy-and-hold return from day +2 minus the closest competitor's. "
                "Outcome: bankrupt, taken over or delisted within five years; otherwise gained (above +10 points), lost "
                "(below -10) or about even. Fate: board seat, a return as CEO, a new firm, a fight with the firm, legal "
                "action naming the founder, death within five years, from the coders' sources.",
            )
        )
        tables.append(
            table(
                "Table IA.2. Excluded: planned successions, not firings",
                ["Company", "Founder", "What the sources say"],
                T["excluded"],
                ["fa.n_planned_dropped"],
                "Founder departures the database codes as forced that the case check found to be planned successions. They "
                "leave every analysis and join no comparison group. The quote is from the source read for each case; the "
                "case files in the replication package give the full text.",
            )
        )
        tables.append(
            table(
                "Table IA.10. What happened to the founder",
                ["What happened", "N", "Named (cells under 10)"],
                T["fates"],
                ["fa.n_kept"],
                "Founder dismissals kept after the case checks. Board seat: kept a seat or the chair for any time after the CEO "
                "exit, from the case sources; Table IA.22 instead counts founders still named in the proxy about two years later. Came back as CEO: of the same firm within five years. Legal action: "
                "charges, regulator action or a lawsuit naming the founder. Percentages of all founder firings kept; cells "
                "under 10 are named instead.",
            )
        )
        if T.get("pairs"):
            tables.append(
                table(
                    "Table IA.23. Founder firms and their closest competitors",
                    ["Company", "Industry (SIC)", "Competitor", "Competitor's industry (SIC)", "Matched on"],
                    T["pairs"],
                    ["fa.n_kept"],
                    "Every founder firing kept, with the competitor of Section 4. The competitor shares the 4-digit SIC code "
                    "where one qualifies, else the 3-digit code, else the Sharadar industry. It is within 50% in market value, "
                    "with no CEO change in the three years before and the nearest prior-year return. A dash marks a firing "
                    "with no qualifying competitor.",
                )
            )
    return [s for s in stats if s], tables


def fv_exhibit():
    """Statistics and tables for the founder CEO in dollars against competitors (D-34)."""
    fv_prepare()
    S = SRC[FV]
    stats, seen = [], set()

    def add(key, label, unit, test=""):
        if key in seen or key not in S or S[key].get("value") is None or not S[key].get("n"):
            return
        seen.add(key)
        stats.append(stat(FV, key, label, unit, test, "founder_value"))

    def cell_stats(cell, bench, windows, full=False):
        for w in windows:
            k = f"fv.{cell}.{bench}.{w}"
            what = f"{FV_CELL[cell]}: {FV_WIN[w][1]}, against {FV_BENCH[bench]}"
            add(f"{k}.ret.count", f"{what}, firings measured", "count", "count")
            add(f"{k}.ret.mean", f"{what}, mean return gap", "pct", "one-sample t")
            add(f"{k}.ret.median", f"{what}, median return gap", "pct", "Wilcoxon signed-rank")
            add(f"{k}.usd.mean", f"{what}, mean dollar change per firm", "usdm", "one-sample t")
            add(f"{k}.usd.median", f"{what}, median dollar change per firm", "usdm", "Wilcoxon signed-rank")
            add(f"{k}.usd.total_bn", f"{what}, total dollar change across firms", "usdbn", "sum")
            if not full:
                continue
            add(f"{k}.usd.count", f"{what}, firings with a dollar change", "count", "count")
            add(f"{k}.ret.mean.ci_low", f"{what}, mean return gap, 95% interval, low end", "pct", "95% interval")
            add(f"{k}.ret.mean.ci_high", f"{what}, mean return gap, 95% interval, high end", "pct", "95% interval")
            add(f"{k}.ret.wmean", f"{what}, mean return gap, winsorised at 1% and 99%", "pct", "one-sample t")
            add(
                f"{k}.usd.wmean",
                f"{what}, mean dollar change per firm, winsorised at 1% and 99%",
                "usdm",
                "one-sample t",
            )
            add(f"{k}.usd.largest_loss", f"{what}, the largest single dollar loss", "usdm", "minimum")
            add(
                f"{k}.usd.largest_loss_share",
                f"{what}, the largest single loss as a share of the total",
                "pct",
                "share",
            )

    def diff_stats(label, bench, windows, units=("ret", "usd"), full=True):
        for w in windows:
            for u in units:
                k = f"fvdiff.{label}.{bench}.{w}.{u}"
                what = f"{FV_PAIR[label]}: {FV_WIN[w][1]}, against {FV_BENCH[bench]}, "
                what += "return gap" if u == "ret" else "dollar change per firm"
                unit = "pp" if u == "ret" else "usdm"
                add(f"{k}.diff", f"{what}, difference in means", unit, "Welch t")
                add(f"{k}.holm_p", f"{what}, Holm-adjusted p across the six windows", "p3", "Holm")
                if not full:
                    continue
                add(
                    f"{k}.diff.ci_low",
                    f"{what}, 95% interval, low end",
                    "pps" if u == "ret" else "usdm",
                    "95% interval",
                )
                add(f"{k}.diff.ci_high", f"{what}, 95% interval, high end", unit, "95% interval")
                add(f"{k}.diff_median", f"{what}, difference in medians", unit, "Mann-Whitney U")
                add(f"{k}.wdiff", f"{what}, difference in means winsorised at 1% and 99%", unit, "Welch t")
                add(f"{k}.mde", f"{what}, smallest gap a 5% test with 80% power would detect", unit, "power")
                add(
                    f"{k}.perm_p", f"{what}, permutation test p (added after the design was fixed)", "p3", "permutation"
                )
                add(
                    f"{k}.sign_p_a",
                    f"{what}, exact sign test p for the first group (added after the design was fixed)",
                    "p3",
                    "sign test",
                )
                add(
                    f"{k}.share_negative_a",
                    f"{what}, share of the first group below zero (added after the design was fixed)",
                    "pct",
                    "share",
                )

    every = FV_MAIN + ("slide_wd", "slideann_wd")
    groups = ("forced", "retired", "fraud", "founder_fraud", "hired_fraud", "scandal", "coup", "other")
    for c in ("founder", "hired"):
        cell_stats(c, "pr", every, full=True)
        cell_stats(c, "sp", FV_MAIN)
        cell_stats(c, "pr3", FV_MAIN)
    # D-42: the founder firm against every normal benchmark, with the Holm adjustment across the five
    for bench in ("sp", "ind", "pr3", "roa"):
        cell_stats("founder", bench, FV_MAIN, full=True)
    for bench in ("pr2", "pr4", "pr5"):  # D-47: averages of k competitors, added after review
        cell_stats("founder", bench, ("slide", "ann", "slideann"))
    for bench in ("sp", "ind", "pr3", "roa", "pr"):
        for w in FV_MAIN:
            for st in ("mean", "median"):
                add(
                    f"fv.founder.{bench}.{w}.ret.{st}.holm5_p",
                    f"{FV_CELL['founder']}: {FV_WIN[w][1]}, against {FV_BENCH[bench]}, {st} return gap, Holm-adjusted p "
                    "across the five benchmarks (added after review)",
                    "p3",
                    "Holm",
                )
    for c in groups:
        cell_stats(c, "pr", FV_MAIN, full=c in ("forced", "retired"))
        cell_stats(c, "sp", FV_MAIN)
    for bench in ("pr", "sp", "roa", "ind", "pr3"):
        diff_stats(
            "main.founder_vs_hired", bench, every if bench == "pr" else FV_MAIN, full=bench in ("pr", "sp", "pr3")
        )
        if bench != "pr3":
            diff_stats("forced_vs_retired", bench, FV_MAIN, full=bench == "pr")
    # checks added after review (D-41): clearly forced founders; 4-digit SIC pairs only
    for sname, what in (("pushed", "founders clearly forced out"), ("sic4", "4-digit SIC pairs only")):
        for w in ("slide", "ann", "slideann"):
            k = f"fvrob.{sname}"
            lbl = f"Check added after review, {what}: {FV_WIN[w][1]}, against the closest competitor"
            add(f"{k}.founder.pr.{w}.ret.count", f"{lbl}, founders measured", "count", "count")
            add(f"{k}.founder.pr.{w}.ret.mean", f"{lbl}, founders' mean return gap", "pct", "one-sample t")
            add(f"{k}.hired.pr.{w}.ret.count", f"{lbl}, hired CEOs measured", "count", "count")
            add(f"{k}.hired.pr.{w}.ret.mean", f"{lbl}, hired CEOs' mean return gap", "pct", "one-sample t")
            d = f"{k}.founder_vs_hired.pr.{w}.ret"
            add(d + ".diff", f"{lbl}, founders minus hired, difference in means", "pp", "Welch t")
            add(d + ".diff.ci_low", f"{lbl}, founders minus hired, 95% interval, low end", "pps", "95% interval")
            add(d + ".diff.ci_high", f"{lbl}, founders minus hired, 95% interval, high end", "pp", "95% interval")
    for label in ("fraud.founder_vs_hired", "scandal_vs_fraud", "scandal_vs_other", "fraud_vs_forced"):
        diff_stats(label, "pr", FV_MAIN, full=False)
    for flag, pair in (("founder", "main.founder_vs_hired"), ("fired", "forced_vs_retired")):
        for w in every if flag == "founder" else FV_MAIN:
            for u, unit, name in (("ret", "pp", "return gap"), ("logusd", "coef", "signed log dollar change")):
                k = f"fvreg.{flag}.pr.{w}.{u}"
                what = f"{FV_PAIR[pair]}: {FV_WIN[w][1]}, {name}, coefficient with controls"
                add(f"{k}.coef", what, unit, "OLS, standard errors clustered by firm")
                add(
                    f"{k}.coef.ci_low",
                    f"{what}, 95% interval, low end",
                    "pps" if u == "ret" else "coef",
                    "95% interval",
                )
                add(f"{k}.coef.ci_high", f"{what}, 95% interval, high end", unit, "95% interval")
                add(f"{k}.holm_p", f"{what}, Holm-adjusted p across the six windows", "p3", "Holm")
    for c in FV_CELL:
        add(f"fv.{c}.n_all", f"{FV_CELL[c]}, firings with share prices", "count", "count")
        add(f"fv.{c}.n_matched", f"{FV_CELL[c]}, firings with a matched competitor", "count", "count")
        add(f"fv.{c}.n_mv", f"{FV_CELL[c]}, firings with a market value at day -31", "count", "count")
        add(f"fv.{c}.mv31.median_bn", f"{FV_CELL[c]}, median market value at day -31", "usdbn", "median")
        add(f"fv.{c}.mv31.mean_bn", f"{FV_CELL[c]}, mean market value at day -31", "usdbn", "mean")
        add(f"fv.{c}.mv31.total_bn", f"{FV_CELL[c]}, total market value at day -31", "usdbn", "sum")
    BAL = (
        ("prior12", "return over trading days -282 to -31", "pct", "pp"),
        ("mcap", "market value at the fiscal year-end before", "usdbn", "coef"),
        ("roa", "return on assets in fiscal year -1", "pct", "pp"),
    )
    bal_groups = ("founder", "hired", "forced", "retired", "fraud")
    for c in bal_groups:
        add(f"fvbal.{c}.n", f"{FV_CELL[c]}, firms with a matched competitor", "count", "count")
        add(f"fvbal.{c}.relaxed", f"{FV_CELL[c]}, competitors found only in the wider size band", "count", "count")
        for m, name, unit, gap_unit in BAL:
            sfx = "_bn" if m == "mcap" else ""
            for side, who in (("firm", "the firm"), ("comp", "its competitor")):
                add(f"fvbal.{c}.{m}.{side}.mean{sfx}", f"{FV_CELL[c]}: {name}, {who}, mean", unit, "mean")
                add(f"fvbal.{c}.{m}.{side}.median{sfx}", f"{FV_CELL[c]}: {name}, {who}, median", unit, "median")
            lbl = f"{FV_CELL[c]}: {name}, firm minus competitor"
            add(f"fvbal.{c}.{m}.gap", lbl + (", mean log gap" if m == "mcap" else ", mean gap"), gap_unit, "paired t")
            add(f"fvbal.{c}.{m}.gap_median", lbl + ", median gap", gap_unit, "Wilcoxon signed-rank")
            add(f"fvbal.{c}.{m}.std_diff", lbl + ", standardised difference", "coef", "standardised difference")
    # D-42 addendum: the balance of the three-competitor mean for founders
    add("fvbal3.founder.n", f"{FV_CELL['founder']}, firms with three closest competitors", "count", "count")
    for m, name, unit, gap_unit in BAL:
        sfx = "_bn" if m == "mcap" else ""
        for side, who in (("firm", "the firm"), ("comp", "the mean of its three closest competitors")):
            add(f"fvbal3.founder.{m}.{side}.mean{sfx}", f"{FV_CELL['founder']}: {name}, {who}, mean", unit, "mean")
            add(
                f"fvbal3.founder.{m}.{side}.median{sfx}", f"{FV_CELL['founder']}: {name}, {who}, median", unit, "median"
            )
        lbl = f"{FV_CELL['founder']}: {name}, firm minus the mean of its three closest competitors"
        add(f"fvbal3.founder.{m}.gap", lbl + (", mean log gap" if m == "mcap" else ", mean gap"), gap_unit, "paired t")
        add(f"fvbal3.founder.{m}.gap_median", lbl + ", median gap", gap_unit, "Wilcoxon signed-rank")
        add(f"fvbal3.founder.{m}.std_diff", lbl + ", standardised difference", "coef", "standardised difference")
    for k in sorted(S):
        if k.startswith("fvcase.") and fv_window(k) in ("slideann", "m12"):
            w = fv_window(k)
            unit, what = ("pct", "return gap") if k.endswith(".ret") else ("usdm", "dollar change")
            add(
                k,
                f"Named founder firing {k.split('.')[1]}, {FV_WIN[w][1]}, {what} against the competitor",
                unit,
                "event return",
            )

    for c in ("founder", "hired", "forced", "retired"):
        for h in FV_INV:
            add(
                f"fvinv.{c}.{h}.count",
                f"{FV_CELL[c]}: $100 at day -31, {FV_INV[h][0].lower()}, firings measured",
                "count",
                "count",
            )
            for a in FV_ASSET:
                lbl = f"{FV_CELL[c]}: $100 put in {FV_ASSET[a]} at day -31, value at {FV_INV[h][0].lower()}"
                add(f"fvinv.{c}.{a}.{h}.mean", lbl + ", mean", "usd2", "mean")
                add(f"fvinv.{c}.{a}.{h}.median", lbl + ", median", "usd2", "median")
            for a in ("pr", "sp"):
                lbl = f"{FV_CELL[c]}: $100 in the firm minus $100 in {FV_ASSET[a]}, value at {FV_INV[h][0].lower()}"
                add(f"fvinv.{c}.firm_minus_{a}.{h}.mean", lbl + ", mean", "usdgap", "paired t")
                add(f"fvinv.{c}.firm_minus_{a}.{h}.median", lbl + ", median", "usdgap", "Wilcoxon signed-rank")
        add(
            f"fvprior.{c}.count",
            f"{FV_CELL[c]}: firings with a prior return for the firm, competitor and S&P 500",
            "count",
            "count",
        )
        for a in FV_ASSET:
            lbl = f"{FV_CELL[c]}: return of {FV_ASSET[a]} over trading days -282 to -31"
            add(f"fvprior.{c}.{a}.mean", lbl + ", mean", "pct", "mean")
            add(f"fvprior.{c}.{a}.median", lbl + ", median", "pct", "median")
        for a in ("pr", "sp"):
            add(
                f"fvprior.{c}.firm_minus_{a}.mean",
                f"{FV_CELL[c]}: prior return of the firm minus that of {FV_ASSET[a]}, mean",
                "pp",
                "paired t",
            )
    # D-42: $100 in the founder's firm against the industry average and the three closest competitors
    for h in FV_INV:
        for a in ("ind", "pr3"):
            add(
                f"fvinv.founder.{a}.{h}.count",
                f"{FV_CELL['founder']}: $100 at day -31 against {FV_BENCH[a]}, {FV_INV[h][0].lower()}, firings measured",
                "count",
                "count",
            )
            for side, who in ((f"firm_{a}", "the firm"), (a, FV_BENCH[a])):
                for st in ("mean", "median"):
                    add(
                        f"fvinv.founder.{side}.{h}.{st}",
                        f"{FV_CELL['founder']}: $100 put in {who} at day -31 (sample with {FV_BENCH[a]}), value at "
                        f"{FV_INV[h][0].lower()}, {st}",
                        "usd2",
                        st,
                    )
    for h in FV_INV:
        for a in FV_ASSET:
            k = f"fvinvdiff.main.founder_vs_hired.{a}.{h}"
            add(
                k + ".diff",
                f"$100 in {FV_ASSET[a]} at day -31, value at {FV_INV[h][0].lower()}, founders minus hired CEOs",
                "usdgap",
                "Welch t",
            )

    def val(key, unit):
        return v(FV, key, unit) if key in S and S[key].get("value") is not None else FV_FEW

    def interval(key, unit):
        lo, hi = S.get(key + ".ci_low"), S.get(key + ".ci_high")
        return "" if not lo or not hi else f"{fmt(lo['value'], unit)} to {fmt(hi['value'], unit)}"

    def both(key_a, key_b, unit):
        return f"{val(key_a, unit)}; {val(key_b, unit)}"

    # D-42: the founder firm against normal firms, five benchmarks, six windows
    BENCH5 = (
        ("sp", "S&P 500"),
        ("ind", "Industry average"),
        ("pr3", "Three closest competitors"),
        ("roa", "Firm matched on profitability"),
        ("pr", "Closest competitor"),
    )
    PANEL_NAME = {
        "slide": "Panel A. Trading days −30 to −2, before the announcement",
        "ann": "Panel B. Trading days −1 to +1, the announcement (well-dated dismissals)",
        "slideann": "Panel C. Trading days −30 to +1, the six-week window",
        "m12": "Panel D. 12 months from day +2",
        "m36": "Panel E. 36 months from day +2",
        "m60": "Panel F. 60 months from day +2",
    }
    rows, ids = [], []
    for title, sfx, unit, with_p in (
        ("Panel A. Return minus the benchmark's, mean (p)", "ret.mean", "pct", True),
        ("Panel B. Return minus the benchmark's, median (p)", "ret.median", "pct", True),
        ("Panel C. Dollar change against the benchmark, median per firm ($ million)", "usd.median", "usdm_cell", False),
    ):
        rows.append([title] + [""] * 7)
        for b, name in BENCH5:
            line = [name]
            for w in FV_MAIN:
                k = f"fv.founder.{b}.{w}.{sfx}"
                cell = val(k, unit)
                if with_p and k in S and S[k].get("p") is not None:
                    cell = f"{cell} ({pv(FV, k)})"
                line.append(cell)
                if w == "slideann" and k in S:
                    ids.append(k)
            line.append(val(f"fv.founder.{b}.slideann.ret.count", "count"))
            rows.append(line)
    t2 = table(
        "Table 3. Founder firms against normal firms: most of the loss comes before the announcement",
        [
            "Benchmark",
            "Days −30 to −2",
            "Days −1 to +1",
            "Days −30 to +1",
            "12 months",
            "36 months",
            "60 months",
            "N, days −30 to +1",
        ],
        rows,
        ids,
        "Founder dismissals for any reason but fraud. Each cell is the founder firm's return minus the benchmark's over the "
        "window; Section 4.1 defines the benchmarks. Days -1 to +1 use well-dated dismissals; months run from day +2. The dollar "
        "change is the return gap times the firm's market value at day -31, in 2023 dollars. In parentheses, p: one-sample "
        "t (mean) or Wilcoxon signed-rank (median), unadjusted; Table IA.5 gives intervals, the Holm adjustment and N for "
        "every window. N differs by benchmark because each needs its own data. Long-run means rest on a few firms.",
    )

    # Table IA.7: the dollar change against every benchmark
    drow, dids = [], []
    for w in FV_MAIN:
        drow.append([PANEL_NAME[w]] + [""] * 7)
        for b, name in BENCH5:
            k = f"fv.founder.{b}.{w}.usd"
            drow.append(
                [
                    name,
                    val(k + ".median", "usdm_cell"),
                    pv(FV, k + ".median"),
                    val(k + ".mean", "usdm_cell"),
                    pv(FV, k + ".mean"),
                    val(k + ".total_bn", "usdbn_cell"),
                    val(k + ".largest_loss_share", "pct"),
                    val(f"fv.founder.{b}.{w}.ret.count", "count"),
                ]
            )
            if k + ".median" in S:
                dids.append(k + ".median")
    t18 = table(
        "Table IA.7. Founder firms against normal firms in dollars: medians, means and totals",
        [
            "Benchmark",
            "$ million, median",
            "p",
            "$ million, mean",
            "p",
            "$ billion, total",
            "Largest single loss, share of total",
            "N",
        ],
        drow,
        dids,
        "The founder firm's return minus the benchmark's, times its market value at day -31, in 2023 dollars; below zero is a "
        "loss. The benchmarks are those of Table 3. p: Wilcoxon signed-rank (median) or one-sample t (mean), unadjusted. Totals "
        "and means rest on a few very large firms; the last column gives the largest single loss as a share of the total, which "
        "exceeds 100% when gains elsewhere offset part of it.",
    )

    # Table 4: $100 in the founder's firm and in each benchmark, from six weeks before the dismissal
    INV_PAIRS = (
        ("S&P 500", "fvinv.founder.firm", "fvinv.founder.sp", "fvinv.founder"),
        ("Industry average", "fvinv.founder.firm_ind", "fvinv.founder.ind", "fvinv.founder.ind"),
        ("Three closest competitors", "fvinv.founder.firm_pr3", "fvinv.founder.pr3", "fvinv.founder.pr3"),
        ("Closest competitor", "fvinv.founder.firm", "fvinv.founder.pr", "fvinv.founder"),
    )
    irow, iids = [], []
    for title, sfx in (
        ("Panel A. Value of $100 put in at day −31, median: founder's firm / benchmark", "median"),
        ("Panel B. Value of $100 put in at day −31, mean: founder's firm / benchmark", "mean"),
    ):
        irow.append([title] + [""] * 5)
        for name, fk, bk, nk in INV_PAIRS:
            line = [name]
            for h in FV_INV:
                line.append(f"{val(f'{fk}.{h}.{sfx}', 'usd2')} / {val(f'{bk}.{h}.{sfx}', 'usd2')}")
                if f"{fk}.{h}.{sfx}" in S:
                    iids.append(f"{fk}.{h}.{sfx}")
            irow.append(line + [val(f"{nk}.d1.count", "count")])
    t3 = table(
        "Table 4. $100 in a founder firm against $100 in normal firms, from six weeks before the dismissal",
        ["Benchmark", "Day +1", "12 months", "36 months", "60 months", "N at day +1"],
        irow,
        iids,
        "Founder dismissals for any reason but fraud. $100 is put in the founder's firm and in the benchmark at the close of "
        "trading day -31. It is valued at the close of day +1, then 12, 36 and 60 months after day +2, dividends reinvested. Each "
        "cell gives the founder's firm, then the benchmark, on the firings that have both, so the firm's value differs across "
        "rows. A delisted stock gets the delisting return of Section 4. The industry average and the three closest competitors "
        "are equal-weighted. The benchmarks are those of Table 3. N falls with the horizon as recent firings have not reached it. "
        "Medians of each column are not the median of each pair.",
    )

    # Table IA.4: how close the competitor is before the firing
    brow, bids = [], []
    for c, name, k in (
        ("founder", "Founders fired: closest competitor", "fvbal.founder"),
        ("founder", "Founders fired: three closest competitors (mean)", "fvbal3.founder"),
        ("forced", "All firings: closest competitor", "fvbal.forced"),
        ("retired", "Retirements: closest competitor", "fvbal.retired"),
        ("fraud", "Fraud firings (comparison): closest competitor", "fvbal.fraud"),
    ):
        brow.append(
            [
                name,
                val(f"{k}.prior12.firm.mean", "pct"),
                val(f"{k}.prior12.comp.mean", "pct"),
                val(f"fvprior.{c}.sp.mean", "pct") if k.startswith("fvbal.") else "",
                both(f"{k}.prior12.gap", f"{k}.prior12.gap_median", "pps"),
                pv(FV, f"{k}.prior12.gap"),
                f"{both(f'{k}.mcap.firm.median_bn', f'{k}.mcap.comp.median_bn', 'bn')} / "
                f"{both(f'{k}.roa.firm.median', f'{k}.roa.comp.median', 'pct')}",
                val(f"{k}.n", "count"),
            ]
        )
        bids += [f"{k}.prior12.firm.mean", f"{k}.prior12.comp.mean"]
    t15 = table(
        "Table IA.4. The competitor before the firing: prior return, size and profitability",
        [
            "Group",
            "Prior return, firm",
            "Prior return, competitor",
            "Prior return, S&P 500",
            "Gap to competitor, points: mean; median",
            "p",
            "Value, USD bn / ROA: firm; competitor",
            "N",
        ],
        brow,
        bids,
        "The competitors of Table 3. Prior return: the mean buy-and-hold return over trading days -282 to -31; the gap is the "
        "firm's minus the competitor's, mean and median, with a paired t test (p). For the three closest competitors each "
        "measure is first averaged over the three. Value and return on assets (ROA, EBITDA over assets) are medians at the "
        "fiscal year-end before. N counts firms with a competitor. The match runs from the 4-digit SIC code to the 3-digit "
        "code to the Sharadar industry (Section 4.1).",
    )

    # Table IA.5: the founder firm against every benchmark, with intervals and the Holm adjustment (D-42)
    rrow, rids = [], []
    for w in FV_MAIN:
        rrow.append([PANEL_NAME[w]] + [""] * 6)
        for b, name in BENCH5:
            k = f"fv.founder.{b}.{w}.ret"
            rrow.append(
                [
                    name,
                    val(k + ".mean", "pct"),
                    interval(k + ".mean", "pct"),
                    pv(FV, k + ".mean"),
                    val(k + ".mean.holm5_p", "p3"),
                    val(k + ".wmean", "pct"),
                    val(k + ".count", "count"),
                ]
            )
            if k + ".mean" in S:
                rids.append(k + ".mean")
    t16 = table(
        "Table IA.5. Founder firms against every benchmark: intervals and the Holm adjustment",
        ["Benchmark", "Mean", "95% interval", "p", "Holm p, five benchmarks", "Winsorised mean", "N"],
        rrow,
        rids,
        "The mean return gap of Table 3 with its 95% interval and one-sample t p. Holm adjusts across the five benchmarks "
        "of each window and was added after review. The winsorised mean clips returns at 1% and 99%. The benchmarks are "
        "defined in Section 4.1. Days -1 to +1 use well-dated dismissals.",
    )

    # Table IA.6: every group against its competitor, returns and dollars
    grow, gids = [], []
    for c, name in (
        ("forced", "All firings (the main sample)"),
        ("retired", "Retirements"),
        ("other", "Fired over performance or another reason"),
        ("scandal", "Fired over a personal scandal"),
        ("coup", "Fired in a boardroom coup"),
        ("fraud", "Fired over fraud (comparison)"),
        ("founder_fraud", "of which founders"),
    ):
        grow.append([name] + [""] * 7)
        for w in FV_MAIN:
            k = f"fv.{c}.pr.{w}"
            grow.append(
                [
                    FV_WIN[w][0],
                    val(k + ".ret.mean", "pct"),
                    val(k + ".ret.median", "pct"),
                    val(k + ".usd.mean", "usdm_cell"),
                    val(k + ".usd.median", "usdm_cell"),
                    val(k + ".usd.total_bn", "usdbn_cell"),
                    f"{val(f'fv.{c}.sp.{w}.ret.mean', 'pct')}; {val(f'fv.{c}.sp.{w}.usd.median', 'usdm_cell')}",
                    val(k + ".ret.count", "count"),
                ]
            )
            if k + ".ret.mean" in S:
                gids.append(k + ".ret.mean")
    t17 = table(
        "Table IA.6. Every group against its competitor: returns and dollars",
        [
            "Group and window",
            "Return gap, mean",
            "Return gap, median",
            "$ million, mean",
            "$ million, median",
            "$ billion, total",
            "Against the S&P 500: return gap, mean; $ million, median",
            "N",
        ],
        grow,
        gids,
        "The measures of Table 3 for every group: the firm's return minus its competitor's, and that gap times the firm's market "
        "value at day -31 in 2023 dollars. Days -1 to +1 uses well-dated departures; months run from day +2. One column sets the "
        "firm against the S&P 500 total return (SPY) instead. N counts departures with a competitor. Fraud firings are outside "
        "the main sample. Means and totals at 36 and 60 months rest on a few very large firms.",
    )
    # Table IA.31: checks added after review (D-41), founders against their competitor only (D-42)
    crow, cids = [], []
    for label, fa_ in (
        ("Every founder dismissal, closest competitor", "fv.founder.pr"),
        ("Founders clearly forced out, closest competitor", "fvrob.pushed.founder.pr"),
        ("Pairs in the same 4-digit SIC code only", "fvrob.sic4.founder.pr"),
        ("Mean of the two closest competitors", "fv.founder.pr2"),
        ("Mean of the three closest competitors", "fv.founder.pr3"),
        ("Mean of the four closest competitors", "fv.founder.pr4"),
        ("Mean of the five closest competitors", "fv.founder.pr5"),
    ):
        if f"{fa_}.slideann.ret.count" not in S:
            continue
        crow.append(
            [
                label,
                val(f"{fa_}.slideann.ret.mean", "pct"),
                pv(FV, f"{fa_}.slideann.ret.mean"),
                val(f"{fa_}.ann.ret.mean", "pct"),
                pv(FV, f"{fa_}.ann.ret.mean"),
                val(f"{fa_}.slideann.ret.count", "count"),
            ]
        )
        cids.append(f"{fa_}.slideann.ret.mean")
    t31 = table(
        "Table IA.31. Checks added after review: the founder firm against its competitors",
        ["Version", "Days −30 to +1, mean", "p", "Days −1 to +1, mean", "p", "N, six weeks"],
        crow,
        cids,
        "Founder dismissals for any reason but fraud; the founder firm's return minus its competitor's. These checks were added "
        "after the main results were known. Clearly forced out: founders the case check found pushed by a board vote, a demand "
        "to resign or a public disagreement. Same 4-digit SIC code: pairs whose competitor shares the firm's 4-digit code. Two "
        "to five closest: the mean return of the k firms nearest on the prior 12-month return, by the rule of Section 4.1; "
        "firms with fewer than k candidates drop out. Days -1 to +1 use well-dated dismissals. p: one-sample t, unadjusted.",
    )

    # Table IA.32: the founder results before and after the forced resignations coded as retirements join (D-44)
    D = SRC[D44]
    drows, dids = [], []

    def dv(when, key, unit):
        r = D.get(f"d44.{when}.{key}")
        return fmt(None if r is None else r.get("value"), unit)

    def dp(when, key):
        r = D.get(f"d44.{when}.{key}") or {}
        p_ = r.get("p")
        return "" if p_ is None else ("<0.001" if p_ < 0.001 else f"{p_:.3f}")

    def dn(when, key):
        r = D.get(f"d44.{when}.{key}") or {}
        return "" if r.get("n") is None else f"{int(r['n']):,}"

    for label, key, unit in (
        ("Founder dismissals kept", "fa.n_kept", "count"),
        ("Against the S&P 500, days −30 to +1, mean", "fv.founder.sp.slideann.ret.mean", "pct"),
        ("Against the industry average, days −30 to +1, mean", "fv.founder.ind.slideann.ret.mean", "pct"),
        ("Against the three closest competitors, days −30 to +1, mean", "fv.founder.pr3.slideann.ret.mean", "pct"),
        ("Against the firm matched on profitability, days −30 to +1, mean", "fv.founder.roa.slideann.ret.mean", "pct"),
        ("Against the closest competitor, days −30 to +1, mean", "fv.founder.pr.slideann.ret.mean", "pct"),
        ("Bankrupt within five years", "exit.forced_founder.bankruptcy_5y", "pct"),
        ("Revenue growth a year against the industry median, to year +3, median", "fg.founder.ind.rev.y3.median", "pp"),
        ("Revenue growth a year against the competitor, to year +3, median", "fg.founder.pr.rev.y3.median", "pp"),
    ) + tuple((lbl, k, u) for lbl, k, u in D44_ALPHA_ROWS):
        if f"d44.after.{key}" not in D and f"d44.before.{key}" not in D:
            continue
        drows.append(
            [
                label,
                dv("before", key, unit),
                dp("before", key),
                dn("before", key),
                dv("after", key, unit),
                dp("after", key),
                dn("after", key),
            ]
        )
        for when in ("before", "after"):
            if f"d44.{when}.{key}" in D:
                dids.append(f"d44.{when}.{key}")
    t32 = table(
        "Table IA.32. Adding the founders forced to resign: the founder results before and after",
        ["Measure", "Before", "p", "N", "After", "p", "N"],
        drows,
        dids,
        "Before: the sample without the three founders the database codes as retirements but the sources "
        "show were forced to resign: J.D. Edwards in 2002, Mednax in 2020 and Cypress Semiconductor in 2016. After: with them. "
        "Return measures are the founder firm's return minus the benchmark's over trading days -30 to +1, founder "
        "dismissals for any reason but fraud; p is a one-sample t test, unadjusted. Growth: median change in revenue growth a "
        "year against the benchmark, Wilcoxon p. Alphas: monthly six-factor intercept of an equal-weighted portfolio of "
        "founder firms held from day +1, Newey-West p. N counts founder firms measured, or portfolio months for the alphas.",
    )
    for k in dids:
        st = stat(
            D44,
            k,
            "D-44 " + k.replace("d44.", "").replace(".", " "),
            "count" if k.endswith(("n_kept", "count")) else "pct",
            "before/after",
            "d44",
        )
        if st:
            stats.append(st)

    return stats, [t2, t3], [t15, t16, t17, t18, t31, t32]


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
    fr_stats, fr_table = fr_exhibit()
    stats = stats + fr_stats
    fv_stats, fv_body, fv_appendix = fv_exhibit()
    ca_stats, ca_tables = cases_exhibits()
    fv_stats += ca_stats
    fv_appendix = list(fv_appendix) + ca_tables
    stats = stats + fv_stats
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
            "caveat": "Day 0 is the first trading day on or after the announcement that the CEO is leaving. Firings for fraud or crime are not in the sample. Reasons other than the checked conduct labels are model codes.",
        },
        stats,
        [
            table(
                "Table 5. At the announcement, a fraud dismissal is followed by a larger fall than a scandal dismissal",
                ["Group", "Mean", "Median", "t", "p", "N"],
                rows,
                ids,
                "Market-model abnormal return over trading days -1 to +1 around the announcement (day 0), on well-dated firings (dated by the "
                "database or from a dated source), fraud and legal violations excluded unless stated. N counts each row's firings. t: the t of the mean, "
                "or the Welch t of a difference; p is two-sided. Panel B: the first group's mean minus the second's; a positive number means a "
                "smaller fall in the first group. Founder, scandal and fraud labels were checked against the sources. The sex or relationship "
                f"row (n = {nv(RS, 'car.sex_or_relationship.mm_m1p1.mean')}) is small and its test has little power. Panel C reweights by size, prior return, "
                "profitability, leverage, founder and scandal flags and year (Table IA.13).",
            ),
            *fv_body,
            fr_table,
            *fv_appendix,
            table(
                "Table IA.14. Before, at and after the announcement, by group",
                ["Group", "Days -30 to -2", "p", "Days -1 to +1", "p", "Days +2 to +60", "p", "N"],
                drows,
                dids,
                "Days -30 to -2 and +2 to +60 are cumulative market-adjusted returns (firm minus market), used because a firing firm's alpha before the event "
                "is strongly negative and a market model would project it forward. Days -1 to +1 is the market-model return of Table 5. Events need every day of "
                "a window. N is the number of departures in the days -1 to +1 window; the outer windows differ by at most a few percent.",
            ),
            table(
                "Table IA.15. Why the board acted: abnormal returns over trading days −1 to +1 by coded reason",
                ["Coded primary reason", "Mean", "t", "p", "Holm p", "N"],
                rrows,
                [f"car.reason.{r}.mm_m1p1.mean" for r in reasons],
                "Firings for any reason but fraud or other legal violation, by the primary reason coded from the database notes, the 8-K filed within 10 days, cited press releases, Wikipedia and matched "
                "New York Times articles. Reasons with fewer than 10 cases are not shown. Holm p adjusts each p for the number of reasons "
                "tested. Financial-misconduct, sexual-conduct and relationship labels were checked against the sources; the others are model codes.",
            ),
            table(
                "Table IA.16. Personal scandals of sitting CEOs in the New York Times, 1998 to 2023",
                ["Company", "CEO", "First report", "Scandal", "Days -1 to +1"],
                scandal_rows(),
                [f"scandal.{g}.first_report.car_m1p1.mean" for g in ("all", "kept", "departed")],
                "Reports of personal misconduct by a sitting CEO of a sample firm, found by searching the New York Times Archive and checked against the sources. "
                "Panel B: the CEO departed within 12 months of the first report (CEO dismissal database, or a reported departure the "
                "database misses). Days -1 to +1: market-adjusted return around the first report. The table lists the "
                f"{len(SRC[SS].get('_cases', []))} of the {v(SS, 'scandal.n_events', 'count')} scandals found whose shares traded around the first report. "
                "The search finds only a few of the database's firings over "
                "a personal scandal, mostly at the largest firms, so the table describes prominent cases, not a sample.",
            ),
            table(
                "Table IA.17. The largest founders fired, among firings both codings read as forced",
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
                "Table IA.20. Long-run returns at 12, 36 and 60 months",
                ["Group", "12m", "36m", "60m", "p, 12m", "p, 36m", "p, 60m", "N, 36m"],
                rows,
                ids,
                "Medians of buy-and-hold returns from day +2 over 12, 36 and 60 months, all firings, with the Wilcoxon p. Panel A subtracts "
                "the market's buy-and-hold return; Panel B subtracts a matched firm in the same industry, with market value within 30 percent "
                "and the nearest return on assets. The last row gives means with t-test p; skewed returns can give means and medians of "
                "opposite sign. Delisted firms take their delisting return and then hold the market. N, 36m counts events at 36 months.",
            ),
            table(
                "Table IA.19. Calendar-time alpha after the announcement",
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
                "Table IA.21. Profitability against the matched firm, fiscal years 0 to +3",
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
    # The firing gap without and with controls (Table IA.18 has the full set), in the main table: the abstract's key
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
                "Table 7. Dismissing firms are delisted and go bankrupt far more often than retirement firms",
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
                "leverage, book-to-market, distress and loss. Table IA.18 adds the checks.",
            ),
            table(
                "Table 6. Dismissing firms are delisted more often than retirement firms in every size band",
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
                "Table IA.22. The board about two years after the departure",
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
        ("well-dated: by the database or from a dated source (announcement sample)", "flow.forced_dated"),
        ("Founder codes from the model, all firings", "flow.founder_model"),
        ("founders confirmed by the first review", "flow.founder_confirmed"),
        ("of which departures 1998 to 2023", "flow.founder_in_years"),
        ("of which with returns, firings over fraud or other legal violation excluded", "flow.founder_returns"),
        ("of which well-dated (announcement sample)", "flow.founder_dated"),
    ]
    flow_rows = [["Panel A. From the database to the samples", ""]] + [[name, v(DS, k, "count")] for name, k in flow]
    code_rows = []
    for c, lbl in (
        ("founder", "Founder codes checked against the sources"),
        ("fraud", "Fraud and legal-violation codes checked against the sources"),
        ("sex", "Sex and relationship codes checked against the sources"),
        ("personal", "Other personal-conduct codes checked against the sources"),
    ):
        code_rows += [
            [lbl, v(RF, f"code.{c}.n_reviewed", "count")],
            ["of which the model's code was kept", v(RF, f"code.{c}.n_kept", "count")],
        ]
    flow_rows += [["Panel B. The first review of the model's codes", ""]] + code_rows
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
            pv(RS, f"car.forced_founder.mm_{w}.mean"),
            v(RS, f"car.forced_founder.mm_{w}.median", "pct"),
            v(RS, f"car.forced.mm_{w}.mean", "pct"),
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
                f"car.forced_founder.mm_{w}.median",
                f"Median CAR, founder fired, {name}",
                "pct",
                "Wilcoxon",
                "founder",
            )
            for name, w in windows
        ]
        + [
            stat(RS, f"car.forced.mm_{w}.mean", f"Mean CAR, every firing, {name}", "pct", "one-sample t", "a")
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
                    ("n_reviewed", "checked against the sources", "count"),
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
            "caveat": "Pushed retirements and the strict sample rest on the evidence-based model coding, not on the case checks.",
        },
        stats,
        [
            table(
                "Table IA.12. Robustness",
                ["Specification", "Estimate", "p", "N", "Horizon"],
                rows,
                [k for _, _, k, _ in specs],
                "Each row changes one thing against the main tables. Evidence agrees: the CEO dismissal database codes the exit forced and the evidence-based coding "
                "(8-K, press releases, Wikipedia, New York Times) also reads it as forced. Pushed retirements: the database codes a retirement and the evidence reads it as forced. "
                "Pre-1998: departures announced 1992 to 1997, three-year return minus the index the firm itself reports in its proxy performance graph.",
            ),
            table(
                "Table IA.13. Well-dated and other firings",
                ["Characteristic", "Well-dated", "Other firings", "p", "N, well-dated", "N, other"],
                dsel_rows,
                dsel_ids,
                "Firings at S&P 1500 firms, 1998 to 2023, fraud and legal violations excluded. Well-dated: the announcement date comes from the "
                "database or a dated source checked case by case; the other firings are dated only by an 8-K or the day the CEO left office. Medians "
                "use a Mann-Whitney test and shares a chi-square test. Founder and scandal firings were dated from the sources, so more of them are "
                "well-dated. Table 5's reweighted return weights each well-dated firing by the inverse of its chance of being well-dated, from a "
                "logit on these traits and the year.",
            ),
            table(
                "Table IA.3. From the database to the main sample",
                ["Step", "N"],
                flow_rows,
                [k for _, k in flow] + code_ids,
                "Firings are database codes 3 and 4; firings over fraud or other legal violation leave the sample after the first review of their codes. A price history covers the announcement when the security trades from 60 days before day 0. Founder codes "
                "come from the evidence-based model coding; every one on a firing was checked against the sources, which also added founders the model had left unclear. "
                "Panel B: one coder; a code not kept was changed to another reason or to not a founder.",
            ),
            table(
                "Table IA.11. The founder firm's abnormal return in every announcement window",
                [
                    "Window (trading days)",
                    "Founder fired, mean",
                    "p",
                    "Founder fired, median",
                    "All dismissals, mean",
                    "N founders",
                ],
                win_rows,
                [f"car.forced_founder.mm_{w}.mean" for _, w in windows],
                "Market-model abnormal returns of founder firms around the announcement, well-dated dismissals for any reason but "
                "fraud; p is a one-sample t test against zero. All dismissals gives the same window for every dismissal in the "
                "main sample, founders included.",
            ),
            table(
                "Table IA.18. Delisting within 60 months, with controls and against matched firms",
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
    sections = [
        s
        for s in (sec_a(), sec_b(), sec_c(), sec_d(), sec_e(), sec_f(), sec_g(), sec_h(), sec_i(), sec_j(), sec_k())
        if s
    ]
    # every statistic a table cites or reads is registered, so its provenance travels with it
    CELL_SOURCES = {}
    have = {s["stat_id"] for sec in sections for s in sec["statistics"]}
    for sec in sections:
        for tb in sec["tables"]:
            CELL_SOURCES[tb["title"]] = match_cells(tb, tb.pop("cell_keys", []))
            for sid in tb["stat_ids"]:
                if sid in have or sid.replace("_v0", "") in have:
                    continue
                src = next((f for f in SRC if isinstance(SRC[f], dict) and sid in SRC[f]), None)
                if src:
                    u = "bn" if sid.endswith("mcap.median") else ("coef" if sid.startswith(("reg", "regc")) else "pct")
                    st = stat(src, sid, sid.replace("_", " "), u, "as in the table", "table")
                    if st:
                        st["stat_id"] = sid
                        sec["statistics"].append(st)
                        have.add(sid)
    files = sorted(p.name for p in OUT.glob("*_stats.json"))
    # cell-level sources for draft_paper.py's provenance gate (kept out of the payload, which MedTwin loads)
    (OUT / "table_cell_sources.json").write_text(json.dumps(CELL_SOURCES))
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
        ]
        + constants.as_payload(),
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
