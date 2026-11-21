"""Collect independent founder evidence from Wikipedia for forced exits coded founder 'yes' or 'unclear'.

For each event: search Wikipedia for the company, read the infobox 'founder(s)' field and the lead paragraph,
and record whether the CEO's surname appears among the founders. Results feed the hand review in
paper/FOUNDER_REVIEW.md, where every disagreement with the model coding is decided and the decision recorded.
Polite use: one request per second, generic client name.
Output: analysis/out/founder_wiki.jsonl
"""

import json
import pathlib
import re
import time
import urllib.parse
import urllib.request

import pandas as pd

HERE = pathlib.Path(__file__).parent / "out"
UA = {"User-Agent": "FounderCEOStudy/1.0 (academic research)"}


def get(url):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:  # nosec B310
            return json.load(r)
    except Exception:
        return {}


def surname(n):
    parts = [p for p in re.sub(r"[.,]", " ", n or "").split() if p.lower() not in ("jr", "sr", "ii", "iii", "iv")]
    return parts[-1].lower() if parts else ""


def clean_co(n):
    n = re.sub(
        r"(?i)\b(inc|corp|corporation|co|company|ltd|plc|holdings?|group|cl a|-cl a|new|del|intl)\b\.?", " ", n or ""
    )
    return " ".join(re.sub(r"[^A-Za-z0-9&' ]", " ", n).split())


def main():
    ev = pd.read_parquet(HERE / "events.parquet")
    c = pd.DataFrame([json.loads(x) for x in open(HERE / "event_coding_v1.jsonl")])
    d = ev.merge(c[["event_id", "ceo_is_founder", "founder_family", "founder_evidence"]], on="event_id")
    d = d[d["code"].isin([3, 4]) & d["ceo_is_founder"].isin(["yes", "unclear"])]
    outf = HERE / "founder_wiki.jsonl"
    done = {json.loads(x)["event_id"] for x in open(outf)} if outf.exists() else set()
    fh = open(outf, "a")
    for _, e in d.iterrows():
        if int(e["event_id"]) in done:
            continue
        q = clean_co(e["coname"]) + " company"
        s = get(
            "https://en.wikipedia.org/w/api.php?"
            + urllib.parse.urlencode(
                {"action": "query", "list": "search", "srsearch": q, "srlimit": 1, "format": "json"}
            )
        )
        time.sleep(1)
        hits = (s.get("query") or {}).get("search") or []
        title = hits[0]["title"] if hits else None
        founders_field, lead = "", ""
        if title:
            w = get(
                "https://en.wikipedia.org/w/api.php?"
                + urllib.parse.urlencode(
                    {
                        "action": "parse",
                        "page": title,
                        "prop": "wikitext",
                        "section": 0,
                        "format": "json",
                        "redirects": 1,
                    }
                )
            )
            time.sleep(1)
            wt = ((w.get("parse") or {}).get("wikitext") or {}).get("*", "")
            m = re.search(r"\|\s*founders?\s*=\s*(.+?)\n\s*\|", wt, re.S | re.I)
            founders_field = re.sub(r"\[\[([^|\]]*\|)?([^\]]*)\]\]", r"\2", m.group(1))[:500] if m else ""
            body = re.sub(r"\{\{.*?\}\}", " ", wt, flags=re.S)
            lead = re.sub(r"\[\[([^|\]]*\|)?([^\]]*)\]\]", r"\2", body)[-1500:]
        sn = surname(e["exec_fullname"])
        rec = {
            "event_id": int(e["event_id"]),
            "coname": e["coname"],
            "ceo": e["exec_fullname"],
            "fyear": int(e["fyear"]),
            "model": e["ceo_is_founder"],
            "model_family": e["founder_family"],
            "model_evidence": e["founder_evidence"],
            "wiki_title": title,
            "wiki_founders": founders_field.strip(),
            "surname_in_founders": bool(sn and sn in founders_field.lower()),
            "surname_founded_in_lead": bool(
                sn
                and re.search(
                    rf"(found|co-?found)[^.]{{0,120}}{re.escape(sn)}|{re.escape(sn)}[^.]{{0,120}}(found|co-?found)",
                    lead,
                    re.I,
                )
            ),
            "notes": (e["notes"] or "")[:600],
        }
        fh.write(json.dumps(rec) + "\n")
        fh.flush()
    print("done", len(d))


if __name__ == "__main__":
    main()
