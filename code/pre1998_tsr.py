"""Pre-1998 robustness: three-year shareholder return against the firm's own index, from proxy performance graphs.

For each departure announced 1992-1997 we take the first proxy filed after the event whose performance graph
covers both fiscal year t (the event year) and t+3. Abnormal TSR = company(t+3)/company(t) - index(t+3)/index(t),
where index is the first index the firm reports (usually the S&P 500 or a broad market index). Values are
read from the graph tables by the extraction step; every ratio here is computed in code.
Inputs : ~/world_raw/sec/extract/DEF14A.jsonl, analysis/out/events.parquet, datasource.sec_filings (proxy dates)
Output : analysis/out/pre1998_tsr.parquet and outputs/pre1998_stats.json
"""

import json
import pathlib
import re

import pandas as pd

import datasource  # noqa: E402
from stats_returns import R, one_group, put, two_group  # noqa: E402

HERE = pathlib.Path(__file__).parent
EXTRACT = pathlib.Path.home() / "world_raw/sec/extract/DEF14A.jsonl"


def year_of(label):
    m = re.search(r"(19|20)\d{2}", str(label))
    if m:
        return int(m.group(0))
    m = re.search(r"\b(\d{1,2})/\d{1,2}/(\d{2})\b", str(label))
    if m:
        yy = int(m.group(2))
        return 1900 + yy if yy > 50 else 2000 + yy
    return None


def main():
    R.clear()
    ev = pd.read_parquet(HERE / "out" / "events.parquet")
    ff = HERE / "out" / "founder_final.parquet"
    if ff.exists():
        ev = ev.merge(pd.read_parquet(ff)[["event_id", "founder"]], on="event_id", how="left")
    ev["year"] = pd.to_datetime(ev["event_date"]).dt.year
    ev = ev[(ev["year"] >= 1992) & (ev["year"] <= 1997) & ev["cik"].notna()]
    dates = datasource.sec_filings(["DEF 14A"])[["cik", "accession", "filing_date"]]
    dates["filing_date"] = pd.to_datetime(dates["filing_date"])
    graphs = {}
    for line in open(EXTRACT):
        r = json.loads(line)
        pts = (r.get("data") or {}).get("points") or []
        if pts:
            graphs[r["accession"]] = pts
    rows = []
    for _, e in ev.iterrows():
        cand = dates[
            (dates["cik"] == int(e["cik"])) & (dates["filing_date"] > pd.Timestamp(e["event_date"]))
        ].sort_values("filing_date")
        for acc in cand["accession"]:
            pts = graphs.get(acc)
            if not pts:
                continue
            by_year = {}
            for p in pts:
                y = year_of(p.get("date_or_year"))
                if y and p.get("company") and p.get("index_1"):
                    by_year[y] = (float(p["company"]), float(p["index_1"]))
            t = int(e["year"])
            if t in by_year and t + 3 in by_year:
                c0, i0 = by_year[t]
                c3, i3 = by_year[t + 3]
                if c0 > 0 and i0 > 0:
                    rows.append(
                        {
                            "event_id": e["event_id"],
                            "forced": int(e["forced"]),
                            "conduct": int(e["conduct"]),
                            "founder": int(e.get("founder") or 0),
                            "accession": acc,
                            "tsr_3y": c3 / c0 - 1,
                            "index_3y": i3 / i0 - 1,
                            "abn_tsr_3y": c3 / c0 - i3 / i0,
                        }
                    )
                    break
    d = pd.DataFrame(rows)
    d.to_parquet(HERE / "out" / "pre1998_tsr.parquet", index=False)
    put("pre.events_1992_1997", len(ev))
    put("pre.events_with_tsr", len(d))
    if len(d):
        f, r = d[d["forced"] == 1], d[d["forced"] == 0]
        put("pre.n_forced", len(f))
        put("pre.n_retired", len(r))
        one_group("pre.forced.abn_tsr_3y", f["abn_tsr_3y"])
        one_group("pre.retired.abn_tsr_3y", r["abn_tsr_3y"])
        two_group("pre.forced_vs_retired.abn_tsr_3y", f["abn_tsr_3y"], r["abn_tsr_3y"])
    out = HERE.parent / "outputs"
    out.mkdir(exist_ok=True)
    (out / "pre1998_stats.json").write_text(json.dumps(R, indent=1))
    for k in [
        "pre.events_1992_1997",
        "pre.events_with_tsr",
        "pre.n_forced",
        "pre.forced.abn_tsr_3y.median",
        "pre.retired.abn_tsr_3y.median",
        "pre.forced_vs_retired.abn_tsr_3y.diff_median",
    ]:
        v = R.get(k, {})
        print(f"{k:50s} {v.get('value')!s:>22} n={v.get('n')} p={v.get('p')}")


if __name__ == "__main__":
    main()
