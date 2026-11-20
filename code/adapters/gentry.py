"""CEO departures: the open CEO dismissal database (Gentry, Harrison, Quigley and Boivie 2021), v10Oct2024.

Source : Zenodo record 17725939, CC BY 4.0 (cite the paper and the record). Free.
Output : gentry  (datasource.TABLES["gentry"])
Usage  : python -m adapters.gentry            downloads the .xlsx and checks its md5
         python -m adapters.gentry FILE.xlsx  converts a copy you already have
"""

import hashlib
import sys
import urllib.request

import pandas as pd
from adapters.common import out_dir, write

URL = (
    "https://zenodo.org/records/17725939/files/CEO%20Dismissal%20Database%20Posted%20to%20Web%2010Oct24.xlsx?download=1"
)
MD5 = "cc56b45861bfdaf8086ccdd11c34b747"


def main(path=None):
    if path is None:
        path = out_dir() / "gentry_10Oct24.xlsx"
        if not path.exists():
            urllib.request.urlretrieve(URL, path)  # nosec B310 - fixed https source
        if hashlib.md5(path.read_bytes()).hexdigest() != MD5:  # nosec B324 - integrity check, not security
            raise SystemExit(f"{path}: md5 does not match the Zenodo record")
    d = pd.read_excel(path)
    for c in ("date_departure_announced", "left_ceo_office"):
        d[c] = pd.to_datetime(d[c], errors="coerce")
    write("gentry", d)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
