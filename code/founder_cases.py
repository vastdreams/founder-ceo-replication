"""The 55 well-dated founder firings of the main sample, one row each, for the case studies (D-35).

Selection is the paper's own: founder_reason.load(), cell founder x main (every reason but fraud), with a three-day
announcement return (well-dated firings only). Nothing is recoded here.

Per firing: identifiers, the database's notes and sources, the reason code, the date source; the 3-day market-model
return; the 1-, 3- and 5-year buy-and-hold return minus the matched competitor (ops_matched: industry, size, ROA);
the 3-year return minus the S&P 500 and the 3-year dollar changes (founder_value, D-34); the 5-year delisting class;
whether the fired CEO still sits on the board about two years later (board_outcomes, from proxy statements).
The D-35 shareholder class is applied by the first rule that holds.

Second step (track): every DEF 14A the firm filed in the five years after the announcement, from the server's proxy
cache, is searched for the founder's surname. A match counts as a board seat only where director words ("director
since", "nominee", "has served as a director", a class or term of office) are within 300 characters; the snippet is
kept so each reading can be checked by hand. A match next to "Chief Executive Officer" is flagged for a possible
return as CEO and then checked against press and filings by hand. A proxy not in the cache is listed as not held.

Third step (batch X, run locally): one coder's batch of the case list, from paper/founder_cases/batch_X.json and the
server numbers (founder_cases_data.csv, copied from the server), into batch_X.csv and batch_X.md.
Fourth step (merge, run locally): the five batches into founder_cases.csv and CASES.md.

Run on the research server:  ~/fce-venv/bin/python analysis/founder_cases.py [track]
Run locally:                 python3 analysis/founder_cases.py batch A | merge
Output: analysis/out/founder_cases_data.csv, analysis/out/founder_cases_board.jsonl (server only; proxy snippets are
        not committed, rebuild with track);
        paper/founder_cases/founder_cases.csv, paper/founder_cases/CASES.md (local)
"""

import gzip
import json
import pathlib
import re
import sys

import founder_reason as fr
import numpy as np
import pandas as pd

HERE = pathlib.Path(__file__).parent / "out"
DATA_END = pd.Timestamp("2026-06-30")  # last month of the price data (Sharadar to June 2026)
GAIN, LOSS = 0.10, -0.10  # D-35, the analyst's proposed thresholds on the 3-year matched return


def shareholder_class(r):
    kind = r["delist_kind_5y"]
    if kind == "bankruptcy":
        return "bankrupt"
    if kind == "acquired":  # the pack's label for a takeover (event_study.delist_return)
        return "taken over"
    if kind in ("delisted_other", "unknown") and r["delisted_5y"] == 1:
        return "delisted, other"
    m = r["mbhar_3y"]
    if pd.isna(m):
        if pd.notna(r["bhar_3y"]):
            return "no matched competitor"  # the 3-year horizon is complete but the pack found no match
        if pd.Timestamp(r["event_date"]) + pd.Timedelta(days=3 * 365 + 60) > DATA_END:
            return "not yet 3 years"
        return "no 3-year return"  # left the price file or stopped trading without a coded delisting
    if m > GAIN:
        return "shareholders gained"
    if m < LOSS:
        return "shareholders lost"
    return "about even"


