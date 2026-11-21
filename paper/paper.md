# Sacked: Sex, Fraud, Founders, and the Fate of Firms That Fire Their CEO

## Abstract

This paper answers what happens when a Standard & Poor's 1500 board fires its CEO: where dated precisely, the shares fall 2.3% over three trading days around the announcement. Over the six weeks before, they had lagged the market by 5.4%. Within five years 12.0% of the firms go bankrupt, against 2.6% after a retirement. After fraud firings, a comparison group, the shares fall 6.9%, including the news of the fraud. Firings over sex or other personal scandals and firings of founders are too few for precise estimates. Their falls, 1.5% and 3.2%, do not differ significantly from other firings'.

## 1. Introduction

This paper asks what follows when the board of a large US company fires its chief executive officer (CEO), and whether it matters who was fired and why. It follows the 1,272 CEOs fired by the boards of listed Standard & Poor's (S&P) 1500 firms from 1998 to 2023. Each firing is followed from six weeks before the announcement to five years after it, against the CEOs who retired. It puts in one sample three comparisons that earlier work makes apart: founders against hired CEOs, personal scandals against other firings, and what became of the firm.

The firings behind the title are familiar. In 2004 Nortel dismissed its CEO, Frank Dunn, together with its finance chief and controller, amid an accounting scandal. In 2018 Steve Wynn resigned from the casino company he had founded after published allegations of sexual misconduct. In 2019 McDonald's board removed its CEO, Steve Easterbrook, over a consensual relationship with an employee. All three are firings in this paper's sense: a board removing its chief executive, whatever the press release says.

Across these firings, the evidence answers the question in three parts. First, a firing usually comes after a long fall in the shares, consistent with boards acting on poor results [@jenter2015]. The announcement adds a smaller, sudden fall, and after the first year the shares move much like those of similar firms. Second, a firing over fraud is followed by a much larger fall than a firing over a personal scandal. Fraud firings are kept apart because the firm itself is in trouble with the law, and part of their fall is the news of the fraud itself. Personal-scandal and founder firings are too few for precise estimates, and neither differs significantly from other firings. Third, what sets firing firms apart is failure. Within five years they go bankrupt far more often than firms whose CEO retired, and the gap remains, though smaller, with controls for size, debt and recent returns. Table 1 gives the main numbers at every horizon, from six weeks before the announcement to five years after.

Two measurement choices shape these results: the date of each announcement and the coding of founders and reasons. A three-day window needs the right day, but most firings are dated only by a filing or by the day the CEO left office, often weeks after the news. The announcement tests therefore use the 531 firings dated by the database or by hand. Who was a founder and why the board acted come from a language model reading filings and news, and one coder checked every founder, fraud and personal-scandal code by hand.

The paper describes what follows a firing rather than what would have happened had the board kept its CEO. Boards fire the CEOs of firms already in trouble, and comparisons with retirements, matched firms and controls narrow that difference without removing it. Section 2 places the paper in the literature and Section 3 describes the data. Sections 4 to 6 report the announcement, delisting and the long run, Section 7 discusses what the comparisons mean, and Section 8 concludes.

::: glance

### Table 1. The firing, horizon by horizon: S&P 1500 firms, 1998 to 2023

| Horizon | What is measured | Firings | Retirements | N | p |
|---|---|---|---|---|---|
| Panel A. Returns |  |  |  |  |  |
| Trading days −30 to −2 | Return minus the market | -5.4% | 0.0% | 531 | <0.001 |
| Trading days −1 to +1 | Abnormal return, market model | -2.3% | -0.3% | 528 | <0.001 |
| Trading days +2 to +60 | Return minus the market | -1.0% | -0.8% | 521 | 0.465 |
| 12 months | Return minus a matched firm, median | -4.6% | 0.0% | 1,220 | 0.035 |
| 36 months | Return minus a matched firm, median | 0.0% | 0.5% | 1,217 | 0.735 |
| 60 months | Return minus a matched firm, median | -4.7% | 2.8% | 1,164 | 0.246 |
| Months 1 to 36 | Risk-adjusted return (alpha), per month | 0.03% | 0.13% | 319 | 0.863 |
| Panel B. The firm |  |  |  |  |  |
| Within 60 months | Share of firms delisted * | 31.9% | 16.8% | 1,215 | <0.001 |
| Fiscal year +1 | Change in return on assets minus the matched firm, median, percentage points | -0.4 | 0.2 | 971 | 0.057 |
| About two years | Share of earlier directors not in the later proxy statement * | 48.0% | 37.8% | 566 | <0.001 |

*Notes.* Firings exclude those over fraud or other legal violation. Day 0 is the first trading day on or after the announcement. The first three rows use well-dated firings (dated by the database or by hand), the rest every firing. A month is 21 trading days from day +2. The alpha is the monthly intercept from the five Fama-French factors and momentum; its N counts calendar months. N falls with the horizon as recent firings have not reached it. p tests the firing number against zero, or, in rows marked *, against retirements.

:::

## 2. Related work

Three strands of work give the paper its predictions. The first explains when boards fire. Boards fire CEOs after poor performance, including poor performance of the whole industry [@jenter2015], and returns fall well before the change [@weisbach1988]. A firing after an industry downturn can be an efficient rematch of CEOs and firms rather than a mistake [@eisfeldt2013]. Because firings are rare, boards seem to treat replacing a CEO as costly [@taylor2010; @kaplan2012], and large pay cuts serve as a substitute [@gao2012]. Accounting performance worsens before a CEO change and improves after it [@huson2004], and volatility rises more after forced than after voluntary exits [@clayton2005]. The market's reaction depends on what the firing reveals about the firm [@kind2011; @chen2026]. Together these studies predict a fall before the announcement, a smaller fall at it, and weak firms afterwards.

The second strand asks whether founders are different. Founder-led firms invest differently and have been valued more highly [@fahlenbrach2009], but founder status itself responds to performance [@adams2009]. Founders are often replaced as their firms mature [@wasserman2003; @aran2024], and in venture-backed startups replacing the founder improves outcomes [@ewens2018]. The value of a founder's leadership may decline with time since the listing [@bebchuk2017], and insider control beyond cash-flow rights goes with lower firm value [@gompers2010]. Yet CEO turnover at dual-class firms is as sensitive to performance as elsewhere [@aran2025]. The share price reaction to a CEO's sudden death does not differ between founders and other CEOs [@jenter2023]. In Poland, poorly performing founder-CEOs are less likely to be fired than outside CEOs [@kowalewski2019]. These findings point both ways. If founders carry value a successor cannot replace, their firing should be followed by a larger fall. If boards act against founders only when the case is overwhelming, it should be followed by a smaller fall or a rise [@taylor2010].

The third strand separates misconduct by the firm from misconduct by the person. Financial misreporting and executive scandals are both followed by falls in the share price [@cline2018; @larcker2016; @borellikjaer2021; @karpoff2008jfqa], and managers who misreport usually lose their jobs [@karpoff2008jfe]. Boards fire CEOs who manage earnings before outside penalties arrive [@hazarika2012], and more often where employees and directors are prosocial [@bereskin2020]. Shares also fall when a CEO is accused of sexual misconduct [@mooibroek2021] and when a firm reports sexual harassment [@abeysekera2024]. Board resignations rose at exposed firms after the #MeToo revelations of 2017 [@baharad2026]. @cline2018 measure the return when a personal indiscretion becomes public; we measure the firing that follows and set it against firings over fraud. A fraud tells investors that numbers they relied on were wrong, while a personal scandal concerns one person. A firing over a personal scandal should therefore be followed by a smaller fall.

Relative to these studies, the paper compares in one sample three things usually studied apart: who was fired, why the board acted, and what became of the firm. It follows each firing from six weeks before the announcement to five years after, with the number of firms measured at every horizon. It checks by hand who was a founder, why the board acted and, for founders and personal scandals, when the firing was announced.

