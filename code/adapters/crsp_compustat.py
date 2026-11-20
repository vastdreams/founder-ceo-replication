"""CRSP and Compustat (WRDS) in place of Sharadar: the standard academic sources, and the better ones for this paper.

Why better: CRSP reports the actual delisting return (DLRET), and the CCM link maps the dismissal database's gvkey to
the security without going through a CIK. The paper's code applies the Shumway convention for delisting returns
(event_study.delist_return) so the two sources are treated alike; a reader who prefers CRSP's own DLRET can read it
from crsp_delist and substitute it there.

Licence: WRDS subscription (most universities). Not redistributed.
Inputs (one CSV or Parquet file each in DIR, exported from WRDS with these columns, lowercase):
  crsp_dsf        permno, date, ret                                     (crsp.dsf, 1997 onward)
  crsp_names      permno, namedt, nameendt, ticker, comnam, shrcd, siccd (crsp.dsenames or crsp.msenames)
  crsp_delist     permno, dlstdt, dlstcd, dlret                          (crsp.dsedelist)
  ccm_link        gvkey, lpermno, linkdt, linkenddt, linktype, linkprim  (crsp.ccmxpf_lnkhist)
  comp_funda      gvkey, datadate, fyear, at, oibdp, ni, revt, xrd, capx, csho, prcc_f
                  (comp.funda with indfmt='INDL', datafmt='STD', popsrc='D', consol='C')
  comp_company    gvkey, cik                                             (comp.company)
Output : securities, prices, actions, fundamentals, gvkey_cik
Usage  : python -m adapters.crsp_compustat DIR

Mapping to the canonical tables (DATA.md):
  security key  ticker = "P" + permno; permaticker = permno
  prices        closeadj = cumulative product of (1 + RET), so its daily change is CRSP's total return
  actions       DLSTCD 200-399 -> acquisition ("acquisitionby"); 400-499 and 574 -> "bankruptcyliquidation";
                other 500-599 -> "delisted"; the action date is DLSTDT
  industry      famaindustry = Fama-French 48-industry name from SICCD (Ken French's Siccodes48 definitions)
  fundamentals  assets = AT, ebitda = OIBDP, netinc = NI, revenue = REVT, rnd = XRD, capex = CAPX,
                marketcap = CSHO x PRCC_F x 1e6 (Sharadar reports USD, Compustat millions); datekey = datadate
  gvkey_cik     from comp.company, so build_events links each departure through the firm's own CIK
"""

import io
import pathlib
import sys
import urllib.request
import zipfile

import numpy as np
import pandas as pd
from adapters.common import write

FF48_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Siccodes48.zip"


def _read(d: pathlib.Path, name: str) -> pd.DataFrame:
    for ext in (".parquet", ".csv.gz", ".csv"):
        p = d / f"{name}{ext}"
        if p.exists():
            x = pd.read_parquet(p) if ext == ".parquet" else pd.read_csv(p, low_memory=False)
            x.columns = [c.lower() for c in x.columns]
            return x
    raise SystemExit(f"{name}.csv or .parquet not found in {d}; see the module docstring for the WRDS query")


def ff48() -> list[tuple[int, int, str]]:
    """(sic_low, sic_high, industry name) ranges from Ken French's Siccodes48.txt."""
    raw = urllib.request.urlopen(FF48_URL, timeout=60).read()  # nosec B310 - fixed https source
    z = zipfile.ZipFile(io.BytesIO(raw))
    text = z.read(z.namelist()[0]).decode("latin1")
    out, name = [], None
    for line in text.splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0].isdigit() and len(parts) >= 3 and not parts[1][0].isdigit():
            name = " ".join(parts[2:]) if len(parts) > 2 else parts[1]
        elif "-" in parts[0] and name:
            lo, hi = parts[0].split("-")
            out.append((int(lo), int(hi), name))
    return out


def industry(sic, ranges) -> str:
    try:
        s = int(sic)
    except (TypeError, ValueError):
        return "Almost Nothing"
    return next((n for lo, hi, n in ranges if lo <= s <= hi), "Almost Nothing")


