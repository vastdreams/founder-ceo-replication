# Sacked: Sex, Fraud, Founders, and the Fate of Firms That Fire Their CEO

## Abstract

This paper answers what happens when a board fires its chief executive. At Standard & Poor's {{index_size}} firms the shares, already lagging the market, fall {{car.forced.mm_m1p1.mean|abs}} over the three trading days around the announcement of a firing. After a sex or other personal scandal the fall is similar, and {{rob.all_dates.conduct_vs_criminal.mm_m1p1.diff_mean}} smaller than after fraud or another legal violation. After a founder's firing it is {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|abs}} larger, which is not significant (p {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|p}}). Risk-adjusted returns over three years are near zero, yet {{exit.forced.delisted_5y}} of the firms are delisted within five years, against {{exit.retired.delisted_5y}} after retirements.

::: keynumbers

- **[−{{car.forced.mm_m1p1.mean|abs}}]{.focal}** share price over trading days −1 to +1 around the announcement of a firing (n = {{car.forced.mm_m1p1.mean|n}})

- **{{exit.forced.delisted_5y}}** of firing firms delisted within five years (n = {{exit.forced.delisted_5y|n}}), against {{exit.retired.delisted_5y}} after a retirement; {{reg.exit5c.gone.forced}} more with controls (p {{reg.exit5c.gone.forced|p}})

:::

## 1. Introduction

::: findings

1. In the six weeks before a firing is announced, the shares lag the market by {{drift.forced.pre_m30m2.mean|abs}} (Table 1).

2. Over the three trading days around the announcement they fall a further {{car.forced.mm_m1p1.mean|abs}}, and the next three months add no significant move (Table 1).

3. Over those three days the shares fall {{car.forced_founder.mm_m1p1.mean|abs}} when a founder is fired and {{car.forced_nonfounder.mm_m1p1.mean|abs}} when a hired chief executive is, a gap that is {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|sig}} (Table 2).

4. After a firing over a personal scandal the shares fall {{rob.all_dates.conduct.mm_m1p1.mean|abs}} over those three days, against {{rob.all_dates.criminal.mm_m1p1.mean|abs}} after a firing over fraud or another legal violation (Table 2).

5. Within five years firing firms are delisted more often than retirement firms of every size (Table 3). With controls for size, leverage and distress the gap is {{reg.exit5c.gone.forced}} (Table 4).

:::

In 1985 Apple's board sided with its new chief executive against Steve Jobs, and Jobs left the company he had founded. By 1997 Apple had bought his next company and he was back in charge. In November 2026 Nvidia's board accepted the resignation of its co-founder and chief executive, Jensen Huang [@nvidia2026form8k]. Three days earlier it had opened an independent investigation after reports that Huang had been the target of a foreign intelligence effort [@nvidia2026board]. News reports also described an affair [@cnbc2026nvidia]. The board gave no reason.

Nvidia's shares closed {{hook.nvda.day_ret|abs}} lower that day, after falling as much as {{nvda_intraday_low_pct}}% during the session [@cnbc2026nvidia]. By 18 November they had lost {{hook.nvda.since_board_statement|abs}} from the last close before the board's statement. Every investor, director and employee asks the same thing when a board turns on its chief executive: what happens to the company now? And does it matter that the person fired built it, or that the trouble was a scandal rather than the business?

This paper answers both questions for the chief executives that Standard & Poor's (S&P) {{index_size}} boards fired from 1998 to 2023. There are {{a.n_lr_forced}} such firings with share prices, {{a.n_lr_forced_founder}} of them of founders. Firings over fraud or another legal violation are a different event, because the firm itself is in trouble with the law, so those {{a.n_criminal_all_dates}} are kept apart as a comparison.

The short answer is that the market has usually seen it coming. Boards tend to fire chief executives after poor results [@jenter2015], and in the six weeks before the announcement the shares lag the market by {{drift.forced.pre_m30m2.mean|abs}}. At the announcement they fall a further {{car.forced.mm_m1p1.mean|abs}} over three trading days, and then they stop: the next three months add no significant move (Table 1). Against a similar firm they trail by a further {{mbhar.forced.1y.median|abs}} over the first year (p {{mbhar.forced.1y.median|p}}), and not significantly after that.

Founders and sex scandals make the headlines, but they change the reaction little. When the chief executive founded the firm, the fall at the announcement is larger, {{car.forced_founder.mm_m1p1.mean|abs}} against {{car.forced_nonfounder.mm_m1p1.mean|abs}}, but not significantly so (p {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|p}}; Table 2). Hold firm size and the prior year's return constant, and the founder gap is {{regc.car_m1p1.founder}} in the other direction (p {{regc.car_m1p1.founder|p}}). A sex or other personal scandal is followed by about the same fall as any other firing. Fraud is the exception: after a firing over fraud or another legal violation the fall is {{rob.all_dates.conduct_vs_criminal.mm_m1p1.diff_mean}} larger than after a personal scandal (Table 2).