def main():
    f = fr.load()
    c = fr.cell(f, "founder", "main")
    c = c[c["car_mm_m1p1"].notna()].copy()
    assert len(c) == 55, len(c)
    c["in_55"] = 1
    extra = HERE / "h1_list.csv"  # the coordinator's case list (H1 founders and flagged others), if copied here
    if extra.exists():
        ids = set(pd.read_csv(extra)["event_id"]) - set(c["event_id"])
        x = f[f["event_id"].isin(ids)].copy()
        x["in_55"] = 0
        c = pd.concat([c, x], ignore_index=True)
        print("extra events from h1_list:", len(ids), "found:", len(x))
    keep = [
        "event_id", "coname", "ticker", "exec_fullname", "event_date", "day0", "date_source", "why", "reason",
        "cik", "gvkey", "fyear", "left_ceo_office", "notes", "sources", "car_mm_m1p1", "pre",
        "bhar_3y", "delisted_5y", "delist_kind_5y", "in_55", "dated",
    ]  # fmt: skip
    c = c[keep]
    om = pd.read_parquet(HERE / "ops_matched.parquet")[["event_id", "ctrl_ticker", "mbhar_1y", "mbhar_3y", "mbhar_5y"]]
    fv = pd.read_parquet(HERE / "founder_value.parquet")
    fv = fv[["event_id", "mv31", "firm_m36", "sp_m36", "roa_m36", "roa_m36_usd", "sp_m36_usd", "pr_m36_usd"]]
    bo = pd.read_parquet(HERE / "board_outcomes.parquet")[["event_id", "ceo_stays_director", "director_turnover"]]
    dd = pd.read_parquet(HERE / "delist_dates.parquet")[["event_id", "bankruptcy_date"]]
    c = c.merge(om, on="event_id", how="left").merge(fv, on="event_id", how="left")
    c = c.merge(bo, on="event_id", how="left").merge(dd, on="event_id", how="left")
    c["sp_excess_3y"] = c["sp_m36"]  # founder_value stores benchmark columns as firm minus benchmark
    c["shareholder_class"] = c.apply(shareholder_class, axis=1)
    c = c.sort_values("event_date")
    c.to_csv(HERE / "founder_cases_data.csv", index=False)
    print(len(c), c["shareholder_class"].value_counts().to_dict())
    print(pd.crosstab(c["shareholder_class"], c["why"]))
    print("stays on board (proxy ~2y):", c["ceo_stays_director"].value_counts(dropna=False).to_dict())
    print("matched 3y found:", int(c["mbhar_3y"].notna().sum()), "sp 3y found:", int(c["sp_excess_3y"].notna().sum()))
    print("mv31 found:", int(np.isfinite(c["mv31"]).sum()))


DIRECTOR = re.compile(
    r"(?i)director since|nominee|has served as (a|our) director|member of (the|our) board|class (i{1,3}|one|two|three)\b"
    r"|term (expir|ending)|chairman emeritus|chairman of the board|non-executive chair|executive chair"
)
CEO = re.compile(r"(?i)chief executive officer")


def surname(full):
    full = re.sub(r",? (Ph\.D\.|M\.D\.|D\.Sc\.|P\.E\.|III|II|Jr\.)", "", str(full)).replace('"', "").strip()
    return full.split()[-1]


def track():
    sys.path.insert(0, str(pathlib.Path.home() / "world_raw"))
    import datasource  # noqa: E402
    from extract_docs import text_of  # noqa: E402

    docs = pathlib.Path.home() / "world_raw/sec/docs/DEF14A"
    c = pd.read_csv(HERE / "founder_cases_data.csv", parse_dates=["event_date"])
    px = datasource.sec_filings(["DEF 14A"])
    out = open(HERE / "founder_cases_board.jsonl", "w")
    for _, r in c.iterrows():
        if pd.isna(r["cik"]):
            out.write(json.dumps({"event_id": int(r["event_id"]), "note": "no CIK"}) + "\n")
            continue
        sn = surname(r["exec_fullname"])
        f = px[(px["cik"] == int(r["cik"])) & (px["filing_date"] > r["event_date"])]
        f = f[f["filing_date"] <= r["event_date"] + pd.Timedelta(days=5 * 365 + 60)].sort_values("filing_date")
        for _, q in f.iterrows():
            fn = docs / f"{int(q['cik'])}_{q['accession']}.gz"
            rec = {
                "event_id": int(r["event_id"]),
                "filing_date": str(q["filing_date"].date()),
                "accession": q["accession"],
            }
            if not fn.exists():
                rec["held"] = False
                out.write(json.dumps(rec) + "\n")
                continue
            text = text_of(gzip.open(fn).read())
            hits = [m.start() for m in re.finditer(rf"\b{re.escape(sn)}\b", text)]
            director, ceo, snip = False, False, ""
            for h in hits:
                w = text[max(0, h - 300) : h + 300]
                if DIRECTOR.search(w) and not director:
                    director, snip = True, w.replace("\n", " ")
                if CEO.search(text[h : h + 150]):
                    ceo = True
            rec.update(held=True, surname=sn, hits=len(hits), director=director, ceo_near=ceo, snippet=snip[:600])
            out.write(json.dumps(rec) + "\n")
    out.close()