def delist_action(code) -> str | None:
    if pd.isna(code):
        return None
    c = int(code)
    if 200 <= c < 400:
        return "acquisitionby"
    if 400 <= c < 500 or c == 574:
        return "bankruptcyliquidation"
    if 500 <= c < 600:
        return "delisted"
    return None


def main(folder: str):
    d = pathlib.Path(folder)
    dsf = _read(d, "crsp_dsf")
    dsf["date"] = pd.to_datetime(dsf["date"])
    dsf["ret"] = pd.to_numeric(dsf["ret"], errors="coerce").fillna(0.0)
    dsf = dsf.sort_values(["permno", "date"])
    dsf["closeadj"] = dsf.groupby("permno")["ret"].transform(lambda r: np.cumprod(1.0 + r.values))
    dsf["ticker"] = "P" + dsf["permno"].astype(int).astype(str)
    write("prices", dsf)

    names = _read(d, "crsp_names").sort_values(["permno", "nameendt"])
    last = names.drop_duplicates("permno", keep="last")
    span = (
        dsf.groupby("permno")["date"]
        .agg(["min", "max"])
        .rename(columns={"min": "firstpricedate", "max": "lastpricedate"})
    )
    dl = _read(d, "crsp_delist")
    dl["dlstdt"] = pd.to_datetime(dl["dlstdt"])
    dl["action"] = dl["dlstcd"].map(delist_action)
    link = _read(d, "ccm_link")
    link = link[link["linktype"].isin(["LU", "LC"]) & link["linkprim"].isin(["P", "C"])]
    comp = _read(d, "comp_company")[["gvkey", "cik"]].dropna()
    comp["cik"] = pd.to_numeric(comp["cik"], errors="coerce")
    perm_cik = (
        link.merge(comp, on="gvkey")[["lpermno", "cik"]]
        .drop_duplicates("lpermno")
        .rename(columns={"lpermno": "permno"})
    )
    ranges = ff48()
    sec = last.merge(span, left_on="permno", right_index=True, how="inner").merge(perm_cik, on="permno", how="left")
    sec["permaticker"] = sec["permno"].astype(int)
    sec["ticker"] = "P" + sec["permno"].astype(int).astype(str)
    sec["name"] = sec["comnam"]
    sec["isdelisted"] = np.where(sec["permno"].isin(dl.loc[dl["action"].notna(), "permno"]), "Y", "N")
    sec["category"] = np.where(sec["shrcd"].isin([10, 11]), "Domestic Common Stock", "Other")
    sec["famaindustry"] = sec["siccd"].map(lambda s: industry(s, ranges))
    write("securities", pd.concat([sec.assign(table="SEP"), sec.assign(table="SF1")]))

    act = dl.dropna(subset=["action"]).assign(
        ticker=lambda x: "P" + x["permno"].astype(int).astype(str), date=lambda x: x["dlstdt"]
    )
    write("actions", act)

    fa = _read(d, "comp_funda")
    fa["datadate"] = pd.to_datetime(fa["datadate"])
    link["linkdt"] = pd.to_datetime(link["linkdt"])
    link["linkenddt"] = pd.to_datetime(link["linkenddt"].replace({"E": None}), errors="coerce").fillna(
        pd.Timestamp("2099-12-31")
    )
    m = fa.merge(link[["gvkey", "lpermno", "linkdt", "linkenddt"]], on="gvkey")
    m = m[(m["datadate"] >= m["linkdt"]) & (m["datadate"] <= m["linkenddt"])]
    out = pd.DataFrame(
        {
            "ticker": "P" + m["lpermno"].astype(int).astype(str),
            "calendardate": m["datadate"],
            "datekey": m["datadate"],
            "assets": m["at"],
            "ebitda": m["oibdp"],
            "netinc": m["ni"],
            "revenue": m["revt"],
            "rnd": m["xrd"],
            "capex": m["capx"],
            "marketcap": m["csho"] * m["prcc_f"] * 1e6,
        }
    )
    write("fundamentals", out)
    write("gvkey_cik", comp.assign(n_links=1))


if __name__ == "__main__":
    main(sys.argv[1])
