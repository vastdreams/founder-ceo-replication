"""Validate 8-K dating rules against the database's own announcement dates (a sample of database-dated events)."""

import re
import sys

import datasource
import keys
import pandas as pd
from redate import HERE, fetch, period_of_report, surname

STRONG = r"(resign|retire|step(?:s|ped|ping)? down|terminat|depart|separat|ousted|dismiss|will leave|has left)"
TITLE = r"(chief executive|\bCEO\b)"


def strong(text, sn):
    if not sn or len(sn) < 3:
        return False
    body = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text))
    for m in re.finditer(re.escape(sn), body, flags=re.I):
        w = body[max(0, m.start() - 300) : m.end() + 300]
        if (
            re.search(STRONG, w, flags=re.I)
            and re.search(TITLE, w, flags=re.I)
            and not re.search(r"\bappoint(?:ed|s|ment)?\b[^.]{0,80}" + re.escape(sn), w, flags=re.I)
        ):
            return True
    return False


def main(n=500, back=365, pick="earliest"):
    ua = keys.get("SEC_USER_AGENT")
    ev = pd.read_parquet(HERE / "events.parquet")
    ev = ev[ev["code"].isin([3, 4, 5]) & ev["date_departure_announced"].notna() & ev["cik"].notna()].copy()
    ev["ann"] = pd.to_datetime(ev["date_departure_announced"])
    ev["ref"] = pd.to_datetime(ev["left_ceo_office"]).fillna(ev["ann"])
    ev = ev.sample(min(n, len(ev)), random_state=1)
    k8 = datasource.sec_filings(["8-K"])
    k8["has502"] = k8["items"].fillna("").str.contains("5.02")
    k8 = k8[(k8["filing_date"] < "2004-08-23") | k8["has502"]].sort_values("filing_date")
    by = dict(list(k8.groupby("cik")))
    out = []
    for _, e in ev.iterrows():
        g = by.get(int(e["cik"]))
        if g is None:
            continue
        g = g[
            (g["filing_date"] >= e["ref"] - pd.Timedelta(days=back))
            & (g["filing_date"] <= e["ref"] + pd.Timedelta(days=15))
        ]
        if pick == "latest":
            g = g.iloc[::-1]
        sn = surname(e["exec_fullname"])
        d = None
        for _, f in g.iterrows():
            t = fetch(int(e["cik"]), f["accession"], ua)
            if t and strong(t, sn):
                d = period_of_report(t)
                d = d if pd.notna(d) and d <= f["filing_date"] else f["filing_date"]
                break
        if d is not None:
            out.append(((d - e["ann"]).days, int(e["code"])))
    df = pd.DataFrame(out, columns=["gap", "code"])
    for c, x in [("all", df), ("forced", df[df.code.isin([3, 4])]), ("retired", df[df.code == 5])]:
        a = x.gap.abs()
        print(
            f"back={back} pick={pick} {c}: n={len(x)} within3={float((a<=3).mean()):.3f} within10={float((a<=10).mean()):.3f} median_gap={float(x.gap.median()) if len(x) else 0}"
        )


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
