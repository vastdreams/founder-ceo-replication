# Sacked: Sex, Fraud, Founders, and the Fate of Firms That Fire Their CEO

## Abstract

When a US board fires its CEO, the market has usually seen the trouble coming. At S&P 1500 firms the stock slides 5.1% in the six weeks before the announcement, drops 2.7% in the three days around it, then stops. Firings over fraud cost 6.1%; firings over sex scandals barely move the price. Fired founders may cost more than hired CEOs, but the evidence is weak. Within five years a third of firing firms stop trading, twice the rate after retirements, with bankruptcy the larger part of the gap. Against similar firms, returns differ little after the first year.

## 1. Introduction

::: findings

1. The stock falls before the board acts: -5.1% against the market over the six weeks before (Figure 2).

2. The firing itself costs -2.7% over the three days around the announcement, and the next three months add no significant move (Table 3).

3. Fraud costs -6.1%; sex and relationship scandals 0.7% (Table IA.1).

4. Fired founders cost -5.4%, against -2.5% for hired CEOs, a gap that is not statistically significant (Table 4).

5. Within five years 32.1% of firing firms have stopped trading, against 16.8% after a retirement (Figure 5).

:::

In 1985 Apple's board sided with its new chief executive against Steve Jobs, and Jobs left the company he had founded. By 1997 Apple had bought his next company and he was back in charge. In November 2026 Nvidia's board accepted the resignation of its co-founder and chief executive, Jensen Huang [@nvidia2026form8k]. Three days earlier the board had opened an independent investigation after reports that Huang had been the target of a foreign intelligence effort [@nvidia2026board]. News reports also described an affair [@cnbc2026nvidia]. The board gave no reason for the departure.

Nvidia's shares closed 4.3% lower on the day the resignation was announced, after falling as much as 14% during the session [@cnbc2026nvidia]. From the last close before the board's statement, they had lost 19.1% by 18 November. Few corporate events are more dramatic than a board turning on the person who built the company. They raise a plain question for investors, directors and employees. What happens to a company after its board fires the boss, and does it matter who the boss was and why the board acted?

This paper answers that question for firings at S&P 1500 firms over a quarter of a century. It answers it horizon by horizon, because a firing is not one event for the stock. There is a slide before the announcement, a drop on the day, and then months and years in which the firm is sold, fails or carries on. Results that mix these horizons, or that hide how many firms are still measured at each, can mislead. Table 1 therefore sets out the paper one horizon per row, with the number of firings measured at each.

::: glance

### Table 1. The firing, horizon by horizon: S&P 1500 firms, 1998 to 2023

| Horizon | What is measured | Firings | Retirements | N firings | p |
|---|---|---|---|---|---|
| Trading days -30 to -2 | Return minus the market | -5.1% | -0.0% | 527 | <0.001 |
| Trading days -1 to +1 | Abnormal return, market model | -2.7% | -0.3% | 524 | <0.001 |
| Trading days +2 to +60 | Return minus the market | -0.3% | -0.8% | 516 | 0.847 |
| 12 months | Return minus a matched firm, median | -4.3% | -0.0% | 1,321 | 0.020 |
| 36 months | Return minus a matched firm, median | -1.6% | 0.5% | 1,318 | 0.470 |
| 60 months | Return minus a matched firm, median | -5.2% | 2.8% | 1,264 | 0.134 |
| Within 60 months | Share no longer trading | 32.1% | 16.8% | 1,335 | <0.001 |
| Fiscal year +1 | Change in ROA minus the matched firm, median (pp) | -0.4 | 0.2 | 1,048 | 0.028 |
| Fiscal year +3 | Change in ROA minus the matched firm, median (pp) | 0.3 | 0.2 | 819 | 0.444 |
| About two years | Share of the earlier directors gone | 48.4% | 37.8% | 611 | <0.001 |

*Notes.* Day 0 is the first trading day on or after the announcement. The first three rows use firings whose announcement date comes from the database, a hand check or the firm's 8-K; the other rows use every firing. A month is 21 trading days counted from day +2. N firings falls with the horizon because recent firings have not reached it and firms that are sold or fail stop filing. The p column tests the firing number against zero; for the share no longer trading and the directors gone, it tests the difference from retirements.

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

The departures come from the open CEO dismissal database of @gentry2021, extended by its authors to 2023. It codes the reason for every CEO departure at S&P 1500 firms from press coverage and filings. An independent recoding agreed with it on 87% of events [@gentry2021]. Codes 3 and 4 (dismissed for job performance, and for legal violations or personal conduct) are firings. Code 5 (voluntary retirement) is the comparison group.

Press releases rarely say that a CEO was fired [@gow2017], and how forced exits are classified changes the results [@fee2018]. Like the database, we treat a resignation under board pressure as a firing. A CEO who resigns during an investigation, a scandal or an activist campaign counts as fired.

We link each departure to the firm's SEC Central Index Key, and through it to daily prices that include firms later delisted. Failed and acquired firms therefore stay in the sample. Daily prices for delisted firms begin in 1998. Table IA.2 traces the firings from the database to the analysis samples. Figure 1 shows how they spread over time.

![Figure 1. Forced CEO exits per year](/static/reports/founder-ceo/figures/fig5_per_year.png)

