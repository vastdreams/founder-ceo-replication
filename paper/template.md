# Sacked: Sex, Fraud, Founders, and the Fate of Firms That Fire Their CEO

## Abstract

This paper answers what happens when the board of a Standard & Poor's {{index_size}} firm fires its CEO. Over the six weeks before the announcement the shares lag the market by {{drift.forced.pre_m30m2.mean|abs}}, and over the three trading days around it they fall a further {{car.forced.mm_m1p1.mean|abs}}. After a sex or other personal scandal the fall is not significantly different from other firings (p {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean|p}}) and {{cardiff.conduct_vs_criminal.mm_m1p1.diff_mean}} smaller than after fraud. After a founder's firing it is not significantly larger (p {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|p}}). Within five years {{exit.forced.bankruptcy_5y}} of firing firms go bankrupt, against {{exit.retired.bankruptcy_5y}} after a retirement.

::: keynumbers

- **[−{{car.forced.mm_m1p1.mean|abs}}]{.focal}** fall in the share price, net of the market, over the three trading days around the announcement of a firing (n = {{car.forced.mm_m1p1.mean|n}})

- **{{exit.forced.bankruptcy_5y}}** of firing firms bankrupt within five years (n = {{exit.forced.bankruptcy_5y|n}}), against {{exit.retired.bankruptcy_5y}} after a retirement; a further {{exit.forced.acquired_5y}} are taken over

:::

## 1. Introduction

::: findings

1. In the six weeks before a firing is announced, the shares lag the market by {{drift.forced.pre_m30m2.mean|abs}} (Table 1).

2. Over the three trading days around the announcement they fall a further {{car.forced.mm_m1p1.mean|abs}}, and the next three months add no significant move (Table 1).

3. After a firing over a personal scandal the shares fall {{car.conduct.mm_m1p1.mean|abs}}, against {{car.performance.mm_m1p1.mean|abs}} after other firings and {{car.criminal.mm_m1p1.mean|abs}} after fraud or other legal violation (Table 2).

4. A founder's firing is followed by a fall of {{car.forced_founder.mm_m1p1.mean|abs}}, against {{car.forced_nonfounder.mm_m1p1.mean|abs}} for a hired CEO, a gap the test cannot tell from zero (Table 2).

5. Within five years {{exit.forced.bankruptcy_5y}} of firing firms go bankrupt and {{exit.forced.acquired_5y}} are taken over, against {{exit.retired.bankruptcy_5y}} and {{exit.retired.acquired_5y}} after a retirement (Table 4).

:::

In 1985 Apple's board backed its chief executive officer (CEO), John Sculley, against Steve Jobs, and Jobs left the company he had co-founded. By 1997 Apple had bought his next company and he was back in charge. In November 2026, after our sample ends, Nvidia's board accepted the resignation of its co-founder and CEO, Jensen Huang [@nvidia2026form8k]. Three days earlier it had opened an independent investigation after reports that Huang had been the target of a foreign intelligence effort [@nvidia2026board]. News reports also described an affair [@cnbc2026nvidia].

The board gave no reason, but a resignation during a board investigation is what this paper counts as a firing. Nvidia's shares closed {{hook.nvda.day_ret|abs}} lower on 12 November, the first trading day after the news, having fallen as much as {{nvda_intraday_low_pct}}% during the session [@cnbc2026nvidia]. By our calculation from Sharadar's adjusted daily closes, they had lost {{hook.nvda.since_board_statement|abs}} from 6 November, the last close before the board's statement, to 18 November.

The question for investors, directors and employees is what happens to a company after its board fires the CEO. Does it matter that the person fired built the company, or that the trouble was a personal scandal rather than fraud? This paper answers both questions for the CEOs fired by the boards of Standard & Poor's (S&P) {{index_size}} firms from 1998 to 2023. There are {{a.n_lr_forced}} such firings with share prices, {{a.n_lr_forced_founder}} of them founders. The {{a.n_criminal_all_dates}} firings over fraud or other legal violation are kept apart as a comparison, because there the firm itself is in trouble with the law.

In the six weeks before a firing is announced, the shares lag the market by {{drift.forced.pre_m30m2.mean|abs}}, consistent with boards firing CEOs after poor results [@jenter2015]. The announcement still moves them: they fall a further {{car.forced.mm_m1p1.mean|abs}} over three trading days (Table 1). Against a similar firm they trail by {{mbhar.forced.1y.median|abs}} over the first year (p {{mbhar.forced.1y.median|p}}), and not significantly at three and five years.

After a firing over fraud or other legal violation the shares fall {{car.criminal.mm_m1p1.mean|abs}}, against {{car.performance.mm_m1p1.mean|abs}} after other firings (Table 2). A personal scandal is followed by a fall of {{car.conduct.mm_m1p1.mean|abs}}, not significantly different from other firings: the 95% interval for the gap runs from {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean.ci_low}} to {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean.ci_high}}.

