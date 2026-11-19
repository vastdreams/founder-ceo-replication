# Data dictionary

Everything the analysis reads, what each column means, where we got it, whether it ships in this package, and what
you can use instead. The code never reads a vendor table directly: `code/datasource.py` serves nine **canonical
tables**, and an **adapter** in `code/adapters/` turns each vendor's export into them. Put the canonical tables in
one folder (Parquet or CSV) and point `FCE_DATA_DIR` at it.

| Canonical table | What it is | We used | Licence | In this package | Equivalent or better source | Adapter |
|---|---|---|---|---|---|---|
| `gentry` | Every CEO departure at S&P 1500 firms, 1992 to 2023, with the reason | Gentry et al. (2021) CEO dismissal database v10Oct2024 | CC BY 4.0 | yes | none: it is the field's standard | `adapters.gentry` (downloads and checks the md5) |
| `gvkey_cik` | Compustat gvkey to SEC CIK | built by us from the database's 8-K links and exact name matches | CC BY 4.0 (ours) | yes | `comp.company.cik` (WRDS), better | `adapters.crsp_compustat` |
| `wikidata_founders` | Founder names by CIK, a cross-check only | Wikidata "founded by" (P112) | CC0 | yes | none needed | — |
| `securities` | One row per security: id, CIK, listing dates, share class, industry | Sharadar TICKERS | commercial | **no** | CRSP `stocknames` + CCM link + `comp.company` (WRDS), better | `adapters.sharadar`, `adapters.crsp_compustat` |
| `prices` | Daily total-return index | Sharadar SEP `closeadj` | commercial | **no** | CRSP `dsf.ret` (WRDS), equivalent | `adapters.sharadar`, `adapters.crsp_compustat` |
| `actions` | How and when a listing ended | Sharadar ACTIONS | commercial | **no** | CRSP `dsedelist` (WRDS), better: it has the actual delisting return | `adapters.sharadar`, `adapters.crsp_compustat` |
| `factors` | Daily Fama-French five factors, momentum, risk-free rate | Kenneth French data library | free, not ours to redistribute | no (downloaded) | — | `adapters.french` |
| `fundamentals` | Annual as-reported statements | Sharadar SF1 (dimension ARY) | commercial | **no** | Compustat `funda` (WRDS), equivalent | `adapters.sharadar`, `adapters.crsp_compustat` |
| `sec_filings` | SEC filing index: 8-K and DEF 14A for the sample's firms | EDGAR submissions API | public domain | yes | — | `adapters.edgar` (set `SEC_USER_AGENT`) |

**Buy your own licensed data.** Prices, corporate actions, securities and fundamentals are licensed and are not
redistributed here. We used Sharadar's Core US Equities Bundle from Nasdaq Data Link (a personal subscription). CRSP
and Compustat through WRDS are the standard academic equivalents and are better on two counts: CRSP reports the
actual delisting return, and the CCM link maps gvkey to the security directly. Free price sources (Yahoo, Alpha
Vantage, Stooq) do not cover firms that were delisted or went bankrupt, which are a third of this sample after five
years, so they would bias every long-run result upward. Do not use them for Level 2.

**Universe.** Matched control firms are drawn from every US common stock in the same industry, not only from the
sample, so `prices`, `actions`, `securities` and `fundamentals` must cover the whole US common-stock universe from
1997 to 2026, including firms that were delisted.

---

## The canonical tables, column by column

### `gentry` — CEO departures

| Column | Type | Meaning |
|---|---|---|
| `dismissal_dataset_id` | int | The departure's id; this paper's `event_id` |
| `gvkey` | int | Compustat firm id |
| `coname` | str | Company name |
| `fyear` | int | Fiscal year of the departure |
| `exec_fullname` | str | Departing CEO |
| `departure_code` | int | 1 death, 2 illness, **3 dismissed for job performance**, **4 dismissed for legal violations or personal conduct**, **5 retired**, 6 new opportunity, 7 other, 9 unknown. Codes 3 and 4 are forced exits; 5 is the comparison group |
| `ceo_dismissal` | 0/1 | The database's dismissal flag |
| `notes` | str | The coders' notes |
| `sources` | str | URLs the coders used |
| `date_departure_announced` | date | Announcement date (day 0 is the first trading day on or after it) |
| `left_ceo_office` | date | Used when the announcement date is missing |

Cite: Gentry, R. J., Harrison, J. S., Quigley, T. J., and Boivie, S. (2021), A database of CEO turnover and dismissal
in S&P 1500 firms, 2000–2018, *Strategic Management Journal* 42(5), 968–991; and the Zenodo record 17725939.

### `gvkey_cik` — firm links

| Column | Type | Meaning |
|---|---|---|
| `gvkey` | int | Compustat firm id |
| `cik` | int | SEC Central Index Key |
| `n_links` | int | How many of the database's 8-K links support this pair; the highest wins |

### `wikidata_founders`

| Column | Type | Meaning |
|---|---|---|
| `cik` | int | SEC CIK |
| `founder` | str | A founder's name; used only as one of three cross-checks before the hand review |

### `securities`

| Column | Type | Meaning |
|---|---|---|
| `table` | str | `SEP` for the price universe, `SF1` for the fundamentals universe (the same rows twice is fine) |
| `permaticker` | int | Permanent security id (CRSP: PERMNO) |
| `ticker` | str | The security key shared by `prices`, `actions` and `fundamentals`. Any unique string works (the CRSP adapter uses `"P" + PERMNO`) |
| `name` | str | Security name |
| `cik` | int | Issuer's SEC CIK, the link to `gvkey_cik` |
| `isdelisted` | Y/N | Whether the security stopped trading |
| `firstpricedate`, `lastpricedate` | date | First and last trading day; the event's security must trade from 60 days before day 0 |
| `category` | str | Must contain `Common Stock` for common shares (others are dropped) |
| `famaindustry` | str | Industry used for matching. Sharadar gives the Fama-French 48 name; the CRSP adapter maps SIC to it with Ken French's definitions. Any consistent classification works |

