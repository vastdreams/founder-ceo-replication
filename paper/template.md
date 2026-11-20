# Sacked: Sex, Fraud, Founders, and the Fate of Firms That Fire Their CEO

## Abstract

When a US board fires its CEO, the market has usually seen the trouble coming. At S&P {{index_size}} firms the stock slides {{drift.forced.pre_m30m2.mean|abs}} in the six weeks before the announcement, drops {{car.forced.mm_m1p1.mean|abs}} in the three days around it, then stops. Firings over fraud cost {{rob.all_dates.financial_misconduct.mm_m1p1.mean|abs}}; firings over sex scandals barely move the price. Fired founders may cost more than hired CEOs, but the evidence is weak. Within five years a third of firing firms stop trading, twice the rate after retirements, with bankruptcy the larger part of the gap. Against similar firms, returns differ little after the first year.

## 1. Introduction

::: findings

1. The stock falls before the board acts: {{drift.forced.pre_m30m2.mean}} against the market over the six weeks before (Figure 2).

2. The firing itself costs {{car.forced.mm_m1p1.mean}} over the three days around the announcement, and the next three months add no significant move (Table 3).

3. Fraud costs {{rob.all_dates.financial_misconduct.mm_m1p1.mean}}; sex and relationship scandals {{rob.all_dates.sex_or_relationship.mm_m1p1.mean}} (Table IA.1).

4. Fired founders cost {{car.forced_founder.mm_m1p1.mean}}, against {{car.forced_nonfounder.mm_m1p1.mean}} for hired CEOs, a gap that is {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|sig}} (Table 4).

5. Within five years {{exit.forced.delisted_5y}} of firing firms have stopped trading, against {{exit.retired.delisted_5y}} after a retirement (Figure 5).

:::

In 1985 Apple's board sided with its new chief executive against Steve Jobs, and Jobs left the company he had founded. By 1997 Apple had bought his next company and he was back in charge. In November 2026 Nvidia's board accepted the resignation of its co-founder and chief executive, Jensen Huang [@nvidia2026form8k]. Three days earlier the board had opened an independent investigation after reports that Huang had been the target of a foreign intelligence effort [@nvidia2026board]. News reports also described an affair [@cnbc2026nvidia]. The board gave no reason for the departure.

Nvidia's shares closed {{hook.nvda.day_ret|abs}} lower on the day the resignation was announced, after falling as much as {{nvda_intraday_low_pct}}% during the session [@cnbc2026nvidia]. From the last close before the board's statement, they had lost {{hook.nvda.since_board_statement|abs}} by 18 November. Few corporate events are more dramatic than a board turning on the person who built the company. They raise a plain question for investors, directors and employees. What happens to a company after its board fires the boss, and does it matter who the boss was and why the board acted?

This paper answers that question for firings at S&P {{index_size}} firms over a quarter of a century. It answers it horizon by horizon, because a firing is not one event for the stock. There is a slide before the announcement, a drop on the day, and then months and years in which the firm is sold, fails or carries on. Results that mix these horizons, or that hide how many firms are still measured at each, can mislead. Table 1 therefore sets out the paper one horizon per row, with the number of firings measured at each.

::: glance

### Table 1. The firing, horizon by horizon: S&P {{index_size}} firms, 1998 to 2023

