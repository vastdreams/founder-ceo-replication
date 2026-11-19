"""Build the event sample: CEO departures linked to SEC CIK and Sharadar price series.

Source of truth:
  world.ceo_turnover_gentry  Gentry et al. open CEO dismissal database v10Oct2024 (ODC-By)
  world.gvkey_cik            gvkey -> CIK from the dataset's 8-K links, plus unique name matches
  world.wikidata_founders    founder names (CC0), a cross-check only
  sharadar.tickers           Sharadar SEP securities with CIK in the secfilings URL

Writes analysis/out/events.parquet. Rules:
  forced   = departure_code in (3, 4)     (D-01: pushed resignations are coded 3 or 4 by Gentry)
  control  = departure_code = 5           (voluntary retirement)
  event_date = date_departure_announced, else left_ceo_office
  founder_v0  = notes mention the CEO founded/co-founded the firm, or Wikidata lists the CEO's surname
                as a founder. v1 replaces this with filing and news coding.
  relationship_v0 = notes mention an affair or a relationship with an employee or subordinate.
"""

import pathlib
import re
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path.home()))
import fce_db  # noqa: E402

OUT = pathlib.Path(__file__).parent / "out"
OUT.mkdir(exist_ok=True)

FOUNDER_RE = re.compile(r"\b(co-?\s?founder|founder|founded|co-?founded)\b", re.I)
REL_RE = re.compile(
    r"(affair|relationship with (an? |the )?(employee|subordinate|staff)|romantic|consensual (sexual )?relationship|"
    r"inappropriate (personal |sexual )?relationship|personal relationship|sexual)",
    re.I,
)


def surname(n: str) -> str:
    parts = [p for p in re.sub(r"[.,]", " ", n or "").split() if p.lower() not in ("jr", "sr", "ii", "iii", "iv")]
    return parts[-1].upper() if parts else ""


def main():
    con = fce_db.connect()
    ev = pd.read_sql(
        """
        select g.dismissal_dataset_id as event_id, g.gvkey, g.coname, g.fyear, g.exec_fullname,
               g.departure_code::int as code, g.ceo_dismissal::int as dismissal, g.notes, g.sources,
               coalesce(g.date_departure_announced, g.left_ceo_office) as event_date,
               g.date_departure_announced, g.left_ceo_office,
               (select c.cik from world.gvkey_cik c where c.gvkey = g.gvkey order by c.n_links desc limit 1) as cik
        from world.ceo_turnover_gentry g
        where g.departure_code in (3, 4, 5)""",
        con,
    )
    ev["event_date"] = pd.to_datetime(ev["event_date"])
    ev["forced"] = ev["code"].isin([3, 4]).astype(int)
    ev["conduct"] = (ev["code"] == 4).astype(int)

    wd = pd.read_sql("select cik, founder from world.wikidata_founders", con)
    wd["s"] = wd["founder"].map(surname)
    wd_set = set(zip(wd["cik"], wd["s"]))
    notes = ev["notes"].fillna("")
    ev["founder_notes"] = notes.str.contains(FOUNDER_RE).astype(int)
    ev["founder_wikidata"] = [
        int((c, surname(n)) in wd_set) if pd.notna(c) else 0 for c, n in zip(ev["cik"], ev["exec_fullname"])
    ]
    ev["founder_v0"] = ((ev["founder_notes"] + ev["founder_wikidata"]) > 0).astype(int)
    ev["relationship_v0"] = notes.str.contains(REL_RE).astype(int)

    tk = pd.read_sql(
        """select permaticker, ticker, name, isdelisted, firstpricedate, lastpricedate, category,
                               (regexp_match(secfilings, 'CIK=0*([0-9]+)'))[1]::bigint as cik
                        from sharadar.tickers where "table" = 'SEP'""",
        con,
    )
    tk = tk.dropna(subset=["cik"])
    tk["firstpricedate"] = pd.to_datetime(tk["firstpricedate"], errors="coerce")
    tk["lastpricedate"] = pd.to_datetime(tk["lastpricedate"], errors="coerce")
    tk = tk[tk["category"].fillna("").str.contains("Common Stock")]
    m = ev.merge(tk, on="cik", how="left")
    # keep the security whose price history spans the event date; prefer the longest history
    m["covers"] = (m["firstpricedate"] <= m["event_date"] - pd.Timedelta(days=60)) & (
        m["lastpricedate"] >= m["event_date"]
    )
    m["span"] = (m["lastpricedate"] - m["firstpricedate"]).dt.days
    m = m.sort_values(["event_id", "covers", "span"], ascending=[True, False, False]).drop_duplicates("event_id")
    m.loc[~m["covers"].fillna(False), ["permaticker", "ticker"]] = None
    m = m.drop(columns=["covers", "span", "name", "category"])
    m.to_parquet(OUT / "events.parquet", index=False)

    s = m.assign(
        era=pd.cut(m["event_date"].dt.year, [1980, 1997, 2009, 2030], labels=["1992-1997", "1998-2009", "2010-2023"])
    )
    print(
        s.groupby(["era", "forced"], observed=True).agg(
            events=("event_id", "size"),
            with_cik=("cik", lambda x: x.notna().sum()),
            with_prices=("permaticker", lambda x: x.notna().sum()),
            founder_v0=("founder_v0", "sum"),
            relationship_v0=("relationship_v0", "sum"),
        )
    )


if __name__ == "__main__":
    main()
