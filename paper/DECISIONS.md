# Decisions

## D-01 (19 Nov 2026): a pushed resignation counts as a board removal

The operator ruled that a CEO who resigns under board pressure is treated as removed by the board,
the same as an outright firing. This holds for every period, not only for Nvidia.

Nvidia 2026 is the reference case: the board opened an investigation into Jensen Huang on
8 Nov 2026 and accepted his resignation on 11 Nov (8-K filed 12 Nov). Under D-01 it is a removal.

How the rule is applied to history is in RESEARCH_PLAN.md, "What counts as a removal".
Each event keeps its evidence (filing, press source, date) so a reader can re-code it.

## D-02 (19 Nov 2026): every removal gets a researched reason, led by relationships with employees

First list every removal in the 30 years under D-01. Then search each one for why it happened and
code the reason from filings and press, with sources. The first focus is a CEO's sexual or romantic
relationship with an employee. The paper then widens to other personal conduct, then to every
other reason.

Nvidia 2026: reports of affairs and an admitted infidelity are on record. Whether either involved
an employee is not established; code it from sources, do not assume it.

## D-03 (20 Nov 2026): founder means founder, checked by hand

A CEO is a founder if they founded or co-founded the firm or its direct predecessor (for example,
Columbia Hospital Corp. for HCA, or LDDS for WorldCom). Heirs of founders are not founders. Long-serving
CEOs who joined after the founding are not founders.

All 166 forced exits the model coded as founders, plus four notes-based candidates, were reviewed by hand.
The 170 decisions are in `founder_review.csv`: 135 founders were confirmed, and 33 model codes were rejected
(a 20% error rate). A case that could not be confirmed independently is coded as not a founder.
Retirements keep the model code, because they serve only as a comparison group.

Effect: before the review, founder removals averaged -4.4% (difference from non-founders p = 0.016).
After the review they average -3.5%, and the difference is no longer significant (p = 0.14). The paper
reports the reviewed result.

## D-04 (20 Nov 2026): main sample starts in 1998

Daily prices that include delisted firms start in 1998 (Sharadar), so the main tests cover 1998-2023.
Earlier events go into a robustness check built from 10-K price ranges and proxy return graphs.

## D-05 (20 Nov 2026): generated results stay out of git

`outputs/*.json` are rebuilt from the committed code on every run. They reach MedTwin through the API
and the public replication repo. The repo's secret scanner flags their `source_key` fields as keys.

## D-06 (20 Nov 2026): wording follows the p-value

Sentences that call a result significant use the `|sig` placeholder, so the text cannot claim
significance the statistics do not show.

## D-07 (20 Nov 2026): reasons come from a second, evidence-based coding pass

Each forced exit is coded a second time from the dataset notes plus the 8-K filed within 10 days
of the announcement, press releases the dataset cites, the CEO's Wikipedia article and matched NYT
Archive articles (1991-2026). These second-pass labels replace the first pass (notes only) for
every forced exit. Retirements keep the first pass. The two passes agree on 89% of primary reasons.
The second pass found no relationship or sexual-misconduct case that the hand review in
`conduct_review.csv` had not already checked. It flagged 25 founders the founder review had not
covered. Each was checked by hand and added to `founder_review.csv` (15 yes, 10 no). Hand
decisions still override model labels.

## D-08 (20 Nov 2026): target the Journal of Corporate Finance

The founder gap is not statistically significant, and the strongest results (conduct, delisting) are
descriptive event-study evidence without a causal design. That fits the Journal of Corporate Finance
better than the Journal of Financial Economics. The Review of Corporate Finance Studies is the
fallback. Both follow Elsevier house style, so the rule set keeps its key `founder_ceo_jfe`. The title
names scandal rather than sex, because the relationship result rests on 13 cases and is not significant.

## D-09 (20 Nov 2026): a strict sample where the evidence agrees the exit was forced

The CEO dismissal database codes some planned successions as forced, sometimes after later events
(Enron 2001, Viasat 2020). Every main result is also reported on the exits that the evidence-based
coding reads as forced too (Table IA.1), and the named founder cases (Table 6) come only from that
strict sample. The full sample stays the main sample, because the database's coding is the field's
standard and our coding reads many exits as "unclear" rather than "not forced".

## D-10 (20 Nov 2026): market-adjusted returns for every window longer than a few days

The market model's intercept, estimated over days -250 to -30, is strongly negative for firms about to
fire their CEO. Projected over days +2 to +60 it manufactured a +5% "rebound" that the market-adjusted
and buy-and-hold paths do not show. Windows before and after the announcement use returns minus the
market; the three-day announcement return keeps the market model (its market-adjusted version is in
Table IA.1).

## D-11 (20 Nov 2026): every number carries its horizon and N, enforced in code

combine_results.py gives each statistic a horizon (`period`) and a population from its key and stops
the build if any statistic lacks N or a horizon, or any table lacks an N column. Table 1 maps the whole
paper horizon by horizon with the number of forced exits measured at each.

## D-12 (20 Nov 2026): title names sex and fraud

The sex-or-relationship versus financial-misconduct comparison is now a tested result (Table 4, the
difference in means p = 0.04 on 17 against 89 cases; medians p = 0.10). The title names both because
the paper studies both; the text calls the comparison suggestive because the sex group is small.
