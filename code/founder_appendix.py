"""Internet Appendix exhibits from the hand check of every founder departure (D-35, corrected per D-37 and D-38).

  (a) Founder firings, case by case: one row per founder firing kept (firm and year, founder, reason, pushed or
      unclear, successor type, three-year return against the D-37 competitor, outcome class, the founder's fate).
  (b) Excluded: planned successions, not firings: the 12 founder departures of D-37 item 1 with the quote that shows
      the handover was planned.
  (c) What happened to the founder: board seat, came back as CEO, started a new firm, went after the firm, legal
      action, died; cells under 10 are named, not given as a share.
Also the hired-CEO audit's sample and rates (D-37 item 5, D-38), and paper/founder_cases/new_pairs.csv: every founder
firing with its D-37 competitor, both SIC descriptions and the matching level, for a plain-terms check.

Outcome class (D-35 rule, first that applies): bankrupt, taken over, delisted other (within five years); otherwise the
three-year buy-and-hold return against the D-37 competitor: gained (above +10 points), lost (below -10), about even.

Inputs : analysis/out/{founder_value,returns}.parquet, founder_reason.load(), paper/founder_cases/*.csv,
         paper/d37_corrections.csv, paper/d38_corrections.csv, datasource.securities
Outputs: outputs/founder_appendix_stats.json; paper/founder_cases/new_pairs.csv
"""

import json
import pathlib
import re

import datasource
import founder_cases as fc
import founder_reason as fr
import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).parent
PAPER = HERE.parent / "paper"
CASES = PAPER / "founder_cases"
OUT = HERE.parent / "outputs"
GAIN, LOSS = 0.10, -0.10
MIN_CELL = 10
WHY = {"fraud": "fraud", "scandal": "personal scandal", "coup": "boardroom coup", "other": "performance or other"}
R = {}


def put(key, value, n):
    key = key.lower()
    R[key] = {
        "value": None if value is None or (isinstance(value, float) and np.isnan(value)) else float(value),
        "n": n,
    }


def outcome(r):
    kind = r["delist_kind_5y"]
    if kind == "bankruptcy":
        return "bankrupt"
    if kind == "acquired":
        return "taken over"
    if kind in ("delisted_other", "unknown") and r["delisted_5y"] == 1:
        return "delisted, other"
    m = r["pr_m36"]
    if pd.isna(m):
        return "no competitor" if pd.notna(r["bhar_3y"]) else "under 3 years"
    if m > GAIN:
        return "gained"
    if m < LOSS:
        return "lost"
    return "about even"


def successor_type(s):
    s = str(s or "")
    low = s.lower()
    if not s or re.match(r"(?i)^(not found|unverified|not read|not verified|nan)", s):
        return "not recorded"
    if "interim" in low:
        return "interim"
    if re.search(r"outsider|outside|from (?!within)|hired from", low):
        return "outsider"
    if re.search(r"insider|\bcoo\b|chief operating|president|\bcfo\b|co-founder|director|board member|internal", low):
        return "insider"
    return "named, type not recorded"


def fate(e, r):
    bits = []
    bits.append("stayed on the board" if e in fc.STAYED else "left the board" if e in fc.LEFT else "board unclear")
    if e in fc.BOOMERANG:
        yr, w = fc.BOOMERANG[e]
        bits.append(f"back as CEO {yr}" + (" (after 5 years)" if w == "outside" else ""))
    if e in fc.NEW_FIRM:
        bits.append("new firm: " + fc.NEW_FIRM[e].split(",")[0].split(" (")[0])
    if e in fc.WENT_AFTER:
        bits.append("went after the firm")
    if is_legal(r.get("legal")):
        bits.append("legal action")
    if str(r.get("died") or "").lower().startswith("y"):
        bits.append("died within 5 years")
    return "; ".join(bits)


def is_legal(s):
    s = str(s or "")
    if re.match(r"(?i)^(none|not found|no\b|nan)", s):
        return False
    return bool(re.search(r"(?i)indict|charg|convict|sued|lawsuit|\bSEC\b|settle|plea|complaint|^y", s))


def name(r):
    # "Firm, 2018", not "Firm (2018)": the citation gate reads "Name (year)" as an author-year citation
    return f"{str(r['coname']).title()}, {str(r['event_date'])[:4]}"