A founder's firing is followed by a fall of {{car.forced_founder.mm_m1p1.mean|abs}}, against {{car.forced_nonfounder.mm_m1p1.mean|abs}} for a hired CEO (Table 2). The gap is not significant (p {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|p}}), and its 95% interval runs from {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean.ci_low}} to {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean.ci_high}}.

Within five years {{exit.forced.bankruptcy_5y}} of firing firms go bankrupt, against {{exit.retired.bankruptcy_5y}} after a retirement, and {{exit.forced.acquired_5y}} are taken over, against {{exit.retired.acquired_5y}} (Table 4).

A portfolio of firing firms, held for three years after each announcement, earns {{alpha.forced.ew.36m}} a month after adjusting for risk. Its 95% interval, from {{alpha.forced.ew.36m.ci_low}} to {{alpha.forced.ew.36m.ci_high}}, is too wide to rule out gains or losses of several percent over three years.

::: glance

### Table 1. The firing, horizon by horizon: S&P {{index_size}} firms, 1998 to 2023

| Horizon | What is measured | Firings | Retirements | N firings | p |
|---|---|---|---|---|---|
| Panel A. Returns |  |  |  |  |  |
| Trading days −30 to −2 | Return minus the market | {{drift.forced.pre_m30m2.mean}} | {{drift.retired.pre_m30m2.mean}} | {{drift.forced.pre_m30m2.mean!n}} | {{drift.forced.pre_m30m2.mean!pv}} |
| Trading days −1 to +1 | Abnormal return, market model | {{car.forced.mm_m1p1.mean}} | {{car.retired.mm_m1p1.mean}} | {{car.forced.mm_m1p1.mean!n}} | {{car.forced.mm_m1p1.mean!pv}} |
| Trading days +2 to +60 | Return minus the market | {{drift.forced.post_p2p60.mean}} | {{drift.retired.post_p2p60.mean}} | {{drift.forced.post_p2p60.mean!n}} | {{drift.forced.post_p2p60.mean!pv}} |
| {{months_1y}} months | Return minus a matched firm, median | {{mbhar.forced.1y.median}} | {{mbhar.retired.1y.median}} | {{mbhar.forced.1y.median!n}} | {{mbhar.forced.1y.median!pv}} |
| {{months_3y}} months | Return minus a matched firm, median | {{mbhar.forced.3y.median}} | {{mbhar.retired.3y.median}} | {{mbhar.forced.3y.median!n}} | {{mbhar.forced.3y.median!pv}} |
| {{months_5y}} months | Return minus a matched firm, median | {{mbhar.forced.5y.median}} | {{mbhar.retired.5y.median}} | {{mbhar.forced.5y.median!n}} | {{mbhar.forced.5y.median!pv}} |
| Months 1 to {{months_3y}} | Risk-adjusted return (alpha), per month | {{alpha.forced.ew.36m}} | {{alpha.retired.ew.36m}} | {{alpha.forced.ew.36m!n}} | {{alpha.forced.ew.36m!pv}} |
| Panel B. The firm |  |  |  |  |  |
| Within {{months_5y}} months | Share of firms delisted * | {{exit.forced.delisted_5y}} | {{exit.retired.delisted_5y}} | {{exit.forced.delisted_5y!n}} | {{exitdiff.forced_vs_retired.delisted_5y!pv}} |
| Fiscal year +1 | Change in return on assets minus the matched firm, median, percentage points | {{roa.forced.abn_d_1.median}} | {{roa.retired.abn_d_1.median}} | {{roa.forced.abn_d_1.median!n}} | {{roa.forced.abn_d_1.median!pv}} |
| About two years | Share of earlier directors not in the later proxy statement * | {{board.forced.director_turnover.mean}} | {{board.retired.director_turnover.mean}} | {{board.forced.director_turnover.mean!n}} | {{boarddiff.forced_vs_retired.director_turnover.diff_mean!pv}} |

*Notes.* Firings exclude those over fraud or other legal violation. Day 0 is the first trading day on or after the announcement. The first three rows use well-dated firings (dated by the database or by hand), the rest every firing. A month is {{trading_days_per_month}} trading days from day +2. The alpha is the monthly intercept from the five Fama-French factors and momentum; its N counts calendar months. N falls with the horizon as recent firings have not reached it. p tests the firing number against zero, or, in rows marked *, against retirements.

:::

## 2. Related work

Boards fire CEOs after poor performance, including poor performance of the whole industry [@jenter2015], and returns fall well before the change [@weisbach1988]. Firing after an industry downturn can be an efficient rematch of CEOs and firms rather than a mistake [@eisfeldt2013]. Firings are rare, which suggests that boards behave as if replacing a CEO were costly [@taylor2010; @kaplan2012], and large pay cuts serve as a substitute [@gao2012]. Accounting performance deteriorates before a CEO change and improves after it [@huson2004], and volatility rises more after forced than after voluntary exits [@clayton2005]. How the market reacts depends on what the firing reveals about the firm [@kind2011; @chen2026]. A firing should therefore lower the share price at the announcement, but by less than the decline that preceded it.