### `prices`

| Column | Type | Meaning |
|---|---|---|
| `ticker` | str | Security key |
| `date` | date | Trading day |
| `closeadj` | float | Split- and dividend-adjusted close. Only its daily change is used, as the total return, so any total-return index works (CRSP adapter: cumulative product of 1 + RET) |

### `actions`

| Column | Type | Meaning |
|---|---|---|
| `ticker` | str | Security key |
| `date` | date | Date of the action |
| `action` | str | Lower case. `acquisitionby`, `mergerfrom`, `mergerto`, `acquisitionof` mean acquired (delisting return 0); `bankruptcyliquidation` means bankrupt (−100%); anything else within 60 days of the last price is another delisting (−30%), after Shumway (1997). CRSP adapter: DLSTCD 200–399 acquired, 400–499 and 574 bankrupt, other 500s delisted |

### `factors`

| Column | Type | Meaning |
|---|---|---|
| `date` | date | Trading day |
| `mkt_rf`, `smb`, `hml`, `rmw`, `cma`, `rf`, `mom` | float | Daily returns **in percent**, as Ken French publishes them |

### `fundamentals`

| Column | Type | Meaning |
|---|---|---|
| `ticker` | str | Security key |
| `calendardate` | date | Fiscal year-end (normalised to the calendar) |
| `datekey` | date | Filing date. Per firm and calendar year the code keeps the last fiscal year-end and, for it, the **first-filed** row, so amendments never replace the as-reported numbers |
| `assets` | float | Total assets (Compustat AT) |
| `ebitda` | float | EBITDA (Compustat OIBDP); ROA = EBITDA / assets |
| `netinc` | float | Net income (NI) |
| `revenue` | float | Revenue (REVT); sales growth |
| `marketcap` | float | Market value in **US dollars** (Compustat CSHO × PRCC_F × 10⁶) |
| `rnd` | float | R&D expense (XRD) |
| `capex` | float | Capital expenditure (CAPX); its absolute value is used |

### `sec_filings`

| Column | Type | Meaning |
|---|---|---|
| `cik` | int | Filer |
| `accession` | str | Accession number, `0000950123-06-001234` |
| `form` | str | `8-K`, `8-K/A` or `DEF 14A` |
| `filing_date` | date | Filing date |
| `items` | str | 8-K items, e.g. `5.02,9.01` (an 8-K from August 2004 on must carry 5.02 to count as a CEO-change filing) |

---

## Event-level files in this package (`data/events/`)

These are what the analysis produces from the canonical tables, and what Level 1 starts from. Returns are derived
quantities (abnormal returns over windows, buy-and-hold returns over horizons); no daily price is published.

| File | One row per | Key columns |
|---|---|---|
| `events.parquet` | departure (codes 3, 4, 5) | `event_id`, `gvkey`, `cik`, `code`, `forced`, `conduct`, `event_date`, `ticker`, `permaticker` |
| `returns.parquet` | departure with returns | `car_mm_m1p1` (market model, days −1 to +1), `car_ff5_*`, `scar_*`, `bhar_{1,3,5}y` (vs market, 12/36/60 months from day +2), `delisted_*`, `delist_kind_*` |
| `drift.parquet` | departure with returns | `pre` (days −30 to −2), `post` (+2 to +60), `car_ma_m1p1` (days −1 to +1), all market-adjusted |
| `ops_matched.parquet` | departure with a matched control | `ctrl_ticker`, `roa_k`, `abn_d_roa_k` (fiscal years 0 to 3 vs −1, minus the control), `mbhar_{1,3,5}y` (vs control) |
| `founder_final.parquet` | departure | `founder` (hand-reviewed for forced exits), `founder_reviewed` |
| `event_coding_final.jsonl` | departure | model codes: `ceo_is_founder`, `forced`, `primary_reason`, relationship details. Model quotes are removed; the hand-checked conduct labels are applied |
| `board_raw.jsonl` | departure | director lists from the proxy before and the proxy at least 600 days after |
| `board_outcomes.parquet` | departure with both proxies | `director_turnover`, `split_after`, `ceo_stays_director` |
| `pre1998_tsr.parquet` | 1992–1997 departure with a proxy return graph | `abn_tsr_3y` (three-year return minus the firm's reported index) |

Hand reviews (`data/reviews/`): `founder_review.csv` (every founder code on a forced exit: decision and basis),
`conduct_review.csv` (every sexual-conduct and relationship code). These decide the labels; the model never does.

## What is not in this package, and why

| Item | Why not | How to get it |
|---|---|---|
| Prices, actions, securities, fundamentals | Licensed | Sharadar (Nasdaq Data Link) or CRSP/Compustat (WRDS); run the adapter |
| Ken French factors | Not ours to redistribute | `python -m adapters.french` (free) |
| Per-firm daily and monthly return paths | Would let anyone rebuild licensed daily returns | `python paths.py` after Level 2; the aggregated series are in `results/figure_series.json` |
| News and filing text used for coding (8-K text, press releases, Wikipedia, New York Times Archive, Guardian) | Publisher terms; the NYT Archive API forbids redistribution | `evidence_fetch.py`, `match_nyt_archive.py` (free keys from each publisher) |
| Proxy statement text | Size | `extract_board.py` and `extract_docs` from EDGAR |