What does change is survival. Within five years {{exit.forced.delisted_5y}} of firing firms are delisted, against {{exit.retired.delisted_5y}} after a retirement, and the gap holds in every size band (Table 3 and Table 4). Yet once risk is priced the shares earn about what they should. A portfolio of firing firms, held for three years after each announcement, earns {{alpha.forced.ew.36m}} a month after the five Fama-French factors and momentum. That portfolio includes the firms that failed. One reading is that a firing marks a firm whose risk has risen, and that the price already reflects it.

Table 1 sets out each result with its horizon and the number of firings behind it.

::: glance

### Table 1. The firing, horizon by horizon: S&P {{index_size}} firms, 1998 to 2023

| Horizon | What is measured | Firings | Retirements | N firings | p |
|---|---|---|---|---|---|
| Trading days -30 to -2 | Return minus the market | {{drift.forced.pre_m30m2.mean}} | {{drift.retired.pre_m30m2.mean}} | {{drift.forced.pre_m30m2.mean!n}} | {{drift.forced.pre_m30m2.mean!pv}} |
| Trading days -1 to +1 | Abnormal return, market model | {{car.forced.mm_m1p1.mean}} | {{car.retired.mm_m1p1.mean}} | {{car.forced.mm_m1p1.mean!n}} | {{car.forced.mm_m1p1.mean!pv}} |
| Trading days +2 to +60 | Return minus the market | {{drift.forced.post_p2p60.mean}} | {{drift.retired.post_p2p60.mean}} | {{drift.forced.post_p2p60.mean!n}} | {{drift.forced.post_p2p60.mean!pv}} |
| {{months_1y}} months | Return minus a matched firm, median | {{mbhar.forced.1y.median}} | {{mbhar.retired.1y.median}} | {{mbhar.forced.1y.median!n}} | {{mbhar.forced.1y.median!pv}} |
| {{months_3y}} months | Return minus a matched firm, median | {{mbhar.forced.3y.median}} | {{mbhar.retired.3y.median}} | {{mbhar.forced.3y.median!n}} | {{mbhar.forced.3y.median!pv}} |
| {{months_3y}} months | Five-factor and momentum alpha, a month | {{alpha.forced.ew.36m}} | {{alpha.retired.ew.36m}} | {{alpha.forced.ew.36m!n}} | {{alpha.forced.ew.36m!pv}} |
| {{months_5y}} months | Return minus a matched firm, median | {{mbhar.forced.5y.median}} | {{mbhar.retired.5y.median}} | {{mbhar.forced.5y.median!n}} | {{mbhar.forced.5y.median!pv}} |
| Within {{months_5y}} months | Share of firms delisted | {{exit.forced.delisted_5y}} | {{exit.retired.delisted_5y}} | {{exit.forced.delisted_5y!n}} | {{exitdiff.forced_vs_retired.delisted_5y!pv}} |
| Fiscal year +1 | Change in ROA minus the matched firm, median (pp) | {{roa.forced.abn_d_1.median}} | {{roa.retired.abn_d_1.median}} | {{roa.forced.abn_d_1.median!n}} | {{roa.forced.abn_d_1.median!pv}} |
| About two years | Share of pre-firing directors not in the later proxy | {{board.forced.director_turnover.mean}} | {{board.retired.director_turnover.mean}} | {{board.forced.director_turnover.mean!n}} | {{boarddiff.forced_vs_retired.director_turnover.diff_mean!pv}} |

*Notes.* Firings exclude firings over fraud or another legal violation. Day 0 is the first trading day on or after the announcement. The first three rows use hand-dated firings, the rest every firing. A month is {{trading_days_per_month}} trading days from day +2. For the alpha row, N counts calendar months and the portfolio holds firms for 36 months after the announcement. N falls with the horizon as recent firings have not reached it. p tests the firing number against zero, or, for the delisted and directors rows, against retirements.

:::

## 2. Related work

Boards fire chief executives after poor performance, including poor performance of the whole industry [@jenter2015], and returns fall well before the change [@weisbach1988]. Forced exits are rare, which suggests that boards behave as if replacing a chief executive were costly [@taylor2010; @kaplan2012]. How the market reacts depends on what the firing reveals about the firm [@kind2011; @chen2026]. A firing should therefore lower the share price at the announcement, but by less than the decline that preceded it.