CASES = pathlib.Path(__file__).resolve().parents[1] / "paper" / "founder_cases"


def pct(x, nd=0):
    return "n/a" if pd.isna(x) else f"{x * 100:+.{nd}f}%"


def usd(x):
    if pd.isna(x):
        return "n/a"
    return (
        f"{'-' if x < 0 else '+'}${abs(x) / 1000:.1f} billion"
        if abs(x) >= 1000
        else f"{'-' if x < 0 else '+'}${abs(x):.0f} million"
    )


NUM = {
    "car_3d": "car_mm_m1p1",
    "slide_pre": "pre",
    "matched_1y": "mbhar_1y",
    "matched_3y": "mbhar_3y",
    "matched_5y": "mbhar_5y",
    "sp500_3y": "sp_excess_3y",
}
CASE_FIELDS = [
    "what", "cause", "cause_source", "how", "was_it_a_push", "push_quote", "successor", "successor_type",
    "board_fate", "board_source", "boomerang", "boomerang_source", "next_role", "next_source", "legal",
    "legal_source", "died_within_5y", "notable", "news_check", "competitor_plausible", "competitor_why", "verdict",
]  # fmt: skip


def batch(letter):
    """One batch of the coordinator's case list: h1_list.csv sorted by event_id, rows cut by BATCHES."""
    h = pd.read_csv(CASES / "h1_list.csv").sort_values("event_id").reset_index(drop=True)
    lo, hi = BATCHES[letter]
    ids = list(h["event_id"].iloc[lo:hi])
    d = pd.read_csv(CASES / "founder_cases_data.csv")
    a = pd.DataFrame(json.load(open(CASES / f"batch_{letter}.json")))
    assert set(a["event_id"]) == set(ids), set(ids) ^ set(a["event_id"])
    m = h[h["event_id"].isin(ids)][["event_id", "in_h1", "why_not_in_h1", "pr_m36"]]
    m = m.merge(d, on="event_id", how="left").merge(a, on="event_id", how="left").sort_values("event_id")
    for k, col in NUM.items():
        m[k] = m[col]
    m["usd_vs_matched_3y_musd"] = m["mbhar_3y"] * m["mv31"]  # same match as the percentage; mv31 in 2023 $m
    m["usd_vs_sp500_3y_musd"] = m["sp_m36_usd"]
    keep = [
        "event_id", "coname", "ticker", "exec_fullname", "event_date", "date_source", "dated", "why", "reason",
        "in_55", "in_h1", "why_not_in_h1", "shareholder_class", *NUM, "pr_m36", "usd_vs_matched_3y_musd",
        "usd_vs_sp500_3y_musd", "mv31", "delist_kind_5y", "bankruptcy_date", "ctrl_ticker", "competitor_name",
        "competitor_ff_industry", "prior_return_match_name", *CASE_FIELDS,
    ]  # fmt: skip
    m[keep].to_csv(CASES / f"batch_{letter}.csv", index=False)
    md = [f"# Founder firing cases, batch {letter} ({len(m)} cases)", "", BATCH_NOTE, ""]
    for _, r in m.iterrows():
        md += [
            f"## {r['event_id']}. {r['coname'].title()}: {r['exec_fullname']} ({r['event_date']})",
            "",
            f"- **Sample:** reason code {r['reason']} ({r['why']}); date from {r['date_source']}; "
            f"{'well-dated' if r['dated'] == 1 else 'not well-dated'}; "
            f"{'in H1' if r['in_h1'] == 'y' else 'not in H1: ' + str(r['why_not_in_h1'])}.",
            f"- **What happened:** {r['what']}",
            f"- **Why (sources):** {r['cause']} Sources: {r['cause_source']}",
            f"- **How:** {r['how']}. **Push or planned:** {r['was_it_a_push']}: {r['push_quote']}",
            f"- **Successor:** {r['successor']} ({r['successor_type']}).",
            f"- **Shareholders:** {r['shareholder_class']}. Three-day return {pct(r['car_3d'], 1)}; slide before "
            f"{pct(r['slide_pre'], 1)}; three years against the matched firm {pct(r['matched_3y'])} "
            f"({usd(r['usd_vs_matched_3y_musd'])}), against the S&P 500 {pct(r['sp500_3y'])} "
            f"({usd(r['usd_vs_sp500_3y_musd'])}).",
            f"- **Competitor:** {r['competitor_name'] if pd.notna(r['competitor_name']) else 'none'}; plausible: "
            f"{r['competitor_plausible']}. {r['competitor_why']}",
            f"- **Founder afterwards:** board: {r['board_fate']} ({r['board_source']}). Came back as CEO: "
            f"{r['boomerang']}{' (' + r['boomerang_source'] + ')' if r['boomerang_source'] else ''}. Next: "
            f"{r['next_role']}{' (' + r['next_source'] + ')' if r['next_source'] else ''}. Legal: {r['legal']}"
            f"{' (' + r['legal_source'] + ')' if r['legal_source'] else ''}. Died within five years: "
            f"{r['died_within_5y']}.",
            f"- **Notable:** {r['notable']}",
            f"- **News check:** {r['news_check']}",
            f"- **Verdict:** {r['verdict']}",
            "",
        ]
    (CASES / f"batch_{letter}.md").write_text("\n".join(md))
    return m


