# Sacked: Sex, Fraud, Founders, and the Fate of Firms That Fire Their CEO

## Abstract

This paper answers what happens when a Standard & Poor's {{index_size}} board fires its CEO: where dated precisely, the shares fall {{car.forced.mm_m1p1.mean|abs}} over three trading days around the announcement. Over the six weeks before, they had lagged the market by {{drift.forced.pre_m30m2.mean|abs}}. Within five years {{exit.forced.bankruptcy_5y}} of the firms go bankrupt, against {{exit.retired.bankruptcy_5y}} after a retirement. After fraud firings, a comparison group, the shares fall {{car.criminal.mm_m1p1.mean|abs}}, including the news of the fraud. Firings over sex or other personal scandals and firings of founders are too few for precise estimates. Their falls, {{car.conduct.mm_m1p1.mean|abs}} and {{car.forced_founder.mm_m1p1.mean|abs}}, do not differ significantly from other firings'.

## 1. Introduction

This paper asks what follows when the board of a large US company fires its chief executive officer (CEO), and whether it matters who was fired and why. It follows the {{a.n_lr_forced}} CEOs fired by the boards of listed Standard & Poor's (S&P) {{index_size}} firms from 1998 to 2023. Each firing is followed from six weeks before the announcement to five years after it, against the CEOs who retired. It puts in one sample three comparisons that earlier work makes apart: founders against hired CEOs, personal scandals against other firings, and what became of the firm.

The firings behind the title are familiar. In 2004 Nortel dismissed its CEO, Frank Dunn, together with its finance chief and controller, amid an accounting scandal. In 2018 Steve Wynn resigned from the casino company he had founded after published allegations of sexual misconduct. In 2019 McDonald's board removed its CEO, Steve Easterbrook, over a consensual relationship with an employee. All three are firings in this paper's sense: a board removing its chief executive, whatever the press release says.

Across these firings, the evidence answers the question in three parts. First, a firing usually comes after a long fall in the shares, consistent with boards acting on poor results [@jenter2015]. The announcement adds a smaller, sudden fall, and after the first year the shares move much like those of similar firms. Second, a firing over fraud is followed by a much larger fall than a firing over a personal scandal. Fraud firings are kept apart because the firm itself is in trouble with the law, and part of their fall is the news of the fraud itself. Personal-scandal and founder firings are too few for precise estimates, and neither differs significantly from other firings. Third, what sets firing firms apart is failure. Within five years they go bankrupt far more often than firms whose CEO retired, and the gap remains, though smaller, with controls for size, debt and recent returns. Table 1 gives the main numbers at every horizon, from six weeks before the announcement to five years after.

Two measurement choices shape these results: the date of each announcement and the coding of founders and reasons. A three-day window needs the right day, but most firings are dated only by a filing or by the day the CEO left office, often weeks after the news. The announcement tests therefore use the {{a.n_forced}} firings dated by the database or by hand. Who was a founder and why the board acted come from a language model reading filings and news, and one coder checked every founder, fraud and personal-scandal code by hand.

The paper describes what follows a firing rather than what would have happened had the board kept its CEO. Boards fire the CEOs of firms already in trouble, and comparisons with retirements, matched firms and controls narrow that difference without removing it. Section 2 places the paper in the literature and Section 3 describes the data. Sections 4 to 6 report the announcement, delisting and the long run, Section 7 discusses what the comparisons mean, and Section 8 concludes.

::: glance

### Table 1. The firing, horizon by horizon: S&P {{index_size}} firms, 1998 to 2023

| Horizon | What is measured | Firings | Retirements | N | p |
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

Three strands of work give the paper its predictions. The first explains when boards fire. Boards fire CEOs after poor performance, including poor performance of the whole industry [@jenter2015], and returns fall well before the change [@weisbach1988]. A firing after an industry downturn can be an efficient rematch of CEOs and firms rather than a mistake [@eisfeldt2013]. Because firings are rare, boards seem to treat replacing a CEO as costly [@taylor2010; @kaplan2012], and large pay cuts serve as a substitute [@gao2012]. Accounting performance worsens before a CEO change and improves after it [@huson2004], and volatility rises more after forced than after voluntary exits [@clayton2005]. The market's reaction depends on what the firing reveals about the firm [@kind2011; @chen2026]. Together these studies predict a fall before the announcement, a smaller fall at it, and weak firms afterwards.