*Figure 1. Forced CEO exits per year.* Notes. Firings by year, 1998 to 2023, by the database's dismissal type; the amber numbers count the founders among them. The bars count every firing in the database, including firms without usable prices; the last year covers part of 2023.

### Dating the announcement

A three-day window needs the right day. The database gives an announcement date for about a third of departures. For the rest it gives only the day the CEO left office, which can come weeks after the news. We therefore look for the firm's own 8-K filing on the departure. It must be filed between 90 days before and 15 days after the CEO left, and from August 2004 it must be filed under the item for officer departures. It must name the CEO with a chief-executive title and a word such as resign, retire or terminate, and not describe an appointment. The 8-K's date of the earliest event reported is then the announcement date.

On departures the database does date, the 8-K date falls within 3 days of it in 58% of cases and within 10 days in 73%. Hand checks corrected a few further dates.

The 8-K dates are useful but noisy. Firings dated by the database earn -2.7% over three days; firings dated by an 8-K earn only -0.6%, as a misplaced day 0 would produce. Announcement-window results therefore use the 527 firings dated by the database or a hand check.

The other 866 firings earn -0.8%, which is not statistically significant (Table IA.1). Long-run results use all 1,393 firings with returns, since a few days of error cannot move a return measured over years.

### Founders and reasons

For each departure we code whether the CEO founded or co-founded the firm or its direct predecessor, and the board's main reason for acting.

A language model (DeepSeek, deepseek-chat, at temperature zero) drafts each code with a supporting quote. It reads the database's notes and sources and the 8-K the firm filed within 10 days of the departure. It also reads cited press releases, the CEO's Wikipedia article and matching New York Times articles. The prompt is in the replication package.

We then check by hand the codes where errors would matter most. Every founder code on a firing is checked against the firm's history: the model coded 191 firings as founder removals, and the review confirmed 148, rejected 43 and added 2. Every financial-misconduct, sexual-misconduct and relationship code is also checked. About a third of the model's financial-misconduct codes did not survive, usually because the misconduct came out only after the CEO had left.

The database's own codes are not always right either. Some departures it codes as forced read as planned successions in the filings and the press. We therefore repeat the main results on a strict sample: the 193 hand-dated firings that our evidence-based coding also reads as forced (Table IA.1). The named cases in Table 6 come only from this strict sample.

### How we measure returns

The announcement return is the abnormal return over three trading days, from the day before the announcement to the day after it. It uses the market model of equation (1):

$$AR_{it} = R_{it} - \hat\alpha_i - \hat\beta_i R_{mt}, \qquad CAR_i = AR_{i,-1} + AR_{i,0} + AR_{i,+1}. \tag{1}$$

Here $R_{it}$ is the stock's total return and $R_{mt}$ the market's. The coefficients come from trading days -250 to -30 before the announcement, with at least 120 days of returns. We test the mean with the cross-sectional t and with the standardized test of @boehmer1991, which allows for event-induced variance. We test the median with the Wilcoxon signed-rank test [@kothari2007]. A five-factor model with momentum gives the same answers [@famafrench2015].

For the six weeks before the announcement (trading days -30 to -2) and the three months after it (+2 to +60), we use returns minus the market. These carry no estimated alpha. A firm about to fire its CEO has usually done badly in the year before, so its estimated alpha is strongly negative. Projected forward, that alpha would manufacture a rebound that is not in the prices.

The long run is measured in months of 21 trading days, counted from day +2. We compare each firm's buy-and-hold return with that of a benchmark, as in equation (2):

$$BHAR_i(h) = \prod_{t=2}^{T_h}(1+R_{it}) - \prod_{t=2}^{T_h}(1+R_{bt}). \tag{2}$$

Here $T_h$ is 252, 756 or 1260 trading days, and the benchmark $b$ is either the market or a matched firm. A horizon counts only if it ends inside the data for every firm, so recent firings never enter because they happened to delist. The matched firm is in the same Fama-French industry, with market value within 30 percent and the nearest operating return on assets in the year before. It had no CEO turnover recorded in the database in the three years up to the event. When no firm meets the size band, the nearest firm in size is used (210 matches; Table IA.1 drops them).

A firm that stops trading inside the window takes a final return of zero for a takeover, minus 100% for a bankruptcy and minus 30% for other delistings [@shumway1997]. The proceeds are then held in the market until the horizon ends. Long-horizon returns are skewed, so we report medians with the Wilcoxon test and means with t-tests, adding the skewness-adjusted t of @lyon1999 for the three-year matched mean.

Operating performance is EBITDA over total assets from as-reported annual statements, winsorized at the 1st and 99th percentiles. We measure its change from fiscal year -1 against the matched firm, which @barber1996 show is needed when firms performed unusually before the event. Board composition comes from the last proxy statement before the departure and the first one filed at least 600 days after it.

### Who gets fired

Table 2 shows the firms before the departure. Firms that fire their CEO are about half the size of firms whose CEO retires: a median market value of 1.0 against 1.9 billion dollars. They are also less profitable, with a median return on assets of 7.9% against 12.3%, and their sales grow more slowly.

Boards fire CEOs of firms that are already struggling [@huson2004; @jenter2015]. That is why every long-run comparison in this paper is made against a matched firm as well as against the market.

### Table 2. Who gets fired: the firm in the year before the departure

