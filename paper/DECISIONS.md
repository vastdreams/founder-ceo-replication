# Method decisions

The choices behind every number in the paper, in the order they were made. Each one is applied in the code named.

1. **A pushed resignation is a firing.** A chief executive who resigns under board pressure counts as fired, as in the
   CEO dismissal database: database codes 3 (job performance) and 4 (legal violations or personal conduct) are
   firings, code 5 (voluntary retirement) is the comparison group (`code/build_events.py`).
2. **Founder means founder, checked by hand.** A chief executive is a founder if they founded or co-founded the firm or
   its direct predecessor; heirs and long-serving successors are not. Every founder code on a firing was checked by
   hand (`data/reviews/founder_review.csv`, `code/founder_final.py`).
3. **The sample starts in 1998**, the first year with daily prices that include later-delisted firms.
4. **Reasons come from an evidence-based coding pass.** A language model read the database notes, the firm's 8-K,
   cited press releases, Wikipedia and matched New York Times articles, and coded the main reason with a quoted
   source passage (`code/evidence_fetch.py`, `code/code_events.py`, `code/coding_final.py`). Every financial-misconduct,
   sexual-misconduct, relationship and other personal-conduct code was then checked by hand
   (`data/reviews/fraud_review.csv`, `conduct_review.csv`, `personal_conduct_review.csv`).
5. **The main sample leaves out fraud, legal violations and criminal charges.** Those firings are a different event,
   since the firm itself is in trouble with the law; they return only as a comparison group (`code/sample.py`).
6. **Announcement windows use only well-dated firings: dated by the database or by hand.** 8-K dates agree with the
   database within three days too rarely for a three-day window. Founder and personal-scandal firings without a
   database date were dated by hand from 8-K filings, press releases and New York Times reports, keeping a date only
   when a dated source states it; each date and its source is in `data/reviews/date_corrections.csv`. Results over
   months and years use every firing (`code/redate.py`).
7. **Windows longer than a few days use returns minus the market.** A firm that was falling before the event has a
   negative market-model alpha; carried forward, it would make ordinary returns afterwards look like a recovery
   (`code/paths.py`, `code/stats_returns.py`).
8. **Matched firms are chosen deterministically:** same Fama-French industry, market value within 30 percent, nearest
   return on assets, no chief executive change in the previous three years; the nearest firm in size when none is in
   the band (`code/ops_matched.py`).
9. **Survival is reported within size bands and with controls** (prior 12-month return, leverage, book-to-market, an
   Altman Z distress flag and a loss flag), and firings with a bankruptcy within 180 days of the announcement are
   reported apart, as already failing (`code/controls.py`, `code/delist_dates.py`, `code/stats_ops.py`).
10. **Calendar-time alpha** uses portfolios of firms in months 1 to 12 and 1 to 36 after the announcement, regressed on
    the five Fama-French factors and momentum with Newey-West t (`code/calendar_alpha.py`).
11. **Every number carries its horizon and N.** `code/combine_results.py` stops if any statistic lacks either, and the
    paper's text is filled from the results file, so no number is typed by hand (`code/draft_paper.py`).
12. **A second coder** will check a random fifth of the hand-coded founder flags and reasons before journal
    submission; the paper says so.
13. **Tests read as nulls carry a 95% interval** (founder and personal-scandal gaps at the announcement and in
    delisting, and the 36-month alpha), computed from each estimate and its test statistic in
    `code/combine_results.py`; small groups in the event-time figure are drawn as medians (`code/figures.py`).