| Horizon | What is measured | Firings | Retirements | N firings | p |
|---|---|---|---|---|---|
| Trading days -30 to -2 | Return minus the market | {{drift.forced.pre_m30m2.mean}} | {{drift.retired.pre_m30m2.mean}} | {{drift.forced.pre_m30m2.mean!n}} | {{drift.forced.pre_m30m2.mean!pv}} |
| Trading days -1 to +1 | Abnormal return, market model | {{car.forced.mm_m1p1.mean}} | {{car.retired.mm_m1p1.mean}} | {{car.forced.mm_m1p1.mean!n}} | {{car.forced.mm_m1p1.mean!pv}} |
| Trading days +2 to +60 | Return minus the market | {{drift.forced.post_p2p60.mean}} | {{drift.retired.post_p2p60.mean}} | {{drift.forced.post_p2p60.mean!n}} | {{drift.forced.post_p2p60.mean!pv}} |
| {{months_1y}} months | Return minus a matched firm, median | {{mbhar.forced.1y.median}} | {{mbhar.retired.1y.median}} | {{mbhar.forced.1y.median!n}} | {{mbhar.forced.1y.median!pv}} |
| {{months_3y}} months | Return minus a matched firm, median | {{mbhar.forced.3y.median}} | {{mbhar.retired.3y.median}} | {{mbhar.forced.3y.median!n}} | {{mbhar.forced.3y.median!pv}} |
| {{months_5y}} months | Return minus a matched firm, median | {{mbhar.forced.5y.median}} | {{mbhar.retired.5y.median}} | {{mbhar.forced.5y.median!n}} | {{mbhar.forced.5y.median!pv}} |
| Within {{months_5y}} months | Share no longer trading | {{exit.forced.delisted_5y}} | {{exit.retired.delisted_5y}} | {{exit.forced.delisted_5y!n}} | {{exitdiff.forced_vs_retired.delisted_5y!pv}} |
| Fiscal year +1 | Change in ROA minus the matched firm, median (pp) | {{roa.forced.abn_d_1.median}} | {{roa.retired.abn_d_1.median}} | {{roa.forced.abn_d_1.median!n}} | {{roa.forced.abn_d_1.median!pv}} |
| Fiscal year +3 | Change in ROA minus the matched firm, median (pp) | {{roa.forced.abn_d_3.median}} | {{roa.retired.abn_d_3.median}} | {{roa.forced.abn_d_3.median!n}} | {{roa.forced.abn_d_3.median!pv}} |
| About two years | Share of the earlier directors gone | {{board.forced.director_turnover.mean}} | {{board.retired.director_turnover.mean}} | {{board.forced.director_turnover.mean!n}} | {{boarddiff.forced_vs_retired.director_turnover.diff_mean!pv}} |

*Notes.* Day 0 is the first trading day on or after the announcement. The first three rows use firings whose announcement date comes from the database, a hand check or the firm's 8-K; the other rows use every firing. A month is {{trading_days_per_month}} trading days counted from day +2. N firings falls with the horizon because recent firings have not reached it and firms that are sold or fail stop filing. The p column tests the firing number against zero; for the share no longer trading and the directors gone, it tests the difference from retirements.

:::

Three findings stand out. First, the market sees the trouble coming. The slide starts weeks before the board acts, and the price stops moving within days of the news (Section 3).

Second, why the board acted matters, but less neatly than the usual story suggests. Firings over the accounts are costly on the day; firings over sex scandals are not. Conduct firings as a group and fired founders cost more than the rest, but neither gap is statistically significant over three days (Section 3).

Third, the lasting difference is survival. Within five years a third of firing firms have stopped trading, twice the rate after a retirement. With controls for size, profitability, year and industry, a firing still adds about one in ten to the chance of leaving the market. More of that comes from bankruptcy than from takeover (Section 5). Returns against similar firms differ little after the first year (Section 4).

The paper adds to three lines of work. Boards fire CEOs after poor performance, including poor performance of the whole industry [@jenter2015], and returns fall well before the change [@weisbach1988]. Forced exits are rare, which suggests that boards behave as if replacing a CEO were costly [@taylor2010; @kaplan2012]. The market's reaction depends on what the firing reveals [@kind2011; @chen2026].

Founder-led firms invest differently and have been valued more highly [@fahlenbrach2009]. Founder status itself responds to performance [@adams2009], founders are often replaced as their firms mature [@wasserman2003; @aran2024], and in venture-backed startups replacing the founder improves outcomes [@ewens2018]. Executive scandals and financial misreporting both cost shareholders [@cline2018; @larcker2016; @borellikjaer2021; @karpoff2008jfqa], and managers who misreport usually lose their jobs [@karpoff2008jfe].

We add three things. We follow firings from six weeks before the announcement to five years after it, and report the number of firms measured at every horizon. Where the database has no announcement date, we take it from the firm's own 8-K filing. We split the firings by founder status and by the reason the board acted, coded from filings and news and checked by hand where it matters most. And we compare sex scandals with fraud on the same sample and the same window.

We test four hypotheses. H1: firings lower the stock price at the announcement. H2: firing a founder lowers it more than firing a hired CEO, because founders carry value a successor cannot replace [@fahlenbrach2009]. The alternative is that boards act against founders only when the case is overwhelming, so the firing ends entrenchment and is good news [@taylor2010]. H3: firings for conduct cost more than firings for performance, because they arrive as surprises. H4: firings change what happens afterwards to the firm's returns, survival, profitability and board.

Section 2 describes the data, the coding and how each horizon is measured. Section 3 reports how the market reacts before, at and after the announcement. Section 4 follows returns and profits for five years. Section 5 asks which firms are sold, go bankrupt or survive. Section 6 examines the board. Section 7 concludes.

## 2. Data and sample

### CEO departures

