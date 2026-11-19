"""Collect evidence on why each forced exit happened, from sources with no daily quota.

Per forced exit (Gentry codes 3 and 4):
  sec8k  the 8-K (and its attached press release) filed within 10 days of the announcement; 2004+ filings must
         carry Item 5.02, earlier ones are taken as filed (Item 5 'Other events'). SEC limit 10/s: we use about 7/s.
  press  press-release and SEC links the dataset itself cites (businesswire, prnewswire, globenewswire, sec.gov).
  wiki   the Wikipedia article on the CEO, plain text.
Text is kept for coding only and is never published. Output: ~/world_raw/news/evidence.jsonl (resumable).
"""

import html
import json
import pathlib
import re
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

import datasource  # noqa: E402

HERE = pathlib.Path(__file__).parent / "out"
OUTF = pathlib.Path.home() / "world_raw/news/evidence.jsonl"
import keys  # noqa: E402

SEC_UA = keys.get("SEC_USER_AGENT")
GEN_UA = "FounderCEOStudy/1.0 (academic research)"
PRESS = re.compile(r"https?://(www\.)?(businesswire\.com|prnewswire\.com|globenewswire\.com|sec\.gov)/[^\s,;]+", re.I)
lock, last = threading.Lock(), {"sec": 0.0, "gen": 0.0}


def pace(kind, gap):
    with lock:
        wait = last[kind] + gap - time.time()
        if wait > 0:
            time.sleep(wait)
        last[kind] = time.time()


def fetch(url, ua, kind, gap):
    for i in range(3):
        pace(kind, gap)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua})
            with urllib.request.urlopen(req, timeout=40) as r:  # nosec B310 - fixed https sources
                return r.read().decode("latin1", "ignore")
        except urllib.error.HTTPError as e:
            if e.code in (403, 404, 410):
                return ""
            time.sleep(5 * (i + 1))
        except Exception:
            time.sleep(5 * (i + 1))
    return ""


def clean(t):
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def around(t, n=6000):
    i = max(t.lower().find("chief executive"), 0)
    return t[max(0, i - 1500) : max(0, i - 1500) + n]


def main():
    ev = pd.read_parquet(HERE / "events.parquet")
    ev = ev[ev["code"].isin([3, 4]) & ev["cik"].notna()].copy()
    ev["d"] = pd.to_datetime(ev["event_date"])
    k8 = datasource.sec_filings(["8-K", "8-K/A"])[["cik", "accession", "filing_date", "items"]]
    k8["filing_date"] = pd.to_datetime(k8["filing_date"])
    k8 = k8.groupby("cik")
    done = {json.loads(x)["event_id"] for x in open(OUTF)} if OUTF.exists() else set()
    fh, wl = open(OUTF, "a"), threading.Lock()

    def one(e):
        recs = []
        cik = int(e["cik"])
        if cik in k8.groups:
            g = k8.get_group(cik)
            g = g[
                (g["filing_date"] >= e["d"] - pd.Timedelta(days=10))
                & (g["filing_date"] <= e["d"] + pd.Timedelta(days=10))
            ]
            g = g[(g["filing_date"] < "2004-08-23") | g["items"].fillna("").str.contains("5.02")]
            for acc in list(g.sort_values("filing_date")["accession"])[:2]:
                txt = clean(
                    fetch(
                        f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{acc}.txt",
                        SEC_UA,
                        "sec",
                        0.14,
                    )
                )
                if txt:
                    recs.append({"source": "sec8k", "url": acc, "text": around(txt)})
        for url in list(dict.fromkeys(m.group(0) for m in PRESS.finditer(e["sources"] or "")))[:3]:
            ua, kind, gap = (SEC_UA, "sec", 0.14) if "sec.gov" in url else (GEN_UA, "gen", 0.5)
            txt = clean(fetch(url, ua, kind, gap))
            if len(txt) > 300:
                recs.append({"source": "press", "url": url, "text": around(txt)})
        q = urllib.parse.quote(re.sub(r",.*$", "", e["exec_fullname"] or ""))
        s = fetch(
            f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={q}&srlimit=1&format=json",
            GEN_UA,
            "gen",
            0.2,
        )
        try:
            title = json.loads(s)["query"]["search"][0]["title"]
            w = json.loads(
                fetch(
                    "https://en.wikipedia.org/w/api.php?"
                    + urllib.parse.urlencode(
                        {
                            "action": "query",
                            "prop": "extracts",
                            "explaintext": 1,
                            "titles": title,
                            "format": "json",
                            "redirects": 1,
                        }
                    ),
                    GEN_UA,
                    "gen",
                    0.2,
                )
            )
            page = next(iter(w["query"]["pages"].values())).get("extract", "")
            if page and (e["coname"] or "").split()[0].lower() in page.lower():
                recs.append({"source": "wiki", "url": title, "text": around(page)})
        except Exception:
            pass
        with wl:
            fh.write(json.dumps({"event_id": int(e["event_id"]), "docs": recs}) + "\n")
            fh.flush()

    todo = [e for _, e in ev.iterrows() if int(e["event_id"]) not in done]
    with ThreadPoolExecutor(8) as ex:
        list(ex.map(one, todo))
    print("done", len(todo))


if __name__ == "__main__":
    main()