The second strand asks whether founders are different. Founder-led firms invest differently and have been valued more highly [@fahlenbrach2009], but founder status itself responds to performance [@adams2009]. Founders are often replaced as their firms mature [@wasserman2003; @aran2024], and in venture-backed startups replacing the founder improves outcomes [@ewens2018]. The value of a founder's leadership may decline with time since the listing [@bebchuk2017], and insider control beyond cash-flow rights goes with lower firm value [@gompers2010]. Yet CEO turnover at dual-class firms is as sensitive to performance as elsewhere [@aran2025]. The share price reaction to a CEO's sudden death does not differ between founders and other CEOs [@jenter2023]. In Poland, poorly performing founder-CEOs are less likely to be fired than outside CEOs [@kowalewski2019]. These findings point both ways. If founders carry value a successor cannot replace, their firing should be followed by a larger fall. If boards act against founders only when the case is overwhelming, it should be followed by a smaller fall or a rise [@taylor2010].

The third strand separates misconduct by the firm from misconduct by the person. Financial misreporting and executive scandals are both followed by falls in the share price [@cline2018; @larcker2016; @borellikjaer2021; @karpoff2008jfqa], and managers who misreport usually lose their jobs [@karpoff2008jfe]. Boards fire CEOs who manage earnings before outside penalties arrive [@hazarika2012], and more often where employees and directors are prosocial [@bereskin2020]. Shares also fall when a CEO is accused of sexual misconduct [@mooibroek2021] and when a firm reports sexual harassment [@abeysekera2024]. Board resignations rose at exposed firms after the #MeToo revelations of 2017 [@baharad2026]. @cline2018 measure the return when a personal indiscretion becomes public; we measure the firing that follows and set it against firings over fraud. A fraud tells investors that numbers they relied on were wrong, while a personal scandal concerns one person. A firing over a personal scandal should therefore be followed by a smaller fall.

Relative to these studies, the paper compares in one sample three things usually studied apart: who was fired, why the board acted, and what became of the firm. It follows each firing from six weeks before the announcement to five years after, with the number of firms measured at every horizon. It checks by hand who was a founder, why the board acted and, for founders and personal scandals, when the firing was announced.

## 3. Data and design

### Which firings

The departures come from the open CEO dismissal database of @gentry2021, which its authors have extended to cover 1992 to 2023. It codes the reason for every CEO departure at S&P {{index_size}} firms from press coverage and filings, and an independent recoding agreed with it on {{lit_gentry_agreement_pct}}% of events [@gentry2021]. Codes 3 and 4, dismissal for job performance and for legal violations or personal conduct, are firings. Code 5, voluntary retirement, is the comparison group.

Press releases rarely say that a CEO was fired [@gow2017], and how firings are classified changes the results [@fee2018]. Like the database, we treat a resignation under board pressure as a firing, including one during an investigation, a scandal or an activist campaign.

From the firings we remove the {{a.n_criminal_all_dates}} whose main reason is fraud or other legal violation. These cover financial misconduct, a legal or regulatory breach by the firm, and criminal charges against the CEO. They are a comparison group throughout, because there the firm itself is in trouble with the law. A personal scandal is a firing over sexual misconduct, a relationship with an employee, conduct at work or another personal failing such as a false degree. There are {{a.n_lr_conduct}} of them, of which {{a.n_lr_founder_personal}} are founders, too few for a test.

Each departure is linked to the firm's identifier at the Securities and Exchange Commission. Through it we take daily prices from Sharadar's Core US Equities data, which include firms later delisted. That leaves {{a.n_lr_forced}} firings and {{a.n_lr_retired}} retirements from 1998 to 2023 with share prices. Table IA.1 traces the firings from the database to the samples, and Figure IA.1 shows them by year. Firing firms are about half the size of retirement firms and less profitable (Table IA.2).

### Dating the announcement

A three-day window needs the right day. The database gives an announcement date for about a third of departures, and otherwise only the day the CEO left office, which can come weeks after the news. A second date comes from the firm's 8-K, the filing a company must make within four business days of a CEO change. Where the database does give a date, the two agree within 3 days in only {{redate_agree_3d_pct}}% of cases.

Of the {{a.n_lr_forced}} firings, {{a.n_forced}} are well-dated: by the database, or by hand from a dated source. The announcement tests use these. Results over months and years use all {{a.n_lr_forced}} firings, since an error of a few days is small against a year.

The well-dated firings are not a random draw. They are larger, fell less in the year before, and include more founders and personal scandals (Table IA.5). We dated those two groups by hand from 8-Ks, press releases and New York Times reports. Section 4 shows that the announcement fall survives reweighting and a wider window.

### Founders and reasons