Founder-led firms invest differently and have been valued more highly [@fahlenbrach2009]. Founder status itself responds to performance [@adams2009], founders are often replaced as their firms mature [@wasserman2003; @aran2024], and in venture-backed startups replacing the founder improves outcomes [@ewens2018]. If founders carry value a successor cannot replace, their firing should cost more. If boards act against founders only when the case is overwhelming, the firing could end entrenchment and be good news [@taylor2010].

Executive scandals and financial misreporting both cost shareholders [@cline2018; @larcker2016; @borellikjaer2021; @karpoff2008jfqa], and managers who misreport usually lose their jobs [@karpoff2008jfe]. Studies of misconduct usually combine the two. A fraud tells investors that numbers they relied on were wrong, while a personal scandal concerns one person, so a firing over a personal scandal should cost less.

Against this work, the paper separates firings over a personal scandal from firings over fraud, which studies of misconduct usually combine. It follows each firing from six weeks before the announcement to five years after, with the number of firms measured at every horizon. And it checks by hand who was a founder and why the board acted, wherever an error would change a result.

## 3. Data and design

### Which firings

The departures come from the open CEO dismissal database of @gentry2021, extended by its authors to 2023. It codes the reason for every chief executive departure at S&P {{index_size}} firms from press coverage and filings, and an independent recoding agreed with it on {{lit_gentry_agreement_pct}}% of events [@gentry2021]. Codes 3 and 4, dismissal for job performance and for legal violations or personal conduct, are firings. Code 5, voluntary retirement, is the comparison group.

Press releases rarely say that a chief executive was fired [@gow2017], and how forced exits are classified changes the results [@fee2018]. Like the database, we treat a resignation under board pressure as a firing, including one during an investigation, a scandal or an activist campaign.

From the firings we remove the {{a.n_criminal_all_dates}} whose main reason is fraud or another legal violation. These are financial misconduct, a legal or regulatory breach by the firm, or a criminal charge against the chief executive. A personal scandal is a firing over sexual misconduct, a relationship with an employee, conduct at work or another personal failing such as a false degree. There are {{a.n_lr_conduct}} of them, of which {{a.n_lr_founder_personal}} are founders, too few for a test.

Each departure is linked to the firm's Central Index Key, its identifier at the Securities and Exchange Commission, and through it to daily prices that include firms later delisted. Table IA.1 traces the firings from the database to the samples, and Figure IA.1 shows them by year.

### Dating the announcement

A three-day window needs the right day. The database gives an announcement date for about a third of departures, and otherwise only the day the chief executive left office, which can come weeks after the news. The firm's own 8-K filing on the departure gives a second date, but on departures the database does date, the two agree within 3 days in only {{redate_agree_3d_pct}}% of cases.

That is too noisy for a three-day window. Firings dated by the database earn {{rob.datesrc_database.mm_m1p1.mean}} over three days and firings dated from a filing {{rob.datesrc_8k.mm_m1p1.mean}}, as a misplaced day 0 would produce. Announcement results therefore use the {{a.n_forced}} firings dated by the database or by hand. Results over months and years use all {{a.n_lr_forced}}, which a few days of error cannot move.

### Founders and reasons

For each departure a language model (DeepSeek, deepseek-chat, at temperature zero) codes whether the chief executive founded the firm or its predecessor. It also codes the board's main reason, each with a supporting quote. It reads the database's notes and sources, the firm's 8-K, cited press releases, the chief executive's Wikipedia article and matching New York Times articles.

Every code that could change a result was then checked by hand, by one coder; a second coder's check of a random fifth of the codes is planned. The model coded {{b.model_founder_codes}} firings as founder removals; the review confirmed {{b.founders_confirmed}}, rejected {{b.founders_rejected}} and added {{b.founders_added}}. Every financial-misconduct, sexual-misconduct, relationship and other personal-conduct code was checked too. About half of the model's other personal-conduct codes turned out to be pay disputes, unexplained personal reasons or criminal charges.

### Returns

The announcement return is the abnormal return over the three trading days from the day before the announcement to the day after it, from the market model of equation (1):

$$AR_{it} = R_{it} - \hat\alpha_i - \hat\beta_i R_{mt}, \qquad CAR_i = AR_{i,-1} + AR_{i,0} + AR_{i,+1}. \tag{1}$$

Here $R_{it}$ is the stock's total return and $R_{mt}$ the market's. The coefficients come from trading days {{estimation_window_start}} to {{estimation_window_end}} before the announcement. We test the mean with the cross-sectional t and the standardized test of @boehmer1991, and the median with the Wilcoxon signed-rank test [@kothari2007]. Over the six weeks before and three months after, we use returns minus the market. A falling firm's negative alpha would otherwise forecast a rebound that is not in the prices.

