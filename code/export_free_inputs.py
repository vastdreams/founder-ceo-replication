"""Write the free canonical inputs from the authors' database, for the public replication package.

Tables: gentry (CC BY 4.0), gvkey_cik (this paper's link table), wikidata_founders (CC0), sec_filings (public
domain SEC data; the 8-K and DEF 14A filings of the sample's firms), factors (Ken French; not redistributed by
default, pass --factors to include). Licensed vendor tables (prices, actions, securities, fundamentals) are never
written here.
Usage: FCE_DATA_SOURCE=postgres python export_free_inputs.py OUT_DIR [--factors]
"""

import pathlib
import sys

import datasource


def main(out: str, factors: bool = False):
    d = pathlib.Path(out)
    d.mkdir(parents=True, exist_ok=True)
    g = datasource.gentry()
    g.to_parquet(d / "gentry.parquet", index=False)
    links = datasource.gvkey_cik()
    links.to_parquet(d / "gvkey_cik.parquet", index=False)
    datasource.wikidata_founders().to_parquet(d / "wikidata_founders.parquet", index=False)
    ciks = set(links[links["gvkey"].isin(g["gvkey"])]["cik"].dropna().astype(int))
    f = datasource.sec_filings(["8-K", "8-K/A", "DEF 14A"])
    f = f[f["cik"].astype(int).isin(ciks)]
    f.to_parquet(d / "sec_filings.parquet", index=False)
    if factors:
        datasource.factors().to_parquet(d / "factors.parquet", index=False)
    for p in sorted(d.glob("*.parquet")):
        print(p.name, p.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1], "--factors" in sys.argv)
