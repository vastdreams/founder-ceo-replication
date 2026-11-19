# Sacked: Sex, Fraud, Founders, and the Fate of Firms That Fire Their CEO

## Abstract

When a US board fires its CEO, the market cares less about who goes than about why. Across {{a.n_forced|n}} forced exits at S&P {{index_size}} firms from {{sample_start_year}} to 2023, the stock slides {{drift.forced.pre_m30m2.mean|abs}} in the six weeks before the announcement and {{car.forced.mm_m1p1.mean|abs}} in the three days around it, then stops. Firings for fraud cost {{car.financial_misconduct.mm_m1p1.mean|abs}}; sex scandals cost {{car.sex_or_relationship.mm_m1p1.mean|abs}}. Firing a founder costs more than firing a hired CEO, but not significantly. Within {{months_5y}} months, {{exit.forced.delisted_5y}} of these firms stop trading, mostly through takeovers. Against matched peers, survivors trail by a few percent and profits recover.

## 1. Introduction

::: findings

1. The stock falls before the board acts: {{drift.forced.pre_m30m2.mean}} against the market over trading days -30 to -2 (Figure 2).
2. The firing itself costs {{car.forced.mm_m1p1.mean}} over days -1 to +1, and nothing more over the next three months (Table 3).
3. Fraud costs {{car.financial_misconduct.mm_m1p1.mean}}; sex and relationship scandals {{car.sex_or_relationship.mm_m1p1.mean}} (Table 5).
4. Fired founders: {{car.forced_founder.mm_m1p1.mean}}, against {{car.forced_nonfounder.mm_m1p1.mean}} for hired CEOs; the gap is {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|sig}} (Table 4).
5. Within {{months_5y}} months, {{exit.forced.delisted_5y}} of the firms are gone, against {{exit.retired.delisted_5y}} after a retirement (Figure 5).
:::

In 1985 Apple's board sided with its new chief executive against Steve Jobs, and Jobs left the company he had founded. Apple bought his next company, NeXT, and by 1997 he was back in charge. In November 2026 the board of Nvidia accepted the resignation of its founder and chief executive, Jensen Huang, days after opening an investigation into his conduct. The shares fell by more than 10% at the next open. Few corporate events are more dramatic than a board turning on the person who built the company. They are rare, and they raise a plain question for investors, directors and employees: what happens to a company after its board fires the boss, and does it matter who the boss was and why the board acted?

This paper answers that question for every forced CEO exit at an S&P {{index_size}} firm from {{sample_start_year}} to 2023, and it answers it horizon by horizon. A firing is not one event for the stock. It is a slide before the announcement, a jump on the day, and then months and years in which the firm is sold, fails, or carries on. Results that mix these horizons, or that do not say how many firms are still being measured at each one, can mislead. Table 1 therefore lays out the whole paper on one line per horizon: what is measured, for forced exits and for retirements, on how many forced exits, and with what confidence.

::: glance

### Table 1. The firing, horizon by horizon

| Horizon | What is measured | Forced exits | Retirements | N forced | p |
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

*Notes.* Day 0 is the first trading day on or after the announcement. A month is {{trading_days_per_month}} trading days counted from day +2, so {{months_1y}}, {{months_3y}} and {{months_5y}} months are {{days_1y}}, {{days_3y}} and {{days_5y}} trading days. N forced is the number of forced exits measured at that horizon; it falls with the horizon because recent departures have not yet reached it and because firms that are sold or fail stop filing. p tests the forced-exit number against zero, except for the share no longer trading and the directors gone, where it tests the difference from retirements. Sections 3 to 6 give the tests and the subgroups.

:::

The answers are sharper than the usual story about founders. First, the market sees trouble coming. Over trading days -30 to -2 the stocks of firms about to fire their CEO trail the market by {{drift.forced.pre_m30m2.mean|abs}} (p {{drift.forced.pre_m30m2.mean|p}}), while firms whose CEO is about to retire do not ({{drift.retired.pre_m30m2.mean}}). Second, the firing itself is news: the stock loses another {{car.forced.mm_m1p1.mean|abs}} over days -1 to +1 (t = {{car.forced.mm_m1p1.mean|t}}), and then nothing more happens. Over the next three months the forced-exit firms earn {{drift.forced.post_p2p60.mean}} against the market (p {{drift.forced.post_p2p60.mean|p}}). The price adjusts at once and stays adjusted.

