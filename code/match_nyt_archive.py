"""Match NYT Archive articles (~/world_raw/news/nyt_archive/YYYY-MM.json.gz) to CEO departures.

An article matches an event when it is published between 30 days before and 60 days after the announcement
and its headline, abstract, snippet or lead paragraph names the company (first distinctive word(s) of the
cleaned name) and either the CEO's surname or the words chief executive / C.E.O.
Output: ~/world_raw/news/nyt_archive_matched.jsonl, one line per event, same shape as the search fetcher's file.
"""

import datetime
import gzip
import json
import pathlib
import re

import pandas as pd

HERE = pathlib.Path(__file__).parent / "out"
NEWS = pathlib.Path.home() / "world_raw/news"
STOP = {
    "inc",
    "corp",
    "corporation",
    "co",
    "company",
    "ltd",
    "plc",
    "holdings",
    "holding",
    "group",
    "the",
    "cl",
    "a",
    "new",
    "del",
    "intl",
    "international",
    "american",
    "first",
    "united",
    "national",
    "general",
}


def co_terms(name):
    words = [w for w in re.sub(r"[^A-Za-z0-9&' ]", " ", name or "").lower().split() if w not in STOP]
    return words[:2] if words else []


def surname(n):
    p = [
        x
        for x in re.sub(r"[.,]", " ", n or "").split()
        if x.lower() not in ("jr", "sr", "ii", "iii", "iv", "phd", "md")
    ]
    return p[-1].lower() if p else ""


KEEP = ("pub_date", "headline", "abstract", "snippet", "lead_paragraph", "web_url")


def main():
    ev = pd.read_parquet(HERE / "events.parquet")
    ev = ev[ev["code"].isin([3, 4, 5])].copy()
    ev["d"] = pd.to_datetime(ev["event_date"])
    ev = ev[ev["d"].notna()]
    # One month in memory at a time: the full archive does not fit in RAM.
    want = {}
    meta = {}
    for _, e in ev.iterrows():
        lo, hi = e["d"] - pd.Timedelta(days=30), e["d"] + pd.Timedelta(days=60)
        terms, sn = co_terms(e["coname"]), surname(e["exec_fullname"])
        if not terms:
            continue
        eid = int(e["event_id"])
        meta[eid] = (lo.date(), hi.date(), terms, sn, [])
        for p in pd.period_range(lo, hi, freq="M"):
            want.setdefault(f"{p.year}-{p.month:02d}", []).append(eid)
    files = sorted((NEWS / "nyt_archive").glob("*.json.gz"))
    for f in files:
        ids = want.get(f.name[:7])
        if not ids:
            continue
        arts = []
        for a in json.loads(gzip.decompress(f.read_bytes())):
            try:
                day = datetime.date.fromisoformat((a.get("pub_date") or "")[:10])
            except ValueError:
                continue
            h = a.get("headline")
            a = {k: a.get(k) for k in KEEP}
            a["headline"] = h.get("main") if isinstance(h, dict) else h
            text = " ".join(str(a.get(k) or "") for k in ("headline", "abstract", "snippet", "lead_paragraph")).lower()
            arts.append((day, text, a))
        for eid in ids:
            lo, hi, terms, sn, docs = meta[eid]
            for day, text, a in arts:
                if (
                    lo <= day <= hi
                    and terms[0] in text
                    and (sn and sn in text or "chief executive" in text or "c.e.o" in text)
                ):
                    docs.append(a)
        del arts
    hits = 0
    with open(NEWS / "nyt_archive_matched.jsonl", "w") as out:
        for eid, (_, _, _, _, docs) in meta.items():
            docs.sort(key=lambda a: a.get("pub_date") or "")
            hits += bool(docs)
            out.write(json.dumps({"event_id": eid, "source": "nyt_archive", "docs": docs[:12]}) + "\n")
    print("events", len(meta), "with matched articles", hits, "months", len(files))


if __name__ == "__main__":
    main()
