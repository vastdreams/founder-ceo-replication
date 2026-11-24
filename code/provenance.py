"""Provenance for every statistic the paper prints (operator, 25 Nov 2026).

combine_results.stat() attaches, to each statistic, where it comes from: the results file and key, the script and
function that computed it, the input data that script reads, the window and N, and a one-line formula. The script
and function are found by reading each producer's source (the function that writes the results file); the inputs are
declared here once per script. draft_paper.py refuses to print a number whose provenance is incomplete and writes
paper/PROVENANCE.csv, one row per printed number.
"""

import ast
import pathlib
import re

HERE = pathlib.Path(__file__).parent

GENTRY = "Gentry et al. (2021) CEO dismissal database (gentry.csv), with paper/date_corrections.csv, d37_corrections.csv, d44_corrections.csv"
SEP = "Sharadar SEP daily prices (sharadar.sep, closeadj)"
SF1 = "Sharadar SF1 annual fundamentals (sharadar.sf1, ARY)"
ACT = "Sharadar corporate actions (sharadar.actions)"
SPY = "FMP SPY close and dividends (public.fmp_daily_prices, public.fmp_dividends)"
FF = "Kenneth French five factors and momentum (world.ff5_daily, world.mom_daily)"
CODES = "evidence-based coding (code_events.py, DeepSeek) with the case checks (paper/founder_review.csv, paper/founder_cases/*.csv)"

# results file -> (producing script, inputs)
PRODUCERS = {
    "returns_stats.json": ("stats_returns.py", [GENTRY, SEP, FF, CODES]),
    "ops_stats.json": ("stats_ops.py", [GENTRY, SEP, SF1, ACT, CODES]),
    "board_stats.json": ("board_outcomes.py", [GENTRY, "SEC DEF 14A proxy statements (extract_board.py cache)"]),
    "coding_stats.json": ("founder_final.py", [GENTRY, CODES]),
    "pre1998_stats.json": ("pre1998_tsr.py", [GENTRY, "SEC proxy-statement performance graphs, 1992-1997"]),
    "describe_stats.json": ("describe.py", [GENTRY, SF1, SEP]),
    "alpha_stats.json": ("calendar_alpha.py", [GENTRY, SEP, FF]),
    "scandal_stats.json": ("scandal_stats.py", ["New York Times Archive API matches (scandal_scan.py)", SEP]),
    "referee_stats.json": ("referee_checks.py", [GENTRY, SEP, SF1, FF, CODES]),
    "founder_reason_stats.json": ("founder_reason.py", [GENTRY, SEP, CODES]),
    "founder_value_stats.json": ("founder_value.py", [GENTRY, SEP, SF1, ACT, SPY, "CPI-U (analysis/cpi_u.csv)", CODES]),
    "founder_value_versions.json": ("founder_value.py", [GENTRY, SEP, SF1, ACT, SPY, CODES]),
    "founder_appendix_stats.json": ("founder_appendix.py", ["paper/founder_cases/*.csv (case checks)", GENTRY]),
    "screen_stats.json": ("screen.py", [GENTRY, CODES]),
    "founder_growth_stats.json": (
        "founder_growth.py",
        [SF1, ACT, "founder_value.py matches (analysis/out/founder_value.parquet)"],
    ),
    "founder_alpha_stats.json": ("founder_alpha.py", [GENTRY, SEP, SPY, FF, CODES]),
    "d44_stats.json": ("d44_compare.py", ["outputs/*_pre_d44.json and the current results files"]),
    "founder_timing_stats.json": (
        "founder_timing.py",
        ["EDGAR 8-K acceptance times", SEP, SPY, FF, "Alpha Vantage 1-minute bars"],
    ),
    "founder_missed_stats.json": (
        "founder_missed_check.py",
        [
            "Wikidata P112 founders (founder_universe/wikidata_founders.csv)",
            "analysis/out/founder_value.parquet export",
        ],
    ),
}

_FUNC_CACHE = {}


def producer_function(script: str, results_file: str) -> str:
    """The function in `script` whose body names the results file (else the one that writes JSON), read from source."""
    key = (script, results_file)
    if key in _FUNC_CACHE:
        return _FUNC_CACHE[key]
    src = (HERE / script).read_text()
    tree = ast.parse(src)
    funcs = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    seg = {n.name: ast.get_source_segment(src, n) or "" for n in funcs}
    writes = ("write_text(json.dumps", "json.dump(")
    best = next((f for f, b in seg.items() if results_file in b and any(w in b for w in writes)), None)
    best = best or next(
        (f for f, b in seg.items() if any(w in b for w in writes) and re.search(r"OUT\s*/|STATS|_stats", b)), None
    )
    best = best or next((f for f, b in seg.items() if results_file in b), None)
    _FUNC_CACHE[key] = best or "main"
    return _FUNC_CACHE[key]