Who was a founder, and why the board acted, come in two steps. First, a language model (DeepSeek, deepseek-chat) reads the database's notes and sources, the 8-K, cited press releases, the CEO's Wikipedia article and New York Times articles. It codes whether the CEO founded the firm, whether the exit was forced and the board's main reason, each with a supporting quote. We call this the evidence-based coding.

Second, one coder, the author, checked by hand every founder code on a firing and every code of fraud, sexual misconduct, a relationship or other personal conduct. The language model had coded {{b.model_founder_codes}} firings as founder removals; the hand check confirmed {{b.founders_confirmed}}, rejected {{b.founders_rejected}} and added {{b.founders_added}}. About half of the model's other personal-conduct codes turned out to be pay disputes, unexplained personal reasons or criminal charges. Table IA.1 reports how often each kind of code was changed. An independent second coder's check of a random fifth of the codes is planned before submission to a journal.

The evidence-based coding is cautious about whether an exit was forced. Of the {{car.forced.mm_m1p1.mean|n}} well-dated firings with returns, it reads {{strict.llm_yes.mm_m1p1.mean|n}} as forced, {{strict.llm_no.mm_m1p1.mean|n}} as not forced and {{strict.llm_unclear.mm_m1p1.mean|n}} as unclear, mostly because the sources do not say. Section 4 and Table 2 report the announcement return for the forced and the unclear groups separately.

### Returns

The announcement return is the abnormal return over the three trading days from the day before the announcement (day −1) to the day after it (day +1). The abnormal return is the stock's return minus what the market model of equation (1) predicts from the market's return and the stock's own past relation to it.

$$AR_{it} = R_{it} - \hat\alpha_i - \hat\beta_i R_{mt}, \qquad CAR_i = AR_{i,-1} + AR_{i,0} + AR_{i,+1}. \tag{1}$$

Here $R_{it}$ is the stock's total return and $R_{mt}$ the market's. The coefficients come from trading days {{estimation_window_start}} to {{estimation_window_end}} before the announcement. We test the mean with the cross-sectional t and the standardized test of @boehmer1991, and the median with the Wilcoxon signed-rank test [@kothari2007]. For the six weeks before and the three months after, we subtract the market's return instead. The reason is the slide before a firing. A stock that was falling gets a negative $\hat\alpha$, and subtracting that negative trend afterwards would make ordinary returns look like a recovery.

For the long run, the main measure is the buy-and-hold return from day +2 over {{days_1y}}, {{days_3y}} or {{days_5y}} trading days, that is one, three or five years. Equation (2) subtracts the return of the market or of a matched firm:

$$BHAR_i(h) = \prod_{t=2}^{T_h}(1+R_{it}) - \prod_{t=2}^{T_h}(1+R_{bt}). \tag{2}$$

The matched firm is in the same Fama-French industry, within {{matching_rule_pct}} percent in market value, with the nearest return on assets. It had no recorded CEO change in the three years before. Matching on prior profitability follows @barber1996, whose tests are well specified only when firms are matched on performance before the event. We also hold a calendar-time portfolio of every firm in its first 36 months after an announcement and regress its excess return on the five Fama-French factors and momentum [@famafrench2015; @lyon1999]. The intercept, the alpha, is the monthly return those risks do not explain.

On the day a firm is delisted, its return is set to zero for a takeover and minus 100% for a bankruptcy. Other delistings get minus 30%, close to the average loss on delistings for poor performance [@shumway1997]. Because firing firms are smaller, every long-run comparison is also made against a matched firm or within size bands.

## 4. The stock around the announcement

If the market had already priced the firing, the announcement would not move the shares; it does. Figure 1 shows the returns of firing and retirement firms from six weeks before the announcement to three months after it. For retirement firms the line stays within one percentage point of zero. For firing firms it slides for six weeks, drops at the announcement and then moves sideways.

![Figure 1. Prices slide before the firing, drop on the news, then stop](/static/reports/founder-ceo/figures/fig1_event_time.png)

*Figure 1. Prices slide before the firing, drop on the news, then stop.* Notes. Cumulative return minus the market from trading day -30 to day +60 around the announcement (day 0), well-dated firings with every day of the window. Panel (a) shows means, with the {{ci_level}}% confidence band for firings; the grey band marks days -1 to +1. Panel (b) shows medians, so that one firm cannot move a small group's line. The lines sum daily returns, so their end points differ slightly from the window returns of Table 1.