## 3. Data and design

### Which firings

The departures come from the open CEO dismissal database of @gentry2021, which its authors have extended to cover 1992 to 2023. It codes the reason for every CEO departure at S&P 1500 firms from press coverage and filings, and an independent recoding agreed with it on 87% of events [@gentry2021]. Codes 3 and 4, dismissal for job performance and for legal violations or personal conduct, are firings. Code 5, voluntary retirement, is the comparison group.

Press releases rarely say that a CEO was fired [@gow2017], and how firings are classified changes the results [@fee2018]. Like the database, we treat a resignation under board pressure as a firing, including one during an investigation, a scandal or an activist campaign.

From the firings we remove the 121 whose main reason is fraud or other legal violation. These cover financial misconduct, a legal or regulatory breach by the firm, and criminal charges against the CEO. They are a comparison group throughout, because there the firm itself is in trouble with the law. A personal scandal is a firing over sexual misconduct, a relationship with an employee, conduct at work or another personal failing such as a false degree. There are 40 of them, of which 3 are founders, too few for a test.

Each departure is linked to the firm's identifier at the Securities and Exchange Commission. Through it we take daily prices from Sharadar's Core US Equities data, which include firms later delisted. That leaves 1,272 firings and 2,253 retirements from 1998 to 2023 with share prices. Table IA.1 traces the firings from the database to the samples, and Figure IA.1 shows them by year. Firing firms are about half the size of retirement firms and less profitable (Table IA.2).

### Dating the announcement

A three-day window needs the right day. The database gives an announcement date for about a third of departures, and otherwise only the day the CEO left office, which can come weeks after the news. A second date comes from the firm's 8-K, the filing a company must make within four business days of a CEO change. Where the database does give a date, the two agree within 3 days in only 58% of cases.

Of the 1,272 firings, 531 are well-dated: by the database, or by hand from a dated source. The announcement tests use these. Results over months and years use all 1,272 firings, since an error of a few days is small against a year.

The well-dated firings are not a random draw. They are larger, fell less in the year before, and include more founders and personal scandals (Table IA.5). We dated those two groups by hand from 8-Ks, press releases and New York Times reports. Section 4 shows that the announcement fall survives reweighting and a wider window.

### Founders and reasons

Who was a founder, and why the board acted, come in two steps. First, a language model (DeepSeek, deepseek-chat) reads the database's notes and sources, the 8-K, cited press releases, the CEO's Wikipedia article and New York Times articles. It codes whether the CEO founded the firm, whether the exit was forced and the board's main reason, each with a supporting quote. We call this the evidence-based coding.

Second, one coder, the author, checked by hand every founder code on a firing and every code of fraud, sexual misconduct, a relationship or other personal conduct. The language model had coded 191 firings as founder removals; the hand check confirmed 148, rejected 43 and added 2. About half of the model's other personal-conduct codes turned out to be pay disputes, unexplained personal reasons or criminal charges. Table IA.1 reports how often each kind of code was changed. An independent second coder's check of a random fifth of the codes is planned before submission to a journal.

The evidence-based coding is cautious about whether an exit was forced. Of the 528 well-dated firings with returns, it reads 190 as forced, 46 as not forced and 292 as unclear, mostly because the sources do not say. Section 4 and Table 2 report the announcement return for the forced and the unclear groups separately.

### Returns

The announcement return is the abnormal return over the three trading days from the day before the announcement (day −1) to the day after it (day +1). The abnormal return is the stock's return minus what the market model of equation (1) predicts from the market's return and the stock's own past relation to it.

$$AR_{it} = R_{it} - \hat\alpha_i - \hat\beta_i R_{mt}, \qquad CAR_i = AR_{i,-1} + AR_{i,0} + AR_{i,+1}. \tag{1}$$

Here $R_{it}$ is the stock's total return and $R_{mt}$ the market's. The coefficients come from trading days -250 to -30 before the announcement. We test the mean with the cross-sectional t and the standardized test of @boehmer1991, and the median with the Wilcoxon signed-rank test [@kothari2007]. For the six weeks before and the three months after, we subtract the market's return instead. The reason is the slide before a firing. A stock that was falling gets a negative $\hat\alpha$, and subtracting that negative trend afterwards would make ordinary returns look like a recovery.

For the long run, the main measure is the buy-and-hold return from day +2 over 252, 756 or 1260 trading days, that is one, three or five years. Equation (2) subtracts the return of the market or of a matched firm:

$$BHAR_i(h) = \prod_{t=2}^{T_h}(1+R_{it}) - \prod_{t=2}^{T_h}(1+R_{bt}). \tag{2}$$

The matched firm is in the same Fama-French industry, within 30 percent in market value, with the nearest return on assets. It had no recorded CEO change in the three years before. Matching on prior profitability follows @barber1996, whose tests are well specified only when firms are matched on performance before the event. We also hold a calendar-time portfolio of every firm in its first 36 months after an announcement and regress its excess return on the five Fama-French factors and momentum [@famafrench2015; @lyon1999]. The intercept, the alpha, is the monthly return those risks do not explain.

On the day a firm is delisted, its return is set to zero for a takeover and minus 100% for a bankruptcy. Other delistings get minus 30%, close to the average loss on delistings for poor performance [@shumway1997]. Because firing firms are smaller, every long-run comparison is also made against a matched firm or within size bands.

## 4. The stock around the announcement

If the market had already priced the firing, the announcement would not move the shares; it does. Figure 1 shows the returns of firing and retirement firms from six weeks before the announcement to three months after it. For retirement firms the line stays within one percentage point of zero. For firing firms it slides for six weeks, drops at the announcement and then moves sideways.

![Figure 1. Prices slide before the firing, drop on the news, then stop](../figures/fig1_event_time.png)

*Figure 1. Prices slide before the firing, drop on the news, then stop.* Notes. Cumulative return minus the market from trading day -30 to day +60 around the announcement (day 0), well-dated firings with every day of the window. Panel (a) shows means, with the 95% confidence band for firings; the grey band marks days -1 to +1. Panel (b) shows medians, so that one firm cannot move a small group's line. The lines sum daily returns, so their end points differ slightly from the window returns of Table 1.

In the six weeks before the announcement, the shares of firing firms lag the market by 5.4%, while those of retirement firms do not move. Over the three trading days around it, their market-model abnormal return is -2.3%, against -0.3% for retirements (Table 2). Over the next three months they earn -1.0% against the market, which is not statistically significant (p = 0.465).

Is the fall an artefact of how firings are defined or dated? Not of the definition (Table 2, Panel C). Where the evidence-based coding agrees the exit was forced, the fall is 1.6% (p = 0.032); where it is unclear, 2.8%; where it reads the exit as not forced, 1.5%. Reweighting the well-dated firings to resemble every firing gives 2.2%, and the five-factor model 2.2%.

Nor of the dating. Over every firing, whatever the source of its date, the three-day fall is only 1.3%. A day 0 that comes days or weeks late puts the news outside the window. Widen the window to trading days −5 to +5 and every firing falls 2.0% (p < 0.001), close to the well-dated firings' 2.6% (Table IA.4).

### Table 2. The announcement: abnormal returns over trading days −1 to +1