Third, why the board acted matters more than who it fired. Firings for financial misconduct cost {{car.financial_misconduct.mm_m1p1.mean|abs}} over the three days. Firings after sexual misconduct or a relationship with an employee cost {{car.sex_or_relationship.mm_m1p1.mean|abs}}, a gap of {{cardiff.sex_or_relationship_vs_financial_misconduct.mm_m1p1.diff_mean}} that is {{cardiff.sex_or_relationship_vs_financial_misconduct.mm_m1p1.diff_mean|sig}} (p {{cardiff.sex_or_relationship_vs_financial_misconduct.mm_m1p1.diff_mean|p}}). Investors punish a CEO who misled them about the numbers; they barely move when a CEO is fired over a sex scandal or an affair with an employee. The founder, by contrast, matters less than the headlines suggest: fired founders cost {{car.forced_founder.mm_m1p1.mean|abs}} against {{car.forced_nonfounder.mm_m1p1.mean|abs}} for hired CEOs, and the gap is {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|sig}} (p {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|p}}).

Fourth, the lasting consequence is not a slow decline but a change of owner. Within {{months_5y}} months {{exit.forced.delisted_5y}} of forced-exit firms have stopped trading, against {{exit.retired.delisted_5y}} after retirements, and most were taken over ({{exit.forced.acquired_5y}}) rather than bankrupt ({{exit.forced.bankruptcy_5y}}). The firms that survive look much like their peers. Against the market, the median forced-exit firm loses {{bhar.forced.5y.median|abs}} over {{months_5y}} months, and the median fired-founder firm {{bhar.forced_founder.5y.median|abs}}. Against a matched firm in the same industry with similar size and profitability, the losses shrink to {{mbhar.forced.5y.median}} and {{mbhar.forced_founder.5y.median}}. The dramatic long-run numbers are about the kind of firm that fires its CEO, not about the firing.

The paper adds to three lines of work. Studies of forced turnover show that boards fire CEOs after poor performance relative to peers and that the market's reaction depends on what the removal reveals [@huson2004; @jenter2015; @kaplan2012; @taylor2010; @kind2011; @chen2026]. Studies of founder-CEOs show that founders shape investment and value, and that boards may wait longer before acting against them [@fahlenbrach2009; @adams2009; @wasserman2003; @jenter2023; @aran2024]. Studies of misconduct show that personal scandals and financial fraud both carry costs beyond the executive [@cline2018; @borellikjaer2021; @karpoff2008jfe; @karpoff2008jfqa]. We find no prior study that follows board-forced exits of founders and hired CEOs at US public firms from the weeks before the announcement to five years after it, splits them by the reason the board acted, and reports the number of firms measured at every horizon. We also add a direct comparison of sex scandals with fraud on the same sample, which earlier studies examine separately.

We test four hypotheses. H1: forced exits lower the stock price at the announcement. H2: removing a founder lowers it more than removing a hired CEO, because founders carry value a successor cannot replace; the alternative view holds that boards act against founders only when the case is overwhelming, so the removal ends entrenchment and should be good news [@wasserman2003; @bebchuk2017]. H3: firings for personal conduct cost more than firings for performance, because they arrive as surprises. H4: forced exits change what happens to the firm afterwards: its returns, its survival, its profitability and its board.

The rest of the paper runs as follows. Section 2 describes the data, the coding and how each horizon is measured. Section 3 reports how the market reacts before, at and after the announcement, by who was fired and why. Section 4 follows returns and profits over {{months_1y}}, {{months_3y}} and {{months_5y}} months. Section 5 asks which firms are sold, go bankrupt or survive. Section 6 examines who stays on the board. Section 7 concludes.

## 2. Data and sample

### CEO departures

