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

import datasource  # noqa: E402
import pandas as pd

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
    g = datasource.gentry()
    g = g[pd.to_numeric(g["departure_code"], errors="coerce").isin([3, 4, 5])].copy()
    links = datasource.gvkey_cik().sort_values("n_links", ascending=False, kind="stable").drop_duplicates("gvkey")
    ev = pd.DataFrame(
        {
            "event_id": g["dismissal_dataset_id"],
            "gvkey": g["gvkey"],
            "coname": g["coname"],
            "fyear": g["fyear"],
            "exec_fullname": g["exec_fullname"],
            "code": pd.to_numeric(g["departure_code"]).astype(int),
            "dismissal": pd.to_numeric(g["ceo_dismissal"], errors="coerce").astype("Int64"),
            "notes": g["notes"],
            "sources": g["sources"],
            "event_date": g["date_departure_announced"].fillna(g["left_ceo_office"]),
            "date_departure_announced": g["date_departure_announced"],
            "left_ceo_office": g["left_ceo_office"],
        }
    ).merge(links[["gvkey", "cik"]], on="gvkey", how="left")
    ev["event_date"] = pd.to_datetime(ev["event_date"])
    # Announcement dates from the firm's 8-K or the first NYT report where the database has none (redate.py, D-15).
    rd = OUT / "redate.parquet"
    ev["date_source"] = ev["date_departure_announced"].notna().map({True: "database", False: "left office"})
    if rd.exists():
        r = pd.read_parquet(rd)[["event_id", "announce_date", "date_source"]]
        ev = ev.drop(columns="date_source").merge(r, on="event_id", how="left")
        ev["event_date"] = pd.to_datetime(ev["announce_date"]).fillna(ev["event_date"])
        ev["date_source"] = ev["date_source"].fillna("left office")
        ev = ev.drop(columns="announce_date")
    # Hand-checked dates (paper/date_corrections.csv, each with a dated source) take precedence, and records that are
    # not CEO exits or duplicate another record are dropped (paper/exclusions.csv).
    paper = pathlib.Path(__file__).resolve().parent.parent / "paper"
    dc = paper / "date_corrections.csv"
    if dc.exists():
        c = pd.read_csv(dc)
        fix = dict(zip(c["event_id"], pd.to_datetime(c["announce_date"])))
        hit = ev["event_id"].isin(fix)
        ev.loc[hit, "event_date"] = ev.loc[hit, "event_id"].map(fix)
        ev.loc[hit, "date_source"] = "hand-checked"
    ex = paper / "exclusions.csv"
    if ex.exists():
        ev = ev[~ev["event_id"].isin(pd.read_csv(ex)["event_id"])]
    # D-37: corrections from the hand check of every founder departure (paper/d37_corrections.csv). A new date moves
    # day 0 to the first public report (a row whose new date equals the old one is a flag, not a change), and a
    # departure the sources show was not a firing leaves the sample and joins no comparison group.
    # D-38 applies the hired-CEO audit's fixes from paper/d38_corrections.csv in the same way.
    # D-44 adds forced resignations the database coded as retirements (field "code", 5 -> 3).
    for d37 in (paper / "d37_corrections.csv", paper / "d38_corrections.csv", paper / "d44_corrections.csv"):
        if not d37.exists():
            continue
        c = pd.read_csv(d37)
        codes = c[c["field"] == "code"]
        if len(codes):
            recode = dict(zip(codes["event_id"], codes["new"].astype(int)))
            hit = ev["event_id"].isin(recode)
            ev.loc[hit, "code"] = ev.loc[hit, "event_id"].map(recode)
        dates = c[(c["field"] == "event_date") & (c["new"] != c["old"])]
        fix = dict(zip(dates["event_id"], pd.to_datetime(dates["new"])))
        hit = ev["event_id"].isin(fix)
        ev.loc[hit, "event_date"] = ev.loc[hit, "event_id"].map(fix)
        ev.loc[hit, "date_source"] = "hand-checked"
        ev = ev[~ev["event_id"].isin(c.loc[c["field"] == "sample", "event_id"])]
    ev["forced"] = ev["code"].isin([3, 4]).astype(int)
    ev["conduct"] = (ev["code"] == 4).astype(int)

    wd = datasource.wikidata_founders()
    wd["s"] = wd["founder"].map(surname)
    wd_set = set(zip(wd["cik"], wd["s"]))
    notes = ev["notes"].fillna("")
    ev["founder_notes"] = notes.str.contains(FOUNDER_RE).astype(int)
    ev["founder_wikidata"] = [
        int((c, surname(n)) in wd_set) if pd.notna(c) else 0 for c, n in zip(ev["cik"], ev["exec_fullname"])
    ]
    ev["founder_v0"] = ((ev["founder_notes"] + ev["founder_wikidata"]) > 0).astype(int)
    ev["relationship_v0"] = notes.str.contains(REL_RE).astype(int)

    tk = datasource.securities("SEP")[
        ["permaticker", "ticker", "name", "isdelisted", "firstpricedate", "lastpricedate", "category", "cik"]
    ]
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
