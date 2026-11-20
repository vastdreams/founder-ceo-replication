"""Announcement dates from the firm's own 8-K, for departures the CEO dismissal database dates only by when the CEO left.

The database gives an announcement date for about a third of departures; for the rest the paper's day 0 would be
the day the CEO left office, often months after the news. For every departure this script looks for the earliest
8-K the firm filed in the 90 days before the CEO left (to 15 days after) that names the CEO, a CEO title and a strong
departure word (resign, retire, step down, terminate, depart, separate, oust, dismiss) in one passage, and does not
describe the CEO's appointment. From August 2004 the
8-K must carry Item 5.02 (departure of officers). The announcement date is the 8-K's "date of earliest event
reported" (CONFORMED PERIOD OF REPORT in the filing header), which is the day the company announced or decided.
Where no such 8-K exists, the first matched New York Times article that names the CEO next to a departure word
(within 30 days before the departure date) gives the date, less one day for print publication.

The database's own announcement date is kept where it exists; the 8-K date is checked against it on those events
(the validation rate is reported). SEC asks for at most 10 requests a second; this waits 0.14 s between requests.
Inputs : analysis/out/events.parquet, datasource.sec_filings, ~/world_raw/news/nyt_archive_matched.jsonl
Output : analysis/out/redate.parquet (event_id, date_8k, accession_8k, date_nyt, announce_date, date_source)
"""

import gzip
import json
import pathlib
import re
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import datasource
import keys
import pandas as pd

HERE = pathlib.Path(__file__).parent / "out"
CACHE = pathlib.Path.home() / "world_raw/sec/8k_cache"
NYT = pathlib.Path.home() / "world_raw/news/nyt_archive_matched.jsonl"
# Strong departure words only: "succeed" and "transition" also match the 8-K that appointed the CEO (validated on the
# database-dated events, D-15).
DEPART = r"(resign|retire|step(?:s|ped|ping)? down|terminat|depart|separat|ousted|dismiss|will leave|has left)"
TITLE = r"(chief executive|\bCEO\b)"
BACK_DAYS = 90
lock, last = threading.Lock(), [0.0]


def surname(name: str) -> str:
    parts = [
        x
        for x in re.sub(r"[.,()]", " ", name or "").split()
        if x.lower() not in ("jr", "sr", "ii", "iii", "iv", "phd", "md", "ph.d")
    ]
    return parts[-1] if parts else ""


def fetch(cik: int, acc: str, ua: str) -> str:
    """The filing's full text (cached gzip, first 200,000 characters)."""
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{acc}.txt.gz"
    if f.exists():
        return gzip.decompress(f.read_bytes()).decode("latin1", "ignore")
    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{acc}.txt"
    for i in range(3):
        with lock:
            wait = last[0] + 0.14 - time.time()
            if wait > 0:
                time.sleep(wait)
            last[0] = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Encoding": "identity"})
            with urllib.request.urlopen(req, timeout=40) as r:  # nosec B310 - fixed https source
                text = r.read(400_000).decode("latin1", "ignore")
            f.write_bytes(gzip.compress(text[:200_000].encode("latin1", "ignore")))
            return text
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ""
            time.sleep(3 * (i + 1))
        except Exception:
            time.sleep(3 * (i + 1))
    return ""


def names_departure(text: str, sn: str) -> bool:
    if not sn or len(sn) < 3:
        return False
    body = re.sub(r"<[^>]+>", " ", text)
    body = re.sub(r"\s+", " ", body)
    for m in re.finditer(re.escape(sn), body, flags=re.I):
        window = body[max(0, m.start() - 300) : m.end() + 300]
        appointed = re.search(r"\bappoint(?:ed|s|ment)?\b[^.]{0,80}" + re.escape(sn), window, flags=re.I)
        if re.search(DEPART, window, flags=re.I) and re.search(TITLE, window, flags=re.I) and not appointed:
            return True
    return False


def period_of_report(text: str):
    m = re.search(r"CONFORMED PERIOD OF REPORT:\s*(\d{8})", text)
    return pd.to_datetime(m.group(1), format="%Y%m%d", errors="coerce") if m else pd.NaT