The departures come from the open CEO dismissal database of @gentry2021, extended by its authors to 2023. It covers every CEO departure at S&P {{index_size}} firms and codes the reason from press coverage and filings. Codes 3 (dismissed for job performance) and 4 (dismissed for legal violations or personal conduct) are forced exits; code 5 (voluntary retirement) is the comparison group. The database treats a resignation under board pressure as a dismissal, and so do we: a CEO who resigns during an investigation, a scandal or an activist campaign counts as fired [@gow2017; @fee2018].

We link each departure to the firm's SEC Central Index Key from the filing links in the database and, for the rest, by an exact name match. Daily prices come through that key and include firms that were later delisted, which keeps failed and acquired firms in the sample [@shumway1997]. The main sample starts in {{sample_start_year}}, when daily prices for delisted firms become available, and runs to 2023. It holds {{a.events_with_returns}} departures with usable returns: {{a.n_forced}} forced exits and {{a.n_retired}} retirements. Figure 1 shows how the forced exits spread over time. They peak in the financial crisis and thin out in the last years, which the database covers for fewer months.

![Figure 1. Forced CEO exits per year](/static/reports/founder-ceo/figures/fig5_per_year.png)

*Figure 1. Forced CEO exits per year.* Notes. Forced exits by year, 1998 to 2023, by the database's dismissal type; the amber numbers count the founders among them. The bars count every forced exit in the database, including firms without usable prices; the last year covers part of 2023.

### Founders and reasons

For each departure we code whether the CEO founded or co-founded the firm or its direct predecessor, the board's main reason for acting, and, where the reason is a relationship with an employee, whether it was consensual, the employee's role, whether the firm cited a policy breach, and how the relationship came to light. A language model drafts each code, with a supporting quote, from the database's notes and sources, the 8-K the firm filed within {{evidence_window_days}} days of the announcement, press releases the database cites, the CEO's Wikipedia article and matching New York Times articles. We then check codes by hand where errors would matter most. Every founder code is checked against the firm's history: the model coded {{b.model_founder_codes}} forced exits as founder removals, and the review confirmed {{b.founders_confirmed}}, rejected {{b.founders_rejected}} (an error rate of {{b.model_error_rate}}) and added {{b.founders_added}} that the model left unclear. Most rejections were founders' children or long-serving CEOs who joined after the founding. Every sexual-misconduct and relationship code is also checked by hand against the public record. All results use the reviewed codes.

The database's own codes are not always right either. Some departures it codes as forced read, in the filings and the press, as planned successions; the coding was sometimes revised after later events. We therefore also report every main result on a strict sample: the {{a.n_forced_strict}} forced exits that the evidence-based coding also reads as forced. The named cases in Table 6 come only from this strict sample.

### How we measure time

Every number in the paper has a horizon, and every table and figure states it. Day 0 is the first trading day on or after the announcement. The announcement return covers trading days -1 to +1 and uses the market model, estimated over days {{estimation_window_start}} to {{estimation_window_end}} with at least {{min_estimation_days}} days of returns. We test its mean with the cross-sectional t and with the standardized test of @boehmer1991, which allows for event-induced variance, and its median with the Wilcoxon signed-rank test [@kothari2007]. A five-factor model with momentum gives the same results [@famafrench2015].

The windows before and after the announcement, days -30 to -2 and days +2 to +60, use returns minus the market, without an estimated alpha. A firm that is about to fire its CEO has usually done badly in the year before, so its market-model alpha is strongly negative; projecting that alpha forward would manufacture a rebound that is not in the prices. Over the three days around the announcement the choice hardly matters (Table IA.1).

The long run is measured in months of {{trading_days_per_month}} trading days, starting on day +2: {{months_1y}}, {{months_3y}} and {{months_5y}} months are {{days_1y}}, {{days_3y}} and {{days_5y}} trading days. Buy-and-hold returns are measured against the market and against a matched control firm in the same Fama-French industry, with market value within {{matching_rule_pct}} percent of the event firm, the closest operating return on assets in the year before, and no CEO turnover of its own within three years [@barber1996]. A firm that stops trading inside the window keeps its last price, followed by a final return of zero for a takeover, minus 100% for a bankruptcy and minus 30% for other delistings [@shumway1997]. Long-horizon returns are skewed, so we report medians, test them with the Wilcoxon test, and add a skewness-adjusted t with a bootstrap interval for the mean [@kothari2007]. Operating performance is EBITDA over total assets from as-reported annual statements, winsorized at the 1st and {{winsor_upper_pct}}th percentiles, measured as the change from fiscal year -1 against the same control. Board composition comes from the last proxy statement before the departure and the first one filed at least {{board_post_lag_days}} days after it, about two years later.