Founder-led firms invest differently and have been valued more highly [@fahlenbrach2009]. Founder status itself responds to performance [@adams2009], founders are often replaced as their firms mature [@wasserman2003; @aran2024], and in venture-backed startups replacing the founder improves outcomes [@ewens2018]. The value of a founder's leadership may decline with time since the listing [@bebchuk2017], and insiders' voting control beyond their cash-flow rights goes with lower firm value [@gompers2010]. Yet CEO turnover at dual-class firms is as sensitive to performance as elsewhere [@aran2025]. When a CEO dies suddenly, the average share price reaction does not differ between founders and other CEOs [@jenter2023]. In Poland, poorly performing founder-CEOs are less likely to be fired than outside CEOs [@kowalewski2019]. If founders carry value a successor cannot replace, their firing should cost more. If boards act against founders only when the case is overwhelming, the firing could end entrenchment and be good news [@taylor2010].

Executive scandals and financial misreporting both cost shareholders [@cline2018; @larcker2016; @borellikjaer2021; @karpoff2008jfqa], and managers who misreport usually lose their jobs [@karpoff2008jfe]. Boards fire CEOs who manage earnings before outside penalties arrive [@hazarika2012], and more often where employees and directors are prosocial [@bereskin2020]. Shares also fall when a CEO is accused of sexual misconduct [@mooibroek2021] and when a firm reports sexual harassment [@abeysekera2024]. Board resignations rose at exposed firms after the #MeToo revelations of 2017 [@baharad2026]. @cline2018 separate personal indiscretions from misconduct in the business and measure the return when the indiscretion becomes public. We measure the firing that follows, and compare it with firings over fraud. A fraud tells investors that numbers they relied on were wrong, while a personal scandal concerns one person, so a firing over a personal scandal should cost less.

Relative to these studies, the paper compares in one sample three things usually studied apart: who was fired, why the board acted, and what became of the firm. It follows each firing from six weeks before the announcement to five years after, with the number of firms measured at every horizon. It checks by hand who was a founder, why the board acted and, for founders and personal scandals, when the firing was announced.

## 3. Data and design

### Which firings

The departures come from the open CEO dismissal database of @gentry2021, which its authors have extended to cover 1992 to 2023. It codes the reason for every CEO departure at S&P {{index_size}} firms from press coverage and filings, and an independent recoding agreed with it on {{lit_gentry_agreement_pct}}% of events [@gentry2021]. Codes 3 and 4, dismissal for job performance and for legal violations or personal conduct, are firings. Code 5, voluntary retirement, is the comparison group.

Press releases rarely say that a CEO was fired [@gow2017], and how firings are classified changes the results [@fee2018]. Like the database, we treat a resignation under board pressure as a firing, including one during an investigation, a scandal or an activist campaign.

From the firings we remove the {{a.n_criminal_all_dates}} whose main reason is fraud or other legal violation. These cover financial misconduct, a legal or regulatory breach by the firm and criminal charges against the CEO. A personal scandal is a firing over sexual misconduct, a relationship with an employee, conduct at work or another personal failing such as a false degree. There are {{a.n_lr_conduct}} of them, of which {{a.n_lr_founder_personal}} are founders, too few for a test.

Each departure is linked to the firm's Central Index Key, its identifier at the Securities and Exchange Commission, and through it to daily prices that include firms later delisted. Prices and fundamentals come from Sharadar's Core US Equities data. Table IA.1 traces the firings from the database to the samples, and Figure IA.1 shows them by year.

### Dating the announcement

A three-day window needs the right day. The database gives an announcement date for about a third of departures, and otherwise only the day the CEO left office, which can come weeks after the news. The firm's 8-K, the filing a company must make within four business days of a CEO change, gives a second date. On departures the database does date, the two agree within 3 days in only {{redate_agree_3d_pct}}% of cases.

Firings dated by the database fall {{rob.datesrc_database.mm_m1p1.mean|abs}} over three days and firings dated only from a filing {{rob.datesrc_8k.mm_m1p1.mean|abs}} (Table IA.4). A misplaced day 0 would produce this gap, but so could differences between the firings the database chooses to date. Announcement results therefore use the {{a.n_forced}} well-dated firings, dated by the database or by hand. Results over months and years use all {{a.n_lr_forced}}, since an error of a few days is small against a window of {{days_1y}} trading days or more.

The founder and personal-scandal tests rest on few well-dated firings, so we dated the rest of them by hand. For each, we read the firm's 8-K, its press releases and New York Times reports, and kept a date only when a dated source states it. The well-dated founder firings rise to {{a.n_forced_founder}} and the personal-scandal firings to {{car.conduct.mm_m1p1.mean|n}}; firings with no dated source stay out of the announcement tests.

### Founders and reasons

For each departure a language model (DeepSeek, deepseek-chat, at temperature zero) codes whether the CEO founded the firm or its predecessor. It also codes whether the exit was forced and the board's main reason, each with a supporting quote. It reads the database's notes and sources, the 8-K, cited press releases, the CEO's Wikipedia article and matching New York Times articles. We call this the evidence-based coding.