| Group | Mean | Median | t | p | N |
|---|---|---|---|---|---|
| Panel A. By group |  |  |  |  |  |
| CEOs fired | -2.3% | -1.2% | -5.18 | <0.001 | 528 |
| CEOs who retired | -0.3% | -0.3% | -1.45 | 0.147 | 969 |
| Founder fired | -3.2% | -0.4% | -1.56 | 0.126 | 52 |
| Hired CEO fired | -2.2% | -1.3% | -5.02 | <0.001 | 476 |
| Fired over a personal scandal | -1.5% | -1.6% | -1.99 | 0.054 | 39 |
| Fired for another reason | -2.3% | -1.2% | -4.97 | <0.001 | 489 |
| Sex or relationship scandal | 0.3% | 0.7% | 0.24 | 0.810 | 16 |
| Fired for fraud or other legal violation (comparison) | -6.9% | -3.9% | -3.28 | 0.002 | 41 |
| Panel B. Differences in the mean, percentage points |  |  |  |  |  |
| Founder minus hired CEO (below zero: larger fall after a founder) | -1.0 |  | -0.49 | 0.627 | 528 |
| Personal scandal minus other firings (above zero: smaller fall after a scandal) | 0.9 |  | 1.01 | 0.317 | 528 |
| Personal scandal minus fraud (above zero: smaller fall after a scandal) | 5.4 |  | 2.44 | 0.018 | 80 |
| Panel C. Who counts as fired, and which dates |  |  |  |  |  |
| Fired, the evidence-based coding agrees | -1.6% | -0.5% | -2.16 | 0.032 | 190 |
| Fired, the evidence-based coding is unclear | -2.8% | -1.9% | -4.67 | <0.001 | 292 |
| Fired, the evidence-based coding reads not forced | -1.5% | -1.1% | -1.44 | 0.156 | 46 |
| Well-dated firings reweighted to resemble every firing | -2.2% |  | -3.34 | <0.001 | 513 |
| Every firing, any date (many days 0 misplaced) | -1.3% | -0.6% | -3.15 | 0.002 | 1,267 |
| Well-dated firings, fraud and legal violation included | -2.6% | -1.4% | -5.97 | <0.001 | 569 |
| CEOs fired, five-factor model | -2.2% | -1.0% | -4.98 | <0.001 | 528 |

*Notes.* Market-model abnormal return over trading days -1 to +1 around the announcement (day 0), on well-dated firings (dated by the database or by hand), fraud and legal violations excluded unless stated. N counts each row's firings. t: the t of the mean, or the Welch t of a difference; p is two-sided. Panel B: the first group's mean minus the second's; a positive number means a smaller fall in the first group. Founder, scandal and fraud labels are hand-checked. The sex or relationship row (n = 16) is too small for a test. Panel C reweights by size, prior return, profitability, leverage, founder and scandal flags and year (Table IA.5).

### Personal scandals and fraud

Is a firing over a personal scandal different? After one, the shares fall 1.5% over the three days, against 2.3% after other firings (Table 2). The scandal fall on its own is not quite significant (p = 0.054, n = 39). With size, the prior year's return and the year held constant, the gap between the two is 0.2 percentage points (Table IA.4).

The scandal fall is 0.9 percentage points smaller, a gap that is not statistically significant (p = 0.317). With so few scandal firings the estimate is imprecise. Its 95% interval runs from -0.9 to 2.6 percentage points, and the test would detect only gaps of about 2.4 percentage points.

After a firing over fraud or other legal violation the shares fall 6.9%, 5.4 percentage points more than after a personal scandal (p = 0.018, n = 80). This is not a clean measure of the firing. A fraud firing is often announced with the fraud itself. Its three-day fall therefore carries the news that the accounts or the business were wrong, as well as the news that the CEO is gone.

A scandal firing may be followed by little because the market priced the scandal when it first broke. To check, we searched the New York Times Archive for personal misconduct by sitting CEOs of the sample's firms and checked each report by hand (Table IA.8). The search finds 27 scandals. In 19 the CEO left within a year; in 8 the board kept them, among them Jeff Bezos at Amazon and Bobby Kotick at Activision Blizzard.

Over the three trading days around the first press report, the shares of the 24 scandal firms with prices fell 2.2% against the market. They fell 2.4% where the CEO later left and 1.9% where the board kept them, too few cases to tell apart. The search finds only 12 of the database's firings over a personal scandal, mostly at the largest firms, so these cases describe prominent scandals rather than test anything.

### Founders

Does it matter that the CEO built the company? A founder's firing is followed by a fall of 3.2% over the three days, against 2.2% for a hired CEO (Table 2). The gap of -1.0 percentage points is not statistically significant (p = 0.627).

This is not evidence that founders and hired CEOs are alike. With 52 well-dated founder firings, the 95% interval for the gap runs from -5.2 to 3.2 percentage points. The test would detect only gaps of about 5.9 percentage points (Table IA.3). A formal equivalence test agrees: the data cannot rule out a founder gap as large as the average firing's whole fall (p = 0.278). That margin is the size of the effect the paper studies, so a gap within it would still matter.

Founder firms also slide further before the announcement: 8.8% over the six weeks, against 5.4% for all firings, on returns minus the market (Table IA.6). With firm size, the prior year's return and the year held constant, the founder gap is 0.8 percentage points (p = 0.647; Table IA.4).

Three founders were fired over a personal scandal: John Schnatter at Papa John's, Steve Wynn at Wynn Resorts and Vince McMahon at World Wrestling Entertainment (WWE). WWE's shares rose 7.9% over the three days around McMahon's departure (Table IA.9); three cases do not support a test.

## 5. Which firms are delisted

If the announcement fall is modest, does the firm itself do worse? A firm is delisted when its stock leaves the price file, through a takeover, a bankruptcy or another exit. Of the 1,215 firing firms followed for a full 60 months, 31.9% were delisted in that time: 19.0% in a takeover and 12.0% in bankruptcy (Table 4, Figure 2).

![Figure 2. Within five years, 31.9% of firing firms are delisted](../figures/fig3_exits.png)

*Figure 2. Within five years, 31.9% of firing firms are delisted.* Notes. Cumulative share of firms delisted, by month after the announcement, for firms with a complete 60-month horizon: (a) for any reason, (b) in bankruptcy. Most of the rest are takeovers; Table 4 gives the shares.

After a retirement the shares are 16.8% delisted, 14.1% taken over and 2.6% bankrupt. Most of the gap is therefore bankruptcy. Takeovers are the larger share in both groups, which fits the view that board removal and takeover are two routes to a change of control [@morck1989].

Small firms fail more often, and firing firms are smaller, so Table 3 compares firms of similar size. In the smallest band, under $300 million in market value, 24.2% of firing firms go bankrupt within five years, against 13.5% of retirement firms. Above $5 billion the bankrupt shares are 0.8% and 0.0%. Firing firms are delisted more often in every band (Table 3).

### Table 3. Firms delisted within 60 months, by market value before the firing

| Market value | Delisted, firings | Delisted, retirements | p | Bankrupt, firings | Bankrupt, retirements | N firings | N retirements |
|---|---|---|---|---|---|---|---|
| Under $0.3 billion | 45.0% | 32.3% | 0.004 | 24.2% | 13.5% | 318 | 229 |
| $0.3 to 1 billion | 33.9% | 20.4% | <0.001 | 8.9% | 3.1% | 280 | 515 |
| $1 to 5 billion | 26.6% | 15.6% | <0.001 | 7.8% | 1.1% | 335 | 793 |
| Over $5 billion | 14.8% | 9.2% | 0.023 | 0.8% | 0.0% | 250 | 617 |
| All, bankruptcies within 180 days of the announcement set aside | 29.8% | 16.6% |  | 9.3% | 2.4% | 1,179 | 2,180 |

*Notes.* Market value at the fiscal year-end before the departure, in US dollars. Delisted: the stock left the price file (taken over, bankrupt or other) within 60 months of the announcement. Bankrupt: the corporate action within 60 days of the final price was a bankruptcy or liquidation. p is a chi-square test of the share gone, firings against retirements. The last row sets aside firms whose bankruptcy was recorded within 180 days after the announcement, which were already failing when the CEO left. Only events with a complete 60-month horizon enter.

Some firms were already failing when the CEO left: for 36 of them a bankruptcy was recorded within 180 days of the announcement, as at Sears and Dana. Setting those aside, 29.8% of firing firms are delisted within five years and 9.3% go bankrupt.