The number of forced exits measured falls with the horizon, and the tables say by how much. All {{car.forced.mm_m1p1.mean|n}} forced exits with returns enter the three-day test. At {{months_5y}} months, {{exit.forced.delisted_5y|n}} have a complete horizon. Profitability in fiscal year +3 is measured for {{roa.forced.abn_d_3.median|n}}, because firms that are sold or fail stop filing, and the board two years later for {{board.forced.director_turnover.mean|n}}.

### Who gets fired

Table 2 shows the firms before the departure. Firms that fire their CEO are about half the size of firms whose CEO retires (median market value {{desc.forced.mcap.median}} against {{desc.retired.mcap.median}} billion dollars) and markedly less profitable (median return on assets {{desc.forced.roa.median}} against {{desc.retired.roa.median}}, p {{descdiff.forced_vs_retired.roa.diff_median|p}}). Their sales grow more slowly ({{desc.forced.salesg.median}} against {{desc.retired.salesg.median}}). Boards fire CEOs of firms that are already struggling [@huson2004; @jenter2015], which is why every long-run comparison in this paper is made against a matched firm as well as against the market.

<!-- TABLE:2 -->

## 3. The market's verdict

### Before, at and after the announcement

Figure 2 shows the whole event from six weeks before the announcement to three months after it. For firms whose CEO retires, the line is flat. For firms that fire their CEO, it slides for weeks, drops on the announcement, and then goes sideways. Table 3 gives the numbers. Over days -30 to -2 forced-exit firms trail the market by {{drift.forced.pre_m30m2.mean|abs}} (p {{drift.forced.pre_m30m2.mean|p}}). Over days -1 to +1 they lose another {{car.forced.mm_m1p1.mean|abs}} on average and {{car.forced.mm_m1p1.median|abs}} at the median, while retirements earn {{car.retired.mm_m1p1.mean}}. The difference of {{cardiff.forced_vs_retired.mm_m1p1.diff_mean}} is {{cardiff.forced_vs_retired.mm_m1p1.diff_mean|sig}} (p {{cardiff.forced_vs_retired.mm_m1p1.diff_mean|p}}), and the standardized test agrees (t = {{car.forced.mm_m1p1.bmp_t}}). The five-factor model gives {{car.forced.ff5_m1p1.mean}}, and the window from day -5 to day +5 gives {{car.forced.mm_m5p5.mean}}. Over days +2 to +60 the forced-exit firms earn {{drift.forced.post_p2p60.mean}} against the market (p {{drift.forced.post_p2p60.mean|p}}): no rebound and no further slide. H1 holds, and the market's verdict is final within days.

![Figure 2. Prices slide before the firing, drop on the news, then stop](/static/reports/founder-ceo/figures/fig1_event_time.png)

*Figure 2. Prices slide before the firing, drop on the news, then stop.* Notes. Mean cumulative return minus the market from trading day -30 to day +60 around the announcement (day 0), with {{ci_level}}% confidence bands in panel (a). Panel (b) splits forced exits by founder status and by the database's dismissal type. N is the number of departures with every day of the window.

<!-- TABLE:3 -->

The slide before the announcement differs by reason. Firms that fire their CEO for performance trail the market by {{drift.performance.pre_m30m2.mean|abs}} over days -30 to -2; firms that fire for conduct trail it by {{drift.conduct.pre_m30m2.mean|abs}} (difference p {{driftdiff.conduct_vs_performance.pre_m30m2.diff_mean|p}}). On the announcement the order reverses: conduct firings cost {{car.conduct.mm_m1p1.mean|abs}} and performance firings {{car.performance.mm_m1p1.mean|abs}}, a gap that is {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean|sig}} (p {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean|p}}). A performance firing confirms what the price already showed; a conduct firing is news [@cline2018; @huson2004]. H3 holds.

### Founders

