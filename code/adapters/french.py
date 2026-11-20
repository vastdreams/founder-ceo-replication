"""Daily Fama-French five factors, momentum and the risk-free rate, in percent (Kenneth R. French data library). Free.

Output : factors  (date, mkt_rf, smb, hml, rmw, cma, rf, mom)
Usage  : python -m adapters.french
"""

import io
import urllib.request
import zipfile

import pandas as pd
from adapters.common import write

BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
FF5 = BASE + "F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
MOM = BASE + "F-F_Momentum_Factor_daily_CSV.zip"


def _csv(url: str) -> pd.DataFrame:
    raw = urllib.request.urlopen(url, timeout=60).read()  # nosec B310 - fixed https source
    text = zipfile.ZipFile(io.BytesIO(raw)).read(zipfile.ZipFile(io.BytesIO(raw)).namelist()[0]).decode("latin1")
    lines = text.splitlines()
    start = next(
        i for i, x in enumerate(lines) if x.strip().startswith(",") or x.lower().startswith(",mkt") or ",Mom" in x
    )
    rows = []
    for x in lines[start + 1 :]:
        parts = [p.strip() for p in x.split(",")]
        if len(parts) < 2 or not parts[0].isdigit() or len(parts[0]) != 8:
            if rows:
                break
            continue
        rows.append(parts)
    cols = [c.strip().lower().replace("-", "_") for c in lines[start].split(",")]
    cols[0] = "date"
    d = pd.DataFrame(rows, columns=cols[: len(rows[0])])
    d["date"] = pd.to_datetime(d["date"], format="%Y%m%d")
    return d


def main():
    f = _csv(FF5).rename(columns={"mkt_rf": "mkt_rf"})
    m = _csv(MOM)
    m = m.rename(columns={m.columns[1]: "mom"})[["date", "mom"]]
    d = f.merge(m, on="date")
    for c in ("mkt_rf", "smb", "hml", "rmw", "cma", "rf", "mom"):
        d[c] = pd.to_numeric(d[c])
    write("factors", d)


if __name__ == "__main__":
    main()