Every founder code on a firing was then checked by hand, as was every financial-misconduct, sexual-misconduct, relationship and other personal-conduct code. The checks were made by one coder; a second coder's check of a random fifth of the codes is planned. The model coded {{b.model_founder_codes}} firings as founder removals; the review confirmed {{b.founders_confirmed}}, rejected {{b.founders_rejected}} and added {{b.founders_added}}. About half of the model's other personal-conduct codes turned out to be pay disputes, unexplained personal reasons or criminal charges.

The model's reading of whether an exit was forced is cautious. Of the {{a.n_forced}} well-dated firings it reads {{a.n_llm_yes}} as forced, {{a.n_llm_no}} as not forced and {{a.n_llm_unclear}} as unclear, mostly because the sources do not say. On the {{a.n_forced_strict}} where it agrees, the fall is {{car.forced_strict.mm_m1p1.mean|abs}} (Table IA.4), against {{car.forced.mm_m1p1.mean|abs}} on all well-dated firings. The headline fall may therefore include some firings that were not described as forced at the time.

### Returns

The announcement return is the abnormal return over the three trading days from the day before the announcement to the day after it, from the market model of equation (1). The market model predicts the stock's return from the market's, using the stock's own past relation to the market.

$$AR_{it} = R_{it} - \hat\alpha_i - \hat\beta_i R_{mt}, \qquad CAR_i = AR_{i,-1} + AR_{i,0} + AR_{i,+1}. \tag{1}$$

Here $R_{it}$ is the stock's total return and $R_{mt}$ the market's. The coefficients come from trading days {{estimation_window_start}} to {{estimation_window_end}} before the announcement. We test the mean with the cross-sectional t and the standardized test of @boehmer1991, and the median with the Wilcoxon signed-rank test [@kothari2007]. Over the six weeks before and three months after, we use returns minus the market instead. A firm that was falling before the event has a negative alpha; carried forward, it would make ordinary returns afterwards look like a recovery.

For the long run, the main measure is the buy-and-hold return from day +2 over {{days_1y}}, {{days_3y}} or {{days_5y}} trading days. Equation (2) subtracts the market's or a matched firm's return:

$$BHAR_i(h) = \prod_{t=2}^{T_h}(1+R_{it}) - \prod_{t=2}^{T_h}(1+R_{bt}). \tag{2}$$

The matched firm is in the same Fama-French industry, within {{matching_rule_pct}} percent in market value, with the nearest return on assets. It had no recorded CEO change in the three years before. Matching on prior profitability follows @barber1996, whose tests are well specified only when firms are matched on performance before the event. We also form a calendar-time portfolio of every firm in its first 36 months after an announcement. Its excess return is regressed on the five Fama-French factors and momentum [@famafrench2015; @lyon1999], and the intercept, the alpha, is the monthly return left over.

On the day a firm is delisted, its return is set to zero for a takeover, minus 100% for a bankruptcy and minus 30% otherwise [@shumway1997]. Firms that fire their CEO are about half the size of those whose CEO retires. Their median market value at the fiscal year-end before is {{desc.forced.mcap.median}} billion dollars, against {{desc.retired.mcap.median}} (Table IA.2). Every long-run comparison is therefore also made against a matched firm or within size bands.

## 4. The stock around the announcement

Figure 1 shows the returns of firing and retirement firms from six weeks before the announcement to three months after it. For retirement firms the line stays within one percentage point of zero. For firing firms it slides for six weeks, drops at the announcement and then moves sideways.

![Figure 1. Prices slide before the firing, drop on the news, then stop](/static/reports/founder-ceo/figures/fig1_event_time.png)

*Figure 1. Prices slide before the firing, drop on the news, then stop.* Notes. Cumulative return minus the market from trading day -30 to day +60 around the announcement (day 0), well-dated firings with every day of the window. Panel (a) shows means, with the {{ci_level}}% confidence band for firings; the grey band marks days -1 to +1. Panel (b) shows medians, so that one firm cannot move a small group's line. The lines sum daily returns, so their end points differ slightly from the window returns of Table 1.

In the six weeks before the announcement, the shares of firing firms lag the market by {{drift.forced.pre_m30m2.mean|abs}}, while those of retirement firms do not move ({{drift.retired.pre_m30m2.mean}}). Over the three days around the announcement they fall a further {{car.forced.mm_m1p1.mean|abs}} (t = {{car.forced.mm_m1p1.mean|t}}), against {{car.retired.mm_m1p1.mean}} for retirements (Table 2).

Other measures give a similar fall: the five-factor model gives {{car.forced.ff5_m1p1.mean}} over the same three days. The standardized test, which weights each firm by the precision of its estimate, gives t = {{car.forced.mm_m1p1.bmp_t}} (Table 2). Over the next three months the shares earn {{drift.forced.post_p2p60.mean}} against the market, which is {{drift.forced.post_p2p60.mean|sig}} (p {{drift.forced.post_p2p60.mean|p}}, n = {{drift.forced.post_p2p60.mean|n}}).