def main():
    ua = keys.get("SEC_USER_AGENT")
    ev = pd.read_parquet(HERE / "events.parquet")
    ev = ev[ev["code"].isin([3, 4, 5])].copy()
    ev["ref"] = pd.to_datetime(ev["left_ceo_office"]).fillna(pd.to_datetime(ev["event_date"]))
    k8 = datasource.sec_filings(["8-K"])
    k8["has502"] = k8["items"].fillna("").str.contains("5.02")
    k8 = k8[(k8["filing_date"] < "2004-08-23") | k8["has502"]].sort_values("filing_date")
    by_cik = dict(list(k8.groupby("cik")))

    def one(e):
        out = {"event_id": int(e["event_id"]), "date_8k": pd.NaT, "accession_8k": None}
        if pd.isna(e["cik"]) or pd.isna(e["ref"]) or int(e["cik"]) not in by_cik:
            return out
        g = by_cik[int(e["cik"])]
        g = g[
            (g["filing_date"] >= e["ref"] - pd.Timedelta(days=BACK_DAYS))
            & (g["filing_date"] <= e["ref"] + pd.Timedelta(days=15))
        ]
        sn = surname(e["exec_fullname"])
        for _, f in g.iterrows():
            text = fetch(int(e["cik"]), f["accession"], ua)
            if text and names_departure(text, sn):
                d = period_of_report(text)
                out["date_8k"] = d if pd.notna(d) and d <= f["filing_date"] else f["filing_date"]
                out["accession_8k"] = f["accession"]
                break
        return out

    with ThreadPoolExecutor(12) as ex:
        rows = list(ex.map(one, [e for _, e in ev.iterrows()]))
    rd = pd.DataFrame(rows)

    nyt = {}
    if NYT.exists():
        sn_by = dict(zip(ev["event_id"], ev["exec_fullname"].map(surname)))
        ref_by = dict(zip(ev["event_id"], ev["ref"]))
        for line in open(NYT):
            r = json.loads(line)
            sn, ref = sn_by.get(r["event_id"]), ref_by.get(r["event_id"])
            if not sn or ref is None or pd.isna(ref):
                continue
            for d in r["docs"]:
                text = " ".join(str(d.get(x) or "") for x in ("headline", "abstract", "snippet", "lead_paragraph"))
                day = pd.to_datetime((d.get("pub_date") or "")[:10], errors="coerce")
                if pd.notna(day) and day <= ref + pd.Timedelta(days=5) and names_departure(text, sn):
                    nyt[r["event_id"]] = day - pd.Timedelta(days=1)
                    break
    rd["date_nyt"] = rd["event_id"].map(nyt)
    m = ev[["event_id", "date_departure_announced", "ref"]].merge(rd, on="event_id", how="left")
    m["date_departure_announced"] = pd.to_datetime(m["date_departure_announced"])
    m["announce_date"] = m["date_departure_announced"]
    m["date_source"] = m["announce_date"].notna().map({True: "database", False: None})
    use8 = m["announce_date"].isna() & m["date_8k"].notna()
    m.loc[use8, "announce_date"], m.loc[use8, "date_source"] = m.loc[use8, "date_8k"], "8-K"
    usen = m["announce_date"].isna() & m["date_nyt"].notna()
    m.loc[usen, "announce_date"], m.loc[usen, "date_source"] = m.loc[usen, "date_nyt"], "NYT"
    left = m["announce_date"].isna()
    m.loc[left, "announce_date"], m.loc[left, "date_source"] = m.loc[left, "ref"], "left office"
    m.drop(columns=["ref"]).to_parquet(HERE / "redate.parquet", index=False)
    both = m[m["date_departure_announced"].notna() & m["date_8k"].notna()]
    gap = (both["date_8k"] - both["date_departure_announced"]).dt.days.abs()
    print("events", len(m), m["date_source"].value_counts().to_dict())
    print(
        "validation on database-dated events with an 8-K:",
        len(both),
        "within 3 days:",
        round(float((gap <= 3).mean()), 3),
        "within 10 days:",
        round(float((gap <= 10).mean()), 3),
    )


if __name__ == "__main__":
    main()
