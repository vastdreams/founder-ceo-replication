# Independent recomputation of the headline numbers

`recompute_headline.py` recomputes the Sacked paper's headline numbers without importing anything from `analysis/`.
It reads the event file only for identifiers and the hand-checked flags (forced, who, why, dated, competitor tickers)
and the case checks' exclusions (`paper/d37_corrections.csv`, `d38`, `d44`), and recomputes every return, delisting
and test from the raw tables with its own SQL: Sharadar SEP and corporate actions, FMP SPY prices and dividends, and
the Kenneth French daily market. Run it on the database host; it writes `headline_recomputed.json`, which
`tests/unit/test_founder_provenance.py` compares with `outputs/combined_results.json`.

| Number | Level | Agreement |
|---|---|---|
| Founder firms against the S&P 500, six weeks | A (raw prices) | exact, N = 73 |
| Against the closest competitor | A | within 0.4 points, N = 66 (one event, see below) |
| Against the three closest competitors | A | within 0.2 points, N = 46 |
| Against the industry average and the profitability match | B (event file's per-event gaps re-aggregated) | exact |
| $100 line, founder firm and three competitors, median | A | exact to the cent, N = 46 |
| Bankrupt within five years, dismissals and retirements | A (corporate actions) | within 0.3 points |
| Scandal and fraud announcement returns | A (own market-model fit) | within 0.1 points, N = 40 and 58 |

Level B: the event file holds no ticker list for the industry pool or the profitability match, so those two
aggregates are re-derived from the per-event gaps with plain pandas, which checks the aggregation and N, not the
returns.

The one difference: Provell (event 6022, 2001), whose competitor Real Goods stops trading inside the window. The pack
applies its delisting return (Section 3); this check holds the last price. Every other founder event agrees to
within 0.2 points.