def formula(key: str, test: str, unit: str) -> str:
    """One-line formula for a statistic, from its key family."""
    k = key
    last = k.split(".")[-1]
    if last == "holm" or k.endswith("holm5_p"):
        return "Holm step-down adjustment of the family's p-values"
    if last == "mde":
        return "2.8 x standard error (80% power, 5% two-sided)"
    if ".ctime." in k:
        return "intercept of daily portfolio return minus rf regressed on the factors, Newey-West lag 5" + (
            "; times days held" if last == "total" else ""
        )
    if k.startswith("fwdalpha."):
        return "intercept of monthly portfolio return minus rf regressed on the factors, Newey-West lag 6"
    if re.search(r"\.(slide|ann|slideann|m12|m36|m60|slide_wd|slideann_wd)\.usd\.", k):
        return (
            "(firm buy-and-hold return - benchmark return) x market value at the close of day -31, 2023 dollars; "
            + last
        )
    if re.search(r"\.(slide|ann|slideann|m12|m36|m60|slide_wd|slideann_wd)\.ret\.", k):
        return "prod(1+r_firm) - prod(1+r_benchmark) over the window; " + last + " across firms"
    if k.startswith(("car.", "cardiff.", "strict.", "rob.forced")) or "mm_m1p1" in k:
        return "sum over the window of r_it - (alpha_i + beta_i r_mt), alpha and beta from days -250 to -30; " + last
    if k.startswith("tm."):
        return "firm return minus S&P 500 return over the window (gap, open-to-close or close-to-close); " + last
    if "inv_" in k or k.startswith("fvinv."):
        return "100 x (1 + buy-and-hold return) from the close of day -31; " + last
    if k.startswith(("exit.", "exitdiff.")) or "delisted" in k or "bankrupt" in k:
        return "share of firms followed for the horizon whose stock left the price file (by the corporate action) within it"
    if k.startswith(("fg.", "fgatt.", "fgpath.")):
        return "(firm change - benchmark change) in the outcome, after minus before the dismissal; " + last
    if k.startswith(("bhar.", "mbhar.")):
        return "prod(1+r_firm) - prod(1+r_benchmark) from day +2; " + last
    if unit == "count" or last in ("n", "count") or k.startswith(("fa.", "fmiss.", "screen.", "code.", "b.")):
        return "count of events meeting the rule"
    if unit in ("pct", "pp") and last in ("share", "mean", "median"):
        return f"{last} of the measure across events"
    return f"{last} computed as described by the test: {test or 'descriptive'}"


def attach(stat: dict, results_file: str, key: str, unit: str, test: str) -> dict:
    script, inputs = PRODUCERS.get(results_file, (None, None))
    stat["provenance"] = {
        "results_file": f"outputs/{results_file}",
        "key": key,
        "script": f"analysis/{script}" if script else None,
        "function": producer_function(script, results_file) if script else None,
        "inputs": inputs,
        "window": stat.get("period"),
        "n": stat.get("n"),
        "formula": formula(key, test, unit),
    }
    return stat


REQUIRED = ("results_file", "key", "script", "function", "inputs", "window", "formula")


def complete(stat: dict) -> list:
    """Missing provenance fields of a statistic (empty when complete)."""
    p = stat.get("provenance") or {}
    return [f for f in REQUIRED if not p.get(f)]


ALLOWED_LITERALS = (
    r"Tables? (IA\.)?\d+(\s*(,|and|to)\s*(IA\.)?\d+)*",
    r"Figures? (IA\.)?\d+",
    r"Sections? \d+(\.\d+)?",
    r"Panels? [A-Z]",
    r"^#+ \d+(\.\d+)?\.?",
    r"S&P (500|1500)",
    r"8-K",
    r"Item \d+\.\d+",
    r"[34]-digit",
    r"\bH[1-5]\b",
    r"#MeToo",
    r"Form 4",
    r"Appendix [A-Z]",
    r"D-\d+",
    r"\b[Dd]ay 0\b",
    r"\b[Yy]ear 0\b",
    r"[Ee]quation \(\d\)",
)


def template_literals(text: str) -> list:
    """Numbers typed into the template outside placeholders, references and names (should be none)."""
    t = re.sub(r"\{\{[^}]*\}\}", "", text)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    t = re.sub(r"\$\$.*?\$\$", "", t, flags=re.S)
    t = re.sub(r"@[a-z0-9]+", "", t)
    out = []
    for i, ln in enumerate(t.split("\n"), 1):
        s = ln
        for a in ALLOWED_LITERALS:
            s = re.sub(a, lambda m: " " * len(m.group()), s)
        for m in re.finditer(r"(?<![A-Za-z\d.])[-−+]?\$?\d[\d,.]*%?", s):
            out.append((i, m.group(), ln[max(0, m.start() - 30) : m.end() + 20]))
    return out