The long run is measured three ways. The first is the buy-and-hold return over {{days_1y}}, {{days_3y}} or {{days_5y}} trading days from day +2, minus the market's or a matched firm's, as in equation (2):

$$BHAR_i(h) = \prod_{t=2}^{T_h}(1+R_{it}) - \prod_{t=2}^{T_h}(1+R_{bt}). \tag{2}$$

The matched firm is in the same Fama-French industry, within {{matching_rule_pct}} percent in market value, with the nearest return on assets. It had no recorded chief executive change in the three years before. The second measure is calendar-time alpha. Each month a portfolio holds every firm in its first 36 months after an announcement, and its excess return is regressed on the five Fama-French factors and momentum [@famafrench2015; @lyon1999]. The third is whether the stock is still listed.

On the day a firm is delisted, its return is set to zero for a takeover, minus 100% for a bankruptcy and minus 30% otherwise [@shumway1997]. Firms that fire their chief executive are about half the size of those whose chief executive retires. Their median market value at the fiscal year-end before is {{desc.forced.mcap.median}} billion dollars, against {{desc.retired.mcap.median}} (Table IA.2). Every long-run comparison is therefore also made against a matched firm or within size bands.

## 4. The stock around the announcement

Figure 1 tells the story of the announcement in one picture. For firms whose chief executive retires, the line barely moves. For firms that fire the chief executive, it slides for six weeks, drops at the announcement and then goes sideways.

![Figure 1. Prices slide before the firing, drop on the news, then stop](/static/reports/founder-ceo/figures/fig1_event_time.png)

*Figure 1. Prices slide before the firing, drop on the news, then stop.* Notes. Mean cumulative return minus the market from trading day -30 to day +60 around the announcement (day 0), hand-dated firings. Panel (a) shows the {{ci_level}}% confidence band for firings; the grey band marks days -1 to +1. Panel (b) splits the firings by founder status and by whether the board acted over a personal scandal. N is the number of departures with every day of the window.

Both the slide and the drop are large. In the six weeks before the announcement the shares of firing firms lag the market by {{drift.forced.pre_m30m2.mean|abs}}, while those of retirement firms do not move ({{drift.retired.pre_m30m2.mean}}). Over the three days around the announcement they fall a further {{car.forced.mm_m1p1.mean|abs}} (t = {{car.forced.mm_m1p1.mean|t}}), against {{car.retired.mm_m1p1.mean}} for retirements (Table 2).

The drop survives the usual checks. On the same {{car.forced.mm_m1p1.mean|n}} firings the standardized test gives t = {{car.forced.mm_m1p1.bmp_t}}, and the five-factor model gives an abnormal return of {{car.forced.ff5_m1p1.mean}} over the same three days. Then the shares stop falling: over the next three months they earn {{drift.forced.post_p2p60.mean}} against the market, which is {{drift.forced.post_p2p60.mean|sig}} (p {{drift.forced.post_p2p60.mean|p}}, n = {{drift.forced.post_p2p60.mean|n}}).

<!-- TABLE:2 -->

### Founders

Theory pulls both ways on founders: a founder may carry value no successor can replace, or the firing may end an entrenched reign. The data lean neither way. A founder's firing is followed by a fall of {{car.forced_founder.mm_m1p1.mean|abs}} over the three days, against {{car.forced_nonfounder.mm_m1p1.mean|abs}} for a hired chief executive (Table 2). The gap of {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean}} is {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|sig}} (p {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|p}}). Nor is there a hint of relief: the upper end of the {{ci_level}}% interval for fired founders is {{car.forced_founder.mm_m1p1.ci_high}}, so the data rule out more than a small gain.

The test has little power, and a few large losses pull the average down. With only {{a.n_forced_founder}} hand-dated founder firings it could detect only a gap of about {{mde.founder_gap.mm_m1p1}} (Table IA.3). The median founder firing is followed by a fall of {{car.forced_founder.mm_m1p1.median|abs}}, against {{car.forced_nonfounder.mm_m1p1.median|abs}} for hired chief executives (Table 2). Holding firm size, the prior year's return and the year constant, the founder gap is {{regc.car_m1p1.founder}} in the other direction (p {{regc.car_m1p1.founder|p}}; Table IA.4).

Founder firms do slide further beforehand, {{drift.forced_founder.pre_m30m2.mean|abs}} over the six weeks against {{drift.forced.pre_m30m2.mean|abs}} for all firings (Table IA.5). Over trading days -30 to +30, however, the founder gap is only {{cardiff.forced_founder_vs_forced_nonfounder.mm_m30p30.diff_mean}} (Table IA.3). Whatever the market learns from a founder's firing, it seems to learn before the board speaks.