Table 4 reports the announcement return for each group. Fired founders cost {{car.forced_founder.mm_m1p1.mean|abs}} over days -1 to +1 (p {{car.forced_founder.mm_m1p1.mean|p}}), against {{car.forced_nonfounder.mm_m1p1.mean|abs}} for hired CEOs. The difference of {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean}} is {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|sig}} (p {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|p}}). In a regression on all departures with event-year effects and standard errors clustered by year, the founder interaction is {{reg.car_m1p1.forced_x_founder}} (p {{reg.car_m1p1.forced_x_founder|p}}). Founder firms also slide further before the announcement ({{drift.forced_founder.pre_m30m2.mean}} over days -30 to -2). With {{a.n_forced_founder}} fired founders the test has limited power, and the point estimate leans towards H2. What the data rule out is the entrenchment view in its strong form: the market does not greet the removal of a founder as good news.

<!-- TABLE:4 -->

### Sex, fraud and the rest

Table 5 and Figure 3 split the forced exits by the reason the board acted. Firings that follow money and the law are the expensive ones: financial misconduct costs {{car.reason.financial_misconduct.mm_m1p1.mean|abs}} over days -1 to +1 (p {{car.reason.financial_misconduct.mm_m1p1.mean|p}}) and legal or regulatory trouble {{car.reason.legal_or_regulatory.mm_m1p1.mean|abs}} (p {{car.reason.legal_or_regulatory.mm_m1p1.mean|p}}), in line with the large costs of misreporting found by @karpoff2008jfqa. Firings for a relationship with an employee cost {{car.relationship.mm_m1p1.mean|abs}} (p {{car.relationship.mm_m1p1.mean|p}}). They include the well-known cases at Intel, Boeing, McDonald's and Priceline, where the company said the CEO had broken its policy on relationships with employees; we checked each of these labels by hand. Taking sexual misconduct and relationships together, the {{car.sex_or_relationship.mm_m1p1.mean|n}} cases cost {{car.sex_or_relationship.mm_m1p1.mean|abs}}, against {{car.financial_misconduct.mm_m1p1.mean|abs}} for the {{car.financial_misconduct.mm_m1p1.mean|n}} fraud cases; the difference of {{cardiff.sex_or_relationship_vs_financial_misconduct.mm_m1p1.diff_mean}} is {{cardiff.sex_or_relationship_vs_financial_misconduct.mm_m1p1.diff_mean|sig}} (p {{cardiff.sex_or_relationship_vs_financial_misconduct.mm_m1p1.diff_mean|p}}), and the difference in medians has p {{cardiff.sex_or_relationship_vs_financial_misconduct.mm_m1p1.diff_median|p}}. A fraud tells investors the numbers they relied on were wrong. A sex scandal tells them about the CEO, and the firing removes the CEO. The sex-scandal group is small, so the comparison is suggestive rather than settled, and it fits evidence that the market's reaction to sexual-misconduct news depends on what it reveals about the firm [@borellikjaer2021; @mooibroek2021].

<!-- TABLE:5 -->

![Figure 3. Fraud is expensive; sex scandals are not, at least on the day](/static/reports/founder-ceo/figures/fig4_reasons.png)

*Figure 3. Fraud is expensive; sex scandals are not, at least on the day.* Notes. Mean abnormal return over trading days -1 to +1 by the coded reason the board acted, with {{ci_level}}% intervals; reasons with at least {{min_reason_cases}} forced exits. Crimson: money and legal cases; violet: personal conduct, including relationships with employees; grey: other reasons.

### The largest founders fired

Table 6 lists the largest firms whose founder was fired, among the exits the evidence also reads as forced. They show how wide the range is. WorldCom lost {{case.49.car_m1p1|abs}} in the three days around Bernard Ebbers's exit in 2002 and was bankrupt within months. Yahoo gained {{case.7398.car_m1p1}} when Jerry Yang stepped aside in 2008. Wynn Resorts rose {{case.8761.car_m1p1}} when Steve Wynn left amid allegations of sexual misconduct in 2018, and WWE {{case.8370.car_m1p1}} when Vince McMahon left in 2022 during an investigation of his conduct. For these firms the market read the founder's exit as removing a problem, not a source of value. Over {{months_3y}} months most of them still trailed the market, which is the pattern of Section 4.

