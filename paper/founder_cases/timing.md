# When the news trades: the announcement day against the long horizon (D-46)

Analysis only; the paper text is unchanged. Code: `analysis/founder_timing.py` (steps `extract` on the database host,
`release`, `minute`, `analyse`). Statistics: `outputs/founder_timing_stats.json` (keys `tm.*`). Returns are the firm
minus the S&P 500 (SPY with dividends) unless marked; "founders" are founder dismissals other than fraud (the paper's
main founder sample, well-dated); "all firings" are every well-dated dismissal other than fraud.

## Coverage

| | Founders | All firings |
|---|---|---|
| Well-dated firings with prices | 57 | 535 |
| Release before the open (8-K accepted before 09:30 New York, or the evening before) | 13 | 127 |
| Release during trading hours | 5 | 32 |
| Release after the close (first trades at the next open) | 17 | 147 |
| Release time unknown (the first 8-K came days after the announcement; 18% of these are before 2004) | 22 | 229 |
| Minute bars that match the day's prices (Alpha Vantage, checked against Sharadar's open-to-close) | 15 | 171 |

EDGAR's `acceptanceDateTime` is UTC (filings cluster at 6-8 am and 4-6 pm New York once converted). An 8-K's acceptance
is the latest time the news could have been public: press releases often come earlier the same day (Intel 2018 and
McDonald's 2019 are "during hours" by their 8-K although the news broke before the open). The "during" class is
therefore unreliable and small; the before-open and after-close classes are not affected in the same way.

## Where the reaction happens (mean, p skewness-adjusted; Holm across windows within each group)

| Window | Founders | All firings |
|---|---|---|
| Run-up, days -30 to -2 | -7.7% (p 0.001, Holm 0.010) | -5.4% (p 0.002, Holm 0.011) |
| First tradeable day: overnight gap | -0.8% (p 0.43) | -1.0% (p <0.001) |
| First tradeable day: open to close | -3.3% (p 0.007, Holm 0.065) | -0.9% (p 0.002) |
| First tradeable day, total | -3.6% (p 0.011, Holm 0.085); median -0.1% | -2.0% (p <0.001); median -0.5% |
| Next day | -0.5% (p 0.46) | -1.0% (p <0.001, Holm 0.003) |
| Days +2 to +5 | -2.8% (p 0.004, Holm 0.039) | -0.5% (p 0.37) |
| Days +6 to +20 | -1.5% (p 0.36) | -1.4% (p 0.015, Holm 0.058) |
| Days +21 to +60 | +3.4% (p 0.53) | -1.1% (p 0.44); median -1.1% (p 0.011) |
| 6 months | +4.3% (p 0.62); median -5.4% | -2.8% (p 0.30); median -5.5% (p <0.001) |

Against the industry (close-to-close) the pattern is the same: run-up -6.8% (founders) and -5.1% (all firings), first
tradeable day -2.3% and -1.7%.

- **All firings: the market reacts at the opening price.** When the news comes out before the open or after the
  previous close, the overnight gap is -1.8% and -2.0% (both p <0.001); the rest of that trading day adds -0.7% to -0.8%
  (not significant). Minute bars agree: from the first trade after release to the close the firm moves -0.3% against
  SPY (p 0.30, 171 firings), and half of that move is in place within 30 minutes.
- **Founders: a few large falls during the first trading day, a median of almost nothing.** The -3.6% mean on the first
  tradeable day has a median of -0.1%. The -2.8% over days +2 to +5 comes almost entirely from firings whose release time
  is unknown (-4.5%, p 0.002, 22 firings); for founders with a known before-open or after-close release it is not
  significant. The most likely reading is that, for those firings, the news reached the market after the recorded day,
  not that prices drift after it.
- **After the news, the typical firing firm keeps lagging, slowly.** The median all-firings firm trails the S&P 500 by
  1.1% over days +21 to +60 and 5.5% over six months.

## Is anything tradeable once the news is public? (short the firm, long SPY)

Tradeable rows use only firings whose release time is known: entry at the open of the first tradeable day for
before-open and after-close releases; at its close for every known release.

| Rule | Founders | All firings |
|---|---|---|
| Short at the open, hold 5 days | +5.4% (p 0.014, Holm 0.11; 30 trades; 63% win); +4.9% net of 50 bp | +1.2% (p 0.17); median +1.1% (p 0.027) |
| Short at the open, hold 20 days | +4.3% (p 0.17) | +2.2% (p 0.041, Holm 0.32) |
| Short at the open, hold 60 days | +4.1% (p 0.62) | +3.3% (p 0.074); median +3.3% (p 0.002) |
| Short at the close, hold 5 days | +2.9% (p 0.029, Holm 0.21; 35 trades) | +0.5% (p 0.49) |
| Short at the close, hold 126 days | -12.5% (p 0.37) | +0.3% (p 0.98); median +4.7% (p 0.005) |

Calendar-time portfolios of firms held after the close of the first tradeable day (all firings, every release class):
-34 bp a day over the first 5 days (five factors plus momentum, p 0.010, about 1 firm at a time), -11 bp a day over 20
days (p 0.034, about 2 firms), and -5.7 bp a day over 126 days (p 0.019, about 10 firms; about -7% over six months). For
founders, -64 bp a day over 5 days (p 0.050) on about one firm at a time, and nothing after 20 days.

**Reading.** No founder rule survives the Holm correction. The founder short-at-the-open rule (+5.4% in five days) rests
on 30 trades and its minimum detectable effect is 8.6 points, so a real effect of that size cannot be confirmed or ruled
out. For all firings the information is in the opening price; what remains is a slow drift (a median six-month lag of
5.5%, a significant calendar-time alpha of about -7% over six months) that is concentrated in small firms and is earned
before borrowing costs and short-sale constraints, which are not modelled.

## Minimum detectable effects (80% power, 5% two-sided), founders

First tradeable day 5.3 points; days +2 to +5 3.7; days +6 to +20 5.0; six months 35 points; the 5-day open short 8.6;
the 5-day calendar-time alpha 92 bp a day.

## Fragile

- Release times come from 8-K acceptance, an upper bound on when the news was public; about 40% of firings have no 8-K close enough to time them.
- Founder windows rest on 57 firings (35 with a known release time, 15 with matching minute bars) and on a few large
  moves; means and medians often disagree.
- The open-entry rules assume the opening print is tradeable at the quoted price; no spread, borrow fee or short-sale
  ban is modelled beyond the flat 20 and 50 bp round trips.
- Minute bars exist only for tickers Alpha Vantage still serves; 4 of 190 series were dropped because their session did
  not match the firm's daily bar.
- Inputs are in the analysis scratch folder (events, 8-K acceptance list, release classes, minute paths); the database
  extract is reproducible with `founder_timing.py extract`.