| Fiscal year -1, medians | Forced exits | Retirements | Founders fired | p, forced vs retired | N forced |
|---|---|---|---|---|---|
| Market value, USD billion | 1.0 | 1.9 | 0.8 | <0.001 | 1,347 |
| Return on assets (EBITDA / assets) | 7.9% | 12.3% | 7.7% | <0.001 | 1,347 |
| Sales growth | 3.2% | 6.7% | 8.4% | <0.001 | 1,318 |
| Capital spending / assets | 3.2% | 3.5% | 4.3% | <0.001 | 1,347 |

*Notes.* Medians in the fiscal year before the departure, from as-reported annual statements; market value at that fiscal year-end. p is from a Mann-Whitney U test of forced exits against retirements. N forced is the number of forced exits with the item.


## 3. The market's verdict

::: answer
**The question.** How does the stock react when a board fires its CEO, and does it matter who was fired and why?

**The answer.** The stock falls before the board acts, falls again on the news, and then stops. Fraud is costly on the day; sex scandals are not. Fired founders cost more in point estimate, though not significantly.
:::

### Before, at and after the announcement

Figure 2 follows the stock from six weeks before the announcement to three months after it. For firms whose CEO retires, the line is flat. For firms that fire their CEO, it slides for weeks, drops on the announcement and then moves sideways.

![Figure 2. Prices slide before the firing, drop on the news, then stop](/static/reports/founder-ceo/figures/fig1_event_time.png)

*Figure 2. Prices slide before the firing, drop on the news, then stop.* Notes. Mean cumulative return minus the market from trading day -30 to day +60 around the announcement (day 0), departures dated by the database or a hand check, with 95% confidence bands. Panel (b) splits firings by founder status and by the database's dismissal type. N is the number of departures with every day of the window.

Table 3 gives the numbers. Over the six weeks before, firing firms trail the market by 5.1%, while retirement firms do not move (-0.0%). In the announcement window firing firms lose another 2.7% (t = -5.99), and retirement firms earn -0.3%.

The difference of -2.4 percentage points is statistically significant. The standardized test of the firing mean gives t = -6.164, the five-factor model -2.7% and the eleven-day window -2.9%. Over the three months after, firing firms earn -0.3% against the market, which is not statistically significant. H1 holds.

### Table 3. Before, at and after the announcement

| Group | Days -30 to -2 | p | Days -1 to +1 | p | Days +2 to +60 | p | N |
|---|---|---|---|---|---|---|---|
| Forced exits | -5.1% | <0.001 | -2.7% | <0.001 | -0.3% | 0.847 | 524 |
| Voluntary retirements | -0.0% | 0.933 | -0.3% | 0.147 | -0.8% | 0.190 | 969 |
| Founder fired | -9.5% | 0.013 | -5.4% | 0.038 | 4.6% | 0.603 | 34 |
| Fired for conduct | -2.5% | 0.162 | -4.7% | 0.003 | 3.8% | 0.083 | 57 |
| Fired for performance | -5.5% | <0.001 | -2.5% | <0.001 | -0.8% | 0.606 | 467 |

*Notes.* Days -30 to -2 and +2 to +60 are cumulative market-adjusted returns (firm minus market), used because a forced-exit firm's alpha before the event is strongly negative and a market model would project it forward. Days -1 to +1 is the market-model return of Table 4. Events need every day of a window. N is the number of departures in the days -1 to +1 window; the outer windows differ by at most a few percent.


Firms that fire for performance trail the market by 5.5% over the six weeks before; firms that fire for legal or personal conduct trail it by 2.5%. On the day the order reverses: conduct firings cost 4.7% and performance firings 2.5%. The gap is not statistically significant.

The pattern fits H3, since conduct firings come with less warning and cost more on the day, but the evidence is weak. On every firing the gap is -1.2 percentage points, also not statistically significant.

### Founders

Table 4 reports the announcement return for each group. Fired founders cost 5.4%, against 2.5% for hired CEOs. The difference of -2.9 percentage points is not statistically significant (p = 0.264). In a regression on all departures with event-year effects, the founder interaction is -3.6 percentage points, also not statistically significant.

The test is not powerful: with 34 hand-dated founder firings, it would detect only a gap of about 7.1 percentage points. Table IA.3 reports the gap in every window. Over trading days -5 to +5 founders cost 7.1 percentage points more, which is statistically significant (p = 0.041).

On every firing, founders cost 2.3% against 1.4%.

Founder firms slide further before the announcement, by 9.5% over the six weeks before, but the difference from hired CEOs is not statistically significant. The data cannot separate a founder premium from zero, though every estimate points the same way. They do rule out the strong form of the entrenchment view. The upper end of the 95% interval for fired founders is -0.5%, so the market does not greet a founder's firing as good news.

The comparison fits earlier evidence from sudden deaths, where founder-CEOs and other CEOs move prices down by similar amounts on average, 1.03% and 1.01% [@jenter2023].

### Table 4. The market's verdict: abnormal returns over trading days -1 to +1