<!-- TABLE:6 -->

## 4. After the dust settles: long-run returns and profits

### Returns over {{months_1y}}, {{months_3y}} and {{months_5y}} months

Figure 4 follows the median firm for {{months_5y}} months. Against the market the picture is grim. The median forced-exit firm trails the market by {{bhar.forced.1y.median|abs}} after {{months_1y}} months, {{bhar.forced.3y.median|abs}} after {{months_3y}} and {{bhar.forced.5y.median|abs}} after {{months_5y}}; the median fired-founder firm trails it by {{bhar.forced_founder.5y.median|abs}} after {{months_5y}} months. But the median retirement firm also trails the market, by {{bhar.retired.5y.median|abs}} after {{months_5y}} months, because the median stock underperforms an index that a few large winners drive. The fair comparison is with a similar firm.

![Figure 4. Against the market the long run looks grim; against a matched firm it does not](/static/reports/founder-ceo/figures/fig2_long_run.png)

*Figure 4. Against the market the long run looks grim; against a matched firm it does not.* Notes. Median buy-and-hold return minus the market, month 1 to month {{months_5y}} after the announcement, months of {{trading_days_per_month}} trading days from day +2. Diamonds mark the median return against a matched firm at {{months_1y}}, {{months_3y}} and {{months_5y}} months. The labels under the curves give the number of forced exits measured at each horizon.

Table 7 makes that comparison. Against a matched firm in the same industry with similar size and profitability, the median forced-exit firm's return is {{mbhar.forced.1y.median}} after {{months_1y}} months (p {{mbhar.forced.1y.median|p}}), {{mbhar.forced.3y.median}} after {{months_3y}} months (p {{mbhar.forced.3y.median|p}}) and {{mbhar.forced.5y.median}} after {{months_5y}} months (p {{mbhar.forced.5y.median|p}}). The skewness-adjusted t for the {{months_3y}}-month mean is {{mbhar.forced.3y.skewadj_t}}. The difference from retirements at {{months_3y}} months is {{mbhardiff.forced_vs_retired.3y.diff_median}} (p {{mbhardiff.forced_vs_retired.3y.diff_median|p}}). For fired founders the matched returns are {{mbhar.forced_founder.1y.median}}, {{mbhar.forced_founder.3y.median}} and {{mbhar.forced_founder.5y.median}}: the founder firms' collapse against the market belongs to their peers too. Founder firms do not differ from other forced-exit firms against matched firms ({{mbhardiff.forced_founder_vs_forced_nonfounder.3y.diff_median}} at {{months_3y}} months, p {{mbhardiff.forced_founder_vs_forced_nonfounder.3y.diff_median|p}}). Against similar firms, then, firing the CEO is followed by modest and uneven underperformance, {{mbhar.forced.1y.median!sig}} at {{months_1y}} months, {{mbhar.forced.3y.median!sig}} at {{months_3y}} and {{mbhar.forced.5y.median!sig}} at {{months_5y}}: a fraction of what the market comparison suggests, and none at all for founders.

<!-- TABLE:7 -->

### Profits

Table 8 follows operating return on assets against the same matched firm. Profitability dips in the first fiscal year after a forced exit (median {{roa.forced.abn_d_1.median}} percentage points, p {{roa.forced.abn_d_1.median|p}}, {{roa.forced.abn_d_1.median|sig}}) and is level by year +3 ({{roa.forced.abn_d_3.median}}, p {{roa.forced.abn_d_3.median|p}}). The dip is larger in the fiscal year of the departure, when write-offs and severance often land. A firing is followed at most by a short dip in profits, not by a lasting change in how profitable the firm is [@huson2004].

<!-- TABLE:8 -->

## 5. Sold, bankrupt, or still standing