The departures come from the open CEO dismissal database of @gentry2021, extended by its authors to 2023. It codes the reason for every CEO departure at S&P {{index_size}} firms from press coverage and filings. An independent recoding agreed with it on {{lit_gentry_agreement_pct}}% of events [@gentry2021]. Codes 3 and 4 (dismissed for job performance, and for legal violations or personal conduct) are firings. Code 5 (voluntary retirement) is the comparison group.

Press releases rarely say that a CEO was fired [@gow2017], and how forced exits are classified changes the results [@fee2018]. Like the database, we treat a resignation under board pressure as a firing. A CEO who resigns during an investigation, a scandal or an activist campaign counts as fired.

We link each departure to the firm's SEC Central Index Key, and through it to daily prices that include firms later delisted. Failed and acquired firms therefore stay in the sample. Daily prices for delisted firms begin in {{sample_start_year}}. Table IA.2 traces the firings from the database to the analysis samples. Figure 1 shows how they spread over time.

![Figure 1. Forced CEO exits per year](/static/reports/founder-ceo/figures/fig5_per_year.png)

*Figure 1. Forced CEO exits per year.* Notes. Firings by year, 1998 to 2023, by the database's dismissal type; the amber numbers count the founders among them. The bars count every firing in the database, including firms without usable prices; the last year covers part of 2023.

### Dating the announcement

A three-day window needs the right day. The database gives an announcement date for about a third of departures. For the rest it gives only the day the CEO left office, which can come weeks after the news. We therefore look for the firm's own 8-K filing on the departure. It must be filed between 90 days before and 15 days after the CEO left, and from August 2004 it must be filed under the item for officer departures. It must name the CEO with a chief-executive title and a word such as resign, retire or terminate, and not describe an appointment. The 8-K's date of the earliest event reported is then the announcement date.

On departures the database does date, the 8-K date falls within 3 days of it in {{redate_agree_3d_pct}}% of cases and within 10 days in {{redate_agree_10d_pct}}%. Hand checks corrected a few further dates.

The 8-K dates are useful but noisy. Firings dated by the database earn {{rob.datesrc_database.mm_m1p1.mean}} over three days; firings dated by an 8-K earn only {{rob.datesrc_8k.mm_m1p1.mean}}, as a misplaced day 0 would produce. Announcement-window results therefore use the {{a.n_forced}} firings dated by the database or a hand check.

The other {{a.n_forced_undated}} firings earn {{rob.undated.forced.mm_m1p1.mean}}, which is {{rob.undated.forced.mm_m1p1.mean|sig}} (Table IA.1). Long-run results use all {{a.n_lr_forced}} firings with returns, since a few days of error cannot move a return measured over years.

### Founders and reasons

For each departure we code whether the CEO founded or co-founded the firm or its direct predecessor, and the board's main reason for acting.

A language model (DeepSeek, deepseek-chat, at temperature zero) drafts each code with a supporting quote. It reads the database's notes and sources and the 8-K the firm filed within {{evidence_window_days}} days of the departure. It also reads cited press releases, the CEO's Wikipedia article and matching New York Times articles. The prompt is in the replication package.

We then check by hand the codes where errors would matter most. Every founder code on a firing is checked against the firm's history: the model coded {{b.model_founder_codes}} firings as founder removals, and the review confirmed {{b.founders_confirmed}}, rejected {{b.founders_rejected}} and added {{b.founders_added}}. Every financial-misconduct, sexual-misconduct and relationship code is also checked. About a third of the model's financial-misconduct codes did not survive, usually because the misconduct came out only after the CEO had left.

The database's own codes are not always right either. Some departures it codes as forced read as planned successions in the filings and the press. We therefore repeat the main results on a strict sample: the {{a.n_forced_strict}} hand-dated firings that our evidence-based coding also reads as forced (Table IA.1). The named cases in Table 6 come only from this strict sample.

### How we measure returns

The announcement return is the abnormal return over three trading days, from the day before the announcement to the day after it. It uses the market model of equation (1):

$$AR_{it} = R_{it} - \hat\alpha_i - \hat\beta_i R_{mt}, \qquad CAR_i = AR_{i,-1} + AR_{i,0} + AR_{i,+1}. \tag{1}$$

Here $R_{it}$ is the stock's total return and $R_{mt}$ the market's. The coefficients come from trading days {{estimation_window_start}} to {{estimation_window_end}} before the announcement, with at least {{min_estimation_days}} days of returns. We test the mean with the cross-sectional t and with the standardized test of @boehmer1991, which allows for event-induced variance. We test the median with the Wilcoxon signed-rank test [@kothari2007]. A five-factor model with momentum gives the same answers [@famafrench2015].