BATCHES = {"A": (0, 20), "B": (20, 40), "C": (40, 60), "D": (60, 80), "E": (80, 103)}
BATCH_NOTE = (
    "Rules: D-35 in DECISIONS.md. Numbers come from the pack (founder_cases_data.csv): the three-day market-model "
    "return, the six-week slide against the market, and buy-and-hold returns from day +2 against the matched firm "
    "(industry, size, return on assets) and the S&P 500; dollars are millions of 2023 dollars (D-34). Facts come "
    "only from the sources named; 'not found' means the sources read are silent. Database notes are the coders' "
    "notes in the CEO dismissal database (Gentry et al.), quoted as written."
)

# Board fate, hand-classified from the coders' text in each case (merge step): stayed = kept a board seat or the chair
# after the CEO exit, for any time; left = left the board at or around the exit; unclear = sources silent or in conflict.
STAYED = {
    7188,  # D-44: transitioned to the board (database coder)
    5946,
    911,
    7740,
    7734,
    7133,
    6352,
    8348,
    1923,
    3135,
    5723,
    5993,
    6969,
    8000,
    7979,
    6702,
    8045,
    7539,
    7327,
    1862,
    7364,
    4119,
    7706,
    7961,
    8710,
    8085,
    4824,
    8733,
    8942,
    7452,
    7398,
    4646,
    9087,
    9406,
    7510,
    7758,
    9560,
    5212,
    7562,
    9071,
    9053,
    6523,
    5365,
    7116,
    7037,
    7647,
    1285,
    6921,
    9454,
    8097,
    10287,
}
LEFT = {
    7861,  # D-44: "McVaney will retire"
    5688,
    6818,
    6408,
    3432,
    5471,
    6881,
    4652,
    49,
    7230,
    7344,
    6659,
    8543,
    5931,
    4377,
    5615,
    7657,
    7394,
    6426,
    1053,
    5774,
    2440,
    6350,
    8801,
    6940,
    9197,
    5298,
    5182,
    8761,
    7915,
    5306,
    9469,
    9750,
    9231,
    9374,
    9699,
    7561,
    7030,
    10360,
    8370,
    8592,
}
# Came back as CEO of the same firm, from the coders' sources: year of return; "outside" = after the 5-year window.
BOOMERANG = {
    1923: ("2001", "within"),
    5502: ("2007", "within"),
    4646: ("2017", "within"),
    8592: ("2018", "within"),
    7647: ("2022", "within"),
    8045: ("2009", "outside"),
}
EARLIER_RETURN = {9071: "returned as CEO in 2017 before this exit", 7030: "this exit ended his second stint as CEO"}
EXEC_CHAIR_RETURN = {8370: "returned as executive chairman in January 2023"}
# Next moves, hand-coded from the coders' text (merge step).
NEW_FIRM = {
    5688: "Rail World (1999)",
    5471: "Command Center, a rival day-labour firm (2002 or 2003)",
    7230: "IP Fabrics (2002)",
    3135: "MP Biomedicals, spun off from ICN (year not given)",
    4119: "Wayin (2010)",
    8710: "Azul, a Brazilian airline (announced March 2008)",
    6350: "American Energy Partners (April 2013, three days after leaving)",
}
WENT_AFTER = {
    1862: "proxy fight within three months, then a bid for the company",
    7327: "bought 5% of the largest rival (2008) and led a proxy fight (2009)",
    5502: "bought the company and took it private (2007)",
    5615: "tried to remove the board at a special meeting (2007)",
    4824: "fought the board for control as largest shareholder (2009)",
    10287: "bought a subsidiary of the company",
    4161: "fought the board as an investor after his ouster (MarketWatch title, 2017; D-44)",
}