| Group | Mean | Median | t | p | N |
|---|---|---|---|---|---|
| Forced exits | -2.7% | -1.4% | -5.99 | <0.001 | 524 |
| Voluntary retirements | -0.3% | -0.3% | -1.45 | 0.147 | 969 |
| Founder fired | -5.4% | -1.7% | -2.17 | 0.038 | 34 |
| Hired CEO fired | -2.5% | -1.4% | -5.59 | <0.001 | 490 |
| Fired for conduct | -4.7% | -2.2% | -3.08 | 0.003 | 57 |
| Fired for performance | -2.5% | -1.4% | -5.23 | <0.001 | 467 |
| Financial misconduct | -7.7% | -4.9% | -2.59 | 0.017 | 23 |
| Sex or relationship scandal | 1.3% | 0.4% | 1.03 | 0.344 | 7 |
| Financial misconduct, all dates | -6.1% | -2.9% | -2.80 | 0.007 | 54 |
| Sex or relationship scandal, all dates | 0.7% | -0.1% | 0.70 | 0.498 | 16 |

*Notes.* Cumulative market-model abnormal return from trading day -1 to day +1 around the announcement (day 0), with the model estimated over days -250 to -30 (at least 120 days). t is the cross-sectional t of the mean; p is two-sided. N is the number of departures with returns over the window. Firings dated by the database or a hand check; the last two rows use every firing, since few sex cases are hand-dated. Forced exits are database codes 3 and 4; founder status and the financial-misconduct, sexual-conduct and relationship labels are hand-checked.


### Sex, fraud and the rest

Table 5 and Figure 3 split the firings by the reason the board acted. Financial misconduct costs 7.7% in the announcement window, and strategy or power disputes 3.6%. Most other reasons cost little, and each group is small.

With so many reasons tested, chance alone would produce a significant one. After a Holm correction for multiple tests, no single reason is significant: financial misconduct has a Holm p of 0.134 and strategy disputes 0.240.

Firings over sex scandals are a different matter. Only 7 have a hand-coded date, so we compare them with fraud on every firing. The 16 firings over sexual misconduct or a relationship earn 0.7%, against -6.1% for the 54 fraud firings.

That difference of 6.8 percentage points is statistically significant (p = 0.006). On hand-dated firings it is 9.0 percentage points.

The relationship cases include Intel, Boeing, McDonald's and Priceline, where the company said the CEO had broken its policy on relationships; we checked each label by hand. A fraud tells investors that the numbers they relied on were wrong. A sex scandal tells them about one person, and the firing removes that person. With so few sex cases, we treat the comparison as exploratory.

Earlier studies point the same way. When executive misbehaviour first becomes public, firms lose about 3.1%, but the later firing itself costs about 0.8% [@larcker2016]. Personal indiscretions cost 3.84% when the offender is the CEO [@cline2018], and sexual-harassment scandals about 1.5% [@borellikjaer2021]. Our window catches the firing, not the first report.

### Table 5. Why the board acted: abnormal returns over trading days -1 to +1 by coded reason

| Coded primary reason | Mean | t | p | Holm p | N |
|---|---|---|---|---|---|
| Merger or restructuring | -8.9% | -2.18 | 0.040 | 0.240 | 23 |
| Financial misconduct | -7.7% | -2.59 | 0.017 | 0.134 | 23 |
| Legal or regulatory | -6.0% | -1.80 | 0.092 | 0.333 | 16 |
| New opportunity | -4.6% | -3.52 | 0.002 | 0.017 | 23 |
| Strategy or power dispute | -3.6% | -2.11 | 0.045 | 0.240 | 27 |
| Pushed out, described as retirement or health | -3.6% | -3.78 | <0.001 | 0.003 | 64 |
| Unclear | -1.7% | -1.75 | 0.083 | 0.333 | 90 |
| Performance | -1.6% | -2.28 | 0.024 | 0.167 | 209 |
| Other personal conduct | -1.0% | -0.30 | 0.767 | 1.000 | 12 |
| Activist or shareholder pressure | -0.7% | -0.58 | 0.566 | 1.000 | 30 |

*Notes.* Forced exits only, by the primary reason coded from the database notes, the 8-K filed within 10 days, cited press releases, Wikipedia and matched New York Times articles. Reasons with fewer than 10 cases are not shown. Holm p adjusts each p for the number of reasons tested. Financial-misconduct, sexual-conduct and relationship labels are hand-checked; the others are model codes.


![Figure 3. Fraud is expensive; sex scandals are not, at least on the day](/static/reports/founder-ceo/figures/fig4_reasons.png)

*Figure 3. Fraud is expensive; sex scandals are not, at least on the day.* Notes. Mean abnormal return over trading days -1 to +1 by the coded reason the board acted, hand-dated firings, with 95% intervals; reasons with at least 10 firings. Crimson: money and legal cases; violet: personal conduct, including relationships with employees; grey: other reasons.

### The largest founders fired

Table 6 lists the largest firms whose founder was fired, among the firings the evidence also reads as forced. The range is wide. WorldCom lost 34.0% in the announcement window when Bernard Ebbers left in 2002, and it was bankrupt within months. Yahoo gained 9.7% when Jerry Yang stepped aside in 2008.

WWE rose 7.9% when Vince McMahon left in 2022 during an investigation of his conduct. There the market read the founder's exit as removing a problem rather than a source of value.

### Table 6. The largest founders fired