For the six weeks before the announcement (trading days -30 to -2) and the three months after it (+2 to +60), we use returns minus the market. These carry no estimated alpha. A firm about to fire its CEO has usually done badly in the year before, so its estimated alpha is strongly negative. Projected forward, that alpha would manufacture a rebound that is not in the prices.

The long run is measured in months of {{trading_days_per_month}} trading days, counted from day +2. We compare each firm's buy-and-hold return with that of a benchmark, as in equation (2):

$$BHAR_i(h) = \prod_{t=2}^{T_h}(1+R_{it}) - \prod_{t=2}^{T_h}(1+R_{bt}). \tag{2}$$

Here $T_h$ is {{days_1y}}, {{days_3y}} or {{days_5y}} trading days, and the benchmark $b$ is either the market or a matched firm. A horizon counts only if it ends inside the data for every firm, so recent firings never enter because they happened to delist. The matched firm is in the same Fama-French industry, with market value within {{matching_rule_pct}} percent and the nearest operating return on assets in the year before. It had no CEO turnover recorded in the database in the three years up to the event. When no firm meets the size band, the nearest firm in size is used ({{h.relaxed_matches}} matches; Table IA.1 drops them).

A firm that stops trading inside the window takes a final return of zero for a takeover, minus 100% for a bankruptcy and minus 30% for other delistings [@shumway1997]. The proceeds are then held in the market until the horizon ends. Long-horizon returns are skewed, so we report medians with the Wilcoxon test and means with t-tests, adding the skewness-adjusted t of @lyon1999 for the three-year matched mean.

Operating performance is EBITDA over total assets from as-reported annual statements, winsorized at the 1st and {{winsor_upper_pct}}th percentiles. We measure its change from fiscal year -1 against the matched firm, which @barber1996 show is needed when firms performed unusually before the event. Board composition comes from the last proxy statement before the departure and the first one filed at least {{board_post_lag_days}} days after it.

### Who gets fired

Table 2 shows the firms before the departure. Firms that fire their CEO are about half the size of firms whose CEO retires: a median market value of {{desc.forced.mcap.median}} against {{desc.retired.mcap.median}} billion dollars. They are also less profitable, with a median return on assets of {{desc.forced.roa.median}} against {{desc.retired.roa.median}}, and their sales grow more slowly.

Boards fire CEOs of firms that are already struggling [@huson2004; @jenter2015]. That is why every long-run comparison in this paper is made against a matched firm as well as against the market.

<!-- TABLE:2 -->

## 3. The market's verdict

::: answer
**The question.** How does the stock react when a board fires its CEO, and does it matter who was fired and why?

**The answer.** The stock falls before the board acts, falls again on the news, and then stops. Fraud is costly on the day; sex scandals are not. Fired founders cost more in point estimate, though not significantly.
:::

### Before, at and after the announcement

Figure 2 follows the stock from six weeks before the announcement to three months after it. For firms whose CEO retires, the line is flat. For firms that fire their CEO, it slides for weeks, drops on the announcement and then moves sideways.

![Figure 2. Prices slide before the firing, drop on the news, then stop](/static/reports/founder-ceo/figures/fig1_event_time.png)

*Figure 2. Prices slide before the firing, drop on the news, then stop.* Notes. Mean cumulative return minus the market from trading day -30 to day +60 around the announcement (day 0), departures dated by the database or a hand check, with {{ci_level}}% confidence bands. Panel (b) splits firings by founder status and by the database's dismissal type. N is the number of departures with every day of the window.

Table 3 gives the numbers. Over the six weeks before, firing firms trail the market by {{drift.forced.pre_m30m2.mean|abs}}, while retirement firms do not move ({{drift.retired.pre_m30m2.mean}}). In the announcement window firing firms lose another {{car.forced.mm_m1p1.mean|abs}} (t = {{car.forced.mm_m1p1.mean|t}}), and retirement firms earn {{car.retired.mm_m1p1.mean}}.

The difference of {{cardiff.forced_vs_retired.mm_m1p1.diff_mean}} is {{cardiff.forced_vs_retired.mm_m1p1.diff_mean|sig}}. The standardized test of the firing mean gives t = {{car.forced.mm_m1p1.bmp_t}}, the five-factor model {{car.forced.ff5_m1p1.mean}} and the eleven-day window {{car.forced.mm_m5p5.mean}}. Over the three months after, firing firms earn {{drift.forced.post_p2p60.mean}} against the market, which is {{drift.forced.post_p2p60.mean|sig}}. H1 holds.