The clearest long-run difference is whether the firm survives as an independent listed company. Figure 5 shows the share of firms that have stopped trading, month by month, on the firms with a complete {{months_5y}}-month horizon. Table 9 gives the numbers at {{months_1y}}, {{months_3y}} and {{months_5y}} months. After a forced exit, {{exit.forced.delisted_1y}} of firms have stopped trading within {{months_1y}} months, {{exit.forced.delisted_3y}} within {{months_3y}} and {{exit.forced.delisted_5y}} within {{months_5y}}. After a retirement the shares are {{exit.retired.delisted_1y}}, {{exit.retired.delisted_3y}} and {{exit.retired.delisted_5y}}. The {{months_5y}}-month difference of {{exitdiff.forced_vs_retired.delisted_5y}} has p {{exitdiff.forced_vs_retired.delisted_5y|p}}.

![Figure 5. One in three is gone within five years, mostly sold](/static/reports/founder-ceo/figures/fig3_exits.png)

*Figure 5. One in three is gone within five years, mostly sold.* Notes. Cumulative share of firms no longer trading, by month after the announcement and by how they left, for firms with a complete {{months_5y}}-month horizon: (a) after a forced exit, (b) after a retirement.

Most of the exits are takeovers: {{exit.forced.acquired_5y}} of forced-exit firms are acquired within {{months_5y}} months and {{exit.forced.bankruptcy_5y}} go bankrupt, against {{exit.retired.acquired_5y}} and {{exit.retired.bankruptcy_5y}} after a retirement. Bankruptcies come early: {{exit.forced.bankruptcy_1y}} of forced-exit firms fail within {{months_1y}} months, while acquisitions build up steadily. After a founder is fired, {{exit.forced_founder.delisted_5y}} stop trading within {{months_5y}} months (difference from hired CEOs p {{exitdiff.forced_founder_vs_forced_nonfounder.delisted_5y|p}}). After a fraud, {{exit.financial_misconduct.delisted_5y}} do; after a sex or relationship scandal, {{exit.sex_or_relationship.delisted_5y}}, on only {{exit.sex_or_relationship.n5}} firms. Sex scandals cost little on the day, but these firms do not last longer than the others. A board that fires its CEO is far more likely to end up selling the firm, which fits the view that board removal and takeover are two routes to the same change of control [@morck1989].

<!-- TABLE:9 -->

## 6. Who stays on the board

Firing the CEO is followed by a wider clear-out. About two years after a forced exit, {{board.forced.director_turnover.mean}} of the directors who served before the departure have left the board, against {{board.retired.director_turnover.mean}} after a retirement (p {{boarddiff.forced_vs_retired.director_turnover.diff_mean|p}}). The roles of chair and chief executive are held by different people at {{board.forced.split_after.mean}} of firms after a forced exit and at {{board.retired.split_after.mean}} after a retirement, so a firing does not by itself lead boards to split the roles. Fired CEOs almost always leave the board too. A fired founder still sits on the board two years later at {{board.forced_founder.founder_stays.mean}} of firms, against {{board.forced_nonfounder.ceo_stays_director.mean}} for fired hired CEOs and {{board.retired.ceo_stays_director.mean}} for CEOs who retire. Figure 6 plots the board results next to the profit path of Section 4. These figures cover the {{g.events_with_board_data}} departures whose firms filed a proxy statement both before and about two years after the event, so they leave out firms that were sold or delisted in between.

![Figure 6. Profits dip and recover; the board turns over](/static/reports/founder-ceo/figures/fig6_roa_board.png)

*Figure 6. Profits dip and recover; the board turns over.* Notes. (a) Median change in return on assets from fiscal year -1, minus the same change at the matched firm, in percentage points, for fiscal years 0 to +3. (b) The board about two years after the departure: the share of earlier directors gone, the share of firms with separate chair and CEO, and the share where the departing CEO is still a director, for forced exits (crimson) and retirements (slate); the diamond marks fired founders.

<!-- TABLE:10 -->

## 7. Conclusion

Boards rarely fire the people who built their companies, and when they do the story usually told is about the founder. The data tell a different story, and they tell it horizon by horizon. The market sees the trouble weeks before the board acts. On the day, it marks the firm down once, by more when the reason is fraud than when it is sex, and by about as much for a founder as for a hired CEO. After that the price stops moving. Over the following {{months_5y}} months the firm's returns end up within a few percent of similar firms' and its profits level with theirs, but the firm is twice as likely to disappear, usually into another company.