How much of the gap reflects firms that were weak already? With controls for size and profitability, firing firms are 9.0 percentage points more likely than retirement firms to be delisted within five years (Table 4). Adding the prior year's return, debt, book-to-market, a distress score and a loss flag lowers the gap to 6.6 percentage points (p = 0.005). Of that gap, 2.3 percentage points is bankruptcy. Debt is the strongest predictor among these controls (Table IA.10).

The gap survives three further checks (Table IA.10). Counting every month a firm is followed, including firms followed for less than five years, firing firms leave the market 1.38 times as fast with every control (p < 0.001). Where the evidence-based coding agrees the exit was forced, the controlled gap is 10.4 percentage points (p = 0.002). Against their own matched firms it is 6.9 percentage points.

The firing need not cause the delisting: a board may fire the CEO of a firm it already expects to struggle. Founder firms are delisted within five years in 37.2% of cases, and the gap from hired CEOs, 5.7 percentage points, is not statistically significant (p = 0.358). After a personal scandal the share is 20.0% of only 35 firms, too few to compare (Table 4).

### Table 4. Firms delisted within 12, 36 and 60 months, by group

| Group | Delisted, 12m | Delisted, 36m | Delisted, 60m | Acquired, 60m | Bankrupt, 60m | p vs retired | N, 60m |
|---|---|---|---|---|---|---|---|
| Panel A. Share of firms |  |  |  |  |  |  |  |
| CEOs fired | 7.6% | 21.3% | 31.9% | 19.0% | 12.0% | <0.001 | 1,215 |
| CEOs who retired | 3.5% | 9.5% | 16.8% | 14.1% | 2.6% |  | 2,185 |
| Founder fired | 10.8% | 30.5% | 37.2% | 19.2% | 15.4% | <0.001 | 78 |
| Hired CEO fired | 7.4% | 20.6% | 31.5% | 19.0% | 11.8% | <0.001 | 1,137 |
| Fired over a personal scandal | 5.0% | 20.0% | 20.0% | 17.1% | 2.9% | 0.778 | 35 |
| Fired for another reason | 7.7% | 21.3% | 32.2% | 19.1% | 12.3% | <0.001 | 1,180 |
| Fired, evidence agrees | 7.4% | 22.9% | 34.1% | 21.3% | 11.9% | <0.001 | 478 |
| Fired for fraud or other legal violation (comparison) | 9.1% | 19.8% | 34.2% | 23.3% | 10.0% | <0.001 | 120 |
| Panel B. Differences in the 60-month share, percentage points |  |  |  |  |  |  |  |
| Firings minus retirements |  |  | 15.1 |  |  | <0.001 | 3,400 |
| Firings minus retirements, size and profitability |  |  | 9.0 | 3.7 | 4.9 | <0.001 | 3,337 |
| Firings minus retirements, every control |  |  | 6.6 | 3.9 | 2.3 | 0.005 | 3,138 |
| Founder minus hired CEO |  |  | 5.7 |  |  | 0.358 | 1,215 |
| Personal scandal minus other firings |  |  | -12.2 |  |  | 0.179 | 1,215 |

*Notes.* Firms whose stock left the price file within 12, 36 and 60 months of the announcement, among firms followed that long. Acquired and Bankrupt classify the corporate action within 60 days of the final price. p vs retired: chi-square test of the 60-month share. Panel B: the 60-month gap, raw or as a linear probability coefficient with year and industry effects; N counts firings and retirements. Size and profitability: log market value and return on assets. Every control adds the prior return, leverage, book-to-market, distress and loss. Table IA.10 adds the checks.

## 6. Returns, profits and the board over five years

Do the extra bankruptcies leave shareholders with lower returns? A portfolio holding every firm in its first three years after a firing earns an alpha of 0.03% a month (Table IA.11). Its 95% interval runs from -0.35% to 0.42% a month, wide enough to include gains or losses of several percent over three years. Against a portfolio of retirement firms the difference is -0.12% a month (p = 0.516).

The portfolio of personal-scandal firms earns 1.49% a month (t = 4.68; Table IA.11). It holds about a dozen firms at a time, so one or two firms can drive it. We do not read it as evidence that scandal firms do better.

Over the 60 months after the announcement, the median firing firm's buy-and-hold return trails the market's by 32.1%, and the median retirement firm's by 7.4% (Figure 3). But a typical stock lags an index over long horizons, because a few large winners lift the index average. A matched firm of the same industry, size and profitability removes that effect.

![Figure 3. Against the market the long run looks grim; against a matched firm it does not](../figures/fig2_long_run.png)

*Figure 3. Against the market the long run looks grim; against a matched firm it does not.* Notes. Median buy-and-hold return minus the market, month 1 to month 60 after the announcement, in months of 21 trading days from day +2, all firings. Diamonds mark the median return against a matched firm at 12, 36 and 60 months; Table IA.12 gives the numbers.

Against its matched firm, the median firing firm's buy-and-hold return is -4.6% after one year (p = 0.035). After three and five years it is 0.0% and -4.7%, neither significant (Table IA.12).

The means at three and five years are 2.3% and 11.7%. Neither is significant with the skewness-adjusted t test (p = 0.709 and 0.286). A few large winners pull the mean above the median, which is why the median and the alpha are the measures we read.

Profits fall in the year of the firing and then recover. In the fiscal year of the departure, return on assets falls 2.0 percentage points against the matched firm (p < 0.001; Table IA.13 and Figure IA.3). By fiscal year +2 the median gap is 0.3 percentage points, on the firms still filing.

A firing may come with a wider change in who governs the firm, which would appear on the board. The proxy statement, the annual filing that lists the directors standing for election, records the board before and after a firing. Of the directors named in the last proxy statement before a firing, 48.0% are missing from the first one filed about two years later. After a retirement the share is 37.8% (Table IA.14). The measure counts every director who disappears, matched on surname and first initial; a proxy does not say whether a director resigned, was not nominated again or lost a vote.

Two years later a fired founder still sits on the board at 9.7% of firms, against 3.6% for a fired hired CEO and 33.3% for a retired one (Table IA.14). The founder gap is not significant (p = 0.113). These results cover the 1,876 departures whose firms filed a proxy statement both before and about two years after.

## 7. Discussion

The timing of the returns fits a simple account of what a firing tells investors. Boards fire CEOs after weeks of falling prices, as studies of forced turnover predict [@jenter2015]. The announcement then tells investors that matters were bad enough for the board to act, and the shares fall again. After that the shares of firing firms move much like those of matched firms. The firms that fail were mostly weak already: controls for debt, distress and the prior year's return remove more than half of the raw delisting gap (Table 4). We cannot tell whether the firing itself speeds failure, slows it or merely marks it.

Fraud firings and personal-scandal firings are followed by clearly different falls; founders and hired CEOs cannot yet be told apart. A fraud firing announces that the firm's numbers or conduct were wrong and that legal costs may follow; a personal scandal concerns one person. The announcement returns line up with that difference, although the fraud return also carries the fraud news. Treating the two as one group of misconduct would blur them. Within five years 34.2% of fraud-firing firms are delisted, 17.4 percentage points more than after a retirement. After a personal scandal the share is 20.0%, but of only 35 firms, too few to compare (Table 4).

For founders the data cannot choose between the two readings of Section 2. A larger fall would suggest that founders carry value a successor cannot replace, and a smaller one that the firing ends entrenchment. The founder interval at the announcement includes both, and so do the founder gaps in delisting and in the long run. Answering it would take several times as many dated founder firings as large US firms have produced in a quarter century. Smaller listed firms, where founders are more common, are the place to look.

For directors and investors the null results carry a limited message. They do not mean that firing a founder, or firing over a scandal, is safe for shareholders (Table 2). Among large US firms such firings are simply too rare to measure the difference. The clearer lesson is where to look after any firing: at the firm's debt and its risk of failure, which the announcement return does not capture (Table 4).