<!-- TABLE:3 -->

Firms that fire for performance trail the market by {{drift.performance.pre_m30m2.mean|abs}} over the six weeks before; firms that fire for legal or personal conduct trail it by {{drift.conduct.pre_m30m2.mean|abs}}. On the day the order reverses: conduct firings cost {{car.conduct.mm_m1p1.mean|abs}} and performance firings {{car.performance.mm_m1p1.mean|abs}}. The gap is {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean|sig}}.

The pattern fits H3, since conduct firings come with less warning and cost more on the day, but the evidence is weak. On every firing the gap is {{rob.all_dates.conduct_vs_performance.mm_m1p1.diff_mean}}, also {{rob.all_dates.conduct_vs_performance.mm_m1p1.diff_mean|sig}}.

### Founders

Table 4 reports the announcement return for each group. Fired founders cost {{car.forced_founder.mm_m1p1.mean|abs}}, against {{car.forced_nonfounder.mm_m1p1.mean|abs}} for hired CEOs. The difference of {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean}} is {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|sig}} (p {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|p}}). In a regression on all departures with event-year effects, the founder interaction is {{reg.car_m1p1.forced_x_founder}}, also {{reg.car_m1p1.forced_x_founder|sig}}.

The test is not powerful: with {{a.n_forced_founder}} hand-dated founder firings, it would detect only a gap of about {{mde.founder_gap.mm_m1p1}}. Table IA.3 reports the gap in every window. Over trading days -5 to +5 founders cost {{cardiff.forced_founder_vs_forced_nonfounder.mm_m5p5.diff_mean|abs}} more, which is {{cardiff.forced_founder_vs_forced_nonfounder.mm_m5p5.diff_mean|sig}} (p {{cardiff.forced_founder_vs_forced_nonfounder.mm_m5p5.diff_mean|p}}).

On every firing, founders cost {{rob.all_dates.forced_founder.mm_m1p1.mean|abs}} against {{rob.all_dates.forced_nonfounder.mm_m1p1.mean|abs}}.

Founder firms slide further before the announcement, by {{drift.forced_founder.pre_m30m2.mean|abs}} over the six weeks before, but the difference from hired CEOs is {{driftdiff.forced_founder_vs_forced_nonfounder.pre_m30m2.diff_mean|sig}}. The data cannot separate a founder premium from zero, though every estimate points the same way. They do rule out the strong form of the entrenchment view. The upper end of the 95% interval for fired founders is {{car.forced_founder.mm_m1p1.ci_high}}, so the market does not greet a founder's firing as good news.

The comparison fits earlier evidence from sudden deaths, where founder-CEOs and other CEOs move prices down by similar amounts on average, {{lit_death_founder_pct}}% and {{lit_death_other_pct}}% [@jenter2023].

<!-- TABLE:4 -->

### Sex, fraud and the rest

Table 5 and Figure 3 split the firings by the reason the board acted. Financial misconduct costs {{car.reason.financial_misconduct.mm_m1p1.mean|abs}} in the announcement window, and strategy or power disputes {{car.reason.strategy_or_power_dispute.mm_m1p1.mean|abs}}. Most other reasons cost little, and each group is small.

With so many reasons tested, chance alone would produce a significant one. After a Holm correction for multiple tests, no single reason is significant: financial misconduct has a Holm p of {{car.reason.financial_misconduct.mm_m1p1.holm_p}} and strategy disputes {{car.reason.strategy_or_power_dispute.mm_m1p1.holm_p}}.

Firings over sex scandals are a different matter. Only {{car.sex_or_relationship.mm_m1p1.mean|n}} have a hand-coded date, so we compare them with fraud on every firing. The {{rob.all_dates.sex_or_relationship.mm_m1p1.mean|n}} firings over sexual misconduct or a relationship earn {{rob.all_dates.sex_or_relationship.mm_m1p1.mean}}, against {{rob.all_dates.financial_misconduct.mm_m1p1.mean}} for the {{rob.all_dates.financial_misconduct.mm_m1p1.mean|n}} fraud firings.

That difference of {{rob.all_dates.sex_vs_fraud.mm_m1p1.diff_mean}} is {{rob.all_dates.sex_vs_fraud.mm_m1p1.diff_mean|sig}} (p {{rob.all_dates.sex_vs_fraud.mm_m1p1.diff_mean|p}}). On hand-dated firings it is {{cardiff.sex_or_relationship_vs_financial_misconduct.mm_m1p1.diff_mean}}.