<!-- TABLE:2 -->

### Personal scandals and fraud

After a firing over a personal scandal the shares fall {{car.conduct.mm_m1p1.mean|abs}} over the three days, against {{car.performance.mm_m1p1.mean|abs}} after other firings and {{car.criminal.mm_m1p1.mean|abs}} after fraud or other legal violation (Table 2).

The personal-scandal gap of {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean}} is {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean|sig}} (p {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean|p}}, n = {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean|n}}). Its 95% interval runs from {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean.ci_low}} to {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean.ci_high}}, so a scandal firing may cost somewhat more than other firings or somewhat less.

Fraud is followed by a fall {{cardiff.conduct_vs_criminal.mm_m1p1.diff_mean}} larger than after a personal scandal (p {{cardiff.conduct_vs_criminal.mm_m1p1.diff_mean|p}}, n = {{cardiff.conduct_vs_criminal.mm_m1p1.diff_mean|n}}). For fraud, though, the firing is often announced with the fraud itself, so this fall includes the news of the fraud as well as of the firing.

With size, the prior year's return and the year held constant, the personal-scandal gap is {{regc.car_m1p1.conduct}} (p {{regc.car_m1p1.conduct|p}}, n = {{regc.car_m1p1.conduct|n}}; Table IA.4). Table IA.6 and Figure IA.2 break the other firings down by the reason coded for them. The firing may say little about the business, or the market may have priced the scandal when it first broke. To separate the two, we went back to the first press report.

We searched the New York Times Archive for personal misconduct by sitting CEOs of the sample's firms and checked each report by hand (Table IA.7). The search finds {{scandal.n_events}} scandals. In {{scandal.n_departed}} the CEO left within a year; in {{scandal.n_kept}} the board kept them, among them Jeff Bezos at Amazon and Bobby Kotick at Activision Blizzard. It finds only {{scandal.n_known_firings_found}} of the database's firings over a personal scandal, mostly at the largest firms, so these cases describe prominent scandals and support no test.

For the {{scandal.all.first_report.car_m1p1.mean|n}} scandals with share prices at the time, the shares fell {{scandal.all.first_report.car_m1p1.mean|abs}} against the market over the three trading days around the first report. They fell {{scandal.departed.first_report.car_m1p1.mean|abs}} where the CEO later left ({{scandal.departed.first_report.car_m1p1.mean|n}} cases) and {{scandal.kept.first_report.car_m1p1.mean|abs}} where the board kept them ({{scandal.kept.first_report.car_m1p1.mean|n}}), too few cases to tell apart.

### Founders

A founder's firing is followed by a fall of {{car.forced_founder.mm_m1p1.mean|abs}} over the three days, against {{car.forced_nonfounder.mm_m1p1.mean|abs}} for a hired CEO (Table 2). The gap of {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean}} is {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|sig}} (p {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|p}}).

With {{a.n_forced_founder}} well-dated founder firings, the test can detect a gap of about {{mde.founder_gap.mm_m1p1}} (Table IA.3). The 95% interval for the gap runs from {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean.ci_low}} to {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean.ci_high}}.

With firm size, the prior year's return and the year held constant, fired founders fall {{regc.car_m1p1.founder}} less than hired CEOs (p {{regc.car_m1p1.founder|p}}; Table IA.4). Founder firms slide further before the announcement: {{drift.forced_founder.pre_m30m2.mean|abs}} over the six weeks, against {{drift.forced.pre_m30m2.mean|abs}} for all firings, on returns minus the market (Table IA.5).

The {{ci_level}}% interval for the return after a founder's firing reaches up to {{car.forced_founder.mm_m1p1.ci_high}}, so a gain at the announcement is unlikely, though the estimate is imprecise. Nvidia's {{hook.nvda.day_ret|abs}} fall on 12 November is a little larger than the average after a founder's firing.

Three founders were fired over a personal scandal: John Schnatter at Papa John's, Steve Wynn at Wynn Resorts and Vince McMahon at World Wrestling Entertainment (WWE). WWE's shares rose {{case.8370.car_m1p1}} over the three days around McMahon's departure (Table IA.8); three cases do not support a test.

## 5. Which firms are delisted

Within five years of a firing, {{exit.forced.delisted_5y}} of the {{exit.forced.delisted_5y|n}} firms with a complete horizon have been delisted: {{exit.forced.acquired_5y}} in a takeover and {{exit.forced.bankruptcy_5y}} in bankruptcy (Table 4).

After a retirement, {{exit.retired.delisted_5y}} of {{exit.retired.delisted_5y|n}} firms are delisted, {{exit.retired.acquired_5y}} in a takeover and {{exit.retired.bankruptcy_5y}} in bankruptcy (Figure 2). Most of the gap is therefore bankruptcy. Takeovers are the larger share in both groups, which fits the view that board removal and takeover are two routes to a change of control [@morck1989].

![Figure 2. Within five years, {{exit.forced.delisted_5y}} of firing firms are delisted](/static/reports/founder-ceo/figures/fig3_exits.png)

