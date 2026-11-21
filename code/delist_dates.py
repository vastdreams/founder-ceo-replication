"""The date of each departure's bankruptcy action, so a firing at or just before a bankruptcy filing can be told
apart from a bankruptcy that followed the firing.

A firm already in Chapter 11 when its CEO left (Sears 2018, Dana 2008, Six Flags 2010) did not fail after the
firing. Survival results set aside bankruptcies recorded within 180 days of the announcement (stats_returns.py).
The output is a derived date per event, not a price, so it ships in the replication package.

Inputs : analysis/out/returns.parquet, datasource.actions
Output : analysis/out/delist_dates.parquet (event_id, bankruptcy_date, days_to_bankruptcy)
"""

import pathlib

import datasource
import pandas as pd

HERE = pathlib.Path(__file__).parent


def main():
    r = pd.read_parquet(HERE / "out" / "returns.parquet")[["event_id", "ticker", "event_date"]].dropna()
    acts = datasource.actions(list(r["ticker"].unique()))
    acts["date"] = pd.to_datetime(acts["date"])
    bk = acts[acts["action"].str.contains("bankrupt", na=False)].groupby("ticker")["date"].min()
    r["bankruptcy_date"] = r["ticker"].map(bk)
    r["days_to_bankruptcy"] = (r["bankruptcy_date"] - pd.to_datetime(r["event_date"])).dt.days
    r[["event_id", "bankruptcy_date", "days_to_bankruptcy"]].to_parquet(
        HERE / "out" / "delist_dates.parquet", index=False
    )
    print("events", len(r), "with a bankruptcy action", int(r["bankruptcy_date"].notna().sum()))


if __name__ == "__main__":
    main()