The relationship cases include Intel, Boeing, McDonald's and Priceline, where the company said the CEO had broken its policy on relationships; we checked each label by hand. A fraud tells investors that the numbers they relied on were wrong. A sex scandal tells them about one person, and the firing removes that person. With so few sex cases, we treat the comparison as exploratory.

Earlier studies point the same way. When executive misbehaviour first becomes public, firms lose about {{lit_larcker_reveal_pct}}%, but the later firing itself costs about {{lit_larcker_fire_pct}}% [@larcker2016]. Personal indiscretions cost {{lit_cline_ceo_pct}}% when the offender is the CEO [@cline2018], and sexual-harassment scandals about {{lit_metoo_car_pct}}% [@borellikjaer2021]. Our window catches the firing, not the first report.

<!-- TABLE:5 -->

![Figure 3. Fraud is expensive; sex scandals are not, at least on the day](/static/reports/founder-ceo/figures/fig4_reasons.png)

*Figure 3. Fraud is expensive; sex scandals are not, at least on the day.* Notes. Mean abnormal return over trading days -1 to +1 by the coded reason the board acted, hand-dated firings, with {{ci_level}}% intervals; reasons with at least {{min_reason_cases}} firings. Crimson: money and legal cases; violet: personal conduct, including relationships with employees; grey: other reasons.

### The largest founders fired

Table 6 lists the largest firms whose founder was fired, among the firings the evidence also reads as forced. The range is wide. WorldCom lost {{case.49.car_m1p1|abs}} in the announcement window when Bernard Ebbers left in 2002, and it was bankrupt within months. Yahoo gained {{case.7398.car_m1p1}} when Jerry Yang stepped aside in 2008.

WWE rose {{case.8370.car_m1p1}} when Vince McMahon left in 2022 during an investigation of his conduct. There the market read the founder's exit as removing a problem rather than a source of value.

<!-- TABLE:6 -->

## 4. After the dust settles: long-run returns and profits

::: answer
**The question.** Does the firm do better or worse in the five years after the firing?

**The answer.** Against the market the median firm does far worse. Against similar firms with no recorded CEO change, it trails in the first year and differs little after that. Profits dip in the first year and then level.
:::

### Returns over five years

Figure 4 follows the median firm for {{months_5y}} months. Against the market the picture is grim. The median firing firm trails the market by {{bhar.forced.1y.median|abs}} after one year, {{bhar.forced.3y.median|abs}} after three and {{bhar.forced.5y.median|abs}} after five. The median fired-founder firm trails it by {{bhar.forced_founder.5y.median|abs}} after five years.

But the median retirement firm trails the market too, by {{bhar.retired.5y.median|abs}} after five years. Long-horizon returns are skewed, so the median stock in most groups lags an index. The fair comparison is with a similar firm.

![Figure 4. Against the market the long run looks grim; against a matched firm it does not](/static/reports/founder-ceo/figures/fig2_long_run.png)

*Figure 4. Against the market the long run looks grim; against a matched firm it does not.* Notes. Median buy-and-hold return minus the market, month 1 to month {{months_5y}} after the announcement, in months of {{trading_days_per_month}} trading days from day +2, all firings. Diamonds mark the median return against a matched firm at {{months_1y}}, {{months_3y}} and {{months_5y}} months; Table 7 gives their N at 36 months.

Table 7 makes that comparison. Against a matched firm, the median firing firm's return is {{mbhar.forced.1y.median}} after one year, which is {{mbhar.forced.1y.median|sig}}. After three and five years the medians are {{mbhar.forced.3y.median}} and {{mbhar.forced.5y.median}}, and neither is statistically significant.

The means tell a softer story still: {{mbhar.forced.1y.mean}}, {{mbhar.forced.3y.mean}} and {{mbhar.forced.5y.mean}} at one, three and five years, none significant. A few firing firms that recovered strongly pull the means above the medians. For fired founders the matched medians are {{mbhar.forced_founder.1y.median}}, {{mbhar.forced_founder.3y.median}} and {{mbhar.forced_founder.5y.median}}: similar firms with no recorded CEO change lost about as much as the founder firms did.

<!-- TABLE:7 -->

### Profits

Table 8 follows operating return on assets against the same matched firm. In the first fiscal year after a firing, the median change is {{roa.forced.abn_d_1.median}} percentage points below the matched firm's, which is {{roa.forced.abn_d_1.median|sig}}. The gap from retirements is {{roadiff.forced_vs_retired.abn_d_1.diff_median}}. By fiscal year +3 the firing firms' gap is {{roa.forced.abn_d_3.median}}.