*Figure 2. Within five years, {{exit.forced.delisted_5y}} of firing firms are delisted.* Notes. Cumulative share of firms delisted, by month after the announcement, for firms with a complete {{months_5y}}-month horizon: (a) for any reason, (b) in bankruptcy. Most of the rest are takeovers; Table 4 gives the shares.

Firing firms are about half as large as retirement firms, and small firms fail more often, so Table 3 compares firms of similar size. In the smallest band, under $300 million, {{exit.forced.size_small.bankruptcy_5y}} of firing firms go bankrupt within five years, against {{exit.retired.size_small.bankruptcy_5y}} of retirement firms. Above $5 billion the bankrupt shares are {{exit.forced.size_mega.bankruptcy_5y}} and {{exit.retired.size_mega.bankruptcy_5y}}.

Firing firms are delisted more often in every band: from $1 to 5 billion, {{exit.forced.size_large.delisted_5y}} within five years, against {{exit.retired.size_large.delisted_5y}} of retirement firms (p {{exitdiff.forced_vs_retired.size_large.delisted_5y|p}}; Table 3).

<!-- TABLE:3 -->

Some firms were already failing when the CEO left: for {{exit.forced.early_bankruptcy_n}} of them a bankruptcy was recorded within 180 days of the announcement, as at Sears and Dana. Setting those aside, {{exit.forced.after.delisted_5y}} of firing firms are delisted within five years and {{exit.forced.after.bankruptcy_5y}} go bankrupt.

With controls for size, return on assets, year and industry, firing firms are {{reg.exit5.gone.forced}} more likely to be delisted within five years (Table 4). Adding the prior year's return, leverage, book-to-market, a distress score and a loss flag lowers the gap to {{reg.exit5c.gone.forced}} (p {{reg.exit5c.gone.forced|p}}). Of that gap, {{reg.exit5c.bankrupt.forced}} is bankruptcy. Leverage is the strongest predictor among these controls (Table IA.9).

Against their matched firms the difference is {{exitdiff.forced_vs_ctrl.delisted_5y}} (p {{exitdiff.forced_vs_ctrl.delisted_5y|p}}; Table IA.9). The firing need not cause the delisting: a board may fire the CEO of a firm it already expects to struggle.

Founder firms are delisted within five years in {{exit.forced_founder.delisted_5y}} of cases (Table 4). The gap from hired CEOs is not significant (p {{exitdiff.forced_founder_vs_forced_nonfounder.delisted_5y|p}}), and its 95% interval runs from {{exitdiff.forced_founder_vs_forced_nonfounder.delisted_5y.ci_low}} to {{exitdiff.forced_founder_vs_forced_nonfounder.delisted_5y.ci_high}}.

After a personal scandal the share is {{exit.conduct.delisted_5y}} (n = {{exit.conduct.delisted_5y|n}}). The gap from other firings is not significant (p {{exitdiff.conduct_vs_performance.delisted_5y|p}}), and its 95% interval, from {{exitdiff.conduct_vs_performance.delisted_5y.ci_low}} to {{exitdiff.conduct_vs_performance.delisted_5y.ci_high}}, is too wide to say much either way.

<!-- TABLE:4 -->

## 6. Returns, profits and the board over five years

Do the higher bankruptcy rates leave shareholders with lower risk-adjusted returns? A portfolio of every firm in its first 36 months after a firing earns an alpha of {{alpha.forced.ew.36m}} a month (Table IA.10). The 95% interval runs from {{alpha.forced.ew.36m.ci_low}} to {{alpha.forced.ew.36m.ci_high}} a month, wide enough to include gains or losses of several percent over three years.

Against a portfolio of retirement firms the difference is {{alphadiff.forced_vs_retired.ew.36m}} a month (p {{alphadiff.forced_vs_retired.ew.36m|p}}). The portfolio of personal-scandal firms earns {{alpha.conduct.ew.36m}} a month (t = {{alpha.conduct.ew.36m|t}}), but it holds about a dozen firms over {{alpha.conduct.ew.36m|n}} months, so one or two firms can drive it. We do not read it as evidence that scandal firms outperform.

Against the market alone, the median firing firm's buy-and-hold return trails by {{bhar.forced.5y.median|abs}}, and the median retirement firm's by {{bhar.retired.5y.median|abs}}, after five years (Figure 3). Fired founders trail it by {{bhar.forced_founder.5y.median|abs}}, but they are small and were falling; against a matched firm their median is {{mbhar.forced_founder.5y.median}} (n = {{mbhar.forced_founder.5y.median|n}}; Table IA.11).

![Figure 3. Against the market the long run looks grim; against a matched firm it does not](/static/reports/founder-ceo/figures/fig2_long_run.png)

*Figure 3. Against the market the long run looks grim; against a matched firm it does not.* Notes. Median buy-and-hold return minus the market, month 1 to month {{months_5y}} after the announcement, in months of {{trading_days_per_month}} trading days from day +2, all firings. Diamonds mark the median return against a matched firm at {{months_1y}}, {{months_3y}} and {{months_5y}} months; Table IA.11 gives the numbers.