In the six weeks before the announcement, the shares of firing firms lag the market by {{drift.forced.pre_m30m2.mean|abs}}, while those of retirement firms do not move. Over the three trading days around it, their market-model abnormal return is {{car.forced.mm_m1p1.mean}}, against {{car.retired.mm_m1p1.mean}} for retirements (Table 2). Over the next three months they earn {{drift.forced.post_p2p60.mean}} against the market, which is {{drift.forced.post_p2p60.mean|sig}} (p {{drift.forced.post_p2p60.mean|p}}).

Is the fall an artefact of how firings are defined or dated? Not of the definition (Table 2, Panel C). Where the evidence-based coding agrees the exit was forced, the fall is {{strict.llm_yes.mm_m1p1.mean|abs}} (p {{strict.llm_yes.mm_m1p1.mean|p}}); where it is unclear, {{strict.llm_unclear.mm_m1p1.mean|abs}}; where it reads the exit as not forced, {{strict.llm_no.mm_m1p1.mean|abs}}. Reweighting the well-dated firings to resemble every firing gives {{dsel.ipw.mm_m1p1.mean|abs}}, and the five-factor model {{car.forced.ff5_m1p1.mean|abs}}.

Nor of the dating. Over every firing, whatever the source of its date, the three-day fall is only {{rob.all_dates.forced.mm_m1p1.mean|abs}}. A day 0 that comes days or weeks late puts the news outside the window. Widen the window to trading days −5 to +5 and every firing falls {{dsel.window.all.mm_m5p5.mean|abs}} (p {{dsel.window.all.mm_m5p5.mean|p}}), close to the well-dated firings' {{dsel.window.dated.mm_m5p5.mean|abs}} (Table IA.4).

<!-- TABLE:2 -->

### Personal scandals and fraud

Is a firing over a personal scandal different? After one, the shares fall {{car.conduct.mm_m1p1.mean|abs}} over the three days, against {{car.performance.mm_m1p1.mean|abs}} after other firings (Table 2). The scandal fall on its own is not quite significant (p {{car.conduct.mm_m1p1.mean|p}}, n = {{car.conduct.mm_m1p1.mean|n}}). With size, the prior year's return and the year held constant, the gap between the two is {{regc.car_m1p1.conduct}} (Table IA.4).

The scandal fall is {{equiv.scandal_gap.mm_m1p1.diff}} smaller, a gap that is {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean|sig}} (p {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean|p}}). With so few scandal firings the estimate is imprecise. Its 95% interval runs from {{equiv.scandal_gap.mm_m1p1.ci95_low}} to {{equiv.scandal_gap.mm_m1p1.ci95_high}}, and the test would detect only gaps of about {{equiv.scandal_gap.mm_m1p1.mde}}.

After a firing over fraud or other legal violation the shares fall {{car.criminal.mm_m1p1.mean|abs}}, {{cardiff.conduct_vs_criminal.mm_m1p1.diff_mean}} more than after a personal scandal (p {{cardiff.conduct_vs_criminal.mm_m1p1.diff_mean|p}}, n = {{cardiff.conduct_vs_criminal.mm_m1p1.diff_mean|n}}). This is not a clean measure of the firing. A fraud firing is often announced with the fraud itself. Its three-day fall therefore carries the news that the accounts or the business were wrong, as well as the news that the CEO is gone.

A scandal firing may be followed by little because the market priced the scandal when it first broke. To check, we searched the New York Times Archive for personal misconduct by sitting CEOs of the sample's firms and checked each report by hand (Table IA.8). The search finds {{scandal.n_events}} scandals. In {{scandal.n_departed}} the CEO left within a year; in {{scandal.n_kept}} the board kept them, among them Jeff Bezos at Amazon and Bobby Kotick at Activision Blizzard.

Over the three trading days around the first press report, the shares of the {{scandal.all.first_report.car_m1p1.mean|n}} scandal firms with prices fell {{scandal.all.first_report.car_m1p1.mean|abs}} against the market. They fell {{scandal.departed.first_report.car_m1p1.mean|abs}} where the CEO later left and {{scandal.kept.first_report.car_m1p1.mean|abs}} where the board kept them, too few cases to tell apart. The search finds only {{scandal.n_known_firings_found}} of the database's firings over a personal scandal, mostly at the largest firms, so these cases describe prominent scandals rather than test anything.

### Founders

Does it matter that the CEO built the company? A founder's firing is followed by a fall of {{car.forced_founder.mm_m1p1.mean|abs}} over the three days, against {{car.forced_nonfounder.mm_m1p1.mean|abs}} for a hired CEO (Table 2). The gap of {{equiv.founder_gap.mm_m1p1.diff}} is {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|sig}} (p {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|p}}).