For investors watching a board fire its CEO, including the board of Nvidia, three questions matter more than whether the person leaving built the company. Was the stock already falling? Did the CEO lie about the numbers, or about something else? And who might buy the firm? For boards, the evidence suggests that firing a founder carries no special long-run penalty, and that the market judges a firing by the reason the board gives and the evidence behind it.

The study has limits. It covers S&P {{index_size}} firms, so it says little about smaller companies where founders hold more control. The reasons other than sexual conduct and relationships are model codes, checked by hand only where errors would matter most. The sex-scandal group is small. And the comparisons describe what follows a firing; they do not show what would have happened had the board kept the CEO.

## Internet Appendix

Table IA.1 changes one thing at a time against the main tables. With the five-factor model plus momentum, the founder gap is {{rob.founder_vs_nonfounder_ff5.m1p1.diff_mean}} (p {{rob.founder_vs_nonfounder_ff5.m1p1.diff_mean|p}}) and the conduct gap {{rob.conduct_vs_performance_ff5.m1p1.diff_mean}} (p {{rob.conduct_vs_performance_ff5.m1p1.diff_mean|p}}), so the founder gap stays {{rob.founder_vs_nonfounder_ff5.m1p1.diff_mean|sig}} and the conduct gap stays {{rob.conduct_vs_performance_ff5.m1p1.diff_mean|sig}}. Returns minus the market, without an estimated model, give {{rob.forced.ma_m1p1.mean}} over days -1 to +1. On the strict sample of {{a.n_forced_strict}} exits that the evidence also reads as forced, the return is {{car.forced_strict.mm_m1p1.mean}}; fired founders earn {{car.forced_strict_founder.mm_m1p1.mean}} against {{car.forced_strict_nonfounder.mm_m1p1.mean}} for hired CEOs, a gap that is {{cardiff.forced_strict_founder_vs_forced_strict_nonfounder.mm_m1p1.diff_mean|sig}} (p {{cardiff.forced_strict_founder_vs_forced_strict_nonfounder.mm_m1p1.diff_mean|p}}), and {{exit.forced_strict.delisted_5y}} of the strict sample stop trading within {{months_5y}} months.

The evidence-based coding identifies {{rob.n_pushed_retirements}} departures that the database records as retirements but that followed board pressure. They earn {{rob.pushed.mm_m1p1.mean}}, and adding them to the forced exits gives {{rob.forced_plus_pushed.mm_m1p1.mean}}. Excluding the crisis years 2008 and 2009 gives a forced-exit return of {{rob.forced_excl_crisis.mm_m1p1.mean}}. Using only matches that meet the size rule, the median {{months_3y}}-month matched return is {{rob.mbhar_strict_matches.3y.median}}.

For departures from 1992 to 1997, before daily prices for delisted firms are available, we use the five-year return graphs that firms print in their proxy statements. For the {{pre.events_with_tsr}} departures with a usable graph, including {{pre.n_forced}} forced exits, the median three-year return against the firm's own reported index is {{pre.forced.abn_tsr_3y.median}} after forced exits and {{pre.retired.abn_tsr_3y.median}} after retirements, a difference of {{pre.forced_vs_retired.abn_tsr_3y.diff_median}} (p {{pre.forced_vs_retired.abn_tsr_3y.diff_median|p}}). Both groups trail the index because large firms drove the market in those years; the comparison between the groups points the same way as in the main sample.

<!-- TABLE:IA.1 -->

## Data and code

All statistics are produced by code from the public CEO dismissal database, SEC filings and licensed daily price and fundamentals data. The replication package at <{{replication_repo_url}}> holds the code, the event-level results, the hand reviews of founder and conduct codes, the figure code, and a data dictionary that names every input, its source, and an equivalent source a reader can use instead. A reader with the event-level files rebuilds every statistic and figure in the paper with one command; a reader who licenses the price and fundamentals data, or uses an equivalent, rebuilds the event-level files too. Licensed prices are not redistributed.

## Use of AI tools

A large language model was used to read SEC filings, proxy statements, press releases and news coverage and to draft codes for founder status, departure reasons and board composition, each with a quoted source passage. Founder codes and every sexual-conduct and relationship code were checked by hand. No statistic was produced by the model; every number comes from the analysis code.

## References