def main():
    cases = pd.read_csv(CASES / "founder_cases.csv")
    corr = pd.concat([pd.read_csv(PAPER / f) for f in ("d37_corrections.csv", "d38_corrections.csv")])
    dropped = set(corr.loc[corr["field"] == "sample", "event_id"].astype(int))
    f = fr.load()
    founders = f[f["who"] == "founder"].copy()
    fv = pd.read_parquet(HERE / "out" / "founder_value.parquet")
    fv = fv[["event_id", "pr_ticker", "pr_level", "sicindustry", "pr_sicindustry", "pr_m36", "pr_m36_usd", "mv31"]]
    founders = founders.merge(fv, on="event_id", how="left")
    text = cases[
        ["event_id", "push_class", "successor", "legal", "died", "push_quote", "board_fate", "verdict"]
    ].drop_duplicates("event_id")
    m = founders.merge(text, on="event_id", how="left")
    m["outcome"] = m.apply(outcome, axis=1)
    m["successor_type"] = m["successor"].map(successor_type)
    m = m.sort_values(["event_date", "event_id"])
    n = len(m)
    put("fa.n_kept", n, n)
    put("fa.n_planned_dropped", len(dropped & set(cases["event_id"])), len(cases))
    # D-44: forced resignations the database coded as retirements, added to the case file from the scan
    d44 = PAPER / "d44_corrections.csv"
    added = set()
    if d44.exists():
        c44 = pd.read_csv(d44)
        added = set(c44.loc[c44["field"] == "code", "event_id"].astype(int))
    n_db = int((~cases["event_id"].isin(added)).sum())
    put("fa.n_checked", n_db, n_db)
    put("fa.n_forced_resign_added", len(added & set(cases["event_id"])), len(cases))
    scan = CASES / "forced_resign_scan.csv"
    if scan.exists():
        sc = pd.read_csv(scan)
        n_scan = len(sc)
        put("fa.n_retirements_scanned", n_scan, n_scan)
        if "second_pass" in sc:
            put("fa.n_forced_resign_unclear", int((sc["second_pass"] == "unclear").sum()), n_scan)

    # (a) case by case
    rows = []
    for r in m.to_dict("records"):
        e = int(r["event_id"])
        g = r["pr_m36"]
        rows.append(
            [
                name(r),
                str(r["exec_fullname"]),
                WHY.get(r["why"], r["why"]),
                str(r["push_class"] or "unclear"),
                r["successor_type"],
                "–" if pd.isna(g) else f"{g * 100:+.0f}",
                r["outcome"],
                fate(e, r),
            ]
        )
    # outcome classes, by reason group (counts)
    for why in ("all", "main", "fraud"):
        x = m if why == "all" else m[m["why"] == "fraud"] if why == "fraud" else m[m["why"] != "fraud"]
        for cls, k in x["outcome"].value_counts().items():
            put(f"fa.outcome.{why}.{cls.replace(' ', '_').replace(',', '')}", int(k), len(x))
        put(f"fa.outcome.{why}.n", len(x), len(x))
    for cls, k in m["push_class"].fillna("unclear").value_counts().items():
        put(f"fa.push.{cls.replace(' ', '_')}", int(k), n)

    # (b) excluded planned successions
    ex = cases[cases["event_id"].isin(dropped)].sort_values("event_date")
    ex_rows = []
    for r in ex.to_dict("records"):
        q = re.sub(r"\s+", " ", str(r["push_quote"])).strip()
        q = re.sub(r"\s*\([^()]*\b(19|20)\d{2}\b[^()]*\)", "", q)  # a dated source in brackets reads as a citation
        q = q if len(q) <= 170 else q[:167].rsplit(" ", 1)[0] + "..."
        ex_rows.append([name(r), str(r["exec_fullname"]), q])

    # (c) what happened to the founder
    ids = set(m["event_id"].astype(int))
    fates = {
        "stayed on the board": [e for e in ids if e in fc.STAYED],
        "left the board": [e for e in ids if e in fc.LEFT],
        "board seat not established": [e for e in ids if e not in fc.STAYED and e not in fc.LEFT],
        "came back as CEO within five years": [e for e in ids if e in fc.BOOMERANG and fc.BOOMERANG[e][1] == "within"],
        "started or led a new firm": [e for e in ids if e in fc.NEW_FIRM],
        "went after the firm": [e for e in ids if e in fc.WENT_AFTER],
        "legal action naming the founder": [int(r["event_id"]) for r in m.to_dict("records") if is_legal(r["legal"])],
        "died within five years": [
            int(r["event_id"]) for r in m.to_dict("records") if str(r["died"] or "").lower().startswith("y")
        ],
    }
    by_id = {int(r["event_id"]): r for r in m.to_dict("records")}
    fate_rows = []
    for label, es in fates.items():
        k = len(es)
        put(f"fa.fate.{label.replace(' ', '_')}", k, n)
        if k >= MIN_CELL:
            cell = f"{k} ({k / n * 100:.0f}%)"
            names = ""
        else:
            cell = str(k)
            parts = []
            for e in sorted(es, key=lambda e: str(by_id[e]["event_date"])):
                r = by_id[e]
                extra = ""
                if e in fc.BOOMERANG:
                    extra = f", back {fc.BOOMERANG[e][0]}"
                elif e in fc.NEW_FIRM:
                    extra = f": {fc.NEW_FIRM[e].split(' (')[0]}"
                parts.append(f"{name(r)}, {str(r['exec_fullname']).split(',')[0]}{extra}")
            names = "; ".join(parts)
        fate_rows.append([label, cell, names])

    # the hired-CEO audit (D-37 item 5, D-38)
    h = pd.read_csv(CASES / "hired_audit.csv")
    nh = len(h)
    put("fa.audit.hired.n", nh, nh)
    for v, key in (("not a firing", "planned"), ("redate", "redate"), ("recode reason", "recode"), ("keep", "keep")):
        put(f"fa.audit.hired.{key}", int((h["verdict"] == v).sum()), nh)
    nf = int((cases["in_h1"] == "y").sum())
    put("fa.audit.founder.n", nf, nf)
    put("fa.audit.founder.planned", len(dropped & set(cases.loc[cases["in_h1"] == "y", "event_id"])), nf)

    # new founder pairs for a plain-terms check
    names_tbl = datasource.securities("SEP")[["ticker", "name"]].drop_duplicates("ticker")
    nm = dict(zip(names_tbl["ticker"], names_tbl["name"]))
    pairs = m[
        ["event_id", "coname", "ticker", "event_date", "why", "sicindustry", "pr_ticker", "pr_sicindustry"]
    ].copy()
    pairs["pr_name"] = pairs["pr_ticker"].map(nm)
    pairs["pr_level"] = m["pr_level"].values
    pairs = pairs[
        [
            "event_id",
            "coname",
            "ticker",
            "event_date",
            "why",
            "sicindustry",
            "pr_ticker",
            "pr_name",
            "pr_sicindustry",
            "pr_level",
        ]
    ]
    pairs.sort_values("event_id").to_csv(CASES / "new_pairs.csv", index=False)
    for level, k in m["pr_level"].fillna("none").value_counts().items():
        put(f"fa.pairs.level.{level}", int(k), n)

    pair_rows = []
    for r in pairs.merge(m[["event_id", "event_date"]].rename(columns={"event_date": "d"}), on="event_id").to_dict(
        "records"
    ):
        pair_rows.append(
            [
                f"{str(r['coname']).title()}, {str(r['event_date'])[:4]}",
                str(r["sicindustry"] or "–"),
                "–" if pd.isna(r["pr_name"]) else str(r["pr_name"]).title(),
                "–" if pd.isna(r["pr_sicindustry"]) else str(r["pr_sicindustry"]),
                {"sic4": "4-digit SIC", "sic3": "3-digit SIC", "industry": "Sharadar industry"}.get(
                    r["pr_level"], "none"
                ),
            ]
        )
    R["_tables"] = {"cases": rows, "excluded": ex_rows, "fates": fate_rows, "pairs": pair_rows}
    (OUT / "founder_appendix_stats.json").write_text(json.dumps(R, indent=1, default=str))
    print(n, "founder firings kept;", len(ex_rows), "excluded;", m["outcome"].value_counts().to_dict())
    print(m["pr_level"].fillna("none").value_counts().to_dict())


if __name__ == "__main__":
    main()