A typical stock lags an index over long horizons, because a few large winners lift the index average. A matched firm of the same industry, size and profitability removes that effect. Against it, the median firing firm's buy-and-hold return is {{mbhar.forced.1y.median}} after one year (p {{mbhar.forced.1y.median|p}}), and {{mbhar.forced.3y.median}} and {{mbhar.forced.5y.median}} after three and five years, neither significant (Table IA.11). The means are {{mbhar.forced.3y.mean}} and {{mbhar.forced.5y.mean}}, also not significant. A few large winners pull the mean above the median, which is why the median and the alpha are the measures we read.

Profits fall in the year of the firing and then recover. In the fiscal year of the departure, return on assets falls {{roa.forced.abn_d_0.median|abs}} percentage points against the matched firm (p {{roa.forced.abn_d_0.median|p}}; Table IA.12 and Figure IA.3). By fiscal year +2 the gap is {{roa.forced.abn_d_2.median}}, on the firms still filing.

About two years after a firing, {{board.forced.director_turnover.mean}} of the directors in the last proxy statement before it are missing from the later one, against {{board.retired.director_turnover.mean}} after a retirement (Table IA.13). The proxy statement is the annual filing that lists the directors standing for election. A proxy does not say why a director left, so these shares do not separate resignations, directors not nominated again and lost votes. Directors are matched on surname and first initial, which may overstate both shares.

A fired founder sits on the board two years later at {{board.forced_founder.founder_stays.mean}} of firms, against {{board.forced_nonfounder.ceo_stays_director.mean}} for a fired hired CEO and {{board.retired.ceo_stays_director.mean}} for a retired one (Table IA.13). These results cover the {{g.events_with_board_data}} departures whose firms filed a proxy statement both before and about two years after.

## 7. Firings over fraud and legal violations

Treating personal scandals and fraud as one group of misconduct would blur two different outcomes. Within five years {{exit.criminal.delisted_5y}} of the firms that fired their CEO over fraud or other legal violation are delisted, {{exitdiff.criminal_vs_retired.delisted_5y}} more than after a retirement (p {{exitdiff.criminal_vs_retired.delisted_5y|p}}). After a personal scandal the share is {{exit.conduct.delisted_5y}}, not significantly different from retirements (p {{exitdiff.conduct_vs_retired.delisted_5y|p}}; Table 4). Pooling the two would also hide the gap of {{cardiff.conduct_vs_criminal.mm_m1p1.diff_mean}} at the announcement.

## 8. Conclusion

When a board fires its CEO, the shares have usually been falling for weeks, and the announcement still takes them down a further {{car.forced.mm_m1p1.mean|abs}} over three days. Against similar firms they trail by {{mbhar.forced.1y.median|abs}} in the first year, and not significantly at three or five years (Table 1).

Fraud is followed by a larger fall, {{car.criminal.mm_m1p1.mean|abs}}. A personal scandal is followed by a fall of {{car.conduct.mm_m1p1.mean|abs}}, not significantly different from other firings (p {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean|p}}). A founder's firing is followed by a fall of {{car.forced_founder.mm_m1p1.mean|abs}}, not significantly larger than a hired CEO's (p {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|p}}; Table 2). The estimate is imprecise: a gap of several points cannot be ruled out.

Within five years {{exit.forced.bankruptcy_5y}} of firing firms go bankrupt, against {{exit.retired.bankruptcy_5y}} after a retirement, a gap that shrinks but remains with controls for leverage and distress (Table 4). For investors and directors, the risk that sets firing firms apart is bankruptcy. After the first year, their shares do not significantly trail matched firms (Table 1). A portfolio of all firing firms, bankrupt ones included, earns an alpha of {{alpha.forced.ew.36m}} a month.

The sample covers S&P {{index_size}} firms, so it says little about smaller companies, where founders often hold more control. Only three founders were fired over a personal scandal, and too few scandals in which the board kept its CEO reached the press to test. Fewer than half the firings have a precise announcement date, and the evidence-based coding reads about a third of those as clearly forced. The fall after a fraud firing includes the news of the fraud. We do not control for who succeeds the CEO, although most new CEOs are insiders or people the board already knows [@cziraki2022]. The comparisons describe what follows a firing, not what would have happened had the board kept its CEO.

## Internet Appendix

### Sample and firms

Table IA.1 traces the firings from the CEO dismissal database to the samples, and Figure IA.1 counts them by year. In the fiscal year before the departure, firing firms are smaller and less profitable than retirement firms: their median return on assets is {{desc.forced.roa.median}}, against {{desc.retired.roa.median}} (Table IA.2).

<!-- TABLE:IA.1 -->

![Figure IA.1. Firings per year](/static/reports/founder-ceo/figures/fig5_per_year.png)