# Field names differ by batch (five coders); MAP gives, per common field, the batch column(s) to read, in order.
MAP = {
    "what": ["what"],
    "why_stated": ["why_stated"],
    "why_reported": ["why_reported"],
    "cause": ["cause"],
    "how": ["how"],
    "was_it_a_push": ["was_it_a_push", "push"],
    "push_quote": ["push_quote"],
    "successor": ["successor"],
    "news_first": ["news_first", "news_first_report", "news_check"],
    "news_agree": ["news_agree", "news_agree_3d"],
    "board_fate": ["board_fate", "fate_board", "fate", "founder_fate"],
    "boomerang": ["boomerang"],
    "boomerang_detail": ["boomerang_source"],
    "next_role": ["next_role"],
    "legal": ["legal", "legal_action"],
    "died": ["died_within_5y", "died"],
    "notable": ["notable", "fact", "notable_fact"],
    "competitor_plausible": ["competitor_plausible", "comp_ok"],
    "competitor_why": ["competitor_why", "comp_why"],
    "verdict": ["verdict"],
    "verdict_note": ["verdict_why", "flags"],
    "sources": ["sources", "src", "cause_source"],
    "more_sources": ["fate_src", "founder_fate_source", "board_source", "next_source", "legal_source"],
}


def first(r, cols):
    for c in cols:
        if c in r and pd.notna(r[c]) and str(r[c]).strip() not in ("", "nan"):
            return str(r[c]).strip()
    return ""


def yn(s):
    s = str(s).strip().lower()
    if s.startswith(("y", "pushed")):
        return "y"
    if s.startswith(("n", "no")):
        return "n"
    return s


def merge():
    """Merge the five batches into founder_cases.csv and CASES.md; numbers always from founder_cases_data.csv."""
    h = pd.read_csv(CASES / "h1_list.csv")
    d = pd.read_csv(CASES / "founder_cases_data.csv")
    rows = []
    for letter in BATCHES:
        b = pd.read_csv(CASES / f"batch_{letter}.csv")
        for _, r in b.iterrows():
            x = {"event_id": int(r["event_id"]), "batch": letter}
            for k, cols in MAP.items():
                x[k] = first(r, cols)
            if letter == "A":  # batch A keeps news agreement inside news_check
                m = re.search(r"Agree: (y|n|not checked)", x["news_first"])
                x["news_agree"] = m.group(1) if m else ""
            rows.append(x)
    c = pd.DataFrame(rows)
    assert c["event_id"].is_unique and set(c["event_id"]) == set(h["event_id"]), "batches do not cover h1_list"
    c["boomerang_yn"] = c["boomerang"].map(yn)
    c["competitor_ok"] = c["competitor_plausible"].map(
        lambda s: "n/a" if not s or s[:3] == "n/a" else "partly" if s.lower().startswith("partly") else yn(s)[:1]
    )
    c["push_class"] = (
        c["was_it_a_push"]
        .str.lower()
        .map(
            lambda s: "pushed" if s.startswith("push") else "planned succession" if s.startswith("plan") else "unclear"
        )
    )
    num = d[[
        "event_id", "coname", "exec_fullname", "event_date", "date_source", "dated", "why", "reason", "in_55",
        "shareholder_class", "car_mm_m1p1", "pre", "mbhar_1y", "mbhar_3y", "mbhar_5y", "sp_excess_3y", "mv31",
        "sp_m36_usd", "delist_kind_5y", "bankruptcy_date", "ctrl_ticker", "competitor_name", "prior_return_match_name",
    ]].copy()  # fmt: skip
    num["usd_vs_matched_3y_musd"] = num["mbhar_3y"] * num["mv31"]
    m = h[["event_id", "in_h1", "why_not_in_h1", "pr_m36"]].merge(num, on="event_id").merge(c, on="event_id")
    m = m.sort_values("event_date")
    m.to_csv(CASES / "founder_cases.csv", index=False)
    (CASES / "CASES.md").write_text(summary(m))
    return m


