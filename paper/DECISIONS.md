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

## D-13 (20 Nov 2026): matched firms chosen deterministically

The annual statements sometimes hold an original filing and an amendment for the same firm-year, and the control
choice kept whichever came last in database order, so a rerun could pick a different matched firm for 67 of 3,572
events. ops_matched.py now keeps, per firm and calendar year, the last fiscal year-end as first filed (earliest
datekey), and breaks ties in the control choice by ticker. Two runs now give identical files. The change moved two
results across the 5% line: the 60-month matched return (now -8.2%, p = 0.044) and the year-1 profit dip (now
-0.5 pp, p = 0.063); the text follows the p-values (D-06).

## D-14 (20 Nov 2026): every raw input behind one data layer, with adapters

analysis/datasource.py serves nine canonical tables (DATA.md in the public package) from the authors' database or
from files, and analysis/adapters/ writes them from Sharadar, CRSP/Compustat, Ken French, EDGAR and Zenodo. Rebuilding
from Sharadar CSV exports through the adapter reproduced the event-level files exactly. The public package is
<https://github.com/vastdreams/founder-ceo-replication> (mirrored on GitLab).

## D-15 (20 Nov 2026): referee round: dating, horizons, delisting and matching

An independent referee read scored the draft 54/100. Changes:

- Announcement dates: two thirds of departures had only the day the CEO left office. analysis/redate.py dates them
  from the firm's 8-K (strict text rule, 90-day window), validated against the database's own dates (58% within 3
  days, 73% within 10). Announcement-window results use departures dated by the database, a hand check or an 8-K;
  long-run results use every departure. Undated firings earn a smaller, insignificant return (Table IA.1).
- Long-run horizons count only if complete for every firm, delisted or not (no conditioning on delisting).
- Delisting proceeds are reinvested in the market; three-year results under other delisting returns in Table IA.1.
- Matched firms are screened only on past CEO turnover (no look-ahead).
- Means reported beside medians; Holm-adjusted p for the reason table; founder gap in every window with the minimum
  detectable effect (Table IA.3); delisting with controls and against matched firms (Table IA.4).
- Results that changed: H3 (conduct vs performance) no longer holds; the 60-month matched return is not significant;
  the excess delisting comes more from bankruptcy than from takeovers.

## D-16 (20 Nov 2026): every financial-misconduct code checked by hand

paper/fraud_review.csv reviews all 121 financial-misconduct codes; about a third changed, mostly because the
misconduct surfaced after the CEO left. paper/exclusions.csv drops one record that was not a CEO exit and one
duplicate; paper/date_corrections.csv fixes dates with a dated source. The Guess label in conduct_review.csv was
corrected (the 2018 allegations ended a chair role, not the 2015 CEO exit).

## D-17 (20 Nov 2026): announcement windows use hand-coded dates only; earlier figures superseded

Firings dated by the database earn -2.7% over three days, firings dated by an 8-K only -0.6% (p = 0.26): the 8-K
dates are too noisy for a three-day window. Announcement-window results therefore use the 527 firings dated by the
database or a hand check (stats_returns.PRECISE); every firing enters the long-run results and the all-dates
robustness rows. Because only 7 sex or relationship firings have hand-coded dates, the sex-versus-fraud comparison
is run on every firing (+0.7% vs -6.1%, p = 0.006) with the hand-dated version as a check. Two relationship codes
whose counterparty was not an employee (Enesco, Stryker) are now relationship_other, still in the sex group.

Superseded numbers: D-03's founder gap (-3.5%, p = 0.14), D-12's 17 against 89 cases (p = 0.04) and D-13's 60-month
matched return (-8.2%, p = 0.044) and year-1 ROA dip (p = 0.063) belong to earlier samples and methods. The current
values are in outputs/combined_results.json and the paper.

## D-18 (20 Nov 2026): the question is firings without a crime; fraud and crime become a comparison