Earlier work finds that operating performance falls before a CEO turnover and improves after it [@huson2004]. Here the recovery brings firing firms level with their matches within three years. Firing the CEO is followed by a short dip in profits, not by a lasting change.

<!-- TABLE:8 -->

## 5. Sold, bankrupt, or still standing

::: answer
**The question.** How many of these firms stop trading, and how?

**The answer.** A third within five years, twice the rate after a retirement. Takeovers are the commonest exit, but bankruptcy explains more of the gap with retirements.
:::

The clearest long-run difference is whether the firm survives as an independent listed company. Figure 5 shows the share of firms that have stopped trading, month by month, among firms with a complete five-year horizon. Table 9 gives the shares at one, three and five years.

![Figure 5. One in three is gone within five years](/static/reports/founder-ceo/figures/fig3_exits.png)

*Figure 5. One in three is gone within five years.* Notes. Cumulative share of firms no longer trading, by month after the announcement and by how they left, for firms with a complete {{months_5y}}-month horizon: (a) after a firing, (b) after a retirement.

After a firing, {{exit.forced.delisted_1y}} of firms stop trading within a year, {{exit.forced.delisted_3y}} within three years and {{exit.forced.delisted_5y}} within five. After a retirement the shares are {{exit.retired.delisted_1y}}, {{exit.retired.delisted_3y}} and {{exit.retired.delisted_5y}}.

Takeovers are the commonest way out: {{exit.forced.acquired_5y}} of firing firms are acquired within five years and {{exit.forced.bankruptcy_5y}} go bankrupt. After a retirement the figures are {{exit.retired.acquired_5y}} and {{exit.retired.bankruptcy_5y}}. The excess over retirements therefore comes more from bankruptcy than from takeovers.

Firing firms are smaller and weaker than retirement firms, so part of the gap could reflect who they are. Table IA.4 controls for size, profitability, year and industry. A firing still adds {{reg.exit5.gone.forced}} to the chance of leaving the market within five years. Of that, {{reg.exit5.bankrupt.forced}} is bankruptcy and {{reg.exit5.acquired.forced}} takeover.

Matched firms give the same answer. Within five years {{exit.ctrl_of_forced.delisted_5y}} of the matched firms stopped trading, against {{exit.paired_forced.delisted_5y}} of the same firing firms, a difference of {{exitdiff.forced_vs_ctrl.delisted_5y}} that is {{exitdiff.forced_vs_ctrl.delisted_5y|sig}}.

Bankruptcies come early: {{exit.forced.bankruptcy_1y}} of firing firms fail within a year. After a founder is fired, {{exit.forced_founder.delisted_5y}} of firms stop trading within five years, a difference from hired CEOs that is {{exitdiff.forced_founder_vs_forced_nonfounder.delisted_5y|sig}}. A board that fires its CEO is more likely to end with the firm sold or failed. That fits the view that board removal and takeover are two routes to a change of control [@morck1989].

<!-- TABLE:9 -->

## 6. Who stays on the board

::: answer
**The question.** What happens to the board after a firing?

**The answer.** Nearly half of the earlier directors are gone two years later, more than after a retirement. Fired CEOs, founders included, rarely stay on the board.
:::

Firing the CEO is followed by a wider clear-out. About two years after a firing, {{board.forced.director_turnover.mean}} of the directors who served before the departure have left, against {{board.retired.director_turnover.mean}} after a retirement. The difference is {{boarddiff.forced_vs_retired.director_turnover.diff_mean|sig}}.

Firing firms more often had separate chair and CEO roles before the departure, {{board.forced.split_before.mean}} against {{board.retired.split_before.mean}}. Two years later the shares are close, {{board.forced.split_after.mean}} and {{board.retired.split_after.mean}}. The rise comes after retirements, when a retiring CEO often hands over both roles.

Fired CEOs almost always leave the board too. A fired founder still sits on the board two years later at {{board.forced_founder.founder_stays.mean}} of firms, against {{board.forced_nonfounder.ceo_stays_director.mean}} for fired hired CEOs and {{board.retired.ceo_stays_director.mean}} for CEOs who retire.

Figure 6 plots these results next to the profit path of Section 4. They cover the {{g.events_with_board_data}} departures whose firms filed a proxy statement both before and about two years after the event. Firms sold or delisted in between are left out.

![Figure 6. Profits dip and recover; the board turns over](/static/reports/founder-ceo/figures/fig6_roa_board.png)

