"""Shared helpers for the adapters: where canonical tables go, and how they are written."""

import os
import pathlib

import pandas as pd


def out_dir() -> pathlib.Path:
    d = pathlib.Path(os.environ.get("FCE_DATA_DIR") or pathlib.Path(__file__).resolve().parents[2] / "data" / "inputs")
    d.mkdir(parents=True, exist_ok=True)
    return d


def write(name: str, d: pd.DataFrame) -> pathlib.Path:
    """Write one canonical table as Parquet, with exactly the columns datasource.TABLES lists."""
    from datasource import TABLES

    missing = [c for c in TABLES[name] if c not in d.columns]
    if missing:
        raise ValueError(f"{name}: adapter did not produce {missing}")
    p = out_dir() / f"{name}.parquet"
    d[TABLES[name]].to_parquet(p, index=False)
    print(f"wrote {p} ({len(d):,} rows)")
    return p


def user_agent() -> str:
    """SEC asks automated clients to identify themselves: set SEC_USER_AGENT='Your Name your@email'."""
    ua = os.environ.get("SEC_USER_AGENT")
    if not ua:
        raise SystemExit("Set SEC_USER_AGENT to 'Name email' before calling SEC EDGAR (https://www.sec.gov/os/accessing-edgar-data)")
    return ua