| Company | Founder | Year | Database reason | Value, USD bn | Days -1 to +1 | 36 months | After 60 months |
|---|---|---|---|---|---|---|---|
| Yahoo | Jerry Yang | 2008 | Performance | 37.9 | 9.7% | -23.1% | still listed |
| WorldCom | Bernard Ebbers | 2002 | Legal or conduct | 22.8 | -34.0% | -114.4% | bankrupt |
| WWE | Vince McMahon | 2022 | Legal or conduct | 3.6 | 7.9% | 37.7% | under 5 years of data |
| Acadia Healthcare | Joey Jacobs | 2018 | Performance | 3.3 | -8.4% | 14.9% | still listed |
| Cara Therapeutics | Derek Chalmers | 2021 | Performance | 1.0 | 1.0% | -125.6% | under 5 years of data |
| Trident Microsystems | Frank Lin | 2006 | Legal or conduct | 0.9 | 3.6% | -77.0% | still listed |
| Inter-Tel | Steven Mihaylo | 2006 | Performance | 0.6 | -0.0% | 10.5% | acquired |
| Northern Oil & Gas | Michael Reger | 2016 | Performance | 0.3 | -7.3% | -90.2% | still listed |
| Enzo Biochem | Elazar Rabbani | 2021 | Performance | 0.1 | -19.5% | -93.5% | under 5 years of data |

*Notes.* Founder-CEOs fired, among exits the evidence-based coding also reads as forced, ranked by market value at the fiscal year-end before the departure. Database reason is the CEO dismissal database's code (performance = 3, legal or conduct = 4). Days -1 to +1 is the market-model abnormal return; 36 months is the buy-and-hold return minus the market from day +2; it can fall below -100% when the stock lost most of its value while the market rose. After 60 months reports whether the stock still traded, and if not, how it left.


## 4. After the dust settles: long-run returns and profits

::: answer
**The question.** Does the firm do better or worse in the five years after the firing?

**The answer.** Against the market the median firm does far worse. Against similar firms with no recorded CEO change, it trails in the first year and differs little after that. Profits dip in the first year and then level.
:::

### Returns over five years

Figure 4 follows the median firm for 60 months. Against the market the picture is grim. The median firing firm trails the market by 6.8% after one year, 15.6% after three and 31.3% after five. The median fired-founder firm trails it by 72.7% after five years.

But the median retirement firm trails the market too, by 7.4% after five years. Long-horizon returns are skewed, so the median stock in most groups lags an index. The fair comparison is with a similar firm.

![Figure 4. Against the market the long run looks grim; against a matched firm it does not](/static/reports/founder-ceo/figures/fig2_long_run.png)

*Figure 4. Against the market the long run looks grim; against a matched firm it does not.* Notes. Median buy-and-hold return minus the market, month 1 to month 60 after the announcement, in months of 21 trading days from day +2, all firings. Diamonds mark the median return against a matched firm at 12, 36 and 60 months; Table 7 gives their N at 36 months.

Table 7 makes that comparison. Against a matched firm, the median firing firm's return is -4.3% after one year, which is statistically significant. After three and five years the medians are -1.6% and -5.2%, and neither is statistically significant.

The means tell a softer story still: -1.7%, 0.2% and 9.3% at one, three and five years, none significant. A few firing firms that recovered strongly pull the means above the medians. For fired founders the matched medians are -2.4%, 0.0% and 1.0%: similar firms with no recorded CEO change lost about as much as the founder firms did.

### Table 7. Long-run returns at 12, 36 and 60 months

| Group | Market, 12m | Market, 36m | Market, 60m | Matched, 12m | Matched, 36m | Matched, 60m | N, 36m |
|---|---|---|---|---|---|---|---|
| Forced exits | -6.8% | -15.6% | -31.3% | -4.3% (0.020) | -1.6% (0.470) | -5.2% (0.134) | 1,318 |
| Voluntary retirements | -0.7% | -4.0% | -7.4% | -0.0% (0.834) | 0.5% (0.457) | 2.8% (0.108) | 2,194 |
| Founder fired | -18.3% | -33.0% | -72.7% | -2.4% (0.523) | 0.0% (0.856) | 1.0% (0.869) | 91 |
| Hired CEO fired | -6.3% | -15.2% | -29.9% | -4.4% (0.026) | -2.4% (0.428) | -7.2% (0.140) | 1,227 |
| Fired for conduct | -9.4% | -12.3% | -19.3% | -5.9% (0.198) | -7.0% (0.478) | -10.3% (0.666) | 147 |
| Fired for performance | -6.3% | -16.0% | -32.8% | -4.2% (0.044) | -1.0% (0.609) | -4.9% (0.155) | 1,171 |
| Forced exits, mean | 4.6% | 10.4% | 19.0% | -1.7% (0.523) | 0.2% (0.974) | 9.3% (0.462) | 1,318 |

*Notes.* Medians of buy-and-hold returns from day +2 over 12, 36 and 60 months, all firings. Market subtracts the market's buy-and-hold return; Matched subtracts a control firm in the same industry with market value within 30 percent and the nearest ROA. Matched cells give the Wilcoxon p in parentheses. The last row gives means with t-test p; skewed returns can give means and medians of opposite sign. Delisted firms take their delisting return and then hold the market. N, 36m counts matched events at 36 months.


### Profits

Table 8 follows operating return on assets against the same matched firm. In the first fiscal year after a firing, the median change is -0.4 percentage points below the matched firm's, which is statistically significant. The gap from retirements is -0.7 percentage points. By fiscal year +3 the firing firms' gap is 0.3.

Earlier work finds that operating performance falls before a CEO turnover and improves after it [@huson2004]. Here the recovery brings firing firms level with their matches within three years. Firing the CEO is followed by a short dip in profits, not by a lasting change.