*Figure IA.1. Firings per year.* Notes. Every firing in the database by year, 1998 to 2023, by the database's dismissal type, whether or not the firm has share prices, less firings over fraud or other legal violation. The bars therefore total more than the paper's {{a.n_lr_forced}} firings with prices. The number above each bar counts the hand-confirmed founders among them; the founder count in Table IA.1 also includes founders fired over fraud. The last year covers part of 2023.

<!-- TABLE:IA.2 -->

### The announcement

The founder gap is negative in all three windows of Table IA.3 and significant in none. With {{a.n_forced_founder}} founders, the smallest gap the main test could detect is {{mde.founder_gap.mm_m1p1}}.

<!-- TABLE:IA.3 -->

Table IA.4 changes one thing at a time against the main tables. With the five-factor model plus momentum, the founder gap is {{rob.founder_vs_nonfounder_ff5.m1p1.diff_mean}} and the personal-scandal gap {{rob.conduct_vs_performance_ff5.m1p1.diff_mean}}. Returns minus the market, with no estimated model, give {{rob.forced.ma_m1p1.mean}} over the three days. Using every firing, whatever its date source, gives {{rob.all_dates.forced.mm_m1p1.mean}}.

On the {{a.n_forced_strict}} well-dated firings that the evidence-based coding also reads as forced, the return over trading days -1 to +1 is {{car.forced_strict.mm_m1p1.mean}}. Excluding 2008 and 2009 gives {{rob.forced_excl_crisis.mm_m1p1.mean}}, and dropping firings coded as leaving for a new job gives {{rob.forced_excl_newopp.mm_m1p1.mean}}.

The long-run results do not depend on how delisting returns are set. With every delisting return at zero, the median three-year return against the market is {{rob.bhar_dl0.forced.3y.median}}, and setting every delisting that is not a takeover to minus 100% gives {{rob.bhar_dlworst.forced.3y.median}}. When no firm meets the size band the nearest firm in size is the match ({{h.relaxed_matches}} matches); using only matches within the band, the median three-year matched return is {{rob.mbhar_strict_matches.3y.median}}.

For departures from 1992 to 1997, before daily prices for delisted firms exist, we use the five-year return graphs that firms print in their proxy statements. Of these departures, {{pre.events_with_tsr}} have a usable graph, including {{pre.n_forced}} firings. The median three-year return against the firm's own reported index is {{pre.forced.abn_tsr_3y.median}} after firings and {{pre.retired.abn_tsr_3y.median}} after retirements. Only firms still filing three years later enter this check.

<!-- TABLE:IA.4 -->

<!-- TABLE:IA.5 -->

Table IA.6 and Figure IA.2 split the firings by the reason coded for them. After a Holm correction for testing every reason, three falls remain statistically significant (Table IA.6). Where a push was described as a retirement or ill health the fall is {{car.reason.retirement_or_health.mm_m1p1.mean|abs}} (Holm p = {{car.reason.retirement_or_health.mm_m1p1.holm_p}}). Where the CEO was coded as leaving for a new job it is {{car.reason.new_opportunity.mm_m1p1.mean|abs}} (Holm p = {{car.reason.new_opportunity.mm_m1p1.holm_p}}). After other personal conduct it is {{car.reason.other_personal_conduct.mm_m1p1.mean|abs}} (Holm p = {{car.reason.other_personal_conduct.mm_m1p1.holm_p}}); performance and the other reasons do not survive the correction.

<!-- TABLE:IA.6 -->

![Figure IA.2. The announcement return by the reason the board acted](/static/reports/founder-ceo/figures/fig4_reasons.png)

*Figure IA.2. The announcement return by the reason the board acted.* Notes. Mean abnormal return over trading days -1 to +1 by the coded reason, well-dated firings, with {{ci_level}}% intervals; reasons with at least {{min_reason_cases}} firings. Table IA.6 gives the numbers.

Table IA.7 lists each scandal the New York Times search found, grouped by whether the board kept its CEO, with the return around the first report. The boards that kept their CEO include News Corp, Goldman Sachs, Amazon and Activision Blizzard; those whose CEO left include Boeing, Hewlett-Packard, Intel and McDonald's. Sexual relationships and harassment allegations appear on both sides. Table IA.8 lists the largest founders fired, with the return at the announcement and what became of the firm.

<!-- TABLE:IA.7 -->

<!-- TABLE:IA.8 -->

### Survival, returns, profits and the board

<!-- TABLE:IA.9 -->

<!-- TABLE:IA.10 -->

<!-- TABLE:IA.11 -->

<!-- TABLE:IA.12 -->

![Figure IA.3. Profits and the board after the firing](/static/reports/founder-ceo/figures/fig6_roa_board.png)

*Figure IA.3. Profits and the board after the firing.* Notes. (a) Median change in return on assets from fiscal year -1, minus the same change at the matched firm, in percentage points, fiscal years 0 to +3. (b) About two years after the departure, three shares: pre-departure directors not named in the later proxy, firms with a separate chair and CEO, and firms where the departing CEO is still a director. Firings are red and retirements grey; the diamond marks fired founders.

<!-- TABLE:IA.13 -->

## References