This is not evidence that founders and hired CEOs are alike. With {{a.n_forced_founder}} well-dated founder firings, the 95% interval for the gap runs from {{equiv.founder_gap.mm_m1p1.ci95_low}} to {{equiv.founder_gap.mm_m1p1.ci95_high}}. The test would detect only gaps of about {{equiv.founder_gap.mm_m1p1.mde}} (Table IA.3). A formal equivalence test agrees: the data cannot rule out a founder gap as large as the average firing's whole fall (p {{equiv.founder_gap.mm_m1p1.tost_p|p}}). That margin is the size of the effect the paper studies, so a gap within it would still matter.

Founder firms also slide further before the announcement: {{drift.forced_founder.pre_m30m2.mean|abs}} over the six weeks, against {{drift.forced.pre_m30m2.mean|abs}} for all firings, on returns minus the market (Table IA.6). With firm size, the prior year's return and the year held constant, the founder gap is {{regc.car_m1p1.founder}} (p {{regc.car_m1p1.founder|p}}; Table IA.4).

Three founders were fired over a personal scandal: John Schnatter at Papa John's, Steve Wynn at Wynn Resorts and Vince McMahon at World Wrestling Entertainment (WWE). WWE's shares rose {{case.8370.car_m1p1}} over the three days around McMahon's departure (Table IA.9); three cases do not support a test.

## 5. Which firms are delisted

If the announcement fall is modest, does the firm itself do worse? A firm is delisted when its stock leaves the price file, through a takeover, a bankruptcy or another exit. Of the {{exit.forced.delisted_5y|n}} firing firms followed for a full 60 months, {{exit.forced.delisted_5y}} were delisted in that time: {{exit.forced.acquired_5y}} in a takeover and {{exit.forced.bankruptcy_5y}} in bankruptcy (Table 4, Figure 2).

![Figure 2. Within five years, {{exit.forced.delisted_5y}} of firing firms are delisted](/static/reports/founder-ceo/figures/fig3_exits.png)

*Figure 2. Within five years, {{exit.forced.delisted_5y}} of firing firms are delisted.* Notes. Cumulative share of firms delisted, by month after the announcement, for firms with a complete {{months_5y}}-month horizon: (a) for any reason, (b) in bankruptcy. Most of the rest are takeovers; Table 4 gives the shares.

After a retirement the shares are {{exit.retired.delisted_5y}} delisted, {{exit.retired.acquired_5y}} taken over and {{exit.retired.bankruptcy_5y}} bankrupt. Most of the gap is therefore bankruptcy. Takeovers are the larger share in both groups, which fits the view that board removal and takeover are two routes to a change of control [@morck1989].

Small firms fail more often, and firing firms are smaller, so Table 3 compares firms of similar size. In the smallest band, under $300 million in market value, {{exit.forced.size_small.bankruptcy_5y}} of firing firms go bankrupt within five years, against {{exit.retired.size_small.bankruptcy_5y}} of retirement firms. Above $5 billion the bankrupt shares are {{exit.forced.size_mega.bankruptcy_5y}} and {{exit.retired.size_mega.bankruptcy_5y}}. Firing firms are delisted more often in every band (Table 3).

<!-- TABLE:3 -->

Some firms were already failing when the CEO left: for {{exit.forced.early_bankruptcy_n}} of them a bankruptcy was recorded within 180 days of the announcement, as at Sears and Dana. Setting those aside, {{exit.forced.after.delisted_5y}} of firing firms are delisted within five years and {{exit.forced.after.bankruptcy_5y}} go bankrupt.

How much of the gap reflects firms that were weak already? With controls for size and profitability, firing firms are {{reg.exit5.gone.forced}} more likely than retirement firms to be delisted within five years (Table 4). Adding the prior year's return, debt, book-to-market, a distress score and a loss flag lowers the gap to {{reg.exit5c.gone.forced}} (p {{reg.exit5c.gone.forced|p}}). Of that gap, {{reg.exit5c.bankrupt.forced}} is bankruptcy. Debt is the strongest predictor among these controls (Table IA.10).

The gap survives three further checks (Table IA.10). Counting every month a firm is followed, including firms followed for less than five years, firing firms leave the market {{cox.gone.full.forced_hr}} times as fast with every control (p {{cox.gone.full.forced_hr|p}}). Where the evidence-based coding agrees the exit was forced, the controlled gap is {{strict.reg.gone.yes}} (p {{strict.reg.gone.yes|p}}). Against their own matched firms it is {{exitdiff.forced_vs_ctrl.delisted_5y}}.