*Figure 6. Profits dip and recover; the board turns over.* Notes. (a) Median change in return on assets from fiscal year -1, minus the same change at the matched firm, in percentage points, for fiscal years 0 to +3. (b) The board about two years after the departure: the share of earlier directors gone, the share of firms with separate chair and CEO, and the share where the departing CEO is still a director, for firings (crimson) and retirements (slate); the diamond marks fired founders.

<!-- TABLE:10 -->

## 7. Conclusion

Boards rarely fire the people who built their companies, and when they do, the story told is about the founder. The data tell a different story, horizon by horizon.

The market sees the trouble weeks before the board acts. On the day it marks the firm down once. It marks it down more for fraud than for sex scandals, and perhaps more for a founder than for a hired CEO. After that the price stops moving.

The lasting difference is survival. A firm that fires its CEO is about twice as likely as a retirement firm to stop trading within five years. Bankruptcy explains more of that gap than takeover does. Its returns against similar firms differ little after the first year, and its profits recover.

For investors watching a board fire its CEO, three questions matter more than who built the company. Was the stock already falling? Did the CEO mislead investors about the numbers, or was the scandal personal? And how fragile is the firm? For boards, firing a founder may carry a larger penalty on the day, but none that lasts.

::: limits
**What these data cannot tell us.**

- The sample covers S&P {{index_size}} firms, so it says little about smaller companies, where founders often hold more control.
- Reasons other than financial misconduct, sexual conduct and relationships are model codes, checked by hand only where errors would matter most.
- The sex-scandal and founder groups are small, so those tests can detect only large gaps.
- Precise announcement dates exist for only part of the sample.
- The window catches the firing, not the first public report of the problem behind it.
- The comparisons describe what follows a firing. They cannot say what would have happened had the board kept the CEO.
:::

## Internet Appendix

Table IA.1 changes one thing at a time against the main tables. With the five-factor model plus momentum, the founder gap is {{rob.founder_vs_nonfounder_ff5.m1p1.diff_mean}} and the conduct gap {{rob.conduct_vs_performance_ff5.m1p1.diff_mean}}. Returns minus the market, with no estimated model, give {{rob.forced.ma_m1p1.mean}} in the announcement window. Using every firing, whatever its date source, gives {{rob.all_dates.forced.mm_m1p1.mean}}.

On the strict sample of {{a.n_forced_strict}} hand-dated firings that the evidence also reads as forced, the announcement return is {{car.forced_strict.mm_m1p1.mean}}, which is {{car.forced_strict.mm_m1p1.mean|sig}}. Fired founders there earn {{car.forced_strict_founder.mm_m1p1.mean}} against {{car.forced_strict_nonfounder.mm_m1p1.mean}} for hired CEOs. Within five years {{exit.forced_strict.delisted_5y}} of the strict sample stop trading.

Our coding finds {{rob.n_pushed_retirements}} hand-dated departures that the database records as retirements but that followed board pressure. Adding them to the firings gives {{rob.forced_plus_pushed.mm_m1p1.mean}}. Excluding 2008 and 2009 gives {{rob.forced_excl_crisis.mm_m1p1.mean}}, and dropping firings coded as leaving for a new job gives {{rob.forced_excl_newopp.mm_m1p1.mean}}.

The long-run results do not depend on how delisting returns are set. With every delisting return at zero, the median three-year return against the market is {{rob.bhar_dl0.forced.3y.median}}. Setting every delisting that is not a takeover to minus 100% gives {{rob.bhar_dlworst.forced.3y.median}}. Using only matches that meet the size rule, the median three-year matched return is {{rob.mbhar_strict_matches.3y.median}}.

For departures from 1992 to 1997, before daily prices for delisted firms exist, we use the five-year return graphs that firms print in their proxy statements. Of these departures, {{pre.events_with_tsr}} have a usable graph, including {{pre.n_forced}} firings. A firm must still file a proxy three years later, so only survivors enter this check.

The median three-year return against the firm's own reported index is {{pre.forced.abn_tsr_3y.median}} after firings and {{pre.retired.abn_tsr_3y.median}} after retirements. The difference of {{pre.forced_vs_retired.abn_tsr_3y.diff_median}} is {{pre.forced_vs_retired.abn_tsr_3y.diff_median|sig}}. Both groups trail their indexes, and the comparison between the groups points the same way as in the main sample.

<!-- TABLE:IA.1 -->

<!-- TABLE:IA.2 -->

<!-- TABLE:IA.3 -->

<!-- TABLE:IA.4 -->

## References