## 8. Conclusion

When a board fires its CEO, the shares have usually been falling for weeks, and the announcement takes them lower still (Table 2). After the first year they move much like those of similar firms.

The reason for a firing matters at the announcement: fraud firings are followed by much larger falls, though those falls also carry the fraud news. Firings over a personal scandal and firings of founders are too rare in large US firms for precise estimates (Table 2).

What sets firing firms apart is failure: within five years 12.0% of them go bankrupt, against 2.6% after a retirement. The gap shrinks but remains with controls for debt and distress (Table 4).

The sample covers S&P 1500 firms, so it says little about smaller companies, where founders often hold more control. Only three founders were fired over a personal scandal, and too few scandals in which the board kept its CEO reached the press to test. Fewer than half the firings have a precise announcement date, and the founder and reason codes rest on one coder's check. We do not follow who succeeds the CEO, although most new CEOs are insiders or people the board already knows [@cziraki2022]. The comparisons describe what follows a firing, not what would have happened had the board kept its CEO.

## Internet Appendix

### Sample and firms

Table IA.1 traces the firings from the CEO dismissal database to the samples, and Figure IA.1 counts them by year. Panel B of Table IA.1 shows how often the hand check changed the model's codes. It kept 75.9% of founder codes, 61.2% of fraud and legal-violation codes and 52.1% of other personal-conduct codes. In the fiscal year before the departure, firing firms are smaller and less profitable than retirement firms: their median return on assets is 7.8%, against 12.3% (Table IA.2).

### Table IA.1. From the database to the main sample