### Personal scandals

Sex scandals make headlines, but the market reacts to them much as it does to any other firing. Only {{car.conduct.mm_m1p1.mean|n}} firings over a personal scandal have a hand-checked date, so we measure them on every date source. On all {{rob.all_dates.conduct.mm_m1p1.mean|n}}, the shares move {{rob.all_dates.conduct.mm_m1p1.mean}} over the three days, which is {{rob.all_dates.conduct.mm_m1p1.mean|sig}} (Table 2). Other firings move {{rob.all_dates.performance.mm_m1p1.mean}} on the same measure, a difference of {{rob.all_dates.conduct_vs_performance.mm_m1p1.diff_mean}} (p {{rob.all_dates.conduct_vs_performance.mm_m1p1.diff_mean|p}}). Table IA.6 and Figure IA.2 break the remaining firings down by the reason coded for them.

With size, the prior year's return and the year held constant, the personal-scandal gap is {{regc.car_m1p1.conduct}} (p {{regc.car_m1p1.conduct|p}}, n = {{regc.car_m1p1.conduct|n}}; Table IA.4). Fraud is another matter: after a firing over fraud or another legal violation the shares fall {{rob.all_dates.criminal.mm_m1p1.mean|abs}} (Table 2). Why would the shares react so little to a scandal? The firing may say little about the business, or the market may have priced the scandal when it first broke. The firing alone cannot separate the two, so we went back to the first report.

We searched the New York Times Archive for personal misconduct by sitting chief executives of the sample's firms and checked each report by hand (Table IA.7). The search finds {{scandal.n_events}} scandals. In {{scandal.n_departed}} the chief executive left within a year; in {{scandal.n_kept}} the board kept them, among them Jeff Bezos at Amazon and Bobby Kotick at Activision Blizzard. It finds only {{scandal.n_known_firings_found}} of the database's firings over a personal scandal, mostly at the largest firms, so these cases describe prominent scandals and support no test.

For the {{scandal.all.first_report.car_m1p1.mean|n}} scandals with share prices at the time, the shares fell {{scandal.all.first_report.car_m1p1.mean|abs}} against the market over the three trading days around the first report. They fell {{scandal.departed.first_report.car_m1p1.mean|abs}} where the chief executive later left ({{scandal.departed.first_report.car_m1p1.mean|n}} cases) and {{scandal.kept.first_report.car_m1p1.mean|abs}} where the board kept them ({{scandal.kept.first_report.car_m1p1.mean|n}}), too few cases to tell apart.

Three founders were fired over a personal scandal: John Schnatter at Papa John's, Steve Wynn at Wynn Resorts and Vince McMahon at World Wrestling Entertainment (WWE). WWE's shares rose {{case.8370.car_m1p1}} over the three days around McMahon's departure (Table IA.8); three cases do not support a test.

## 5. Which firms are delisted

The lasting difference is survival. Figure 2 follows the firms with a complete five-year horizon month by month. Within five years of a firing {{exit.forced.delisted_5y}} of the {{exit.forced.delisted_5y|n}} firms have been delisted, against {{exit.retired.delisted_5y}} of the {{exit.retired.delisted_5y|n}} firms after a retirement. In that time {{exit.forced.acquired_5y}} of firing firms are taken over and {{exit.forced.bankruptcy_5y}} go bankrupt.

![Figure 2. Within five years, {{exit.forced.delisted_5y}} of firing firms are delisted](/static/reports/founder-ceo/figures/fig3_exits.png)

*Figure 2. Within five years, {{exit.forced.delisted_5y}} of firing firms are delisted.* Notes. Cumulative share of firms no longer trading, by month after the announcement, for firms with a complete {{months_5y}}-month horizon: (a) for any reason, (b) in bankruptcy. Most of the rest are takeovers; Table 4 gives the shares.

A natural worry is size: firing firms are about half as large, and small firms fail more often. Table 3 therefore compares firms of similar size. In the smallest band, under $300 million, {{exit.forced.size_small.bankruptcy_5y}} of firing firms go bankrupt within five years, against {{exit.retired.size_small.bankruptcy_5y}} of retirement firms. Above $5 billion the bankrupt shares are {{exit.forced.size_mega.bankruptcy_5y}} and {{exit.retired.size_mega.bankruptcy_5y}}.

The gap in delisting holds in every band. In the $1 to 5 billion band, {{exit.forced.size_large.delisted_5y}} of firing firms are delisted within five years, against {{exit.retired.size_large.delisted_5y}} of retirement firms (p {{exitdiff.forced_vs_retired.size_large.delisted_5y|p}}; Table 3).

