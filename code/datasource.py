"""Every raw input the analysis reads, behind one interface, so a replicator can plug in their own data.

Two backends, chosen by the environment variable FCE_DATA_SOURCE:
  files     (default when FCE_DATA_DIR is set) canonical tables as Parquet or CSV files in FCE_DATA_DIR, written by
            the adapters in adapters/ from Sharadar, CRSP/Compustat (WRDS), Ken French, EDGAR and Zenodo.
  postgres  the authors' research database (R&D Alpha), via ~/fce_db.py.

Each function returns the same columns whichever backend serves it; DATA.md defines every column, its source, and
equivalent sources. The analysis never reads a vendor table directly.

  gentry()             CEO departures (Gentry et al. 2021, v10Oct2024)
  gvkey_cik()          gvkey -> SEC CIK links
  wikidata_founders()  founder names by CIK (cross-check only)
  securities(table)    one row per security: ticker (the security key), permaticker, cik, dates, category, industry
  prices(tickers)      daily split- and dividend-adjusted close (its daily change is the total return)
  actions(tickers)     corporate actions that end a listing (acquisition, merger, bankruptcy, delisting)
  factors()            daily Fama-French five factors, momentum and the risk-free rate, in percent
  fundamentals()       annual as-reported fundamentals
  sec_filings(forms)   SEC filing index: cik, accession, form, filing date, 8-K items
"""

from __future__ import annotations

import os
import pathlib
import sys

import pandas as pd

TABLES = {
    "gentry": [
        "dismissal_dataset_id",
        "gvkey",
        "coname",
        "fyear",
        "exec_fullname",
        "departure_code",
        "ceo_dismissal",
        "notes",
        "sources",
        "date_departure_announced",
        "left_ceo_office",
    ],
    "gvkey_cik": ["gvkey", "cik", "n_links"],
    "wikidata_founders": ["cik", "founder"],
    "securities": [
        "table",
        "permaticker",
        "ticker",
        "name",
        "cik",
        "isdelisted",
        "firstpricedate",
        "lastpricedate",
        "category",
        "famaindustry",
    ],
    "prices": ["ticker", "date", "closeadj"],
    "actions": ["ticker", "date", "action"],
    "factors": ["date", "mkt_rf", "smb", "hml", "rmw", "cma", "rf", "mom"],
    "fundamentals": [
        "ticker",
        "calendardate",
        "datekey",
        "assets",
        "ebitda",
        "netinc",
        "revenue",
        "marketcap",
        "rnd",
        "capex",
    ],
    "sec_filings": ["cik", "accession", "form", "filing_date", "items"],
}


def backend() -> str:
    return os.environ.get("FCE_DATA_SOURCE") or ("files" if os.environ.get("FCE_DATA_DIR") else "postgres")


def _dir() -> pathlib.Path:
    return pathlib.Path(
        os.environ.get("FCE_DATA_DIR") or pathlib.Path(__file__).resolve().parents[1] / "data" / "inputs"
    )


def _read(name: str, filters=None) -> pd.DataFrame:
    """A canonical table; ``filters`` (pyarrow style) are pushed down into Parquet so a price file is never read whole."""
    base = _dir()
    for ext in (".parquet", ".csv.gz", ".csv"):
        p = base / f"{name}{ext}"
        if p.exists():
            if ext == ".parquet":
                d = pd.read_parquet(p, columns=TABLES[name], filters=filters)
            else:
                d = pd.read_csv(p, low_memory=False)
            missing = [c for c in TABLES[name] if c not in d.columns]
            if missing:
                raise ValueError(f"{p} lacks columns {missing}; see DATA.md")
            return d[TABLES[name]].copy()
    raise FileNotFoundError(f"{name} not found in {base} (.parquet, .csv.gz or .csv); see DATA.md for how to build it")


def _con():
    sys.path.insert(0, str(pathlib.Path.home()))
    import fce_db  # noqa: E402  the authors' database connector

    return fce_db.connect()


def _sql(q: str, params=None) -> pd.DataFrame:
    return pd.read_sql(q, _con(), params=params)


def _dates(d: pd.DataFrame, cols) -> pd.DataFrame:
    for c in cols:
        d[c] = pd.to_datetime(d[c], errors="coerce")
    return d


def gentry() -> pd.DataFrame:
    if backend() == "files":
        d = _read("gentry")
    else:
        d = _sql(f"select {', '.join(TABLES['gentry'])} from world.ceo_turnover_gentry")
    return _dates(d, ["date_departure_announced", "left_ceo_office"])


def gvkey_cik() -> pd.DataFrame:
    return _read("gvkey_cik") if backend() == "files" else _sql("select gvkey, cik, n_links from world.gvkey_cik")


def wikidata_founders() -> pd.DataFrame:
    return (
        _read("wikidata_founders") if backend() == "files" else _sql("select cik, founder from world.wikidata_founders")
    )


def securities(table: str = "SEP") -> pd.DataFrame:
    if backend() == "files":
        d = _read("securities")
        d = d[d["table"] == table]
    else:
        d = _sql(
            """select "table", permaticker, ticker, name, (regexp_match(secfilings, 'CIK=0*([0-9]+)'))[1]::bigint as cik,
                      isdelisted, firstpricedate, lastpricedate, category, famaindustry
               from sharadar.tickers where "table" = %(t)s""",
            {"t": table},
        )
    return _dates(d, ["firstpricedate", "lastpricedate"])


def prices(tickers) -> pd.DataFrame:
    tickers = tuple(sorted({t for t in tickers if isinstance(t, str)}))
    if backend() == "files":
        d = _read("prices", filters=[("ticker", "in", list(tickers))])
        d = d[d["ticker"].isin(tickers) & (d["closeadj"] > 0)]
    else:
        d = _sql(
            "select ticker, date, closeadj from sharadar.sep where ticker in %(t)s and closeadj > 0 order by ticker, date",
            {"t": tickers},
        )
    return _dates(d, ["date"]).sort_values(["ticker", "date"])


def actions(tickers) -> pd.DataFrame:
    tickers = tuple(sorted({t for t in tickers if isinstance(t, str)}))
    if backend() == "files":
        d = _read("actions", filters=[("ticker", "in", list(tickers))])
        d = d[d["ticker"].isin(tickers)]
    else:
        d = _sql(
            "select ticker, date::date as date, action from sharadar.actions where ticker in %(t)s", {"t": tickers}
        )
    return _dates(d, ["date"])


def factors() -> pd.DataFrame:
    if backend() == "files":
        d = _read("factors")
    else:
        d = _sql(
            "select f.date, f.mkt_rf, f.smb, f.hml, f.rmw, f.cma, f.rf, m.mom from world.ff5_daily f join world.mom_daily m using(date)"
        )
    return _dates(d, ["date"])


def fundamentals() -> pd.DataFrame:
    if backend() == "files":
        d = _read("fundamentals")
    else:
        d = _sql(
            """select ticker, calendardate, datekey, assets, ebitda, netinc, revenue, marketcap, rnd, capex
               from sharadar.sf1 where dimension = 'ARY'"""
        )
    return _dates(d, ["calendardate", "datekey"])


def sec_filings(forms) -> pd.DataFrame:
    forms = tuple(forms)
    if backend() == "files":
        d = _read("sec_filings")
        d = d[d["form"].isin(forms)]
    else:
        d = _sql(
            "select cik, accession, form, filing_date, items from world.sec_filings where form in %(f)s", {"f": forms}
        )
    return _dates(d, ["filing_date"])
