# Sacked: Sex, Fraud, Founders, and the Fate of Firms That Fire Their CEO

Replication package for Abhishek Sehgal, *Sacked: Sex, Fraud, Founders, and the Fate of Firms That Fire Their CEO*
(working paper, November 2026). Every number, table and figure in the paper is produced by the code here.

**Read the paper:** [paper/Sacked.pdf](paper/Sacked.pdf) (two columns, 19 pages). The text with every statistic
filled in is [paper/paper.md](paper/paper.md).

**The question.** What happens to a US public company after its board fires the CEO, and does it matter whether the
CEO founded the company, or was fired over a sex or other personal scandal rather than fraud? We follow every firing at
an S&P 1500 firm from 1998 to 2023 (1,272 firings with prices, 83 of them founders; 2,253 retirements as the
comparison) from six weeks before the announcement to five years after it, with the number of firms measured at every
horizon. The 121 firings over fraud or other legal violation are kept apart as a comparison group. Announcement
windows use the 531 well-dated firings (dated by the database or by hand); long-run results use every firing.

![Prices slide before the firing, drop on the news, then stop](figures/fig1_event_time.png)

## What we find

| Horizon | Firings | Retirements | N firings |
|---|---|---|---|
| Trading days −30 to −2, return minus the market | −5.4% | 0.0% | 531 |
| Trading days −1 to +1, abnormal return | −2.3% | −0.3% | 528 |
| Trading days +2 to +60, return minus the market | −1.0% (n.s.) | −0.8% | 521 |
| 12 / 36 / 60 months, median return minus a matched firm | −4.6% / 0.0% (n.s.) / −4.7% (n.s.) | 0.0% / 0.5% / 2.8% | 1,220 / 1,217 / 1,164 |
| 36 months, five-factor and momentum alpha, a month | 0.03% (n.s.; 95% interval −0.35% to 0.42%) | 0.13% | 319 months |
| Within 60 months, delisted | 31.9% (19.0% taken over, 12.0% bankrupt) | 16.8% (14.1%, 2.6%) | 1,215 |

* **Before and at the announcement.** In the six weeks before a firing is announced the shares lag the market by
  5.4%; over the three trading days around it they fall a further 2.3%, and the next three months add no significant
  move.
* **The reason and the person.** After a firing over fraud or other legal violation the shares fall 6.9% (41
  well-dated firings). After a personal scandal they fall 1.5% (39), not significantly different from the 2.3% after
  other firings (95% interval for the gap −0.9 to 2.6 points). A fired founder's shares fall 3.2% (52) against 2.2%
  for a hired CEO; the gap is not significant (p = 0.63; 95% interval −5.2 to 3.2 points). Both groups are too small
  for precise estimates.
* **Who counts and which dates.** Firings the evidence-based coding also reads as forced fall 1.6% (190); reweighting
  the well-dated firings to resemble every firing gives 2.2%; over trading days −5 to +5 every firing at any date
  falls 2.0%. Delisting is also modelled as a duration (Cox hazard ratio 1.38 with every control).
* **What becomes of the firm.** Within five years 12.0% of firing firms go bankrupt, against 2.6% after a retirement,
  and 19.0% are taken over, against 14.1%. With controls for size, profitability, prior return, leverage,
  book-to-market, distress and losses, the delisting gap is 6.6 percentage points (p = 0.005), 2.3 of them
  bankruptcy.

![Within five years, 31.9% of firing firms are delisted](figures/fig3_exits.png)

## Replicate it

Three levels, from no data at all to the full pipeline.

| Level | What it rebuilds | What you need | Command |
|---|---|---|---|
| **1** | Every statistic, table and figure in the paper | Python and this repository | `python check.py` |
| **2** | The event-level files (returns, delistings, matched firms) from raw prices and statements, then Level 1 | Licensed prices and fundamentals: Sharadar, or CRSP and Compustat (WRDS), or an equivalent; see [DATA.md](DATA.md) | `make inputs-sharadar SHARADAR_DIR=...` or `make inputs-crsp WRDS_DIR=...`, then `python run_level2.py` |
| **3** | The founder, reason and board codes from filings and news | An OpenAI-compatible LLM key, `SEC_USER_AGENT`, free news API keys | `code/evidence_fetch.py`, `code/code_events.py`, `code/extract_board.py` |

```bash
git clone https://github.com/vastdreams/founder-ceo-replication && cd founder-ceo-replication
python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python check.py      # 518 statistics and 17 tables checked, 0 differ; figures in outputs/figures/
```

**Bring your own data (Level 2).** The code never reads a vendor table. `code/datasource.py` serves nine canonical
tables from `data/inputs/`, and an adapter in `code/adapters/` writes them from your vendor's export:
`sharadar.py` (Nasdaq Data Link bulk CSVs), `crsp_compustat.py` (WRDS exports; the better source, with actual
delisting returns), `french.py` and `gentry.py` (free downloads), `edgar.py` (SEC filing index). The free tables
ship in `data/inputs/` already. [DATA.md](DATA.md) defines every table and column and names an equivalent source
for each. Buy your own licence for prices and fundamentals: they are not redistributed here, and free price sources
miss the delisted firms that make up a third of the sample after five years.

We verified the plug-in path end to end: exporting our Sharadar tables as vendor CSVs, running the adapter and
rebuilding the event-level files reproduces ours exactly. With CRSP and Compustat expect small differences (price
adjustments, delisting dates, matched firms) and the same conclusions; `run_level2.py` reports them.

## What is here

```
check.py            Level 1: rebuild and compare every statistic and table, redraw the figures
run_level2.py       Level 2: rebuild the event-level files from your data, then compare
DATA.md             data dictionary: every input, every column, sources, licences, equivalents
code/               the analysis (the same code that produced the paper) and the adapters
data/inputs/        free canonical inputs: CEO dismissal database, gvkey-CIK links, Wikidata founders, SEC index
data/events/        event-level results: returns, delistings, matched firms, codes, board outcomes
data/reviews/       hand reviews of every founder, fraud, conduct and scandal code, date corrections and exclusions
results/            the published statistics (combined_results.json), figure series and the inputs that need licensed data to rebuild
figures/            the paper's figures
paper/              the paper (PDF and filled text), its template and the method decisions (DECISIONS.md)
```

Every statistic carries its horizon (how long after the announcement it is measured) and its N, and the build
stops if one does not (`code/combine_results.py`).

## Licences and citation

Code: MIT ([LICENSE](LICENSE)). Our data (event-level results, codes, hand reviews, link tables): CC BY 4.0
([LICENSE-DATA](LICENSE-DATA)). The CEO dismissal database is CC BY 4.0: cite Gentry, Harrison, Quigley and Boivie
(2021, *Strategic Management Journal*) and Zenodo record 17725939. SEC data are public domain. Wikidata is CC0.

Cite this package with [CITATION.cff](CITATION.cff).
