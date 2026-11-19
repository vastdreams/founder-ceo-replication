"""Sharadar Core US Equities (Nasdaq Data Link): prices, corporate actions, securities and fundamentals.

Licence: commercial (the authors use a personal Core US Equities Bundle subscription). Not redistributed.
Get it : https://data.nasdaq.com/databases/SFA -> bulk export each table as CSV (SEP, ACTIONS, TICKERS, SF1).
Output : securities, prices, actions, fundamentals
Usage  : python -m adapters.sharadar DIR    where DIR holds SHARADAR_SEP*.csv, SHARADAR_ACTIONS*.csv,
                                             SHARADAR_TICKERS*.csv and SHARADAR_SF1*.csv (zipped or not)
Sharadar's column names are the canonical names, so this adapter mostly selects columns and pulls the CIK out of
the TICKERS 'secfilings' URL.
"""

import pathlib
import sys

import pandas as pd

from adapters.common import write


def _find(d: pathlib.Path, table: str) -> pathlib.Path:
    hits = sorted(d.glob(f"SHARADAR_{table}*.csv*")) + sorted(d.glob(f"SHARADAR_{table}*.zip"))
    if not hits:
        raise SystemExit(f"no SHARADAR_{table} export in {d}")
    return hits[-1]


def write_chunked(name: str, src: pathlib.Path, cols: list[str], rows: int = 2_000_000) -> None:
    """Stream a large CSV into Parquet a few million rows at a time, so SEP (about 1 GB) fits in modest memory."""
    import pyarrow as pa
    import pyarrow.parquet as pq

    from adapters.common import out_dir

    path, writer, n = out_dir() / f"{name}.parquet", None, 0
    for chunk in pd.read_csv(src, usecols=cols, chunksize=rows, dtype={"ticker": str, "date": str}):
        chunk["date"] = pd.to_datetime(chunk["date"])
        table = pa.Table.from_pandas(chunk[cols], preserve_index=False)
        writer = writer or pq.ParquetWriter(path, table.schema)
        writer.write_table(table)
        n += len(chunk)
    if writer:
        writer.close()
    print(f"wrote {path} ({n:,} rows)")


def main(folder: str):
    d = pathlib.Path(folder)
    tk = pd.read_csv(_find(d, "TICKERS"), low_memory=False)
    tk["cik"] = pd.to_numeric(tk["secfilings"].astype(str).str.extract(r"CIK=0*(\d+)")[0], errors="coerce")
    write("securities", tk)
    write_chunked("prices", _find(d, "SEP"), ["ticker", "date", "closeadj"])
    act = pd.read_csv(_find(d, "ACTIONS"), usecols=["ticker", "date", "action"], low_memory=False)
    write("actions", act)
    sf1 = pd.read_csv(_find(d, "SF1"), low_memory=False)
    sf1 = sf1[sf1["dimension"] == "ARY"]
    write("fundamentals", sf1)


if __name__ == "__main__":
    main(sys.argv[1])
