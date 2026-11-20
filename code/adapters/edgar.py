"""SEC filing index for the sample's firms, from the EDGAR submissions API. Free; set SEC_USER_AGENT first.

Output : sec_filings  (cik, accession, form, filing_date, items)
Input  : the CIKs in gvkey_cik (data/inputs/gvkey_cik.*), or a list of CIKs as arguments.
Usage  : SEC_USER_AGENT="Name email" python -m adapters.edgar
Rate   : SEC allows 10 requests a second; this waits 0.15 s between requests.
"""

import json
import sys
import time
import urllib.request

import pandas as pd
from adapters.common import out_dir, user_agent, write

FORMS = {"8-K", "8-K/A", "DEF 14A"}


def get(url: str, ua: str):
    for i in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Encoding": "identity"})
            with urllib.request.urlopen(req, timeout=30) as r:  # nosec B310 - fixed https source
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(2**i)
        except Exception:
            time.sleep(2**i)
    return None


def rows(block, cik):
    keys = ("accessionNumber", "form", "filingDate", "items")
    for acc, form, date, items in zip(*(block.get(k, []) for k in keys)):
        if form in FORMS:
            yield {"cik": cik, "accession": acc, "form": form, "filing_date": date, "items": items}


def main(ciks=None):
    ua = user_agent()
    if not ciks:
        from datasource import gvkey_cik

        ciks = sorted({int(c) for c in gvkey_cik()["cik"].dropna()})
    cache = out_dir() / "edgar_submissions"
    cache.mkdir(exist_ok=True)
    out = []
    for n, cik in enumerate(ciks, 1):
        f = cache / f"CIK{cik:010d}.json"
        d = json.loads(f.read_text()) if f.exists() else get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json", ua)
        time.sleep(0.15)
        if not d:
            continue
        f.write_text(json.dumps(d))
        out += list(rows(d["filings"]["recent"], cik))
        for extra in d["filings"].get("files", []):
            g = cache / extra["name"]
            e = (
                json.loads(g.read_text())
                if g.exists()
                else get(f"https://data.sec.gov/submissions/{extra['name']}", ua)
            )
            time.sleep(0.15)
            if e:
                g.write_text(json.dumps(e))
                out += list(rows(e, cik))
        if n % 200 == 0:
            print(n, "of", len(ciks))
    d = pd.DataFrame(out)
    d["filing_date"] = pd.to_datetime(d["filing_date"])
    write("sec_filings", d.drop_duplicates(["cik", "accession", "form"]))


if __name__ == "__main__":
    main([int(x) for x in sys.argv[1:]])