| Step | N |
|---|---|
| Panel A. From the database to the samples |  |
| Firings in the database, departures 1998 to 2023 | 1,799 |
| with an SEC company identifier | 1,620 |
| with a price history covering the announcement | 1,441 |
| with announcement returns | 1,393 |
| less firings for fraud or other legal violation (comparison only) | 121 |
| firings for any other reason (the paper's sample) | 1,272 |
| well-dated: by the database or by hand (announcement sample) | 531 |
| Founder codes from the model, all firings | 191 |
| founders confirmed by hand | 150 |
| of which departures 1998 to 2023 | 132 |
| of which with returns, firings over fraud or other legal violation excluded | 83 |
| of which well-dated (announcement sample) | 52 |
| Panel B. The hand review of the model's codes |  |
| Founder codes checked by hand | 195 |
| of which the model's code was kept | 148 |
| Fraud and legal-violation codes checked by hand | 121 |
| of which the model's code was kept | 74 |
| Sex and relationship codes checked by hand | 30 |
| of which the model's code was kept | 20 |
| Other personal-conduct codes checked by hand | 48 |
| of which the model's code was kept | 25 |

*Notes.* Firings are database codes 3 and 4; firings over fraud or other legal violation leave the sample after the hand review of their codes. A price history covers the announcement when the security trades from 60 days before day 0. Founder codes come from the evidence-based model coding; every one on a firing was checked by hand, which also added founders the model had left unclear. Panel B: one coder; a code not kept was changed to another reason or to not a founder.

![Figure IA.1. Firings per year](../figures/fig5_per_year.png)

*Figure IA.1. Firings per year.* Notes. Every firing in the database by year, 1998 to 2023, by the database's dismissal type, whether or not the firm has share prices, less firings over fraud or other legal violation. The bars therefore total more than the paper's 1,272 firings with prices. The number above each bar counts the hand-confirmed founders among them; the founder count in Table IA.1 also includes founders fired over fraud. The last year covers part of 2023.

### Table IA.2. Who gets fired: the firm in the year before the departure

| Fiscal year -1, medians | Firings | Retirements | Founders fired | p, firings vs retirements | N firings |
|---|---|---|---|---|---|
| Market value, USD billion | 1.0 | 1.9 | 0.8 | <0.001 | 1,240 |
| Return on assets, year -1 (EBITDA / assets) | 7.8% | 12.3% | 7.6% | <0.001 | 1,240 |
| Sales growth | 2.9% | 6.7% | 8.5% | <0.001 | 1,215 |
| Capital spending / assets | 3.2% | 3.5% | 4.2% | <0.001 | 1,240 |

*Notes.* Medians in the fiscal year before the departure, from as-reported annual statements; market value at that fiscal year-end. Return on assets is earnings before interest, taxes, depreciation and amortization (EBITDA) over total assets. p is from a Mann-Whitney U test of firings against retirements. N firings is the number of firings with the item.

### The announcement

The founder gap is negative in all three windows of Table IA.3 and significant in none. With 52 founders, the smallest gap the main test could detect is 5.9 percentage points.

### Table IA.3. The founder gap in every window

| Window (trading days) | Founder fired | Hired CEO fired | Gap, pp | p | Detectable gap, pp | N founders |
|---|---|---|---|---|---|---|
| Days 0 to +1 | -4.0% | -2.0% | -2.0 | 0.373 | 6.2 | 52 |
| Days -1 to +1 | -3.2% | -2.2% | -1.0 | 0.627 | 5.9 | 52 |
| Days -5 to +5 | -6.0% | -2.2% | -3.8 | 0.370 | 11.8 | 52 |

*Notes.* Mean market-model abnormal returns of fired founders and fired hired CEOs over each window, the gap with its Welch p, and the smallest gap the test would detect with 80% power at the 5% level. The paper's main window is days -1 to +1.

Table IA.4 changes one thing at a time against the main tables. With the five-factor model plus momentum, the founder gap is -1.0 percentage points and the personal-scandal gap 1.7 percentage points. Returns minus the market, with no estimated model, give -2.5% over the three days. Using every firing, whatever its date source, gives -1.3%.

Table 2, Panel C, already splits the firings by how the evidence-based coding reads them. Excluding 2008 and 2009 gives -2.4%, and dropping firings coded as leaving for a new job gives -2.2%.

The long-run results do not depend on how delisting returns are set. With every delisting return at zero, the median three-year return against the market is -12.9%, and setting every delisting that is not a takeover to minus 100% gives -15.4%. When no firm meets the size band the nearest firm in size is the match (206 matches); using only matches within the band, the median three-year matched return is 0.0%.

For departures from 1992 to 1997, before daily prices for delisted firms exist, we use the five-year return graphs that firms print in their proxy statements. Of these departures, 225 have a usable graph, including 41 firings. The median three-year return against the firm's own reported index is -68.3% after firings and -39.5% after retirements. Only firms still filing three years later enter this check.

### Table IA.4. Robustness

| Specification | Estimate | p | N | Horizon |
|---|---|---|---|---|
| Panel A. The announcement return |  |  |  |  |
| Return minus the market instead of the market model | -2.5% | <0.001 | 528 | Trading days -1 to +1 |
| Adding retirements the evidence reads as pushed | -2.2% | <0.001 | 537 | Trading days -1 to +1 |
| Excluding 2008 and 2009 | -2.4% | <0.001 | 491 | Trading days -1 to +1 |
| Excluding firings coded as leaving for a new job | -2.2% | <0.001 | 505 | Trading days -1 to +1 |
| Not precisely dated (8-K, news report or leaving office) | -0.5% | 0.385 | 739 | Trading days -1 to +1 |
| Dated by an 8-K only | -0.6% | 0.321 | 428 | Trading days -1 to +1 |
| Well-dated, wider window | -2.6% | <0.001 | 527 | Trading days -5 to +5 |
| Every firing, any date, wider window | -2.0% | <0.001 | 1,265 | Trading days -5 to +5 |
| Not precisely dated, wider window | -1.5% | 0.078 | 738 | Trading days -5 to +5 |
| Panel B. Gaps between groups at the announcement |  |  |  |  |
| Founder minus hired CEO, controlling for size, prior 12-month return and year | 0.8 pp | 0.647 | 513 | Trading days -1 to +1 |
| Personal scandal minus other firings, same controls | 0.2 pp | 0.889 | 513 | Trading days -1 to +1 |
| Five-factor plus momentum: founder minus hired CEO | -1.0 pp | 0.648 | 528 | Trading days -1 to +1 |
| Five-factor plus momentum: personal scandal minus other reasons | 1.7 pp | 0.057 | 528 | Trading days -1 to +1 |
| Evidence agrees: founder minus hired CEO | -0.2 pp | 0.973 | 190 | Trading days -1 to +1 |
| All dates: sex or relationship minus fraud | 6.5 pp | 0.010 | 71 | Trading days -1 to +1 |
| All dates: personal scandal minus other firings | -0.2 pp | 0.793 | 1,267 | Trading days -1 to +1 |
| All dates: founder minus hired CEO | -1.9 pp | 0.236 | 1,267 | Trading days -1 to +1 |
| Panel C. The long run |  |  |  |  |
| Return minus a matched firm, 36 months, matches within the size band only | 0.0% | 0.906 | 1,164 | 36 months (756 trading days) from day +2 |
| Evidence agrees: return minus the market, 36 months | -9.9% | 0.011 | 497 | 36 months (756 trading days) from day +2 |
| Evidence agrees: return minus a matched firm, 36 months, median | 2.4% | 0.202 | 476 | 36 months (756 trading days) from day +2 |
| Return minus the market, 36 months, every delisting return 0 | -12.9% | <0.001 | 1,269 | 36 months (756 trading days) from day +2 |
| Return minus the market, 36 months, non-takeover delistings -100% | -15.4% | <0.001 | 1,269 | 36 months (756 trading days) from day +2 |
| Pre-1998: 3-year return minus reported index, firings minus retirements | -28.8 pp | 0.021 | 221 | Three fiscal years from the event year, departures announced 1992 to 1997 |

*Notes.* Each row changes one thing against the main tables. Evidence agrees: the CEO dismissal database codes the exit forced and the evidence-based coding (8-K, press releases, Wikipedia, New York Times) also reads it as forced. Pushed retirements: the database codes a retirement and the evidence reads it as forced. Pre-1998: departures announced 1992 to 1997, three-year return minus the index the firm itself reports in its proxy performance graph.

Table IA.5 compares the well-dated firings with the others. The well-dated firms are larger, with a median market value of 1.3 billion dollars against 0.8, and fell less over the prior year. They are also more recent, with a median year of 2014 against 2008, and fewer of them are delisted within five years. Reweighting them to resemble every firing leaves the announcement return almost unchanged (Table 2).

### Table IA.5. Well-dated and other firings

| Characteristic | Well-dated | Other firings | p | N, well-dated | N, other |
|---|---|---|---|---|---|
| Market value, USD billion, median | 1.3 | 0.8 | <0.001 | 515 | 725 |
| Return over the prior year, median | -7.9% | -21.5% | <0.001 | 515 | 725 |
| Return on assets, year -1, median | 8.4% | 7.0% | 0.003 | 515 | 725 |
| Liabilities over assets, median | 57.6% | 56.3% | 0.525 | 515 | 725 |
| Founder fired, share | 9.8% | 4.2% | <0.001 | 531 | 741 |
| Fired over a personal scandal, share | 7.3% | 0.1% | <0.001 | 531 | 741 |
| Evidence-based coding agrees it was forced, share | 36.1% | 41.5% | 0.063 | 515 | 725 |
| Delisted within 60 months, share | 26.0% | 33.8% | 0.006 | 458 | 725 |
| Year of the announcement, median | 2014 | 2008 |  | 531 | 741 |

*Notes.* Firings at S&P 1500 firms, 1998 to 2023, fraud and legal violations excluded. Well-dated: the announcement date comes from the database or a hand check of a dated source; the other firings are dated only by an 8-K or the day the CEO left office. Medians use a Mann-Whitney test and shares a chi-square test. Founder and scandal firings were dated by hand, so more of them are well-dated. Table 2's reweighted return weights each well-dated firing by the inverse of its chance of being well-dated, from a logit on these traits and the year.

### Table IA.6. Before, at and after the announcement, by group

| Group | Days -30 to -2 | p | Days -1 to +1 | p | Days +2 to +60 | p | N |
|---|---|---|---|---|---|---|---|
| CEOs fired | -5.4% | <0.001 | -2.3% | <0.001 | -1.0% | 0.465 | 528 |
| CEOs who retired | 0.0% | 0.933 | -0.3% | 0.147 | -0.8% | 0.190 | 969 |
| Founder fired | -8.8% | 0.005 | -3.2% | 0.126 | 2.7% | 0.684 | 52 |
| Fired over a personal scandal | -4.3% | 0.030 | -1.5% | 0.054 | -3.5% | 0.411 | 39 |
| Fired for another reason | -5.5% | <0.001 | -2.3% | <0.001 | -0.8% | 0.581 | 489 |

*Notes.* Days -30 to -2 and +2 to +60 are cumulative market-adjusted returns (firm minus market), used because a firing firm's alpha before the event is strongly negative and a market model would project it forward. Days -1 to +1 is the market-model return of Table 2. Events need every day of a window. N is the number of departures in the days -1 to +1 window; the outer windows differ by at most a few percent.

Table IA.7 and Figure IA.2 split the firings by the reason coded for them. After a Holm correction for testing every reason, three falls remain statistically significant (Table IA.7). Where a push was described as a retirement or ill health the fall is 3.5% (Holm p = 0.003). Where the CEO was coded as leaving for a new job it is 4.6% (Holm p = 0.015). After other personal conduct it is 2.7% (Holm p = 0.039); performance and the other reasons do not survive the correction.

### Table IA.7. Why the board acted: abnormal returns over trading days −1 to +1 by coded reason

| Coded primary reason | Mean | t | p | Holm p | N |
|---|---|---|---|---|---|
| Merger or restructuring | -9.2% | -2.35 | 0.028 | 0.167 | 24 |
| Left for a new job | -4.6% | -3.52 | 0.002 | 0.015 | 23 |
| Strategy or power dispute | -3.6% | -2.11 | 0.045 | 0.179 | 27 |
| Pushed out, described as retirement or health | -3.5% | -3.81 | <0.001 | 0.003 | 66 |
| Other personal conduct | -2.7% | -3.07 | 0.006 | 0.039 | 23 |
| Reason unclear | -1.6% | -1.71 | 0.090 | 0.271 | 93 |
| Performance | -1.6% | -2.21 | 0.028 | 0.167 | 221 |
| Relationship with an employee | -0.5% | -0.44 | 0.668 | 1.000 | 11 |
| Activist or shareholder pressure | -0.3% | -0.28 | 0.780 | 1.000 | 34 |

*Notes.* Firings for any reason but fraud or other legal violation, by the primary reason coded from the database notes, the 8-K filed within 10 days, cited press releases, Wikipedia and matched New York Times articles. Reasons with fewer than 10 cases are not shown. Holm p adjusts each p for the number of reasons tested. Financial-misconduct, sexual-conduct and relationship labels are hand-checked; the others are model codes.

![Figure IA.2. The announcement return by the reason the board acted](../figures/fig4_reasons.png)

*Figure IA.2. The announcement return by the reason the board acted.* Notes. Mean abnormal return over trading days -1 to +1 by the coded reason, well-dated firings, with 95% intervals; reasons with at least 10 firings. Table IA.7 gives the numbers.

Table IA.8 lists each scandal the New York Times search found, grouped by whether the board kept its CEO, with the return around the first report. The boards that kept their CEO include News Corp, Goldman Sachs, Amazon and Activision Blizzard; those whose CEO left include Boeing, Hewlett-Packard, Intel and McDonald's. Sexual relationships and harassment allegations appear on both sides. Table IA.9 lists the largest founders fired, with the return at the announcement and what became of the firm.

### Table IA.8. Personal scandals of sitting CEOs in the New York Times, 1998 to 2023

| Company | CEO | First report | Scandal | Days -1 to +1 |
|---|---|---|---|---|
| Panel A. The board kept the CEO |  |  |  |  |
| News Corp | Rupert Murdoch | 1998-10-04 | Sexual relationship | -15.0% |
| Global Crossing | John J. Legere | 2002-04-08 | Harassment allegation | 2.5% |
| Bausch & Lomb | Ronald L. Zarrella | 2002-10-19 | Other personal conduct | -1.1% |
| Goldman Sachs Group | Henry M. Paulson Jr. | 2003-02-04 | Other personal conduct | 0.3% |
| News Corporation | Rupert Murdoch | 2012-11-19 | Other personal conduct | 1.1% |
| KB Home | Jeffrey Mezger | 2017-09-19 | Other personal conduct | -2.8% |
| Amazon | Jeff Bezos | 2019-02-07 | Sexual relationship | 0.8% |
| Activision Blizzard | Bobby Kotick | 2021-07-29 | Harassment allegation | -0.8% |
| Mean, 8 cases |  |  |  | -1.9% |
| Panel B. The CEO left within a year |  |  |  |  |
| Ashland Inc. | Paul W. Chellgren | 2002-08-04 | Sexual relationship | 3.6% |
| Boeing Co | Harry C. Stonecipher | 2005-03-08 | Sexual relationship | 0.1% |
| RadioShack | David J. Edmondson | 2006-02-16 | Other personal conduct | -13.1% |
| Bear Stearns | James Cayne | 2007-11-02 | Other personal conduct | 1.2% |
| Hewlett-Packard | Mark V. Hurd | 2010-08-06 | Harassment allegation | -8.9% |
| Best Buy | Brian J. Dunn | 2012-04-10 | Sexual relationship | -0.7% |
| Yahoo | Scott Thompson | 2012-05-03 | Other personal conduct | -0.4% |
| Wynn Resorts | Stephen Wynn | 2018-01-26 | Harassment allegation | -20.0% |
| Lululemon Athletica | Laurent Potdevin | 2018-02-06 | Other personal conduct | 5.7% |
| Intel | Brian Krzanich | 2018-06-21 | Sexual relationship | -0.4% |
| Barnes & Noble | Demos Parneros | 2018-07-03 | Other personal conduct | -5.6% |
| Texas Instruments | Brian Crutcher | 2018-07-18 | Other personal conduct | -0.4% |
| McDonald's | Steve Easterbrook | 2019-11-03 | Sexual relationship | -3.7% |
| L Brands | Leslie H. Wexner | 2020-01-29 | Other personal conduct | 14.3% |
| Tapestry | Jide Zeitlin | 2020-07-21 | Sexual relationship | -1.2% |
| World Wrestling Entertainment | Vince McMahon | 2022-06-17 | Sexual relationship | -8.8% |
| Mean, 16 cases |  |  |  | -2.4% |

*Notes.* Reports of personal misconduct by a sitting CEO of a sample firm, found by searching the New York Times Archive and checked by hand. Panel B: the CEO departed within 12 months of the first report (CEO dismissal database, or a reported departure the database misses). Days -1 to +1: market-adjusted return around the first report. The table lists the 24 of the 27 scandals found whose shares traded around the first report. The search finds only a few of the database's firings over a personal scandal, mostly at the largest firms, so the table describes prominent cases, not a sample.

### Table IA.9. The largest founders fired, among firings both codings read as forced

| Company | Founder | Year | Database reason | Value, USD bn | Days -1 to +1 | 36 months | After 60 months |
|---|---|---|---|---|---|---|---|
| Yahoo | Jerry Yang | 2008 | Performance | 37.9 | 9.7% | -23.1% | still listed |
| Wynn Resorts | Steve Wynn | 2018 | Legal or personal conduct | 17.3 | 9.6% | -94.6% | still listed |
| Chesapeake Energy | Aubrey McClendon | 2013 | Legal or personal conduct | 13.1 | 4.7% | -117.5% | still listed |
| WWE | Vince McMahon | 2022 | Legal or personal conduct | 3.6 | 7.9% | 37.7% | under 5 years of data |
| Career Education | John Larson | 2006 | Performance | 3.4 | 14.9% | 12.9% | still listed |
| Acadia Healthcare | Joey Jacobs | 2018 | Performance | 3.3 | -8.4% | 14.9% | still listed |
| Papa Johns International | John Schnatter | 2017 | Legal or personal conduct | 3.1 | -4.9% | 7.4% | still listed |
| ICN Pharmaceuticals | Milan Panic | 2002 | Performance | 2.7 | 0.2% | -47.7% | still listed |
| Jetblue Airways | David Gary Neeleman | 2007 | Performance | 2.4 | 2.7% | -30.5% | still listed |
| Calpine | Peter Cartwright | 2005 | Performance | 1.5 | -58.7% | -76.6% | bankrupt |
| Cara Therapeutics | Derek Chalmers | 2021 | Performance | 1.0 | 1.0% | -125.6% | under 5 years of data |
| Pss World Medical | Patrick Kelly | 2000 | Performance | 0.8 | -15.9% | 225.3% | still listed |

*Notes.* Founder-CEOs fired, among exits the evidence-based coding also reads as forced, ranked by market value at the fiscal year-end before the departure. Database reason is the CEO dismissal database's code (performance = 3, legal or personal conduct = 4). Days -1 to +1 is the market-model abnormal return; 36 months is the buy-and-hold return minus the market from day +2; it can fall below -100% when the stock lost most of its value while the market rose. After 60 months reports whether the stock still traded, and if not, how it left.

### Survival, returns, profits and the board

### Table IA.10. Delisting within 60 months, with controls and against matched firms

| Outcome | Firings | Retirements | Firing effect with controls, pp | p | N |
|---|---|---|---|---|---|
| Delisted | 31.9% | 16.8% | 9.0 | <0.001 | 3,337 |
| Acquired | 19.0% | 14.1% | 3.7 | 0.065 | 3,337 |
| Bankrupt | 12.0% | 2.6% | 4.9 | <0.001 | 3,337 |
| Delisted, against the matched firm | 30.8% | 23.9% (matched) | 6.9 | <0.001 | 1,164 |
| Delisted, adding prior return, leverage, book-to-market, distress and loss |  |  | 6.6 | 0.005 | 3,138 |
| Acquired, same controls |  |  | 3.9 | 0.074 | 3,138 |
| Bankrupt, same controls |  |  | 2.3 | 0.003 | 3,138 |
| Founder, within firings, same controls |  |  | 1.6 | 0.801 | 1,082 |
| Personal scandal, within firings, same controls |  |  | -1.8 | 0.806 | 1,082 |
| Leverage (debt over assets), coefficient in the same model |  |  | 21.6 | <0.001 | 3,138 |
| Delisted, fired with the evidence agreeing, every control |  |  | 10.4 | 0.002 | 2,478 |
| Bankrupt, fired with the evidence agreeing, every control |  |  | 3.8 | 0.018 | 2,478 |
| Delisted, fired with the evidence unclear, every control |  |  | 4.5 | 0.078 | 2,654 |
| Delisted, fraud firings beyond other firings, every control |  |  | 3.5 | 0.379 | 3,234 |
| Delisting hazard ratio (Cox), size and profitability |  |  | 1.56 | <0.001 | 3,461 |
| Delisting hazard ratio (Cox), every control |  |  | 1.38 | <0.001 | 3,253 |
| Bankruptcy hazard ratio (Cox), every control |  |  | 1.86 | <0.001 | 3,253 |
| Delisting hazard ratio (Cox), evidence agreeing, every control |  |  | 1.64 | <0.001 | 2,560 |

*Notes.* Firing effect with controls: the coefficient on the firing dummy in a linear probability model with log market value, return on assets (ROA) in fiscal year -1, event-year and Fama-French industry effects, standard errors clustered by year. The matched row compares each firing firm with its own matched firm (paired t). The rows marked same controls add the prior 12-month return, leverage, book-to-market, an Altman Z distress flag and a loss flag, on the firms with every item; the founder and personal-scandal rows estimate that model within firings. Evidence agreeing or unclear: firings as the evidence-based coding reads them, against retirements. Hazard ratios: Cox model, every month of follow-up to 60 months, industry strata; above one, firing firms leave sooner.

### Table IA.11. Calendar-time alpha after the announcement

| Portfolio | Equal-weighted, % a month | t | Value-weighted, % a month | t | N months | Firms a month |
|---|---|---|---|---|---|---|
| CEOs fired, 12 months | 0.04% | 0.17 | -0.20% | -0.78 | 294 | 49 |
| CEOs who retired, 12 months | 0.16% | 1.68 | -0.16% | -1.27 | 298 | 89 |
| Firings minus retirements, 12 months | -0.15% | -0.60 | -0.04% | -0.15 | 294 |  |
| CEOs fired, 36 months | 0.03% | 0.17 | -0.11% | -0.70 | 319 | 127 |
| CEOs who retired, 36 months | 0.13% | 1.59 | -0.10% | -0.92 | 322 | 239 |
| Founder fired, 36 months | 0.38% | 0.43 | -0.22% | -0.24 | 128 | 11 |
| Fired over a personal scandal, 36 months | 1.49% | 4.68 | 0.39% | 0.79 | 35 | 12 |
| Firings minus retirements, 36 months | -0.12% | -0.65 | -0.02% | -0.10 | 319 |  |

*Notes.* Each calendar month the portfolio holds every firm whose announcement fell 1 to H months before. Its return minus the risk-free rate is regressed on the Fama-French five factors and momentum; alpha is the intercept, with Newey-West t (6 lags). Value weights are market values at the fiscal year-end before the event. Months with fewer than 10 firms are dropped. The difference rows regress the firing portfolio's return minus the retirement portfolio's. Delisted firms take their delisting return in their last month.

### Table IA.12. Long-run returns at 12, 36 and 60 months

| Group | 12m | 36m | 60m | p, 12m | p, 36m | p, 60m | N, 36m |
|---|---|---|---|---|---|---|---|
| Panel A. Median return minus the market |  |  |  |  |  |  |  |
| CEOs fired | -6.3% | -15.3% | -32.1% | <0.001 | <0.001 | <0.001 | 1,269 |
| CEOs who retired | -0.7% | -4.0% | -7.4% | 0.669 | 0.218 | 0.083 | 2,253 |
| Founder fired | -10.8% | -19.2% | -64.0% | 0.173 | 0.124 | 0.010 | 82 |
| Hired CEO fired | -6.1% | -15.0% | -31.2% | 0.001 | <0.001 | <0.001 | 1,187 |
| Fired over a personal scandal | -5.9% | 9.2% | 3.1% | 0.826 | 0.685 | 0.610 | 40 |
| Fired for another reason | -6.3% | -15.7% | -33.2% | <0.001 | <0.001 | <0.001 | 1,229 |
| Panel B. Median return minus a matched firm |  |  |  |  |  |  |  |
| CEOs fired | -4.6% | 0.0% | -4.7% | 0.035 | 0.735 | 0.246 | 1,217 |
| CEOs who retired | 0.0% | 0.5% | 2.8% | 0.834 | 0.457 | 0.108 | 2,194 |
| Founder fired | -2.2% | 2.0% | 5.7% | 0.716 | 0.629 | 1.000 | 74 |
| Hired CEO fired | -4.8% | -1.0% | -5.2% | 0.038 | 0.637 | 0.242 | 1,143 |
| Fired over a personal scandal | -8.0% | 3.4% | -4.1% | 0.609 | 0.931 | 0.554 | 40 |
| Fired for another reason | -4.6% | 0.0% | -4.7% | 0.040 | 0.708 | 0.209 | 1,177 |
| CEOs fired, mean | -0.9% | 2.3% | 11.7% | 0.748 | 0.735 | 0.387 | 1,217 |

*Notes.* Medians of buy-and-hold returns from day +2 over 12, 36 and 60 months, all firings, with the Wilcoxon p. Panel A subtracts the market's buy-and-hold return; Panel B subtracts a matched firm in the same industry, with market value within 30 percent and the nearest return on assets. The last row gives means with t-test p; skewed returns can give means and medians of opposite sign. Delisted firms take their delisting return and then hold the market. N, 36m counts events at 36 months.

### Table IA.13. Profitability against the matched firm, fiscal years 0 to +3

| Group | Year 0 | Year +1 | Year +2 | Year +3 | N, year +1 | N, year +3 |
|---|---|---|---|---|---|---|
| CEOs fired | -2.0 (<0.001) | -0.4 (0.057) | 0.3 (0.519) | 0.3 (0.537) | 971 | 760 |
| CEOs who retired | -0.2 (0.189) | 0.2 (0.144) | 0.3 (0.549) | 0.2 (0.379) | 1,922 | 1,629 |
| Founder fired | -2.2 (0.057) | -2.0 (0.190) | 1.4 (0.722) | -0.5 (0.518) | 52 | 38 |
| Hired CEO fired | -2.0 (<0.001) | -0.4 (0.101) | 0.2 (0.560) | 0.3 (0.419) | 919 | 722 |
| Fired over a personal scandal | 0.0 (0.692) | 0.0 (0.846) | 0.8 (0.777) | 1.8 (0.048) | 33 | 25 |
| Fired for another reason | -2.1 (<0.001) | -0.4 (0.058) | 0.3 (0.546) | 0.2 (0.761) | 938 | 735 |

*Notes.* Median change in return on assets (ROA) from fiscal year -1 to year 0 (the year of the departure), +1, +2 and +3, minus the same change at the matched firm, in percentage points, with the Wilcoxon p in parentheses. ROA is earnings before interest, taxes, depreciation and amortization (EBITDA) over total assets, winsorized at the 1st and 99th percentiles. N falls with the horizon because firms stop filing after a sale or bankruptcy.

![Figure IA.3. Profits and the board after the firing](../figures/fig6_roa_board.png)

*Figure IA.3. Profits and the board after the firing.* Notes. (a) Median change in return on assets from fiscal year -1, minus the same change at the matched firm, in percentage points, fiscal years 0 to +3. (b) About two years after the departure, three shares: pre-departure directors not named in the later proxy, firms with a separate chair and CEO, and firms where the departing CEO is still a director. Firings are red and retirements grey; the diamond marks fired founders.

### Table IA.14. The board about two years after the departure

| Group | Earlier directors gone | N | Split before | Split after | N, split | Departing CEO still a director |
|---|---|---|---|---|---|---|
| CEOs fired | 48.0% | 566 | 56.3% | 66.1% | 177 | 3.9% |
| CEOs who retired | 37.8% | 1,310 | 27.2% | 65.9% | 440 | 33.3% |
| Founder fired | 52.5% | 31 | 26.7% | 81.8% | 11 | 9.7% |
| Hired CEO fired | 47.8% | 535 | 58.5% | 65.1% | 166 | 3.6% |
| Fired over a personal scandal | 46.0% | 13 | 0.0% | 100.0% | 1 | 0.0% |
| p, firings against retirements | <0.001 | 1,876 |  |  |  |  |
| p, founder against hired CEO | 0.438 | 566 |  |  |  | 0.113 |

*Notes.* Directors in the last proxy before the departure and the first one at least 600 days after it, matched on surname and first initial. Earlier directors gone: the share no longer named; a proxy does not say why. Split: the chair and CEO roles held by different people, where the later proxy names a chair (N, split). Last column: the founder for fired founders, otherwise the departing CEO. The p rows: Welch t for directors gone, Fisher exact test for the last column.

## References