### Table 8. Profitability against the matched firm, fiscal years +1 to +3

| Group | Year +1 | Year +2 | Year +3 | N, year +1 | N, year +3 |
|---|---|---|---|---|---|
| Forced exits | -0.4 (0.028) | 0.2 (0.733) | 0.3 (0.444) | 1,048 | 819 |
| Voluntary retirements | 0.2 (0.144) | 0.3 (0.549) | 0.2 (0.379) | 1,922 | 1,629 |
| Founder fired | -1.5 (0.420) | 2.4 (0.423) | -0.5 (0.472) | 65 | 47 |
| Hired CEO fired | -0.4 (0.042) | -0.1 (0.897) | 0.3 (0.323) | 983 | 772 |
| Fired for conduct | -0.8 (0.161) | -1.9 (0.229) | 0.9 (0.164) | 111 | 85 |
| Fired for performance | -0.4 (0.064) | 0.3 (0.411) | 0.2 (0.729) | 937 | 734 |

*Notes.* Median change in ROA (EBITDA over total assets) from fiscal year -1 to year +1, +2 and +3, minus the same change at the matched firm, in percentage points, with the Wilcoxon p in parentheses. ROA winsorized at the 1st and 99th percentiles. N falls with the horizon because firms stop filing after a sale or bankruptcy.


## 5. Sold, bankrupt, or still standing

::: answer
**The question.** How many of these firms stop trading, and how?

**The answer.** A third within five years, twice the rate after a retirement. Takeovers are the commonest exit, but bankruptcy explains more of the gap with retirements.
:::

The clearest long-run difference is whether the firm survives as an independent listed company. Figure 5 shows the share of firms that have stopped trading, month by month, among firms with a complete five-year horizon. Table 9 gives the shares at one, three and five years.

![Figure 5. One in three is gone within five years](/static/reports/founder-ceo/figures/fig3_exits.png)

*Figure 5. One in three is gone within five years.* Notes. Cumulative share of firms no longer trading, by month after the announcement and by how they left, for firms with a complete 60-month horizon: (a) after a firing, (b) after a retirement.

After a firing, 7.8% of firms stop trading within a year, 21.2% within three years and 32.1% within five. After a retirement the shares are 3.5%, 9.5% and 16.8%.

Takeovers are the commonest way out: 19.4% of firing firms are acquired within five years and 11.8% go bankrupt. After a retirement the figures are 14.1% and 2.6%. The excess over retirements therefore comes more from bankruptcy than from takeovers.

Firing firms are smaller and weaker than retirement firms, so part of the gap could reflect who they are. Table IA.4 controls for size, profitability, year and industry. A firing still adds 9.4 percentage points to the chance of leaving the market within five years. Of that, 5.0 percentage points is bankruptcy and 4.0 percentage points takeover.

Matched firms give the same answer. Within five years 24.2% of the matched firms stopped trading, against 31.2% of the same firing firms, a difference of 7.0 percentage points that is statistically significant.

Bankruptcies come early: 4.8% of firing firms fail within a year. After a founder is fired, 35.7% of firms stop trading within five years, a difference from hired CEOs that is not statistically significant. A board that fires its CEO is more likely to end with the firm sold or failed. That fits the view that board removal and takeover are two routes to a change of control [@morck1989].

### Table 9. Firms that stop trading within 12, 36 and 60 months

| Group | Gone, 12m | Gone, 36m | Gone, 60m | Acquired, 60m | Bankrupt, 60m | p vs retired | N, 60m |
|---|---|---|---|---|---|---|---|
| Forced exits | 7.8% | 21.2% | 32.1% | 19.4% | 11.8% | <0.001 | 1,335 |
| Voluntary retirements | 3.5% | 9.5% | 16.8% | 14.1% | 2.6% |  | 2,185 |
| Founder fired | 9.7% | 28.4% | 35.7% | 20.4% | 13.3% | <0.001 | 98 |
| Hired CEO fired | 7.6% | 20.6% | 31.8% | 19.3% | 11.7% | <0.001 | 1,237 |
| Fired for conduct | 7.9% | 18.3% | 29.1% | 22.8% | 5.7% | <0.001 | 158 |
| Fired for performance | 7.7% | 21.5% | 32.5% | 18.9% | 12.7% | <0.001 | 1,177 |
| Financial misconduct | 5.6% | 18.5% | 37.0% | 24.1% | 11.1% | <0.001 | 54 |
| Sex or relationship scandal | 12.5% | 43.8% | 35.7% | 28.6% | 7.1% | 0.126 | 14 |

*Notes.* Share of firms whose stock left the price file within 12, 36 and 60 months of the announcement. Each horizon uses the events whose horizon is complete in the data for every firm, delisted or not; N, 60m counts those for 60 months. Acquired and Bankrupt classify the corporate action within 60 days of the final price. p vs retired is a chi-square test of the 60-month share against retirements; Table IA.4 adds controls and matched firms. Small groups can show a lower share at 60 months than at 36 because fewer firms have a complete 60-month horizon.


## 6. Who stays on the board

::: answer
**The question.** What happens to the board after a firing?

**The answer.** Nearly half of the earlier directors are gone two years later, more than after a retirement. Fired CEOs, founders included, rarely stay on the board.
:::