<!-- TABLE:3 -->

Some firms were already failing when the chief executive left: for {{exit.forced.early_bankruptcy_n}} of them a bankruptcy was recorded within 180 days of the announcement, as at Sears and Dana. Setting those aside, {{exit.forced.after.delisted_5y}} of firing firms are delisted within five years and {{exit.forced.after.bankruptcy_5y}} go bankrupt.

Controls shrink the gap but do not close it. With controls for size, return on assets, year and industry, firing firms remain {{reg.exit5.gone.forced}} more likely to be delisted within five years (Table 4 and Table IA.9). Adding the prior year's return, leverage, book-to-market, a distress score and a loss flag lowers the gap to {{reg.exit5c.gone.forced}} (p {{reg.exit5c.gone.forced|p}}). Of that, {{reg.exit5c.bankrupt.forced}} is bankruptcy. Leverage predicts delisting strongly (t = {{reg.exit5c.gone.leverage_w|t}}).

Against their matched firms the difference is {{exitdiff.forced_vs_ctrl.delisted_5y}} (p {{exitdiff.forced_vs_ctrl.delisted_5y|p}}; Table IA.9). The firing need not cause the delisting: a board may fire the chief executive of a firm it already expects to struggle.

Founders and scandals again look ordinary. Founder firms are delisted within five years in {{exit.forced_founder.delisted_5y}} of cases (Table 4). The difference from hired chief executives is {{exitdiff.forced_founder_vs_forced_nonfounder.delisted_5y|sig}} (p {{exitdiff.forced_founder_vs_forced_nonfounder.delisted_5y|p}}), and {{reg.exit5c.gone.founder}} with the full controls. After a personal scandal the share is {{exit.conduct.delisted_5y}}, close to the {{exit.retired.delisted_5y}} after a retirement. Most delistings are takeovers, which fits the view that board removal and takeover are two routes to a change of control [@morck1989].

<!-- TABLE:4 -->

## 6. Returns, profits and the board over five years

If firing firms fail more often, do their shareholders lose more? Once risk is priced, not by any margin the data can detect. A portfolio of every firm in its first 36 months after a firing earns an alpha of {{alpha.forced.ew.36m}} a month equally weighted (t = {{alpha.forced.ew.36m|t}}) and {{alpha.forced.vw.36m}} value-weighted (Table IA.10). The difference from a portfolio of retirement firms is {{alphadiff.forced_vs_retired.ew.36m}} a month (t = {{alphadiff.forced_vs_retired.ew.36m|t}}), which is {{alphadiff.forced_vs_retired.ew.36m|sig}}.

Against the market alone the picture looks much worse. After five years the median firing firm's buy-and-hold return trails the market by {{bhar.forced.5y.median|abs}}, and the median retirement firm's by {{bhar.retired.5y.median|abs}} (Figure 3). The typical stock lags an index over long horizons because returns are skewed, and firing firms are small and have been falling; the factor model allows for both.

![Figure 3. Against the market the long run looks grim; against a matched firm it does not](/static/reports/founder-ceo/figures/fig2_long_run.png)

*Figure 3. Against the market the long run looks grim; against a matched firm it does not.* Notes. Median buy-and-hold return minus the market, month 1 to month {{months_5y}} after the announcement, in months of {{trading_days_per_month}} trading days from day +2, all firings. Diamonds mark the median return against a matched firm at {{months_1y}}, {{months_3y}} and {{months_5y}} months; Table IA.11 gives the numbers.

A matched firm of the same industry, size and profitability is the fairer yardstick. Against it, the median firing firm's buy-and-hold return is {{mbhar.forced.1y.median}} after one year (p {{mbhar.forced.1y.median|p}}). After three and five years it is {{mbhar.forced.3y.median}} and {{mbhar.forced.5y.median}}, neither statistically significant (Table IA.11). For fired founders the matched medians are {{mbhar.forced_founder.3y.median}} and {{mbhar.forced_founder.5y.median}}.

Profits barely move either. Return on assets changes little against the matched firm (Table IA.12 and Figure IA.3). In the first fiscal year after a firing the median change is {{roa.forced.abn_d_1.median}} percentage points, which is {{roa.forced.abn_d_1.median|sig}} (p {{roa.forced.abn_d_1.median|p}}). By fiscal year +3 it is {{roa.forced.abn_d_3.median}}, on the firms still filing.