The firing need not cause the delisting: a board may fire the CEO of a firm it already expects to struggle. Founder firms are delisted within five years in {{exit.forced_founder.delisted_5y}} of cases, and the gap from hired CEOs, {{exitdiff.forced_founder_vs_forced_nonfounder.delisted_5y}}, is {{exitdiff.forced_founder_vs_forced_nonfounder.delisted_5y|sig}} (p {{exitdiff.forced_founder_vs_forced_nonfounder.delisted_5y|p}}). After a personal scandal the share is {{exit.conduct.delisted_5y}} of only {{exit.conduct.delisted_5y|n}} firms, too few to compare (Table 4).

<!-- TABLE:4 -->

## 6. Returns, profits and the board over five years

Do the extra bankruptcies leave shareholders with lower returns? A portfolio holding every firm in its first three years after a firing earns an alpha of {{alpha.forced.ew.36m}} a month (Table IA.11). Its 95% interval runs from {{alpha.forced.ew.36m.ci_low}} to {{alpha.forced.ew.36m.ci_high}} a month, wide enough to include gains or losses of several percent over three years. Against a portfolio of retirement firms the difference is {{alphadiff.forced_vs_retired.ew.36m}} a month (p {{alphadiff.forced_vs_retired.ew.36m|p}}).

The portfolio of personal-scandal firms earns {{alpha.conduct.ew.36m}} a month (t = {{alpha.conduct.ew.36m|t}}; Table IA.11). It holds about a dozen firms at a time, so one or two firms can drive it. We do not read it as evidence that scandal firms do better.

Over the 60 months after the announcement, the median firing firm's buy-and-hold return trails the market's by {{bhar.forced.5y.median|abs}}, and the median retirement firm's by {{bhar.retired.5y.median|abs}} (Figure 3). But a typical stock lags an index over long horizons, because a few large winners lift the index average. A matched firm of the same industry, size and profitability removes that effect.

![Figure 3. Against the market the long run looks grim; against a matched firm it does not](/static/reports/founder-ceo/figures/fig2_long_run.png)

*Figure 3. Against the market the long run looks grim; against a matched firm it does not.* Notes. Median buy-and-hold return minus the market, month 1 to month {{months_5y}} after the announcement, in months of {{trading_days_per_month}} trading days from day +2, all firings. Diamonds mark the median return against a matched firm at {{months_1y}}, {{months_3y}} and {{months_5y}} months; Table IA.12 gives the numbers.

Against its matched firm, the median firing firm's buy-and-hold return is {{mbhar.forced.1y.median}} after one year (p {{mbhar.forced.1y.median|p}}). After three and five years it is {{mbhar.forced.3y.median}} and {{mbhar.forced.5y.median}}, neither significant (Table IA.12).

The means at three and five years are {{mbhar.forced.3y.mean}} and {{mbhar.forced.5y.mean}}. Neither is significant with the skewness-adjusted t test (p {{mbhar.forced.3y.skewadj_t|p}} and {{mbhar.forced.5y.skewadj_t|pv}}). A few large winners pull the mean above the median, which is why the median and the alpha are the measures we read.

Profits fall in the year of the firing and then recover. In the fiscal year of the departure, return on assets falls {{roa.forced.abn_d_0.median|abs}} percentage points against the matched firm (p {{roa.forced.abn_d_0.median|p}}; Table IA.13 and Figure IA.3). By fiscal year +2 the median gap is {{roa.forced.abn_d_2.median}} percentage points, on the firms still filing.

A firing may come with a wider change in who governs the firm, which would appear on the board. The proxy statement, the annual filing that lists the directors standing for election, records the board before and after a firing. Of the directors named in the last proxy statement before a firing, {{board.forced.director_turnover.mean}} are missing from the first one filed about two years later. After a retirement the share is {{board.retired.director_turnover.mean}} (Table IA.14). The measure counts every director who disappears, matched on surname and first initial; a proxy does not say whether a director resigned, was not nominated again or lost a vote.

Two years later a fired founder still sits on the board at {{board.forced_founder.founder_stays.mean}} of firms, against {{board.forced_nonfounder.ceo_stays_director.mean}} for a fired hired CEO and {{board.retired.ceo_stays_director.mean}} for a retired one (Table IA.14). The founder gap is not significant (p {{board.founder_vs_hired.ceo_stays_director.diff|p}}). These results cover the {{g.events_with_board_data}} departures whose firms filed a proxy statement both before and about two years after.

## 7. Discussion