Operator: the paper is about boards firing their CEO, above all a founder, over a personal scandal, a power or
strategy fight or the business, not over a crime. Firings whose final reason (after the hand reviews) is financial
misconduct or a legal or regulatory violation (117 with returns, 20 of them founders) leave every main result
through analysis/sample.py, which every script applies. They return only in Section 6, as a comparison.
`conduct` now means a firing over a personal scandal (sexual misconduct, a relationship, other personal conduct;
51 firings, 19 hand-dated); `performance` is every other non-criminal reason. Only 3 founders were fired over a
personal scandal (Papa John's, Wynn Resorts, WWE), so they are reported as cases, not tested.

Structure: the main text keeps Table 1, three figures and Tables 2 to 4; firm characteristics, reasons, the largest
founders, long-run returns, profits and the board move to the Internet Appendix (Tables IA.5 to IA.10, Figures
IA.1 to IA.3), so the conclusion is not preceded by pages of exhibits. Title: "Sacked: Founders, Sex Scandals, and
the Fate of Firms That Fire Their CEO".

## D-19 (20 Nov 2026): every personal-conduct code checked; survival by size; calendar-time alpha; prose

paper/personal_conduct_review.csv checks the 48 firings the model coded as other personal conduct: 25 are
personal scandals; 3 criminal charges (personal_crime) and 5 money or securities matters leave the sample; 15 pay
disputes, an activist fight and unexplained personal reasons move to other reasons. A personal scandal now costs
about what any other firing costs (-1.1% on all dates), still much less than fraud (p = 0.021).

Operator: the bankruptcy numbers looked too high and the firms too small. A quarter of firing firms were worth under
$300 million at the fiscal year-end before (10% of retirement firms), and that band holds most bankruptcies. Survival
is now reported within size bands (Table 4), and firings with a bankruptcy recorded within 180 days of the
announcement (36, e.g. Sears, Dana) are set aside as already failing (analysis/delist_dates.py). The gap holds in
every band.

Operator: "look at alpha". analysis/calendar_alpha.py forms calendar-time portfolios of firms in months 1 to 12 and
1 to 36 after the announcement and regresses them on the five Fama-French factors and momentum (Newey-West t). The
36-month alpha is 0.04% a month equal-weighted (t = 0.18), -0.06% value-weighted: no abnormal return once risk is
priced (Table IA.11).

Prose rewritten after the cost-of-living paper: no question-and-answer or limits boxes, measures defined in the
sentence that reports them, no closing slogans, limits in the conclusion's prose.

## D-20 (20 Nov 2026): title, the NYT table, a second coder (operator: "go with your calls")

Title for SSRN: "Sacked: Share Prices and Survival After Boards Fire Their CEO". Sex and founders are no longer
headline claims: the founder gap is not significant (-2.8 points, p = 0.32; +0.6 with size and prior-return controls)
and there are 40 personal-scandal and 3 founder-scandal firings. The coordinator suggested "Misconduct Firings" from an
older version in which code-4 conduct mixed crimes with personal conduct; since D-18 crimes are outside the main
sample, so that title would mislabel the paper. For JCF: "Firing the Chief Executive: Announcement Returns, Long-Run
Performance and Survival". The NYT kept-CEO table stays in the appendix as descriptive (Table IA.12). A second coder
checks a random fifth of the hand-coded reasons and founder flags before JCF, not before SSRN; the pack and the kappa
script are in ~/Desktop/founder-ceo-final/second_coder/, and the data section says the check is planned.

## D-21 (20 Nov 2026): the operator kept the title; D-20's retitle is withdrawn

The coordinator's advice to drop "Sex" and "Founders" was its own, not the operator's. The operator kept "Sacked: Sex,
Fraud, Founders, and the Fate of Firms That Fire Their CEO" for SSRN and, until further notice, for JCF. The text, not
the title, carries the results: personal-scandal firings are no different from other firings (-1.1%), the founder gap
is not significant (-5.0% against -2.2%, p = 0.32; +0.6 points with size and prior-return controls, p = 0.69), and
firings over fraud or another legal violation are the comparison (-4.8%, p = 0.021 against personal scandals). The
NYT table and second-coder parts of D-20 stand.

## D-22 (21 Nov 2026): SSRN gates and the two-column layout

- **Abstract opener restored.** The operator asked on 20 Nov for the abstract to open "This paper answers what happens
  when a board fires ..." (AB-01); the D-18 rewrite had dropped it. The abstract now opens that way and states the
  founder result with its p-value. The cover's key numbers (`::: keynumbers`) sit in the Abstract; MedTwin's abstract
  word count now skips them, since no journal edition prints them.
- **Main tests in the main tables.** Every number in the abstract and conclusion must be printed in a body table.
  Table 2 gains Panel B (founder minus hired CEO; personal scandal minus other firings; personal scandal minus fraud),
  Table 4 gains Panel B (firings minus retirements, raw and with both sets of controls).
- **Exhibits.** The old Table 2 (before, at and after, by group) repeated Table 1 for the main groups and crowded
  Sections 4 and 5 in the two-column edition; it moves to the Internet Appendix. Main tables are now 1 to 4 (the
  survival tables are Table 3 by size and Table 4 by group). Internet Appendix exhibits are renumbered in the order the
  text first names them, and each follows the paragraph that discusses it.
- **Corrections found in the audit.** The robustness row "fraud minus sex or relationship" had its sign reversed
  (+6.9 points is sex or relationship minus fraud); the appendix said no reason survives the Holm correction, but two
  do (pushed out described as retirement, Holm p 0.002; left for a new job, 0.012). Both fixed.

## D-23 (21 Nov 2026): review round 1, the claims, the dating and the terms

- **Hand-dating the founder and personal-scandal firings (review item 8).** The 54 founder and 25 personal-scandal
  firings without a database date (77 events; two were both) were dated by hand. For each, the firm's 8-K filings
  around the departure, its press releases, the database's cited sources and New York Times Archive reports were read,
  and a date was kept only when a dated source states the announcement (a press release date, a filing that names the
  announcement day, or a dated news report of the news). 45 were dated this way and are in
  `paper/date_corrections.csv` with the source for each; 32 had no dated source and stay out of the announcement tests.
  Well-dated founder firings rise from 29 to 52 and personal-scandal firings from 15 to 39. One coder; the second
  coder's check (planned before JCF, D-20) will cover these dates too.
- **One sample for the announcement.** Every announcement comparison in the text and in Table 2 uses well-dated firings
  (dated by the database or by hand). The all-dates numbers appear only in Table IA.4, labelled as such. The standfirst
  uses the well-dated fraud fall (6.9%), not the all-dates one (4.8%).
- **Nulls with intervals.** Each test the paper reads as a null carries its 95% interval or the smallest detectable
  gap: founder and personal-scandal announcement gaps, founder and personal-scandal delisting gaps, and the 36-month
  alpha. Intervals come from each estimate and its t (or the z implied by its p), registered as `.ci_low`/`.ci_high`.
- **Figures.** Figure 1(b) plots medians: one founder firm (Jazz Pharmaceuticals, +210% on day +47) moved the mean of a
  52-firm group. Figure 3's founder line (−64% against the market at 60 months) is explained in the text against the
  matched-firm median. Table IA.12 adds fiscal year 0, where the return-on-assets fall (2.0 points) sits.
- **Founder windows.** Table IA.3 drops the market-model window of trading days −30 to +30, which the paper itself
  rejects for long windows; the founder slide before the announcement is reported on returns minus the market.
- **Terms.** One word each: firing (not forced exit or dismissal, except the database's own name), personal scandal,
  fraud or other legal violation, delisted (split into taken over and bankrupt), CEO (defined at first use), well-dated.
- **Second coder.** Not simulated. It needs a human coder and stays planned before JCF; the data section says so.
- **Literature (review R1; MedTwin literature-depth gate G1).** Sixteen more works are cited, each held in full text in
  the project library and read for the sentence it supports: forced turnover (huson2004, gao2012, eisfeldt2013,
  clayton2005, cziraki2022, barber1996), founders (jenter2023, aran2025, bebchuk2017, gompers2010, kowalewski2019) and
  misconduct (hazarika2012, bereskin2020, mooibroek2021, abeysekera2024, baharad2026). Related work now closes by
  positioning the paper against them. Papers a referee names that are not held in full text (Parrino 1997; Huson,
  Parrino and Starks 2001; Warner, Watts and Wruck 1988; Denis and Denis 1995; Anderson and Reeb 2003; Villalonga and
  Amit 2006) are not cited until obtained and read.

## D-24. Platform review r3 (22 Nov 2026): referee checks, a discussion section, a reader-first rewrite

- **Referee checks, each run as a test** (analysis/referee_checks.py, outputs/referee_stats.json): equivalence tests
  and minimum detectable gaps for the scandal and founder contrasts, with the margin fixed before looking at the
  answer as the average firing's own three-day fall; the evidence-forced and evidence-unclear firings at the
  announcement and in delisting with every control; who gets a precise date (new Table IA.5) and an inverse-probability
  reweighted announcement return; Cox hazards with every month of follow-up; fraud firings put back with an indicator;
  founder against hired CEO on the board, with tests; how often the hand check changed each model code (Table IA.1 B).
- **Abstract: "no larger fall" after a personal scandal.** Backed by the one-sided test in Table 2, Panel B (a scandal
  fall larger by the average firing's fall is rejected, p < 0.001) and the 95% interval; it replaces "not significantly
  different". The founder contrast stays a non-answer: the equivalence test cannot exclude a gap of that size.
- **Section 7 is now "Discussion"** (the platform audit: the paper restated results without synthesis). The fraud
  comparison it held moved into Sections 4, 5 and the discussion. The rule set binds the section by its number.
- **Introduction** opens with the question and the contribution (rule set instruction), keeps Nvidia and Apple as the
  illustration, states the answer in words and leaves the numbers to the findings box.
- **Cover page off** (export_settings cover_page false): the introduction starts on page 1 under the findings, as the
  page reader asked twice (a quarter of page 1 blank).
- **Internet Appendix renumbered:** the new Table IA.5 shifts the old IA.5 to IA.13 by one.
- **Not done, with reasons in the review's reply ledger:** the title (operator's), the second coder (needs a person),
  first-report dating of every fraud and a media search beyond the New York Times (no licensed archive), BoardEx roles.

## D-25. Platform review round 2 (22 Nov 2026): claims cut back to the tests, one statement of the results

- **Personal scandals.** "No larger fall" is withdrawn: the two-sided equivalence test does not reach 5%, so the
  abstract, introduction, Section 4 and conclusion say the scandal firings are too few for a precise estimate and do
  not differ significantly from other firings. Founders get the same plain statement.
- **The headline sample is named.** The abstract says "where the date is precise"; Table 2 Panel C adds every firing at
  any date and the not-forced group, so the evidence-based coding's three groups add to the table's firings.
- **The cover.** Key-number cells, the cover chart and the findings box are removed (the platform review counted the
  same numbers three times on page 1). The operator's standfirst stays, rewritten to the cut-back claims.
- **Related work** is three strands, each ending in the prediction the paper tests.
- **Title:** the author's decision (operator, 20 Nov 2026); the review's title comment is waived with that reason.

## D-26. Platform review round 3 (22 Nov 2026): reader clarity, the dating check, no out-of-sample hook

- **Hook.** Every reader run read the Nvidia opening (November 2026, after the sample ends) as outside the evidence or
  as invented. The introduction now opens its illustration with three in-sample firings that match the title (Nortel
  2004, fraud; Wynn Resorts 2018, a founder and sexual-misconduct allegations; McDonald's 2019, a relationship). The
  Nvidia statistics stay in the payload; the operator can restore the paragraph.
- **Dating.** Every firing over trading days -5 to +5 falls 2.0% (p < 0.001), close to the well-dated firings' 2.6%:
  a late day 0 moves the news outside a three-day window but not outside a wider one (Table IA.4).
- **Equivalence margin** justified in the text: the average firing's fall is the effect the paper studies.
- **Discussion** gains a practical reading of the null results; the conclusion keeps numbers only where needed.
- **Table 1's** N column header no longer says "firings" (the alpha row counts months); Table 2's differences carry
  their sign in the label.

## D-27. Round 4 reader draft (22 Nov 2026)

- Section 6 opens with its answer: the market and the matched firm give opposite answers, and the matched firm is
  the right benchmark; the alpha follows as the second, risk-adjusted check.
- The founder-count details move from Section 3 to the Internet Appendix next to Table IA.1; Section 3 keeps the
  change rates in words.
- Table 4 headers spell out the horizon ("Delisted by 12 months", "Taken over by 60 months").

## D-28. Prose to the operator's abstract rules (23 Nov 2026)

The operator's rules from the cost-of-living paper (23 Nov) applied to the abstract, introduction, discussion,
conclusion and body. No statistic, sample or claim changed; only the order and wording of the telling.

- **Order.** The abstract and introduction now lead with failure (bankrupt within five years, against retirements),
  then why the share price reaction misses it (most of the fall comes in the six weeks before the news), then the
  benchmark (controls; matched firms), and the fraud, scandal and founder groups last. The abstract keeps the
  operator's opener "This paper answers what happens when ... board fires its CEO" and puts the headline after its
  colon (editorial call: the new rule says headline first; the opener was asked for on 20 Nov).
- **Where the data cut against the story,** the text says so: the extra failures do not come with lower returns than
  at matched firms; controls remove more than half of the delisting gap; scandal and founder firings cannot be told
  apart from other firings.
- **Wording.** No roadmap paragraph; no "N times" (the hazard ratio is defined in words); no "set against"; no
  one-line topic fragments; nulls stated as imprecision ("the data cannot pin the difference down"), not as "no
  difference". Standfirst rewritten in the same order.

## D-29. Founders and hired CEOs, by why the board acted (23 Nov 2026): definitions frozen before the cell results

Operator, 23 Nov 2026: "there are two groupings you need to do: non-founder, then founder CEO ... the critical one is
Founder we are focusing on, and demarking it on grouping of fraud i.e. direct company-level fraud vs event ... driven
by coups or scandals".

Written and committed before any cell of the new table was computed. No event is recoded; every group is built from
the final reason code (sample.final_reasons: the evidence-based coding after the three hand reviews) and the
hand-checked founder flag (founder_final.py, D-03). The code is analysis/founder_reason.py.

- **Who.** Founder: the hand-checked founder flag is yes. Hired CEO: every other fired CEO.
- **Why, three groups that partition every firing.**
  - *Fraud:* the paper's existing fraud or other legal violation group (sample.CRIMINAL: financial misconduct, a
    legal or regulatory breach, criminal charges against the CEO).
  - *Event:* a personal scandal (sample.PERSONAL: sexual misconduct, a relationship, other personal conduct) or a
    boardroom coup (the existing code "strategy or power dispute"). Scandal and coup are reported separately and
    combined. The coup code is the evidence-based coding's; unlike the fraud and scandal codes it was not checked by
    hand one by one (only where a hand review moved a firing into it), and the table note says so.
  - *Performance or other:* every remaining firing (performance, activist or shareholder pressure, merger or
    restructuring, a push described as retirement or health, a new job, pay or perks, unclear, uncoded).
- **The main sample still excludes fraud firings (D-18).** The new table shows the fraud columns as the comparison
  group, labelled as outside the main sample, and an "all but fraud" row that reproduces the paper's existing founder
  and hired-CEO numbers. No main-sample statistic changes.
- **Measures, each by the paper's existing method.** For every cell (founder or hired, by reason):
  - N: all firings with share prices, and well-dated firings (dated by the database or by hand, D-17);
  - the announcement return: market-model abnormal return over trading days -1 to +1, well-dated firings, mean with
    the cross-sectional t;
  - the slide before: return minus the market over trading days -30 to -2, well-dated firings with every day of the
    window;
  - delisted and bankrupt within 60 months: all firings followed for the full 60 months.
- **Tests.** Founder minus hired CEO within each reason: Welch t with its 95% interval for the two returns; for the
  two shares, the chi-square test the paper already uses, replaced by Fisher's exact test when any expected count is
  under 5, with the Newcombe (Wilson score) 95% interval for the difference of two shares. Also, within founders and
  within hired CEOs, fraud minus event by the same tests, and the difference between those two differences (a z test
  on the four cell means), since the operator's question is whether the fraud-versus-event split matters more for
  founders.
- **Small cells.** N is printed in every cell. A cell with fewer than 10 events on a measure gets no mean, share or
  test for that measure: the table prints N only and the text names the cases. A difference is tested only when both
  cells have at least 10 events. The threshold is the paper's existing one for reasons (min_reason_cases).
- **Many tests.** p-values are unadjusted. The three-way partition (fraud, event, performance or other) gives three
  founder-minus-hired tests per measure; a p under 0.05 is called significant in the text only if it also survives a
  Holm correction across those three, and is otherwise called suggestive. The paper states no difference that its
  test does not support, and a wide interval is reported as "the data cannot say", not as "no difference".
- **Text.** Founder columns come first in the table and the founder comparison leads its subsection in Sections 4
  and 5 and in the Discussion. The title is unchanged.

**Addendum to D-29, after the cell counts were seen (23 Nov 2026).** Two things follow from the counts alone, and one
test was added that D-29 did not list.

- *The founder cells the operator asked about are too small to test.* Of the 103 founders fired, 20 were fired over
  fraud (5 well-dated) and 9 over an event (3 scandals, 6 coups; 6 well-dated; 7 followed for 60 months). Under the
  frozen rule those cells get N and named cases, no mean and no test at the announcement; only the delisted and
  bankrupt shares of the 20 fraud founders can be compared with hired CEOs. The 15 fraud founders and 3 coup founders
  without a precise date were not hand-dated in D-23 (that pass covered the main sample). Dating them by hand is the
  one step that could bring the founder fraud cell to a testable size; it is not done here.
- *Added test, not pre-specified: the mix of reasons.* Whether founders and hired CEOs are fired for the same
  reasons is the first thing a two-way table shows, so the share of each group's firings that falls in fraud, event
  and performance or other is tested (chi-square on the two-by-three table, and each share's founder-minus-hired
  difference with its Newcombe interval). It was chosen after seeing the counts, and the table note says so.

**What D-29 changed in the paper (23 Nov 2026).** New body table, Table 3, "Founders and hired CEOs, by why the board
acted" (founder columns first; five panels: mix of reasons, announcement return, slide before, delisted, bankrupt).
The old Tables 3 and 4 become Tables 4 and 5. Section 4's founder subsection now comes before the scandal and fraud
subsection and takes the new table; Section 5 gains a founder subsection; the Discussion and Conclusion put the
founder material before the fraud-against-scandal paragraph. The abstract's second paragraph states the one founder
difference the data support (fraud is 19.4% of founder firings against 7.8% for hired CEOs) and that 9 founders were
fired over a scandal or coup. The introduction's fraud example is now Ebbers at WorldCom, a founder, in place of
Nortel (editorial call). No existing statistic changed; 227 statistics were added (outputs/founder_reason_stats.json).

## D-30. Founder fraud and coup firings dated by hand (23 Nov 2026): the dating finished before any return was read

The addendum to D-29 left the founder fraud and founder event cells untestable: 15 of the 20 founders fired over fraud
and 3 of the 6 founders fired in a boardroom coup had no precise announcement date (the 3 founder scandals were already
dated). On 23 Nov 2026 those 18 firings were dated by hand, by the rule used for founders and personal scandals in D-23.
This entry and `paper/date_corrections.csv` were written and committed before the event study was re-run. The
returns of these 18 firings had not been computed on their new dates, and no date was chosen or revised after a return
was seen. Every result that follows this entry was computed after the dating was complete.

- **Rule (unchanged from D-17 and D-23).** The date is the day the departure was first public, taken from a dated
  primary source, in this order: the firm's 8-K, the firm's press release, a New York Times or major wire report. The
  pipeline takes the first trading day on or after that date as day 0, so an announcement after the close falls inside
  the window of trading days -1 to +1. Where sources give two dates, the earliest verifiable one is used and the other
  is noted. No date is guessed; an event with no dated source would have stayed undated.
- **Leave before removal.** Three boards first put the CEO on leave and removed him later (Vitesse, HealthSouth,
  AdaptHealth). The date is the leave announcement: from that day the CEO was publicly out of the job, and it is the
  earlier of the two dates. This follows the existing entry for Lattice (event 5038, "acting CEO named") and the
  database's own left-office dates for Vitesse and HealthSouth. The later removal dates are listed below.
- **Sources read.** The 8-K texts held on the server (`~/world_raw/sec/8k_cache`, `~/world_raw/news/evidence.jsonl`),
  the New York Times Archive records matched to each event, filing lists from the SEC's public submissions endpoint,
  and, for filings not held, the EDGAR documents and press pages read one by one. The New York Times site refused the
  reader, so its reports are cited from the Archive record (date, headline, abstract), not from the full text.
- **Outcome.** All 18 were dated; none stays undated. One coder; the second coder's check (D-20) will cover them.
- **One return seen by accident.** A web search for the Iconix press release returned a wire summary that mentioned the
  share price move after the announcement. The Iconix date (6 August 2015) rests on the wire report's "Iconix said
  Thursday" and the 8-K's resignation date of 5 August, not on the price. No other return was seen.
- **Judgement calls a second coder should re-check.** (1) Presidential Life: Kurz's resignation was announced on 17
  April 2008, to take effect on 12 May 2009, as a planned succession; the 8-K of 14 May 2009 reports only his
  successor's appointment as CEO and does not name Kurz. The earliest verifiable date is used, 13 months before the
  handover. (2) The three leave dates above. (3) Iconix: the resignation is dated 5 August 2015 in the 8-K, the
  company's announcement Thursday 6 August, after the close.
- **Tests.** Nothing in D-29 changes: a cell under 10 well-dated firings gets N and named cases only; a founder-minus-
  hired difference is tested only when both cells reach 10; a p under 0.05 is called significant only if it survives
  the Holm correction across the three reasons, and is otherwise called suggestive.
- **Side effect.** The 3 coup founders are in the main sample, so the well-dated count and the founder announcement
  return move. Every statistic cited in the paper that changes is listed in CHANGES.md with its old and new value.

| Event | Firm, CEO | Date | Source | Support |
|---|---|---|---|---|
| 4824 | Presidential Life, Herbert Kurz | 2008-04-17 | 8-K filed 22 Apr 2008, <https://www.sec.gov/Archives/edgar/data/80124/000008012408000018/0000080124-08-000018.txt> | "On April 17, 2008, Herbert Kurz announced his resignation as President of Presidential Life Corporation ... effective May 12, 2009." Later: 8-K of 14 May 2009 (successor appointed 13 May 2009). |
| 5298 | Iconix Brand Group, Neil Cole | 2015-08-06 | Wire report (AP, 7 Aug 2015), <https://www.foxbusiness.com/markets/iconix-drops-as-founder-cole-steps-down-from-president-chairman-and-ceo-posts>; 8-K filed 11 Aug 2015, <https://www.sec.gov/Archives/edgar/data/857737/000119312515286548/0001193125-15-286548.txt> | AP, Friday 7 Aug: "Iconix said Thursday that Cole would serve as a special adviser". 8-K: Cole resigned on 5 August; interim CEO appointed 6 August. |
| 5502 | Swift Transportation, Jerry Moyes | 2005-10-27 | 8-K (report date 27 Oct 2005, press release of that day), <https://www.sec.gov/Archives/edgar/data/863557/000095015305002725/0000950153-05-002725.txt> | The company announced on 27 October 2005 that Moyes "had resigned as Chief Executive Officer and Chairman of the Board of the Company, effective immediately." |
| 5615 | Atmel, George Perlegos | 2006-08-07 | 8-K with press releases dated 7 Aug 2006, <https://www.sec.gov/Archives/edgar/data/872448/000095013406015049/0000950134-06-015049.txt>; NYT 8 Aug 2006 | "Atmel Corporation ... has announced that on August 5, 2006, the Board of Directors terminated four officers"; press releases "dated as of August 7, 2006". 5 August was a Saturday. |
| 5931 | Vitesse Semiconductor, Louis Tomasetta | 2006-04-18 | 8-K with press release dated 18 Apr 2006, <https://www.sec.gov/Archives/edgar/data/880446/000095010306001101/0000950103-06-001101.txt> | "Vitesse also announced today that Louis R. Tomasetta ... have been placed on administrative leave ... has appointed Chris Gardner as Acting President and Chief Executive Officer." Later: terminated 15 May 2006 (press release 17 May; NYT 18 May 2006). |
| 5993 | PolyMedica, Steven Lee | 2002-08-05 | Press release (Business Wire, Monday 5 Aug 2002, cited by the database: "PolyMedica CEO Retires, Will Remain as Chairman Through Year-end"); NYT 6 Aug 2002, <https://www.nytimes.com/2002/08/06/business/company-news-polymedica-s-co-founder-retires-as-chief-executive.html>; 10-Q, <https://www.sec.gov/Archives/edgar/data/878748/000095013502003770/0000950135-02-003770.txt> | 10-Q: on 4 August 2002 (a Sunday) Lee "informed the Board of Directors of his intention to retire as Chief Executive Officer, effective as of that date." No 8-K was filed. |
| 6659 | Mercury Interactive, Amnon Landan | 2005-11-02 | 8-K with press release dated 2 Nov 2005, <https://www.sec.gov/Archives/edgar/data/867058/000119312505213792/0001193125-05-213792.txt>; NYT 3 Nov 2005 | "Mercury Interactive Corporation ... announced today that Amnon Landan has resigned from his positions as the Company's Chief Executive Officer and Chairman". |
| 6940 | Amedisys, William Borne | 2014-02-24 | 8-K with press release dated 24 Feb 2014, <https://www.sec.gov/Archives/edgar/data/896262/000119312514065248/0001193125-14-065248.txt> | Press release, "Feb. 24, 2014": Amedisys "today announced that William (Bill) F. Borne ... has stepped down as CEO, Chairman and Director." The 8-K dates the departure 20 February; the announcement came on the 24th. |
| 7230 | RadiSys, Glenford Myers | 2002-05-03 | 8-K with press release dated 3 May 2002, <https://www.sec.gov/Archives/edgar/data/873044/000102589402000301/0001025894-02-000301.txt> | "RadiSys Corporation (Nasdaq: RSYS) announced today that Dr. Glen Myers has stepped down as President, CEO and Chairman of the Board". |
| 7327 | LCA-Vision, Stephen Joffe | 2006-02-03 | 8-K (report date 3 Feb 2006), <https://www.sec.gov/Archives/edgar/data/1003130/000095015206000779/0000950152-06-000779.txt> | "On February 3, 2006, LCA-Vision Inc. announced the appointment of Craig Joffe as interim Chief Executive Officer ... Stephen Joffe ... has announced that he will step down effective that date [1 March]." |
| 7344 | IMPATH, Anu Saad | 2003-02-10 | 8-K with press release of 10 Feb 2003, <https://www.sec.gov/Archives/edgar/data/1003114/000116923203000984/0001169232-03-000984.txt>; NYT 11 Feb 2003 | "On February 10, 2003, IMPATH Inc. ... announced that its Board of Directors had appointed Carter H. Eckert as Chairman and Chief Executive Officer, to replace Anu D. Saad, Ph.D., who resigned following a review of expenses". |
| 7394 | Sapient, Jerry Greenberg | 2006-10-17 | 8-K with press release dated 17 Oct 2006, <https://www.sec.gov/Archives/edgar/data/1008817/000115752306010150/0001157523-06-010150.txt>; NYT 18 Oct 2006 | Press release, "Oct. 17, 2006": Herrick "succeeds former co-chairman and chief executive officer Jerry A. Greenberg, who has resigned". The 8-K dates the resignation 16 October. |
| 7657 | Monster Worldwide, Andrew McKelvey | 2006-10-09 | 8-K with press release dated 9 Oct 2006, <https://www.sec.gov/Archives/edgar/data/1020416/000110465906065893/0001104659-06-065893.txt>; NYT 10 Oct 2006 | Press release, "October 9, 2006": Monster "today announced that founder Andrew J. McKelvey, 71, has resigned as Chairman and Chief Executive Officer." The 8-K dates the resignation Friday 6 October. |
| 8045 | AXT, Morris Young | 2004-05-24 | 8-K with press release dated 24 May 2004, <https://www.sec.gov/Archives/edgar/data/1051627/000089161804001030/0000891618-04-001030.txt> | Press release, "May 24, 2004", "AXT, Inc. Announces Executive Management Changes: Chen Becomes Chairman; Tatzin Becomes Interim CEO". The database's left-office date is 1 May 2004. |
| 8085 | Mannatech, Samuel Caster | 2007-08-21 | 8-K with press release dated 21 Aug 2007, <https://www.sec.gov/Archives/edgar/data/1056358/000119312507187200/0001193125-07-187200.txt> | "Mannatech, Inc. (NASDAQ - MTEX) announced today that Samuel L. Caster has resigned as Chief Executive Officer of the company, effective immediately." |
| 8543 | SFBC International (later PharmaNet), Arnold Hantman | 2006-01-03 | Press release (Business Wire, 3 Jan 2006), <https://www.biospace.com/sfbc-international-inc-appoints-b-jeffrey-p-mcmullen-b-as-chief-executive-officer>; 8-K filed 6 Jan 2006, <https://www.sec.gov/Archives/edgar/data/1089542/000111650206000058/0001116502-06-000058.txt> | Press release, Miami, 3 January 2006: McMullen appointed CEO in place of Hantman. 8-K: "Mr. Hantman resigned his positions as chief executive officer and a director of SFBC" (agreements of 30 December 2005). 3 January was the first trading day after the resignation. |
| 10360 | AdaptHealth, Luke McGee | 2021-04-13 | 8-K with the board's statement of 13 Apr 2021, <https://www.sec.gov/Archives/edgar/data/1725255/000110465921049573/0001104659-21-049573.txt> | The board "placed Mr. McGee on unpaid leave from his roles" as co-CEO and director after Danish authorities charged him. Later: resignation announced 14 June 2021 (8-K, effective 11 June). |
| 10421 | HealthSouth (later Encompass Health), Richard Scrushy | 2003-03-20 | 8-K with press release dated 20 Mar 2003, <https://www.sec.gov/Archives/edgar/data/785161/000100515003000617/0001005150-03-000617.txt> | HealthSouth "announced that its Board of Directors has placed Chairman and Chief Executive Officer Richard M. Scrushy on administrative leave ... Robert P. May as Acting Chief Executive Officer". Later: removal announced 31 March 2003, effective 19 March. |

**What D-30 changed in the results (23 Nov 2026, computed after the dating commit e015fbb3d).**

- *Founder fraud cell, now testable.* All 20 founders fired over fraud are well-dated (5 before). Their three-day fall
  is 7.4% (t = -2.41, p = 0.026; median 4.2%), against 6.7% for the 36 well-dated hired CEOs fired over fraud. Founder
  minus hired: -0.7 points, 95% interval -8.4 to 7.0, p = 0.86 (Holm 1.00). The six-week slide before: 5.8% against
  3.0%, gap -2.8 points, p = 0.56. Not significant, and the intervals are wide: the data cannot say.
- *Founder event cell, still not testable.* All 9 are well-dated (6 before), one short of the 10 the rule requires, so
  the cell keeps N and named cases, and founder fraud against founder event is not tested. The threshold is not moved.
- *HealthSouth.* Trading in its shares was halted from 19 to 25 March 2003, so the window on 20 March records -3.4% on
  stale prices; the shares lost about 97% when trading resumed on 26 March. The date was fixed before this was seen and
  is not changed; the text says the founder fraud average understates this case.
- *Main sample.* The 3 coup founders are in the main sample: well-dated firings 531 to 534, well-dated founders 52 to
  55, the founder fall 3.2% to 3.1% (gap to hired CEOs -1.0 to -0.9 points, p 0.627 to 0.645). The fraud comparison
  group gains 15 dated firings: its fall 6.9% to 7.0% (n 41 to 56), and personal scandal minus fraud 5.4 to 5.5 points
  (p 0.018 to 0.006, n 80 to 95). The full old-and-new list is in CHANGES.md.
- *Scripts.* `controls.py` is not in `run_all.sh`; it was run after it, and the statistics scripts were run again.

## D-31 Title names the founder CEO (23 Nov 2026)

Operator, 23 Nov 2026: "FIRE THEIR FOUNDER CEO founder ceo is a critical word here ... keeping ceo there is a key word".
Title changed from "Sacked: Sex, Fraud, Founders, and the Fate of Firms That Fire Their CEO" to "Sacked: Sex, Fraud, and the Fate of Firms That Fire Their Founder CEO". The sample and the text still cover every fired CEO, founder or not; the abstract
says so in its first sentence.

## D-32 Fraud out of the headline; Nvidia opening restored (23 Nov 2026)

Operator, 23 Nov 2026: "we eliminate the fraud part of the numbers ... that is the entire point as this is a hot proof
paper on board decision on Jensen". The main numbers already excluded fraud firings. The abstract, introduction,
discussion and conclusion no longer lead with the founder fraud results (reason mix, founder-vs-hired fraud fall); the
founder story is the non-fraud comparison. Fraud stays only as a comparison group (Table 3, Sections 4 and 5). The
Nvidia paragraph removed in D-26 is restored after the opening paragraph, as the operator's call.

## D-33 The scandal-against-fraud contrast leads the second paragraph (23 Nov 2026)

Operator, 23 Nov 2026: "take it to 8/10 on the delivery". The abstract, introduction and conclusion now state the one
significant reason contrast (personal scandal against fraud, Table 2) and name the founder scandal cases (Wynn Resorts,
World Wrestling Entertainment). Fraud stays outside the main sample and serves as the comparison. Section 4 no longer
calls the fraud reason mix the clearest founder result. Wording is Claude's editorial call.

## D-34 The main hypothesis is the founder CEO, measured in dollars against competitors (23 Nov 2026, fixed before any of these numbers is computed)

Operator, 23 Nov 2026: "the case of point has to be around founder CEOs the rest is support ... including other ceos
and including fraud reasons as findings ... quantifying only the bankruptcies is [not enough], it should quantify the
exact share $ loss vs competitors and to ensure it is not unfair or performance, as in ... the company is already
performing bad and it is biased". Also: write "S&P 1500", not the full name.

Design, frozen here:

- **Main hypothesis (H1).** When a board fires a founder CEO, shareholders lose more than when it fires a hired CEO,
  measured against competitors that were doing equally badly before. Two-sided test; a null is reported as a null.
- **Sample.** Main sample as before (every firing but fraud). Fraud firings and hired CEOs are supporting findings,
  each reported in full with the same measures.
- **Competitor benchmark (primary).** A matched firm in the same Fama-French industry, within 30% in market value,
  with no CEO change in the prior three years, nearest on the prior 12-month return (days -282 to -31). This is the
  answer to "already performing badly". Robustness: the existing match on return on assets, and the equal-weighted
  mean of all same-industry S&P 1500 firms.
- **Windows.** Slide (days -30 to -2), announcement (-1 to +1, well-dated firings only), slide plus announcement
  (-30 to +1), then buy-and-hold from day +2 for 12, 36 and 60 months, delisting returns as in Section 3.
- **Dollar loss.** Firm return minus the competitor's, times the firm's market value at day -31, in 2023 dollars
  (CPI-U). Reported as mean, median, and the total across firms; the percentage return is reported beside every
  dollar number. Means are winsorised at 1% and 99% as a robustness row, not the main row.
- **Tests.** Founder minus hired: Welch t on returns, Wilcoxon on medians, and a regression of the return and of the
  log dollar change on a founder flag with size, prior 12-month return, return on assets, leverage, industry and
  year. Holm across the six windows. Standard errors clustered by firm.
- **Disclosure.** Every cell is reported, significant or not; cells under 10 firings get names, not averages.

### D-34 addendum, added at the operator's request before any D-34 result was shown to him (23 Nov 2026)

Three additions to D-34. Nothing frozen in D-34 changes, and the matched competitor stays the primary benchmark: the
S&P 500 does not correct for how the firm was doing before, and a typical stock lags an index that a few large winners
lift.

- **S&P 500 benchmark.** For every window and group, the firm's return minus the S&P 500's total return, and the dollar
  change on that basis, beside the matched-competitor numbers. The series is the SPDR S&P 500 ETF (SPY) held on the research server (FMP daily
  closes and FMP dividends), with each dividend reinvested on its ex-dividend day; no index-level total-return series is
  held. It ends on 14 July 2026, so a window that runs past that day has no S&P 500 number, and its dividends end in
  December 2025, so 2026 returns miss two quarterly dividends (about 0.3% each).
- **An investment line for H1.** $100 in the firm at day -31, against $100 in the S&P 500 and $100 in the matched
  competitor, valued at day +1 and at 12, 36 and 60 months from day +2; founders and hired CEOs, medians and means, on
  the firings that have all three.
- **The prior decline, stated.** Returns of the firm, its competitor and the S&P 500 over trading days -282 to -31, for
  founders and hired CEOs, so the reader sees that the stock was already falling and how far the competitor fell.

Two further rows were added by the analyst while implementing D-34 and are labelled as addenda in the tables: the slide
and slide-plus-announcement windows on well-dated firings only (D-34 puts every firing in those two windows). One
implementation rule was fixed before any number was computed: where no competitor is inside the 30% size band, the band
is widened to a factor of two and the match is flagged; with none there either, the firing has no competitor. The "log
dollar change" of D-34 is the signed log, sign(x) times log(1 + |x|) with x in millions of dollars, since a loss has no
logarithm.

## D-35 Case studies of the 55 well-dated founder firings (23 Nov 2026, rules fixed before any per-firm return was read)

Operator, 23 Nov 2026: "more comprehensively map the 55 well-dated, actually pull them out, do a case study on each of
them and properly structure what, why, how, and classify by shareholder return ... and what happens to the director ...
like how many are brought back like Steve Jobs". The cases are in `paper/founder_cases/` (CASES.md, founder_cases.csv),
built by `analysis/founder_cases.py`. They describe; they test nothing.

**The 55.** Founder firings in the main sample (every firing but fraud) with a well-dated announcement and a three-day
return: `founder_reason.load()`, cell founder × main, `car_mm_m1p1` not missing. 46 performance or other, 6 coups,
3 personal scandals. The paper's codes are kept as they are; where a case's sources describe a planned succession
rather than a firing, the case says so and is flagged, but it is not removed (that would change Table 3 after the fact).

**Shareholder outcome (proposed thresholds, the analyst's call).** One class per firing, by the first rule that applies:

1. *Bankrupt* within 5 years (delist_kind_5y = bankruptcy).
2. *Taken over* within 5 years (delist_kind_5y = takeover), with the price paid if a source states it.
3. *Delisted, other* within 5 years.
4. Otherwise by the 3-year buy-and-hold return from day +2 minus the matched competitor (mbhar_3y: same Fama-French
   industry, size within 30%, nearest return on assets; the pack's long-run match):
   *shareholders gained* above +10 percentage points, *shareholders lost* below -10, *about even* in between.
5. *Not yet 3 years* where the horizon is not complete; the 1-year matched return is then reported, not classified.
Reported beside each, not used to classify: the 3-day announcement return (market model), the 3-year return minus the
S&P 500 total return (D-34 series), and the 3-year dollar change against the competitor and the S&P 500 (D-34 output,
2023 dollars). Rule 1-3 take precedence because a firm that leaves the market has no clean 3-year return.

**Founder fate within 5 years of the announcement.** Each recorded with a source; "not found" where sources are silent.

- Board: stayed on the board (as chair or director) / left the board at once / left the board later (year).
- *Boomerang*: came back as CEO of the same firm (year), the Jobs case. Coming back as executive chair is recorded
  separately, not counted as a boomerang.
- Next role: founded or led another public or notable company (name).
- Legal: charges, regulator action or a lawsuit naming the founder over conduct at the firm.
- Died within 5 years.

**What, why, how.** Trigger (what happened just before); reason the board gave, and the reason reported by press if it
differs; how it was done: outright firing, pushed resignation, leave then removal, coup (co-founders, investors,
activist), or described as a planned succession; successor: insider, outsider, co-founder, interim.

**Sources and limits.** Filings from the server's 8-K and proxy cache, the database's own notes and sources, Wikipedia
and press read one by one; cite only what was read; unverified facts are marked unverified. Cells under 10 get names,
not percentages.

## D-36 The paper is rebuilt around H1 of D-34 (23 Nov 2026)

- **Result.** H1 is not supported. Through the announcement a founder's firm loses 7.2% against its competitor and a
  hired CEO's firm 7.6%; the gap is 0.4 points (95% interval -6.2 to 7.0, p = 0.909, Holm p = 1.000). In dollars the
  founder's firing is the smaller loss because the firms are smaller; with size held constant the gap could be chance.
- **Order.** Abstract, introduction, Section 4, discussion and conclusion lead with the founder result in percent and
  dollars. Every firing, hired CEOs, the reasons and fraud follow as supporting findings (Sections 4 to 7).
- **Tables.** New Table 2 (the founder against competitors) and Table 3 ($100 in the firm, its competitor and the
  S&P 500). The older body tables move: founders by reason is Table 4, the announcement Table 5, size bands Table 6,
  delisting Table 7. New appendix Tables IA.15 to IA.18.
- **Fragile numbers, stated in the text.** Dollar means and totals rest on a few very large firms: Enron's announcement
  gain against its competitor is larger than the whole founder total, JDS Uniphase is the founder total through the
  announcement, and Intel against Broadcom is half of the 60-month total for all firings. Medians and the $100 line
  are the numbers to read.
- **No new figure.** The served figures are redrawn from the repository on deploy, so a new figure would be missing on
  the live paper until a deploy; the path series is kept in outputs/founder_value_stats.json for a later figure.
- **Name.** "S&P 1500" throughout, as the operator asked.

### D-35 addendum (23 Nov 2026): wider case list, five coders, extra fields, three fixes

- **Case list.** At the coordinator's request the cases cover `paper/founder_cases/h1_list.csv`: 103 founder departures
  (the 77 founders in H1 of D-34, and flagged others such as fraud firings), including the 55 of D-35. Five coders took
  rows 1-20, 21-40, 41-60, 61-80 and 81-103 (batches A to E); the merge keeps each coder's text as written and takes
  every number from `founder_cases_data.csv`. Case codes are not changed in the sample; verdicts are recorded only.
- **Extra fields** (coordinator): was it a push (pushed, planned succession, unclear, with a quote); news check (first
  press report against day 0, within 3 days or not); cause as the sources state it, never read from the return;
  whether the matched competitor is a plausible competitor; the coder's verdict (keep, recode as not a firing, recode
  the reason, redate, bad competitor match).
- **Board fate, boomerangs and next moves** are hand-classified from the coders' text in `analysis/founder_cases.py`
  (STAYED, LEFT, BOOMERANG, NEW_FIRM, WENT_AFTER), so a reader can check each call against its case.
- **Fixes, made before the summary tables were written.** (1) A firing with a complete three-year return but no matched
  firm is labelled "no matched competitor", not "not yet 3 years" (CA, Comverse and three others); the thresholds are
  unchanged. (2) The S&P 500 column is founder_value's `sp_m36`, which is already the firm minus the S&P 500; an early
  draft subtracted it again and showed the index's own return. It was never used to classify. (3) The three-year dollar
  gap against the matched firm is `mbhar_3y` times market value at day -31 (2023 dollars), so the dollar and percentage
  figures use the same match; founder_value's own return-on-assets match differs slightly.

## D-37 Corrections from the manual check of all 103 founder departures (23 Nov 2026, before any corrected number)

Operator, 23 Nov 2026: "this manual check with multi parallel and news check and actual causative check will filter out
bad match", then "figure out the final analysis and results on founder CEO firing or ousting". The five-coder check
(paper/founder_cases/, D-35) found three kinds of error. All corrections below are fixed now, before any corrected
statistic is computed, and every corrected result is reported beside the D-34 result it replaces.

1. **Not a firing (12, all in H1).** Planned successions by the sources: Enron 2000, Cree 2001, Aspen Technology 2002,
   Alpha Natural Resources 2008, Datascope 2009, Five Below 2014, Guess 2015, Ralph Lauren 2015, BankUnited 2016,
   KLX Energy 2020, ViaSat 2020, Greenbrier 2021. They leave the firing sample (H1 goes from 77 to 65 founders) and
   join no comparison group.
2. **Reason recoded.** Synchronoss 2017 and AstroPower 2003 to fraud (outside the main sample); AdaptHealth 2021 to
   personal conduct (into the main sample); AXT 2004 from coup to other. Batch files give the quotes.
3. **Redated (13).** Day 0 moves to the first public report in the batch files; the cases stay in their groups.
4. **Competitor re-matched for every firing and retirement, not only founders.** 56 of 103 founder matches were not
   real competitors because the Fama-French 48 groups are broad. New primary match: same 4-digit SIC, else same
   3-digit SIC, else same Sharadar industry; market value within 50%; no CEO change in the prior three years; nearest
   prior 12-month return. The level used is recorded per firm. The D-34 match is kept as a robustness row. Every new
   founder pair is listed with both names for a plain-terms check.
5. **Asymmetry guard.** Only founders were checked by hand, which could bias founder against hired. A random sample of
   hired-CEO firings is checked with the same push/date rules; its error rate is reported, and H1 is also shown with
   the uncorrected codes.

The frozen H1 test, windows, dollar measure and inference of D-34 are unchanged. Medians and the $100 line lead the
text because dollar means and totals rest on single firms (D-34 report).

## D-38 The same corrections on the hired side, and one screen for every firing (23 Nov 2026, before any D-38 number)

The hired-CEO audit of D-37 item 5 (paper/founder_cases/hired_audit.csv and hired_audit.md) drew 60 hired-CEO
firings from the 1,131 in the H1 comparison group at random (numpy default_rng(20261123), list fixed before reading).
It found 5 planned successions (8.3%, Wilson 3.6 to 18.1), against 12 of 77 founders (15.6%; Fisher p = 0.30), and 5
wrong dates (8.3%, against 13.0% for founders). To keep founder against hired symmetric:

1. **Hired fixes, applied as the founder fixes were.** The 5 planned successions leave the sample (Coca-Cola 2004 and
   2016, ConAgra 2014, Ascena 2015, Ulta 2010); 5 are redated to the first public report (A.M. Castle to the first 8-K,
   10 May 2012; Pfizer 28 Jul 2006; Network Equipment 19 Jul 2005; Steel Connect 20 Feb 2002; Compass Minerals 19 Nov
   2018); Symmetry Medical 2011 is recoded to financial misconduct (outside the main sample). They are applied in the
   pipeline from paper/d38_corrections.csv, in the same columns as paper/d37_corrections.csv.
2. **A rule-based planned-succession screen applied to every firing, founder or hired.** A firing is flagged when
   either holds, using only fields held for every event:
   - (a) the announcement (day 0 after D-37 and D-38) came 90 or more calendar days before the database's
     left_ceo_office date; or
   - (b) the database notes or the coded evidence quote say the CEO stayed on as chairman or executive chairman, and
     the same text names the chief operating officer or the president as the successor.
   The screen is validated against the 163 hand-checked cases (103 founder departures, D-35; 60 hired, the audit),
   where 17 are planned successions. Sensitivity (flagged among the 17) and false positives (flagged among the
   other 146 cases) are reported before the screen is used.
3. **H1 four ways:** as published (D-34); D-37 founder corrections; D-37 plus the hired fixes; and all of that with
   the screen dropping flagged firings on both sides. The screened version is the primary result only if the
   validation sensitivity is at least 0.7; otherwise it is a robustness row. The audit's sample and rates go in the
   Internet Appendix.

### D-38 addendum: exact small-sample tests (23 Nov 2026, operator's request, before any of them is computed)

Beside the Welch and Mann-Whitney tests of D-34, H1 also gets a two-sided permutation test of the founder minus
hired difference in means (founder and hired labels shuffled 20,000 times, seed 20261123), and an exact sign test of
whether the founders' own gaps against the competitor are more often negative than positive. Labelled as an addendum
wherever they appear; they do not replace the frozen tests.

## D-39 The paper as a standard empirical finance article (23 Nov 2026)

Operator, 23 Nov 2026: finalise for publication; then "It can't be a story story for a journal": a standard empirical
article in formal register. The main text is now Introduction; Related literature and hypotheses (H1 founder against
hired, with the irreplaceable-founder and entrenchment predictions; H2 firings against retirements; H3 personal scandal
against fraud); Data and sample (census, hand verification, exclusions, summary statistics as Table 2); Empirical design;
Results by hypothesis; Evidence from the cases; Robustness; Discussion and limitations; Conclusion. The hand checks,
audits, balance, benchmarks, the four-way H1 table, the case-by-case, excluded and founder-fate tables and the
founder-competitor pairs are in the Internet Appendix (A to G).

Primary H1 result (D-37 and D-38 codes, D-37 competitor): through the announcement founders' firms trail their
competitors by 4.2% and hired CEOs' firms by 7.7%; the difference of 3.5 points is not significant (p = 0.366,
interval -4.1 to 11.1, Holm 1.000, permutation p = 0.373). The D-38 screen's sensitivity on the 163 hand-checked cases
is 0.59 (10 of 17), below the 0.7 required, so the screened version is a robustness row. The exhibits were renumbered
in order of appearance; Figure 3 stays in the main text and Table IA.23 lists the founder-competitor pairs.

## D-40 Long-run growth after a founder or scandal dismissal (23 Nov 2026, fixed before any of these numbers)

Operator, 23 Nov 2026: "what should have been obvious is firing a founder or after sex scandal [damages] the company
... especially long term advantage and growth tanks". Share returns alone do not test this. Design, frozen here:

- **H4.** After a founder dismissal, the firm grows more slowly than its competitor over the next five years, and by
  more than after a hired-CEO dismissal. **H5.** The same for dismissals over a personal scandal against other
  dismissals (and the sex-or-relationship subset, named if under 10). Two-sided tests; nulls reported as nulls.
- **Outcomes** (Sharadar SF1 annual, fiscal years -3 to +5 around the dismissal year 0): revenue growth (log change,
  cumulative to +3 and +5), R&D to sales, capital spending to assets, asset growth, return on assets, gross margin,
  and market value. Employees if the data hold them.
- **Benchmark.** The D-37 competitor (primary) and the industry median (robustness). Difference-in-differences:
  (firm - competitor) after minus (firm - competitor) over years -3 to -1, so a firm already shrinking is not counted
  as a new loss.
- **Attrition.** Firms that go bankrupt or are delisted for cause stay in: revenue growth is set to -100% from the
  exit year (reported with and without); takeovers leave at the takeover and are counted. Every table shows how many
  firms remain at each year.
- **Tests.** Founder minus hired and scandal minus other: medians (Wilcoxon), means (Welch), and a regression with
  size, prior growth, prior return, leverage, industry and year, clustered by firm. Holm across outcomes at +3 and
  +5. Cells under 10 are named, not averaged. Share-return results at 36 and 60 months are reported beside these.

## D-40 addendum: how the growth tests were built, and what they found (23 Nov 2026)

Implementation choices D-40 left open, fixed in `analysis/founder_growth.py` before any result was read:

- Year 0 is the calendar year of the announcement; the base year is -1, the last full year before the dismissal. The
  earlier year is -3, or -2 where year -3 has no filing. Growth is a year (log change divided by the years).
- "Delisted for cause" is a regulatory delisting in the corporate actions around the last share price, read as
  `event_study.delist_return` reads them. With failed firms at -100%, growth is simple growth a year, which is -100%
  at zero; the same rule is applied to the competitor. A pair leaves when the firm or its competitor is taken over.
- R&D to sales is tested only for firms that report R&D in year -1. Employees are not in the data.
- The regression's outcome is the firm-minus-competitor change after year -1, with the firm's prior revenue growth as
  a control; outcome and controls are winsorised at 1% and 99%.

Labelled additions, not in D-40: the year-by-year revenue index (Table IA.27, descriptive) and the levels before and
after for the firm and its competitor (Table IA.26).

Results. H4 is not supported: against the competitor the median founder firm's revenue growth changes by -0.6 points a
year to year +3 (p 0.670, N 30) and -2.0 to year +5 (p 0.634, N 25); founder minus hired has Holm p 1.000 on every
outcome. H5 is not supported: scandal dismissals +0.8 points (p 0.937, N 25). Against the industry median the founder
firm slows 7.2 points a year and the hired-CEO firm 1.4 (difference in medians p 0.053, unadjusted, robustness
benchmark). Only 16 dismissals are over sex or a relationship and 7 have a competitor filing in year +3: named
(Table IA.30), not averaged.

Layout. The body carries one compact table a hypothesis (Tables 9 and 10, seven rows each); the full tests are
Tables IA.24 and IA.25. The full tables in the body pushed the earlier exhibits more than a page from their text, and
so did a longer design section before the results, so the design of these tests is stated at the start of Section 5.4. No new figure: served figures deploy from `main`,
so a new one would be missing on the live paper until a deploy; the series is in the statistics payload.

## D-41 Changes after the four internal audits (23 Nov 2026)

Four read-only audits (prose, claims against evidence, a referee report, narrative) were run on the D-40 draft. What
changed, and why:

- **WWE redated** from 22 Jul 2022 (McMahon's retirement) to 17 Jun 2022, by the leave rule of D-30: the 8-K of 22 Jun
  2022 records that on 17 Jun he "voluntarily stepped back ... until the conclusion of the investigation" and an
  interim CEO was named. Added to d37_corrections.csv; the pipeline was re-run. The stored version runs of D-34 and
  D-37 (Table IA.8 rows other than the primary and the screen) were not re-run and keep the old date.
- **Three checks added after review, labelled as such in the text:** H1 on the founders the case check found clearly
  forced out (push_class = pushed); H1 on pairs matched within the same 4-digit SIC code only; H1 against the mean of
  the three nearest competitors (pr3, same rule as the primary match). They were added after the primary result was
  known and are robustness rows only.
- **Text:** the reading of the null, the benchmark sign, who did each coding pass, which hypotheses were fixed in
  advance, and the internal labels, per the audits. Title unchanged (operator's call).

## D-42 The question is founder firms against normal firms; founder against hired CEO is dropped (24 Nov 2026)

Operator, 24 Nov 2026: "Not a hired ceo we were never benchmarking against that ... we were benchmarking against
normal", and "Fix it rebuild it ... that should never be a secondary question we have too few firings to even answer
it."

- **The question.** Do founder firms lose against normal firms (the market, their industry, comparable competitors)
  around and after the board's dismissal of the founder CEO? That is H1 from here on.
- **Founder against hired CEO is removed** as a hypothesis and as a test everywhere in the paper. With about 65 founder
  dismissals the comparison cannot be answered (D-34, D-41: every version insignificant, the bound too wide to say the
  groups are alike). Hired-CEO firms appear only inside the results on all dismissals (dismissals against retirements;
  personal scandal against fraud), never as the founder comparison group.
- **Benchmarks.** One table reports founder firms against each benchmark already computed under D-34, D-37, D-38 and
  D-41: the S&P 500, the industry average, the three closest competitors (same rule as the primary match), the firm
  matched on profitability, and the single closest competitor. No new statistic is estimated. The text leads with the
  three closest competitors as the control for the decline before the dismissal, because an average of three removes
  much of one firm's own noise. That choice was made after the results were seen (the D-34 design named the single
  competitor primary) and the single-competitor row stays in the same table and the text.
- **Timing.** This change was made after the D-34 to D-41 results were seen. The earlier design and its results stay
  in this log (D-34 to D-41) and the stored statistics; nothing is deleted from the record.

D-42 implementation (24 Nov 2026). No existing statistic changed (founder_value.py re-run; 0 of 22,692 values moved).
Added to founder_value.py, as labelled addenda: the $100 line against the industry average and the three closest
competitors (values only; their tests are the return-gap tests already computed), and the Holm adjustment across the
five benchmarks of each window (fv.founder.{bench}.{window}.ret.{mean,median}.holm5_p). The text leads with the
three-competitor average; its sample is 44 founder firms against 63 for the single competitor. Its prior-year
balance was added on the coordinator's request (fvbal3.*; see the note below). Removed from every table: founder-against-hired rows, columns and tests (a filter in
combine_results.table() drops any left in shared builders). Table 3 now gives the founder firm against five benchmarks
by window; Table 4 the $100 line against four; Table 8 founders only; Tables 9 and IA.24 founders against the competitor
and the industry median; IA.5 intervals and Holm; IA.7 dollars; IA.8 the founder firm under each version; IA.11 the
founder CAR by window; IA.26 founders only; IA.31 founders only. The founder reason mix (fraud 23.1% of founder
dismissals) stays as a descriptive fact, without the hired comparison.

D-42 addendum, three-competitor balance (24 Nov 2026, coordinator's request). founder_value.py now records, for each
firing with three closest competitors, the mean of the three on the prior 12-month return (days -282 to -31), market
value and ROA (pr3_prior12, pr3_mcap_fy, pr3_roa) and reports balance() as fvbal3.*. No existing value changed. Founder
firms (n 44): prior return -17.4% (median -31.6%) against -12.3% (median -13.9%) for the mean of the three; gap -5.2
points (p 0.200), median gap -1.5 (Wilcoxon p 0.081). Median market value $0.58bn against $0.45bn (log gap +0.16,
p < 0.001); median ROA 4.8% against 3.9% (gap p 0.372). The three competitors fell nearly as far as the founder firms,
so the -11.2% six-week loss against them does not mainly carry a prior slide the competitors escaped. Table IA.4 and
Sections 4.1, 8 and Internet Appendix B state it.

## D-43 Forward-looking: what an investor earns after a founder firing, against the stock market (24 Nov 2026, fixed before any of these numbers)

Operator, 24 Nov 2026: "industry was same as them so that is not primary firing concern ... it is on forward looking
basis and performance on $ to $ so we can answer a simpler question here: how much do shareholders lose when board
makes these calls and how much stock market is there so we can establish alpha for investing". The question becomes
what an investor who buys (or shorts) the founder firm once the firing is public earns against the stock market.

Design, frozen here:

- **Entry.** The close of trading day +1 after the announcement, on well-dated founder firings (primary).
  Robustness: entry at the close of day 0; and every founder firing, entered at the close of the trading day after
  left_ceo_office (the database's date, which lags the news for many firings).
- **Horizons.** 1, 3, 6, 12 and 36 months, a month being 21 trading days, measured from the entry close.
- **Benchmarks.** The S&P 500 total return (SPY, dividend-adjusted; primary, the operator's words). Context rows: the
  industry average and the three closest competitors, as defined in founder_value.py.
- **Measures.**
  1. $100 in the founder firm against $100 in the S&P 500 at each horizon: mean and median value, and the share of
     firms ending above the S&P 500.
  2. The buy-and-hold gap (firm minus S&P 500): mean with the skewness-adjusted t of Lyon, Barber and Tsai (1999)
     and a bootstrap p-value and 95% interval (10,000 draws); median with the Wilcoxon test.
  3. Calendar-time portfolio: each calendar month, hold every founder-firing firm in months 1 to H after the month
     of entry (H = 1, 3, 6, 12, 36), equal- and value-weighted (market value at day -31). Monthly excess return
     regressed on the market (CAPM) and on the five Fama-French factors plus momentum; Newey-West standard errors
     with lag 6. Every month with at least one firm is kept (founder firings are too few for the 10-firm floor of
     calendar_alpha.py); the number of months and the average number of firms held are reported. The minimum
     detectable monthly alpha is 2.8 standard errors of the alpha (80% power, 5% two-sided).
- **Delisting.** As in Section 3 and founder_value.Book: the delisting return (0 takeover, -100% bankruptcy, -30%
  other), then the proceeds held in the market to the end of the window.
- **Context rows** (same measures, larger N): every firing but fraud, and retirements. Founder firings over fraud and
  over a personal scandal are named case by case ($100 against the S&P 500 at 12 months), never averaged.
- **Reuse.** founder_value.py already reports the firm-minus-S&P 500 gap from the close of day +1 at 12, 36 and 60
  months on every firing with a complete horizon (fv.founder.sp.m12 and so on). Those keys are cited, not recomputed;
  the new script adds the 1-, 3- and 6-month horizons, the well-dated entry and its robustness, the $100 line
  against the S&P 500, the share beating it, the bootstrap and the calendar-time alpha.
- **Inference.** No Holm family is claimed across horizons for the $100 line, which is descriptive; the calendar-time
  alphas at the five holding periods are a Holm family per weighting.

Nothing here changes after numbers are seen; any addition is labelled as an addendum.

## D-44 Forced resignations coded as retirements join the founder sample (24 Nov 2026, before any re-run)

Operator, 24 Nov 2026: "remember to capture the ones where founder was forced to resign, that counts too", then "add
forced resignations". Under D-01 a resignation under board pressure is a dismissal, but the sample took only the
database's dismissal codes (3 and 4). A scan of the 448 founder departures coded as retirements (code 5), with a second
pass on 24 Nov (paper/founder_cases/forced_resign_scan.md), found three forced resignations. They join the founder
dismissal sample with database code 3 (paper/d44_corrections.csv), and their founder status is set by hand:

| Event | Firm, founder | Day 0 | Date source | Evidence |
|---|---|---|---|---|
| 7861 | J.D. Edwards, C. Edward McVaney | 4 Jan 2002 | database announcement date | "its board decided to swap long-term chief executive officer Ed McVaney for Robert Dutkowsky" (Computer Weekly, as quoted in the database note) |
| 7188 | Mednax, Roger J. Medel | 13 Jul 2020 (was 12 Jul, the day he left office) | Business Wire, 13 Jul 2020 | "pursuant to an agreement that Mednax has reached with Starboard Value LP ... which owns approximately 9.9%" (as quoted in the database note) |
| 4161 | Cypress Semiconductor, T.J. Rodgers | 28 Apr 2016 (was 1 Apr) | Mercury News, 28 Apr 2016 | database coder: "the board of directors pressured Mr. Rodgers to make way for new blood"; MarketWatch title "Burning Cypress: ousted CEO wages bruising battle with company he built" |

Reasons: J.D. Edwards performance (an "ailing" company, per the same report); Mednax activist or shareholder pressure;
Cypress unclear (no source gives the board's reason). Eleven cases stay out as unclear and are listed in the scan.
This changes the sample after earlier results were seen, so the founder results are reported before and after it.

Title: the operator's call, 24 Nov 2026: "keep the title as is it is sexy unless it is false". It stays "Sacked: Sex,
Fraud, and the Fate of Firms That Fire Their Founder CEO". It is not false: the paper reports dismissals over sex or a
relationship and over fraud, and founder dismissals are its subject.

## D-45 A wider founder-removal dataset from 8-K filings (24 Nov 2026, design fixed before collection)

Operator, 24 Nov 2026: "How can it be only one founders are not just fired ceo there is board and other function
firing of founders etc .. figure it out how many founder are you using?" A separate dataset of founder departures
from any role (CEO, chair, director, officer) at all US-listed firms, 2004-2025, built from 8-K Item 5.02 filings, is
designed in founder_universe/DESIGN.md. It does not change the paper's sample until a later decision.

## D-46 When the news trades: announcement day against the long horizon (24 Nov 2026, design fixed before any number)

Operator, 24 Nov 2026: "Did you also analyse market factored in i.e. on trading floor day when this news is released
vs long horizon? that will be interesting on alpha no?" Analysis only (analysis/founder_timing.py,
outputs/founder_timing_stats.json, paper/founder_cases/timing.md); the paper text is unchanged until a later decision.

- **Release time.** For each well-dated firing (founders and all firings), the acceptance timestamp of the firm's 8-K
  filed on the announcement date or the trading day before or after it (EDGAR, data.sec.gov submissions), and the
  press-release time where the case files hold one. Classes: before the open (before 09:30 New York), during trading
  hours (09:30 to 16:00), after the close (after 16:00), unknown. The first tradeable day t* is day 0 for before-open
  and during-hours releases and the next trading day for after-close releases; unknown releases keep day 0 and are
  reported separately.
- **Windows** (firm minus the S&P 500, SPY with dividends; and firm minus its industry equal-weighted mean, D-34):
  run-up days -30 to -2; day t*split into the overnight gap (prior close to open) and the trading day (open to close),
  each against SPY's own overnight and open-to-close return; day t*+1; days +2 to +5, +6 to +20, +21 to +60 after t*;
  6, 12 and 36 months reuse the D-43 statistics. Industry is close-to-close only (no intraday industry series).
- **Intraday path** where Alpha Vantage 1-minute bars exist: the firm's return minus SPY's from the first trade after
  release to +5, +30 and +60 minutes and to the close, and from the close of t* onward, to see whether the reaction is
  complete by the close of the first tradeable day.
- **Tests.** Means (skewness-adjusted t and firm-clustered t) and medians (Wilcoxon) per window, founders and all
  firings; Holm across the windows within each group.
- **Trading rules** (short the firm, long SPY): enter at the open of t*or at the close of t*, hold to +5, +20, +60
  trading days and 6 months; net of 20 bp and 50 bp round trips; the share of winning trades; calendar-time alpha
  (CAPM and five factors plus momentum, Newey-West) for the close-of-t* holds; the minimum detectable effect for
  founders at 80% power.
- Delisting returns as in Section 3 for the daily windows. Nothing here changes after numbers are seen; any addition
  is an addendum.

## D-47 Review round on the final Sacked text (24 Nov 2026)

The operator's standing instruction (24 Nov): fix every open major and iterate review, fix, review until readiness is
at least 70. Added after the main results were known, and labelled so in the paper:

- **Benchmark choice.** The founder loss against the mean of the 2, 4 and 5 closest competitors on the prior-year return
  (the Section 4.1 rule with k = 2, 4, 5), beside the 3 already reported (Table IA.31). The three-competitor benchmark
  was chosen after the results were seen (D-42); the k sweep shows whether the result depends on k.
- **Founders coded as hired CEOs.** A Wikidata check of the 1,170 dismissals not coded as founders
  (founder_missed_check.py): 198 are at firms whose founders Wikidata lists; none of those CEOs founded the firm, and
  the four who share a founder's surname are heirs.
- **Fiscal year 0 profitability** added to Table 1 beside fiscal year +1.
- **Wording.** Association, not cause; the benchmark choice stated once in the introduction and once in Section 4.1;
  Table 8's note on Panel A shares; coups checked case by case for founders.