The board changes more visibly. About two years after a firing, {{board.forced.director_turnover.mean}} of the earlier directors are no longer named in the proxy statement, against {{board.retired.director_turnover.mean}} after a retirement (Table IA.13). A proxy statement lists the directors standing for election, not why others left, so these shares do not separate resignations, directors not nominated again and lost votes. Directors are matched on surname and first initial, which may overstate both shares.

A fired founder sits on the board two years later at {{board.forced_founder.founder_stays.mean}} of firms, against {{board.forced_nonfounder.ceo_stays_director.mean}} for a fired hired chief executive and {{board.retired.ceo_stays_director.mean}} for a retired one (Table IA.13). These results cover the {{g.events_with_board_data}} departures whose firms filed a proxy statement both before and about two years after.

## 7. Firings over fraud and legal violations

Fraud does change the market's verdict. The {{a.n_criminal_all_dates}} firings over fraud, a legal or regulatory breach, or a criminal charge are a different event, since the firm itself is in trouble with the law. Over the three days around the announcement their shares fall {{rob.all_dates.criminal.mm_m1p1.mean|abs}}, on every firing whatever its date source (Table 2). After a personal scandal the shares fall {{rob.all_dates.conduct.mm_m1p1.mean|abs}} on the same measure. The difference of {{rob.all_dates.conduct_vs_criminal.mm_m1p1.diff_mean}} is {{rob.all_dates.conduct_vs_criminal.mm_m1p1.diff_mean|sig}} (p {{rob.all_dates.conduct_vs_criminal.mm_m1p1.diff_mean|p}}; Table 2). One reading is that a fraud tells investors the numbers they relied on were wrong, while a personal scandal concerns one person, whom the firing removes.

In the long run, {{exit.criminal.delisted_5y}} of the firms that fired their chief executive over fraud or another legal violation are delisted within five years. That is {{exitdiff.criminal_vs_retired.delisted_5y}} more than after a retirement (p {{exitdiff.criminal_vs_retired.delisted_5y|p}}). After a personal scandal the share is {{exit.conduct.delisted_5y}}, not significantly different from retirements (p {{exitdiff.conduct_vs_retired.delisted_5y|p}}; Table 4). Treating both as misconduct, as earlier studies often do, would hide the difference at the announcement.

## 8. Conclusion

Boards rarely surprise the market when they fire a chief executive. The shares have usually fallen for weeks; they fall a further {{car.forced.mm_m1p1.mean|abs}} over the three days around the announcement and then stop. Against similar firms they trail by a further {{mbhar.forced.1y.median|abs}} in the first year, and the gap is not significant at three or five years (Table 1).

Neither a founder at the top nor a sex scandal changes that picture much. When a founder is fired the shares fall {{car.forced_founder.mm_m1p1.mean|abs}} on average, against {{car.forced_nonfounder.mm_m1p1.mean|abs}} for a hired chief executive, a gap that is {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|sig}} (p {{cardiff.forced_founder_vs_forced_nonfounder.mm_m1p1.diff_mean|p}}; Table 2). It disappears once firm size and the prior year's return are held constant. After a personal scandal the shares fall about as much as after any other firing, and {{rob.all_dates.conduct_vs_criminal.mm_m1p1.diff_mean}} less than after fraud or another legal violation. These firms are delisted about as often as firms whose chief executive retired.

What does change is the chance that the firm survives. Within five years firing firms are delisted more often than retirement firms in every size band, a gap that shrinks but remains once leverage and distress are held constant. A portfolio of all firing firms, including those that failed, earns an abnormal return close to zero once risk is priced.

The sample covers S&P {{index_size}} firms, so it says little about smaller companies, where founders often hold more control. Only three founders were fired over a personal scandal, and too few scandals in which the board kept its chief executive reached the press to test. Announcement dates are precise for part of the sample only. Proxy statements do not say why a director left. The comparisons describe what follows a firing, not what would have happened had the board kept its chief executive.

## Internet Appendix

### Sample and firms

Table IA.1 traces the firings from the CEO dismissal database to the samples, and Figure IA.1 counts them by year. In the fiscal year before the departure, firing firms are smaller and less profitable than retirement firms: their median return on assets is {{desc.forced.roa.median}}, against {{desc.retired.roa.median}} (Table IA.2).

<!-- TABLE:IA.1 -->

![Figure IA.1. Firings per year](/static/reports/founder-ceo/figures/fig5_per_year.png)

*Figure IA.1. Firings per year.* Notes. Firings by year, 1998 to 2023, by the database's dismissal type, after firings over fraud or another legal violation are removed; the number above each bar counts the founders among them. The last year covers part of 2023.

<!-- TABLE:IA.2 -->

### The announcement

