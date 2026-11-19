# Sacked: Sex, Fraud, Founders, and the Fate of Firms That Fire Their CEO

Replication package for Abhishek Sehgal, *Sacked: Sex, Fraud, Founders, and the Fate of Firms That Fire Their CEO*
(working paper, November 2026). Every number, table and figure in the paper is produced by the code here.

**The question.** What happens to a US public company after its board fires the CEO, and does it matter whether the
CEO founded the company and why the board acted? We follow every forced CEO exit at an S&P 1500 firm from 1998 to
2023 (1,396 forced exits, 2,254 retirements as the comparison) from six weeks before the announcement to five years
after it, and report the number of firms measured at every horizon.

![Prices slide before the firing, drop on the news, then stop](figures/fig1_event_time.png)

## What we find

| Horizon | Forced exits | Retirements | N forced |
|---|---|---|---|
| Trading days −30 to −2, return minus the market | −5.7% | 0.4% | 1,396 |
| Trading days −1 to +1, abnormal return | −1.6% | −0.1% | 1,390 |
| Trading days +2 to +60, return minus the market | −0.5% (n.s.) | −0.1% | 1,371 |
| 12 / 36 / 60 months, median return minus a matched firm | −4.2% / −2.9% (n.s.) / −8.2% | 0.1% / −0.9% / 1.7% | 1,326 / 1,324 / 1,278 |
| Within 60 months, share no longer trading | 33.1% | 17.3% | 1,346 |

* **The market sees it coming** and reacts once: the stock slides for six weeks, drops on the news, then stops.
* **Why matters more than who.** Firings for financial misconduct cost 6.4% in three days; sex and relationship
  scandals cost 1.0% (difference p = 0.04, 17 against 89 cases). Fired founders cost 3.4% against 1.4% for hired
  CEOs, a gap that is not statistically significant (p = 0.15).
* **The lasting consequence is a change of owner.** A third of the firms stop trading within five years, mostly
  through takeovers (20.1%) rather than bankruptcy (12.1%). Against the market the median fired-founder firm loses
  80% over five years; against a matched firm, nothing.

![One in three is gone within five years, mostly sold](figures/fig3_exits.png)

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
python check.py      # 262 statistics and 10 tables checked, 0 differ; figures in outputs/figures/
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
data/reviews/       hand reviews of every founder code and every sexual-conduct and relationship code
results/            the published statistics (combined_results.json) and figure series
figures/            the paper's figures
paper/              the paper as built from paper/template.md, and the decision log (DECISIONS.md)
```

Every statistic carries its horizon (how long after the announcement it is measured) and its N, and the build
stops if one does not (`code/combine_results.py`).

## Licences and citation

Code: MIT ([LICENSE](LICENSE)). Our data (event-level results, codes, hand reviews, link tables): CC BY 4.0
([LICENSE-DATA](LICENSE-DATA)). The CEO dismissal database is CC BY 4.0: cite Gentry, Harrison, Quigley and Boivie
(2021, *Strategic Management Journal*) and Zenodo record 17725939. SEC data are public domain. Wikidata is CC0.

Cite this package with [CITATION.cff](CITATION.cff).