The timing of the returns fits a simple account of what a firing tells investors. Boards fire CEOs after weeks of falling prices, as studies of forced turnover predict [@jenter2015]. The announcement then tells investors that matters were bad enough for the board to act, and the shares fall again. After that the shares of firing firms move much like those of matched firms. The firms that fail were mostly weak already: controls for debt, distress and the prior year's return remove more than half of the raw delisting gap (Table 4). We cannot tell whether the firing itself speeds failure, slows it or merely marks it.

Fraud firings and personal-scandal firings are followed by clearly different falls; founders and hired CEOs cannot yet be told apart. A fraud firing announces that the firm's numbers or conduct were wrong and that legal costs may follow; a personal scandal concerns one person. The announcement returns line up with that difference, although the fraud return also carries the fraud news. Treating the two as one group of misconduct would blur them. Within five years {{exit.criminal.delisted_5y}} of fraud-firing firms are delisted, {{exitdiff.criminal_vs_retired.delisted_5y}} more than after a retirement. After a personal scandal the share is {{exit.conduct.delisted_5y}}, but of only {{exit.conduct.delisted_5y|n}} firms, too few to compare (Table 4).

For founders the data cannot choose between the two readings of Section 2. A larger fall would suggest that founders carry value a successor cannot replace, and a smaller one that the firing ends entrenchment. The founder interval at the announcement includes both, and so do the founder gaps in delisting and in the long run. Answering it would take several times as many dated founder firings as large US firms have produced in a quarter century. Smaller listed firms, where founders are more common, are the place to look.

For directors and investors the null results carry a limited message. They do not mean that firing a founder, or firing over a scandal, is safe for shareholders (Table 2). Among large US firms such firings are simply too rare to measure the difference. The clearer lesson is where to look after any firing: at the firm's debt and its risk of failure, which the announcement return does not capture (Table 4).

## 8. Conclusion

When a board fires its CEO, the shares have usually been falling for weeks, and the announcement takes them lower still (Table 2). After the first year they move much like those of similar firms.

The reason for a firing matters at the announcement: fraud firings are followed by much larger falls, though those falls also carry the fraud news. Firings over a personal scandal and firings of founders are too rare in large US firms for precise estimates (Table 2).

What sets firing firms apart is failure: within five years {{exit.forced.bankruptcy_5y}} of them go bankrupt, against {{exit.retired.bankruptcy_5y}} after a retirement. The gap shrinks but remains with controls for debt and distress (Table 4).

The sample covers S&P {{index_size}} firms, so it says little about smaller companies, where founders often hold more control. Only three founders were fired over a personal scandal, and too few scandals in which the board kept its CEO reached the press to test. Fewer than half the firings have a precise announcement date, and the founder and reason codes rest on one coder's check. We do not follow who succeeds the CEO, although most new CEOs are insiders or people the board already knows [@cziraki2022]. The comparisons describe what follows a firing, not what would have happened had the board kept its CEO.

## Internet Appendix

### Sample and firms

Table IA.1 traces the firings from the CEO dismissal database to the samples, and Figure IA.1 counts them by year. Panel B of Table IA.1 shows how often the hand check changed the model's codes. It kept {{code.founder.share_kept}} of founder codes, {{code.fraud.share_kept}} of fraud and legal-violation codes and {{code.personal.share_kept}} of other personal-conduct codes. In the fiscal year before the departure, firing firms are smaller and less profitable than retirement firms: their median return on assets is {{desc.forced.roa.median}}, against {{desc.retired.roa.median}} (Table IA.2).

<!-- TABLE:IA.1 -->

![Figure IA.1. Firings per year](/static/reports/founder-ceo/figures/fig5_per_year.png)

*Figure IA.1. Firings per year.* Notes. Every firing in the database by year, 1998 to 2023, by the database's dismissal type, whether or not the firm has share prices, less firings over fraud or other legal violation. The bars therefore total more than the paper's {{a.n_lr_forced}} firings with prices. The number above each bar counts the hand-confirmed founders among them; the founder count in Table IA.1 also includes founders fired over fraud. The last year covers part of 2023.

<!-- TABLE:IA.2 -->

### The announcement

The founder gap is negative in all three windows of Table IA.3 and significant in none. With {{a.n_forced_founder}} founders, the smallest gap the main test could detect is {{mde.founder_gap.mm_m1p1}}.

<!-- TABLE:IA.3 -->

Table IA.4 changes one thing at a time against the main tables. With the five-factor model plus momentum, the founder gap is {{rob.founder_vs_nonfounder_ff5.m1p1.diff_mean}} and the personal-scandal gap {{rob.conduct_vs_performance_ff5.m1p1.diff_mean}}. Returns minus the market, with no estimated model, give {{rob.forced.ma_m1p1.mean}} over the three days. Using every firing, whatever its date source, gives {{rob.all_dates.forced.mm_m1p1.mean}}.