The founder gap is negative in all four windows of Table IA.3 and significant in none. With {{a.n_forced_founder}} founders, the smallest gap the main test could detect is {{mde.founder_gap.mm_m1p1}}.

<!-- TABLE:IA.3 -->

Table IA.4 changes one thing at a time against the main tables. With the five-factor model plus momentum, the founder gap is {{rob.founder_vs_nonfounder_ff5.m1p1.diff_mean}} and the personal-scandal gap {{rob.conduct_vs_performance_ff5.m1p1.diff_mean}}. Returns minus the market, with no estimated model, give {{rob.forced.ma_m1p1.mean}} over the three days. Using every firing, whatever its date source, gives {{rob.all_dates.forced.mm_m1p1.mean}}.

On the {{a.n_forced_strict}} hand-dated firings that the evidence-based coding also reads as forced, the return over trading days -1 to +1 is {{car.forced_strict.mm_m1p1.mean}}. Excluding 2008 and 2009 gives {{rob.forced_excl_crisis.mm_m1p1.mean}}, and dropping firings coded as leaving for a new job gives {{rob.forced_excl_newopp.mm_m1p1.mean}}.

The long-run results do not depend on how delisting returns are set. With every delisting return at zero, the median three-year return against the market is {{rob.bhar_dl0.forced.3y.median}}, and setting every delisting that is not a takeover to minus 100% gives {{rob.bhar_dlworst.forced.3y.median}}. When no firm meets the size band the nearest firm in size is the match ({{h.relaxed_matches}} matches); using only matches within the band, the median three-year matched return is {{rob.mbhar_strict_matches.3y.median}}.

For departures from 1992 to 1997, before daily prices for delisted firms exist, we use the five-year return graphs that firms print in their proxy statements. Of these departures, {{pre.events_with_tsr}} have a usable graph, including {{pre.n_forced}} firings. The median three-year return against the firm's own reported index is {{pre.forced.abn_tsr_3y.median}} after firings and {{pre.retired.abn_tsr_3y.median}} after retirements. Only firms still filing three years later enter this check.

<!-- TABLE:IA.4 -->

<!-- TABLE:IA.5 -->

Table IA.6 and Figure IA.2 split the firings by the reason coded for them. After a Holm correction for testing every reason, two falls remain statistically significant (Table IA.6). Where a push was described as a retirement or ill health the fall is {{car.reason.retirement_or_health.mm_m1p1.mean|abs}} (Holm p = {{car.reason.retirement_or_health.mm_m1p1.holm_p}}). Where the chief executive was coded as leaving for a new job it is {{car.reason.new_opportunity.mm_m1p1.mean|abs}} (Holm p = {{car.reason.new_opportunity.mm_m1p1.holm_p}}). Strategy or power disputes are followed by a fall of {{car.reason.strategy_or_power_dispute.mm_m1p1.mean|abs}} (Holm p = {{car.reason.strategy_or_power_dispute.mm_m1p1.holm_p}}).

<!-- TABLE:IA.6 -->

![Figure IA.2. The announcement return by the reason the board acted](/static/reports/founder-ceo/figures/fig4_reasons.png)

*Figure IA.2. The announcement return by the reason the board acted.* Notes. Mean abnormal return over trading days -1 to +1 by the coded reason, hand-dated firings, with {{ci_level}}% intervals; reasons with at least {{min_reason_cases}} firings. Table IA.6 gives the numbers.

Table IA.7 lists each scandal the New York Times search found, grouped by whether the board kept its chief executive, with the return around the first report. The boards that kept their chief executive include News Corp, Goldman Sachs, Amazon and Activision Blizzard; those whose chief executive left include Boeing, Hewlett-Packard, Intel and McDonald's. Sexual relationships and harassment allegations appear on both sides. Table IA.8 lists the largest founders fired, with the return at the announcement and what became of the firm.

<!-- TABLE:IA.7 -->

<!-- TABLE:IA.8 -->

### Survival, returns, profits and the board

<!-- TABLE:IA.9 -->

<!-- TABLE:IA.10 -->

<!-- TABLE:IA.11 -->

<!-- TABLE:IA.12 -->

![Figure IA.3. Profits and the board after the firing](/static/reports/founder-ceo/figures/fig6_roa_board.png)

*Figure IA.3. Profits and the board after the firing.* Notes. (a) Median change in return on assets from fiscal year -1, minus the same change at the matched firm, in percentage points, fiscal years 0 to +3. (b) About two years after the departure, three shares: pre-departure directors not named in the later proxy, firms with a separate chair and chief executive, and firms where the departing chief executive is still a director. Firings are red and retirements grey; the diamond marks fired founders.

<!-- TABLE:IA.13 -->

## References