Firing the CEO is followed by a wider clear-out. About two years after a firing, 48.4% of the directors who served before the departure have left, against 37.8% after a retirement. The difference is statistically significant.

Firing firms more often had separate chair and CEO roles before the departure, 54.0% against 27.2%. Two years later the shares are close, 66.7% and 65.9%. The rise comes after retirements, when a retiring CEO often hands over both roles.

Fired CEOs almost always leave the board too. A fired founder still sits on the board two years later at 9.1% of firms, against 3.6% for fired hired CEOs and 33.3% for CEOs who retire.

Figure 6 plots these results next to the profit path of Section 4. They cover the 1,921 departures whose firms filed a proxy statement both before and about two years after the event. Firms sold or delisted in between are left out.

![Figure 6. Profits dip and recover; the board turns over](/static/reports/founder-ceo/figures/fig6_roa_board.png)

*Figure 6. Profits dip and recover; the board turns over.* Notes. (a) Median change in return on assets from fiscal year -1, minus the same change at the matched firm, in percentage points, for fiscal years 0 to +3. (b) The board about two years after the departure: the share of earlier directors gone, the share of firms with separate chair and CEO, and the share where the departing CEO is still a director, for firings (crimson) and retirements (slate); the diamond marks fired founders.

### Table 10. The board about two years after the departure

| Group | Earlier directors gone | N | Split before | Split after | N, split | Departing CEO still a director |
|---|---|---|---|---|---|---|
| Forced exits | 48.4% | 611 | 54.0% | 66.7% | 195 | 3.9% |
| Voluntary retirements | 37.8% | 1,310 | 27.2% | 65.9% | 440 | 33.3% |
| Founder fired | 52.1% | 33 | 25.0% | 75.0% | 12 | 9.1% |
| Hired CEO fired | 48.2% | 578 | 56.2% | 66.1% | 183 | 3.6% |
| Fired for conduct | 49.1% | 58 | 36.8% | 88.9% | 18 | 5.2% |

*Notes.* Director lists from the last proxy filed before the departure and the first proxy filed at least 600 days after it. Directors match on surname and first initial. Split before and after: the chair and CEO roles held by different people in the earlier and the later proxy, on the departures where the later proxy names a chair (N, split; the earlier proxy names one slightly more often). For fired founders the last column is the founder; otherwise the departing CEO.


## 7. Conclusion

Boards rarely fire the people who built their companies, and when they do, the story told is about the founder. The data tell a different story, horizon by horizon.

The market sees the trouble weeks before the board acts. On the day it marks the firm down once. It marks it down more for fraud than for sex scandals, and perhaps more for a founder than for a hired CEO. After that the price stops moving.

The lasting difference is survival. A firm that fires its CEO is about twice as likely as a retirement firm to stop trading within five years. Bankruptcy explains more of that gap than takeover does. Its returns against similar firms differ little after the first year, and its profits recover.

For investors watching a board fire its CEO, three questions matter more than who built the company. Was the stock already falling? Did the CEO mislead investors about the numbers, or was the scandal personal? And how fragile is the firm? For boards, firing a founder may carry a larger penalty on the day, but none that lasts.

::: limits
**What these data cannot tell us.**

- The sample covers S&P 1500 firms, so it says little about smaller companies, where founders often hold more control.
- Reasons other than financial misconduct, sexual conduct and relationships are model codes, checked by hand only where errors would matter most.
- The sex-scandal and founder groups are small, so those tests can detect only large gaps.
- Precise announcement dates exist for only part of the sample.
- The window catches the firing, not the first public report of the problem behind it.
- The comparisons describe what follows a firing. They cannot say what would have happened had the board kept the CEO.
:::

## Internet Appendix

Table IA.1 changes one thing at a time against the main tables. With the five-factor model plus momentum, the founder gap is -2.3 percentage points and the conduct gap -1.8 percentage points. Returns minus the market, with no estimated model, give -2.9% in the announcement window. Using every firing, whatever its date source, gives -1.5%.

On the strict sample of 193 hand-dated firings that the evidence also reads as forced, the announcement return is -2.3%, which is statistically significant. Fired founders there earn -4.5% against -2.2% for hired CEOs. Within five years 34.1% of the strict sample stop trading.

Our coding finds 9 hand-dated departures that the database records as retirements but that followed board pressure. Adding them to the firings gives -2.6%. Excluding 2008 and 2009 gives -2.8%, and dropping firings coded as leaving for a new job gives -2.6%.

The long-run results do not depend on how delisting returns are set. With every delisting return at zero, the median three-year return against the market is -13.8%. Setting every delisting that is not a takeover to minus 100% gives -15.8%. Using only matches that meet the size rule, the median three-year matched return is -0.9%.

For departures from 1992 to 1997, before daily prices for delisted firms exist, we use the five-year return graphs that firms print in their proxy statements. Of these departures, 225 have a usable graph, including 45 firings. A firm must still file a proxy three years later, so only survivors enter this check.

The median three-year return against the firm's own reported index is -68.3% after firings and -39.5% after retirements. The difference of -28.8 percentage points is statistically significant. Both groups trail their indexes, and the comparison between the groups points the same way as in the main sample.

### Table IA.1. Robustness

