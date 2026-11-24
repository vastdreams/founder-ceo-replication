# Hired-CEO audit: the asymmetry guard of D-37 (item 5)

Only founder departures were checked by hand (D-35, batches A to E). To see whether hired-CEO firings carry the same
errors, 60 hired-CEO firings were drawn at random and checked with the same rules: was it a push, does day 0 match the
first public report (within 3 days), is the reason right, and a verdict.

**Sample.** Hired-CEO firings in the H1 comparison group (forced = 1, not fraud, not a founder by the hand-checked
founder code, with a primary competitor), 1,131 events in `analysis/out/founder_value.parquet`. Sorted by event_id,
60 drawn without replacement with `numpy.random.default_rng(20261123)`. The list and seed were written to
`hired_audit_list.csv` before any case was read.

**Sources.** The pipeline's cached 8-Ks (`~/world_raw/news/evidence.jsonl` on the server), the database's own notes and
source list, and the model's coded evidence quote. No new web pages were fetched; where only the database note supports
a fact, the CSV says so. Anything not confirmed is marked unverified. One coder (Claude), 23 Nov 2026.

## Verdicts

| Verdict | Hired, n = 60 | % (95% interval) | Founders in H1, n = 77 | % (95% interval) | Fisher p |
|---|---|---|---|---|---|
| Not a firing (planned succession) | 5 | 8.3 (3.6 to 18.1) | 12 | 15.6 (9.1 to 25.3) | 0.30 |
| Redate (day 0 off by more than 3 days) | 5 | 8.3 (3.6 to 18.1) | 10 | 13.0 (7.2 to 22.3) | 0.42 |
| Recode reason | 1 | 1.7 (0.3 to 8.9) | 3 (AdaptHealth, AXT, Synchronoss) | 3.9 | not tested |
| Keep | 49 | 81.7 | | | |

Intervals are Wilson. The founder counts are the 77 H1 founders in `founder_cases.csv` (D-37).

**Was it a push?** 24 pushed, 31 unclear, 5 planned successions.

## Cases not kept

- **Not a firing (5):**
  - Coca-Cola, Daft (2004): retirement announced about ten months ahead; borderline, he left earlier than planned.
  - Coca-Cola, Kent (2016): "widely expected" handover to the COO; Kent stayed chairman.
  - ConAgra, Rodkin (2014): retirement announced eight months ahead.
  - Ascena, Rayden (2015): a subsidiary CEO retiring, not the listed firm's CEO.
  - Ulta, Kirby (2010): exit announced four months ahead with an insider successor; borderline.
- **Redate (5):**
  - A.M. Castle (day 0 is a later press date; the 8-Ks came 10 to 17 May 2012).
  - Pfizer (news 28 Jul 2006, day 0 3 Aug).
  - Network Equipment (news 19 Jul 2005, day 0 1 Jul).
  - CMGI (news 20 Feb 2002, day 0 1 Mar).
  - Compass Minerals (news 19 Nov 2018, day 0 17 Sep).
- **Recode reason (1):** Symmetry Medical (2011): left amid an accounting probe the SEC later called "pervasive" fraud;
  belongs with fraud.

**Second looks, not changed:**

- Nash Finch (2005): SEC insider-trading scrutiny.
- Visteon (2015): the conduct code rests on facts that came out two years later.
- AutoNation (2020): a leave of absence from April 2020.
- MedCath (2011): 8-K filing date not read.
- Unverified announcement dates: SGI, Plains Resources, Birmingham Steel and FormFactor.

## Do founder and hired error rates differ?

- **Not significantly.** Founders show about twice the hired rate of planned successions (15.6% against 8.3%) and of
  redates (13.0% against 8.3%), but neither gap is significant (p = 0.30 and 0.42) and the intervals overlap widely.
- **The checks are not identical.** The founder check used five coders and fetched new pages; this audit used one coder
  and cached sources only. It may find fewer errors per case.
- **What it means for the comparison.** Dropping planned successions only among founders would remove a known error
  from one side. Applied to the 1,131 hired firings, the hired rate implies about 94 planned successions (41 to 205)
  and a similar number of misdated events left in the comparison group.

**Recommendation for D-37:**

- Report H1 three ways: uncorrected codes; founders corrected only; and founders corrected with hired firings
  reweighted or trimmed by the audit's error rate.
- Or extend the same push-and-date check to every hired firing before the final run.