Table 2, Panel C, already splits the firings by how the evidence-based coding reads them. Excluding 2008 and 2009 gives {{rob.forced_excl_crisis.mm_m1p1.mean}}, and dropping firings coded as leaving for a new job gives {{rob.forced_excl_newopp.mm_m1p1.mean}}.

The long-run results do not depend on how delisting returns are set. With every delisting return at zero, the median three-year return against the market is {{rob.bhar_dl0.forced.3y.median}}, and setting every delisting that is not a takeover to minus 100% gives {{rob.bhar_dlworst.forced.3y.median}}. When no firm meets the size band the nearest firm in size is the match ({{h.relaxed_matches}} matches); using only matches within the band, the median three-year matched return is {{rob.mbhar_strict_matches.3y.median}}.

For departures from 1992 to 1997, before daily prices for delisted firms exist, we use the five-year return graphs that firms print in their proxy statements. Of these departures, {{pre.events_with_tsr}} have a usable graph, including {{pre.n_forced}} firings. The median three-year return against the firm's own reported index is {{pre.forced.abn_tsr_3y.median}} after firings and {{pre.retired.abn_tsr_3y.median}} after retirements. Only firms still filing three years later enter this check.

<!-- TABLE:IA.4 -->

Table IA.5 compares the well-dated firings with the others. The well-dated firms are larger, with a median market value of {{dsel.mcap_m1.dated}} billion dollars against {{dsel.mcap_m1.undated}}, and fell less over the prior year. They are also more recent, with a median year of {{dsel.year.dated}} against {{dsel.year.undated}}, and fewer of them are delisted within five years. Reweighting them to resemble every firing leaves the announcement return almost unchanged (Table 2).

<!-- TABLE:IA.5 -->

<!-- TABLE:IA.6 -->

Table IA.7 and Figure IA.2 split the firings by the reason coded for them. After a Holm correction for testing every reason, three falls remain statistically significant (Table IA.7). Where a push was described as a retirement or ill health the fall is {{car.reason.retirement_or_health.mm_m1p1.mean|abs}} (Holm p = {{car.reason.retirement_or_health.mm_m1p1.holm_p}}). Where the CEO was coded as leaving for a new job it is {{car.reason.new_opportunity.mm_m1p1.mean|abs}} (Holm p = {{car.reason.new_opportunity.mm_m1p1.holm_p}}). After other personal conduct it is {{car.reason.other_personal_conduct.mm_m1p1.mean|abs}} (Holm p = {{car.reason.other_personal_conduct.mm_m1p1.holm_p}}); performance and the other reasons do not survive the correction.

<!-- TABLE:IA.7 -->

![Figure IA.2. The announcement return by the reason the board acted](/static/reports/founder-ceo/figures/fig4_reasons.png)

*Figure IA.2. The announcement return by the reason the board acted.* Notes. Mean abnormal return over trading days -1 to +1 by the coded reason, well-dated firings, with {{ci_level}}% intervals; reasons with at least {{min_reason_cases}} firings. Table IA.7 gives the numbers.

Table IA.8 lists each scandal the New York Times search found, grouped by whether the board kept its CEO, with the return around the first report. The boards that kept their CEO include News Corp, Goldman Sachs, Amazon and Activision Blizzard; those whose CEO left include Boeing, Hewlett-Packard, Intel and McDonald's. Sexual relationships and harassment allegations appear on both sides. Table IA.9 lists the largest founders fired, with the return at the announcement and what became of the firm.

<!-- TABLE:IA.8 -->

<!-- TABLE:IA.9 -->

### Survival, returns, profits and the board

<!-- TABLE:IA.10 -->

<!-- TABLE:IA.11 -->

<!-- TABLE:IA.12 -->

<!-- TABLE:IA.13 -->

![Figure IA.3. Profits and the board after the firing](/static/reports/founder-ceo/figures/fig6_roa_board.png)

*Figure IA.3. Profits and the board after the firing.* Notes. (a) Median change in return on assets from fiscal year -1, minus the same change at the matched firm, in percentage points, fiscal years 0 to +3. (b) About two years after the departure, three shares: pre-departure directors not named in the later proxy, firms with a separate chair and CEO, and firms where the departing CEO is still a director. Firings are red and retirements grey; the diamond marks fired founders.

<!-- TABLE:IA.14 -->

## References