def names(x, n=12):
    v = [f"{r.coname.title()} ({str(r.event_date)[:4]})" for r in x.itertuples()]
    return ", ".join(v[:n]) + (f", and {len(v) - n} more" if len(v) > n else "")


def table(m, rows, cols, label):
    t = pd.crosstab(m[rows], m[cols], margins=True, margins_name="All")
    head = f"| {label} | " + " | ".join(str(c) for c in t.columns) + " |"
    out = [head, "|" + "---|" * (len(t.columns) + 1)]
    for i, r in t.iterrows():
        out.append(f"| {i} | " + " | ".join(str(int(v)) for v in r) + " |")
    return out


def summary(m):
    s55 = m[m["in_55"] == 1]
    h1 = m[m["in_h1"] == "y"]
    L = [
        "# Founder firings: case studies",
        "",
        "Rules: D-35 in `../DECISIONS.md` (fixed before any per-firm return was read). Cases: the coordinator's list "
        f"`h1_list.csv`, {len(m)} founder departures: the {len(h1)} founders in H1 (D-34) and flagged others, including "
        f"the {len(s55)} well-dated founder firings of the main sample (D-35). Five coders, batches A to E; fields are "
        "merged as written, numbers are the pack's (`founder_cases_data.csv`). Each case's sources are in its batch "
        "file and in `founder_cases.csv`. A cell under 10 cases gets names, not shares.",
        "",
        "Shareholder class (D-35, first rule that applies): bankrupt, taken over, delisted other (all within five "
        "years); otherwise the three-year buy-and-hold return against the matched firm: gained (> +10 points), lost "
        "(< -10), about even. The thresholds are the analyst's proposal.",
        "",
        f"## 1. Shareholders, by why the board acted: the {len(s55)} well-dated founder firings (D-35)",
        "",
        *table(s55, "shareholder_class", "why", "Shareholder class"),
        "",
        f"## 2. Shareholders, by why the board acted: all {len(m)} cases",
        "",
        *table(m, "shareholder_class", "why", "Shareholder class"),
        "",
        "## 3. Was it a push?",
        "",
        *table(m, "push_class", "why", "Push or planned"),
        "",
        "Planned successions, named: " + names(m[m["push_class"] == "planned succession"], 40) + ".",
        "",
        "## 4. What happened to the founder",
        "",
    ]
    m = m.copy()
    m["board"] = m["event_id"].map(lambda e: "stayed" if e in STAYED else "left" if e in LEFT else "unclear")
    L += [
        "Board seat after the CEO exit, hand-classified from each case's text (stayed = kept a seat or the chair for "
        "any time):",
        "",
        *table(m, "board", "why", "Board"),
        "",
    ]
    within = [e for e, (_, w) in BOOMERANG.items() if w == "within"]
    L += [f"**Came back as CEO of the same firm within five years (the Jobs case): {len(within)} of {len(m)}.**", ""]
    for e, (yr, w) in sorted(BOOMERANG.items(), key=lambda kv: kv[1][0]):
        r = m[m["event_id"] == e].iloc[0]
        tag = "" if w == "within" else " (just outside the five-year window)"
        L.append(
            f"- {r.coname.title()}, {r.exec_fullname}: fired {str(r.event_date)[:10]}, back as CEO {yr}{tag}. "
            f"{(r.boomerang_detail or r.notable or r.board_fate)[:260]}"
        )
    for e, note in {**EARLIER_RETURN, **EXEC_CHAIR_RETURN}.items():
        r = m[m["event_id"] == e].iloc[0]
        L.append(f"- Not counted: {r.coname.title()}, {r.exec_fullname}: {note}.")
    L.append("")
    leg = m[m["legal"].str.contains(r"(?i)indict|charg|convict|sued|lawsuit|SEC|settle|plea|complaint", na=False)]
    leg = leg[~leg["legal"].str.match(r"(?i)^(none|not found|no\b)", na=False)]
    died = m[m["died"].str.match(r"(?i)^y", na=False)]
    L += [
        f"- Legal action naming the founder (charges, regulator action or lawsuit; any time, see each case): {len(leg)}: "
        + names(leg, 40)
        + ".",
        f"- Started or led a new company within about five years: {len(NEW_FIRM)}: "
        + "; ".join(f"{m.loc[m.event_id == e, 'coname'].iloc[0].title()} founder: {v}" for e, v in NEW_FIRM.items())
        + ".",
        f"- Went after the firm that fired them: {len(WENT_AFTER)}: "
        + "; ".join(f"{m.loc[m.event_id == e, 'coname'].iloc[0].title()}: {v}" for e, v in WENT_AFTER.items())
        + ".",
        f"- Died within five years: {len(died)}" + (": " + names(died) if len(died) else "") + ".",
        "",
        "## 5. The matched competitor",
        "",
        *table(m, "competitor_ok", "batch", "Competitor plausible"),
        "",
        "Implausible matches come from the Fama-French 48-industry groups, which put a broker beside an energy trader "
        "(Enron and Charles Schwab) and a railcar maker beside a boat builder (Greenbrier and Malibu Boats). Recorded "
        "only; the matching is unchanged.",
        "",
        "## 6. Coders' verdicts",
        "",
    ]
    vc = m["verdict"].str.lower()
    for label, pat in [
        ("keep", r"^keep"),
        ("recode as not a firing", r"not a firing"),
        ("recode the reason", r"recode (the )?reason|reason may|recode as (fraud|performance|scandal)"),
        ("redate", r"redate"),
        ("bad competitor match", r"bad competitor|weak competitor"),
    ]:
        x = m[vc.str.contains(pat, regex=True, na=False)]
        L.append(f"- {label}: {len(x)}" + (": " + names(x, 40) if 0 < len(x) < 30 else "") + ".")
    x = m[m["usd_vs_matched_3y_musd"].notna()].sort_values("usd_vs_matched_3y_musd")
    L += ["", "## 7. Largest three-year dollar gaps against the matched firm (2023 dollars)", ""]
    for label, part in (("Largest losses", x.head(5)), ("Largest gains", x.tail(5).iloc[::-1])):
        L.append(
            f"**{label}:** "
            + "; ".join(
                f"{r.coname.title()} ({str(r.event_date)[:4]}, {r.why}): {usd(r.usd_vs_matched_3y_musd)} ({pct(r.mbhar_3y)})"
                for r in part.itertuples()
            )
            + "."
        )
        L.append("")
    L.append(
        f"Sum across the {len(x)} cases with a three-year matched return: {usd(x['usd_vs_matched_3y_musd'].sum())}; "
        f"without Enron: {usd(x.loc[x.event_id != 1923, 'usd_vs_matched_3y_musd'].sum())}. Descriptive only; "
        "H1's tests are in the paper (D-34)."
    )
    L += ["", "## 8. Notable facts, as recorded by the coders", ""]
    for r in m[m["notable"].str.len() > 20].itertuples():
        L.append(f"- {r.coname.title()} ({str(r.event_date)[:4]}): {r.notable[:300]}")
    L += ["", "## 9. The cases", ""]
    for letter in BATCHES:
        L += [f"See `batch_{letter}.md`."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    if "track" in sys.argv:
        track()
    elif "merge" in sys.argv:
        merge()
    elif "batch" in sys.argv:
        batch(sys.argv[sys.argv.index("batch") + 1])
    else:
        main()