| Specification | Estimate | p | N | Horizon |
|---|---|---|---|---|
| Five-factor plus momentum: founder minus hired CEO | -2.3 pp | 0.397 | 524 | Trading days -1 to +1 |
| Five-factor plus momentum: conduct minus performance | -1.8 pp | 0.259 | 524 | Trading days -1 to +1 |
| Market-adjusted, forced exits | -2.9% | <0.001 | 524 | Trading days -1 to +1 |
| Evidence agrees the exit was forced | -2.3% | 0.002 | 193 | Trading days -1 to +1 |
| Evidence agrees: founder minus hired CEO | -2.2 pp | 0.584 | 193 | Trading days -1 to +1 |
| Adding retirements the evidence reads as pushed | -2.6% | <0.001 | 533 | Trading days -1 to +1 |
| Pushed retirements alone | 4.1% | 0.102 | 9 | Trading days -1 to +1 |
| Excluding 2008 and 2009 | -2.8% | <0.001 | 490 | Trading days -1 to +1 |
| Matched BHAR, 36 months, strict size matches | -0.9% | 0.619 | 1,261 | 36 months (756 trading days) from day +2 |
| Evidence agrees: BHAR vs market, 36 months | -10.8% | 0.004 | 577 | 36 months (756 trading days) from day +2 |
| All dates, every firing with returns | -1.5% | <0.001 | 1,388 | Trading days -1 to +1 |
| Not precisely dated (8-K, news report or leaving office) | -0.8% | 0.162 | 864 | Trading days -1 to +1 |
| Dated by an 8-K only | -0.6% | 0.261 | 512 | Trading days -1 to +1 |
| All dates: fraud minus sex or relationship | 6.8 pp | 0.006 | 70 | Trading days -1 to +1 |
| All dates: conduct minus performance | -1.2 pp | 0.214 | 1,388 | Trading days -1 to +1 |
| All dates: founder minus hired CEO | -0.9 pp | 0.507 | 1,388 | Trading days -1 to +1 |
| Excluding firings coded as leaving for a new job | -2.6% | <0.001 | 501 | Trading days -1 to +1 |
| BHAR vs market, 36 months, every delisting return 0 | -13.8% | <0.001 | 1,390 | 36 months (756 trading days) from day +2 |
| BHAR vs market, 36 months, non-takeover delistings -100% | -15.8% | <0.001 | 1,390 | 36 months (756 trading days) from day +2 |
| Pre-1998: 3-year return minus reported index, forced minus retired | -28.8 pp | 0.017 | 225 | Three fiscal years from the event year, departures announced 1992 to 1997 |

*Notes.* Each row changes one thing against the main tables. Evidence agrees: the CEO dismissal database codes the exit forced and the evidence-based coding (8-K, press releases, Wikipedia, NYT) also reads it as forced. Pushed retirements: the database codes a retirement and the evidence reads it as forced. Pre-1998: departures announced 1992 to 1997, three-year return minus the index the firm itself reports in its proxy performance graph.


### Table IA.2. From the database to the main sample

| Step | N |
|---|---|
| Firings in the database, departures 1998 to 2023 | 1,799 |
| with an SEC company identifier | 1,620 |
| with a price history covering the announcement | 1,441 |
| with announcement returns | 1,393 |
| dated by the database or a hand check (announcement sample) | 527 |
| Founder codes from the model, all firings | 191 |
| founders confirmed by hand | 150 |
| of which departures 1998 to 2023 | 132 |
| of which with announcement returns | 103 |
| of which dated (main sample) | 34 |

*Notes.* Firings are database codes 3 and 4. A price history covers the announcement when the security trades from 60 days before day 0. Founder codes come from the evidence-based model coding; every one on a firing was checked by hand, which also added founders the model had left unclear.


### Table IA.3. The founder gap in every window

| Window (trading days) | Founder fired | Hired CEO fired | Gap, pp | p | Detectable gap, pp | N founders |
|---|---|---|---|---|---|---|
| Days 0 to +1 | -4.8% | -2.3% | -2.5 | 0.354 | 7.5 | 34 |
| Days -1 to +1 | -5.4% | -2.5% | -2.9 | 0.264 | 7.1 | 34 |
| Days -5 to +5 | -9.5% | -2.4% | -7.1 | 0.041 | 9.3 | 34 |
| Days -30 to +30 | -8.8% | -3.9% | -4.9 | 0.603 | 26.1 | 34 |

*Notes.* Mean market-model abnormal returns of fired founders and fired hired CEOs over each window, the gap with its Welch p, and the smallest gap the test would detect with 80% power at the 5% level. The paper's main window is days -1 to +1.


### Table IA.4. Who stops trading within 60 months, with controls and against matched firms

| Outcome | Firings | Retirements | Firing effect with controls, pp | p | N |
|---|---|---|---|---|---|
| Stopped trading | 32.1% | 16.8% | 9.4 | <0.001 | 3,443 |
| Acquired | 19.4% | 14.1% | 4.0 | 0.038 | 3,443 |
| Bankrupt | 11.8% | 2.6% | 5.0 | <0.001 | 3,443 |
| Stopped trading, against the matched firm | 31.2% | 24.2% (matched) | 7.0 | <0.001 | 1,264 |

*Notes.* Firing effect with controls: the coefficient on the firing dummy in a linear probability model with log market value, ROA in year -1, event-year and Fama-French industry effects, standard errors clustered by year. The last row compares each firing firm with its own matched firm (paired t).


## References
