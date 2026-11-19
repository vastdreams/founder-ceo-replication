# Replication archive: Firing the Founder, what happens after US boards remove their CEO

Code and event-level data for the paper by Abhishek Sehgal (2026). `python check.py` rebuilds every statistic in the paper from the files here and compares each one with the published results.

## What is here

| Path | Contents |
|---|---|
| `code/` | Every analysis step: building the event sample, the event study, coding, founder review, matched controls, statistics, board outcomes, the results payload and the draft builder |
| `data/events.parquet` | CEO departures from the open CEO dismissal database (Gentry, Harrison, Quigley and Boivie 2021, Zenodo record 17725939, v10Oct2024, ODC-By), linked to SEC CIK and ticker |
| `data/event_coding_v1.jsonl` | Codes for founder status, reason and relationship details. Drafted by a language model from the database notes; every sexual-conduct and relationship label was checked by hand (`data/conduct_review.csv`) and the model's free-text quotes are not published |
| `data/conduct_review.csv` | The hand review of every sexual-conduct and relationship label, with the public-record basis for each decision |
| `data/founder_review.csv` | The hand review of every founder code: decision and reason for each of 170 cases |
| `data/founder_final.parquet` | The founder flag used in the paper |
| `data/returns.parquet` | Per-event abnormal returns, buy-and-hold returns and delisting outcomes |
| `data/ops_matched.parquet` | Per-event matched controls, operating ratios and matched buy-and-hold returns (log size only) |
| `data/board_raw.jsonl`, `data/board_outcomes.parquet` | Director lists read from SEC proxy statements, and the board outcomes computed from them |
| `results/` | Every results file and `combined_results.json`, the payload the paper's numbers come from |
| `data/DECISIONS.md` | Method decisions taken during the study |

## What is not here, and how to get it

Daily prices and annual statements come from the Sharadar Core US Equities Bundle (Nasdaq Data Link), which may not be redistributed. The files here hold only per-event results derived from it. To rebuild those from scratch, subscribe to the bundle, load the SEP, SF1, TICKERS and ACTIONS tables, and run `code/build_events.py`, `code/event_study.py` and `code/ops_matched.py`. Factor returns come from Kenneth French's data library. SEC filings come from EDGAR.

## Run

```
pip install pandas numpy scipy statsmodels pyarrow
python check.py
```

Expected output: every statistic checked, none different.

## Licences

Code: MIT. The departure data derive from the CEO dismissal database under the Open Data Commons Attribution License; cite Gentry et al. (2021) and the database version. Coding, review and derived results: CC BY 4.0.
