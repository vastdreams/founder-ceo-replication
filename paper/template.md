# Sacked: Sex, Fraud, and the Fate of Firms That Fire Their Founder CEO

## Abstract

Founder CEOs are dismissed once their firms have fallen behind normal firms. We study {{fr.founder_main.n_all}} founder dismissals not over fraud at S&P {{index_size}} firms, {{sample_start}} to {{sample_end}}, each checked against filings and press.

From six weeks before the announcement to the day after, these firms trail the S&P 500 by {{fv.founder.sp.slideann.ret.mean|abs}}, their industry by {{fv.founder.ind.slideann.ret.mean|abs}} and their three closest competitors by {{fv.founder.pr3.slideann.ret.mean|abs}}. Most of it comes before the news. Against the closest single competitor the gap, {{fv.founder.pr.slideann.ret.mean|abs}}, could be chance.

Across all dismissals, shares fall {{car.conduct.mm_m1p1.mean|abs}} over the three announcement days after a personal scandal and {{car.criminal.mm_m1p1.mean|abs}} after fraud.

## 1. Introduction

Founders are said to carry knowledge and commitment that no hired successor can replace [@fahlenbrach2009]. They are also said to entrench themselves, so that removing them ends a cost [@bebchuk2017; @gompers2010]. Either way, dismissing a founder is a rare and visible decision for a board. This paper asks what the founder's shareholders lose against normal firms when the board takes it, and when the loss arrives (Table 1).

The question arose again in {{hook_month}}, after our sample ends, when Nvidia's board accepted the resignation of its co-founder and CEO, Jensen Huang [@nvidia2026form8k]. The board had opened an independent investigation three days earlier [@nvidia2026board], and news reports described an affair [@cnbc2026nvidia]. Nvidia's shares closed {{hook.nvda.day_ret|abs}} lower on the first trading day after the news [@cnbc2026nvidia]. Twelve days later the board voted unanimously to reinstate him as CEO [@nvidia2026reinstate]. It cited input from senior levels of the United States government. The case lies outside our sample, and our data hold only {{fr.founder_scandal.n_all}} founders dismissed over a personal scandal, too few for an estimate.

The evidence on this question is thin. Studies of forced CEO turnover show that boards act after poor performance and that share prices fall before the announcement [@jenter2015; @weisbach1988]. Studies of founders compare founder-led firms with others, or examine startups and sudden deaths [@ewens2018; @jenter2023]. Few measure, in dollars, what shareholders lose against normal firms when a public firm's board removes the founder. Fewer separate that loss from the decline that comes before it.

We take every founder dismissal in an open database of CEO departures [@gentry2021] and check each case against filings and press reports. AI research assistants, working case by case under rules fixed in advance, read the record for all {{fa.n_checked}} founder departures the database codes as forced. They found {{fa.n_planned_dropped}} planned successions, which we exclude, and dates and reasons that the record contradicted, which we correct. A founder forced to resign counts as dismissed, so we also read the {{fa.n_retirements_scanned}} founder departures the database codes as retirements; {{fa.n_forced_resign_added}} were forced resignations and join the sample. The final sample holds {{fa.n_kept}} founder dismissals, {{fr.founder_main.n_all}} of them for reasons other than fraud.

We set each founder firm against five benchmarks of normal firms, defined in Section 4.1, over a six-week window that runs to the day after the announcement. Over the six-week window, founder firms trail the market index by {{fv.founder.sp.slideann.ret.mean|abs}}, their industry by {{fv.founder.ind.slideann.ret.mean|abs}} and their three closest competitors by {{fv.founder.pr3.slideann.ret.mean|abs}} (Table 3). Each of these losses is statistically significant after a Holm adjustment across the five benchmarks (Table IA.5).

In {{dollar_year}} dollars, the median founder firm loses {{fv.founder.pr3.slideann.usd.median|abs}} against its three closest competitors and {{fv.founder.sp.slideann.usd.median|abs}} against the market index over the same six weeks (Table 3). Totals rest on a few very large firms and are in Table IA.7.

The loss is smaller against benchmarks matched on the firm's own record. Against a firm matched on profitability it is {{fv.founder.roa.slideann.ret.mean|abs}} (p {{fv.founder.roa.slideann.ret.mean|p}}). Against the single competitor closest on the prior year's return it is {{fv.founder.pr.slideann.ret.mean|abs}}, which could be chance (p {{fv.founder.pr.slideann.ret.mean|p}}). We lead with the average of three competitors because one competitor carries its own news into the comparison. We chose it after seeing the results, and report the single competitor beside it throughout (Section 4.1).

The result does not hinge on three: against the average of two, four or five competitors the loss is {{fv.founder.pr2.slideann.ret.mean|abs}}, {{fv.founder.pr4.slideann.ret.mean|abs}} and {{fv.founder.pr5.slideann.ret.mean|abs}} (Table IA.31).

Most of the loss comes before the announcement, while the decline that precedes the board's action is under way. Before the news, founder firms lose {{fv.founder.pr3.slide.ret.mean|abs}} against their three closest competitors (p {{fv.founder.pr3.slide.ret.mean|p}}). The three announcement days add {{fv.founder.pr3.ann.ret.mean|abs}}, which could be chance (p {{fv.founder.pr3.ann.ret.mean|p}}; Table 3). The design cannot tell investors anticipating the dismissal from the bad news that prompts it. Once the news is public, no founder trading rule survives the correction for testing several rules (Section 5.5).

Over longer horizons the answer depends on the benchmark. Index benchmarks carry the typical stock's lag behind indexes lifted by a few winners, while the matched firm also controls for the firm's own record. Five years on, the median founder firm trails its industry by {{fv.founder.ind.m60.ret.median|abs}} (p {{fv.founder.ind.m60.ret.median|p}}). Against a firm matched on profitability the median gap is {{fv.founder.roa.m60.ret.median}}, which could be chance (Table 3). Revenue growth slows by {{fg.founder.ind.rev.y3.median|abs}} a year against the industry to the third year (p {{fg.founder.ind.rev.y3.median|p}}), but not detectably against the closest competitor (Table 9).

Two further results concern all dismissals, founders and hired CEOs together. Within five years {{exit.forced.bankruptcy_5y}} of dismissing firms go bankrupt, against {{exit.retired.bankruptcy_5y}} of firms whose CEO retired (Table 7). The recorded reason goes with the announcement return. Shares fall {{car.criminal.mm_m1p1.mean|abs}} over three days after a fraud dismissal and {{car.conduct.mm_m1p1.mean|abs}} after a personal scandal (p {{cardiff.conduct_vs_criminal.mm_m1p1.diff_mean|p}}; Table 5). Scandal dismissals do not differ from other dismissals not over fraud (p {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean|p}}).

The census is itself a contribution. AI research assistants checked every founder dismissal at large US firms case by case, and every exclusion is documented. The check removes {{fa.n_planned_dropped}} planned successions that the database records as dismissals. The paper also measures what founder firms lose against normal firms, in percent and in dollars, under five benchmarks and in each part of the window (Table 3). It then follows the founder firm's growth against its industry and its competitors for five years (Table 9).

The analysis is descriptive. Boards dismiss the CEOs of firms already in difficulty, and no comparison here identifies what would have happened had the founder stayed. Nor can the data separate the founder's departure from the slowing of firms that had grown fast.

::: glance

### Table 1. Dismissing firms decline, fall at the announcement and fail more often; founder firms fall behind normal firms: S&P {{index_size}} firms, {{sample_start}} to {{sample_end}}

| Horizon | What is measured | Dismissals (Panel C: founder firms) | Retirements | N | p |
|---|---|---|---|---|---|
| Panel A. Returns |  |  |  |  |  |
| Trading days {{d_slide0}} to {{d_slide1}} | Return minus the market | {{drift.forced.pre_m30m2.mean}} | {{drift.retired.pre_m30m2.mean}} | {{drift.forced.pre_m30m2.mean!n}} | {{drift.forced.pre_m30m2.mean!pv}} |
| Trading days {{d_ann0}} to {{d_ann1}} | Abnormal return, market model | {{car.forced.mm_m1p1.mean}} | {{car.retired.mm_m1p1.mean}} | {{car.forced.mm_m1p1.mean!n}} | {{car.forced.mm_m1p1.mean!pv}} |
| Trading days {{d_post0}} to {{d_post1}} | Return minus the market | {{drift.forced.post_p2p60.mean}} | {{drift.retired.post_p2p60.mean}} | {{drift.forced.post_p2p60.mean!n}} | {{drift.forced.post_p2p60.mean!pv}} |
| Trading days {{d_slide0}} to {{d_ann1}} | Return minus the closest competitor, mean | {{fv.forced.pr.slideann.ret.mean}} | {{fv.retired.pr.slideann.ret.mean}} | {{fv.forced.pr.slideann.ret.count}} | {{fvdiff.forced_vs_retired.pr.slideann.ret.diff!pv}} |
| Trading days {{d_slide0}} to {{d_ann1}} | Dollar change against that competitor, mean per firm | {{fv.forced.pr.slideann.usd.mean}} | {{fv.retired.pr.slideann.usd.mean}} | {{fv.forced.pr.slideann.usd.count}} | {{fvdiff.forced_vs_retired.pr.slideann.usd.diff!pv}} |
| {{months_1y}} months | Return minus a matched firm, median | {{mbhar.forced.1y.median}} | {{mbhar.retired.1y.median}} | {{mbhar.forced.1y.median!n}} | {{mbhar.forced.1y.median!pv}} |
| {{months_3y}} months | Return minus a matched firm, median | {{mbhar.forced.3y.median}} | {{mbhar.retired.3y.median}} | {{mbhar.forced.3y.median!n}} | {{mbhar.forced.3y.median!pv}} |
| {{months_5y}} months | Return minus a matched firm, median | {{mbhar.forced.5y.median}} | {{mbhar.retired.5y.median}} | {{mbhar.forced.5y.median!n}} | {{mbhar.forced.5y.median!pv}} |
| Months {{m_first}} to {{months_3y}} | Risk-adjusted return (alpha), per month | {{alpha.forced.ew.36m}} | {{alpha.retired.ew.36m}} | {{alpha.forced.ew.36m!n}} | {{alpha.forced.ew.36m!pv}} |
| Panel B. The firm |  |  |  |  |  |
| Within {{months_5y}} months | Share of firms delisted * | {{exit.forced.delisted_5y}} | {{exit.retired.delisted_5y}} | {{exit.forced.delisted_5y!n}} | {{exitdiff.forced_vs_retired.delisted_5y!pv}} |
| Fiscal year 0 | Change in return on assets minus the matched firm, median, percentage points | {{roa.forced.abn_d_0.median}} | {{roa.retired.abn_d_0.median}} | {{roa.forced.abn_d_0.median!n}} | {{roa.forced.abn_d_0.median!pv}} |
| Fiscal year {{fy_plus1}} | Change in return on assets minus the matched firm, median, percentage points | {{roa.forced.abn_d_1.median}} | {{roa.retired.abn_d_1.median}} | {{roa.forced.abn_d_1.median!n}} | {{roa.forced.abn_d_1.median!pv}} |
| About two years | Share of earlier directors not in the later proxy statement * | {{board.forced.director_turnover.mean}} | {{board.retired.director_turnover.mean}} | {{board.forced.director_turnover.mean!n}} | {{boarddiff.forced_vs_retired.director_turnover.diff_mean!pv}} |
| Panel C. Founder firms against normal firms |  |  |  |  |  |
| {{sample_start}} to {{sample_end}} | Founder dismissals kept after the case check | {{fa.n_kept}} |  | {{fa.n_kept}} |  |
| Trading days {{d_slide0}} to {{d_ann1}} | Return minus the S&P 500, mean | {{fv.founder.sp.slideann.ret.mean}} |  | {{fv.founder.sp.slideann.ret.count}} | {{fv.founder.sp.slideann.ret.mean!pv}} |
| Trading days {{d_slide0}} to {{d_ann1}} | Return minus the industry average, mean | {{fv.founder.ind.slideann.ret.mean}} |  | {{fv.founder.ind.slideann.ret.count}} | {{fv.founder.ind.slideann.ret.mean!pv}} |
| Trading days {{d_slide0}} to {{d_ann1}} | Return minus the three closest competitors, mean | {{fv.founder.pr3.slideann.ret.mean}} |  | {{fv.founder.pr3.slideann.ret.count}} | {{fv.founder.pr3.slideann.ret.mean!pv}} |
| Trading days {{d_ann0}} to {{d_ann1}} | Return minus the three closest competitors, mean | {{fv.founder.pr3.ann.ret.mean}} |  | {{fv.founder.pr3.ann.ret.count}} | {{fv.founder.pr3.ann.ret.mean!pv}} |
| Within {{months_5y}} months | Share of firms bankrupt | {{exit.forced_founder.bankruptcy_5y}} | {{exit.retired.bankruptcy_5y}} | {{exit.forced_founder.n5}} |  |

*Notes.* Dismissals exclude those over fraud or other legal violation. Day 0 is the first trading day on or after the announcement. Days {{d_ann0}} to {{d_ann1}} use well-dated dismissals. The closest competitor shares the firm's industry and size band and has the nearest prior-year return; the three closest competitors are averaged (Section 4.1). Dollars are {{dollar_year}} dollars; a month is {{trading_days_per_month}} trading days from day {{d_post0}}. The alpha is the monthly five-factor and momentum intercept; its N counts months. p tests against zero or, in competitor rows and rows marked *, against retirements. In Panel C, N counts founder firms, p tests the return gap against zero, and the bankruptcy row is descriptive.

:::

## 2. Related literature and hypotheses

Three strands of earlier work bear on what follows a dismissal. The first asks when boards act. Boards dismiss CEOs after poor performance, including poor performance of the whole industry [@jenter2015], and returns fall well before the change [@weisbach1988]. A dismissal after an industry downturn can be an efficient rematch of CEOs and firms rather than a mistake [@eisfeldt2013]. Dismissals are rare, which suggests that boards treat replacing a CEO as costly [@taylor2010; @kaplan2012], and large pay cuts serve as a substitute [@gao2012]. Accounting performance worsens before a CEO change and improves after it [@huson2004], and volatility rises more after forced than after voluntary exits [@clayton2005]. The market's reaction depends on what the dismissal reveals about the firm [@kind2011; @chen2026]. Together these studies predict a fall in the share price before the announcement and a smaller fall at it.

The second strand, on whether founders are different, points both ways. Founder-led firms invest differently and have been valued more highly [@fahlenbrach2009], but founder status itself responds to performance [@adams2009]. Founders are often replaced as their firms mature [@wasserman2003; @aran2024], and in venture-backed startups replacing the founder improves outcomes [@ewens2018]. The value of a founder's leadership may decline with time since the listing [@bebchuk2017], and insider control beyond cash-flow rights goes with lower firm value [@gompers2010]. Yet CEO turnover at dual-class firms is as sensitive to performance as elsewhere [@aran2025]. The share price reaction to a CEO's sudden death does not differ between founders and other CEOs [@jenter2023]. In Poland, poorly performing founder CEOs are less likely to be dismissed than other CEOs [@kowalewski2019].

The third strand separates misconduct by the firm from misconduct by the person. Financial misreporting and executive scandals are both followed by falls in the share price [@cline2018; @larcker2016; @borellikjaer2021; @karpoff2008jfqa], and managers who misreport usually lose their jobs [@karpoff2008jfe]. Boards dismiss CEOs who manage earnings before outside penalties arrive [@hazarika2012], and more often where employees and directors are prosocial [@bereskin2020]. Shares also fall when a CEO is accused of sexual misconduct [@mooibroek2021] and when a firm reports sexual harassment [@abeysekera2024]. Board resignations rose at exposed firms after the #MeToo revelations of {{metoo_year}} [@baharad2026]. Where @cline2018 measure the return when a personal indiscretion becomes public, we measure the dismissal that follows and compare it with dismissals over fraud.

The paper brings together in one sample what founder firms lose against normal firms, why boards act, and what becomes of the firm. It follows each dismissal from six weeks before the announcement to five years after and reports the number of firms at every horizon. It states the loss in dollars, against five benchmarks. And it checks, case by case, who was a founder, why the board acted and when the dismissal was announced.

We state two hypotheses about founders and two supporting comparisons for all dismissals. Founders could also be set against hired CEOs. With {{fv.founder.pr.slideann.ret.count}} founder dismissals measured against a competitor, that comparison would be too weak to answer. The paper therefore does not test it. The founder question below was set after those results, and every benchmark computed before it is reported (Internet Appendix A).

**H1 (founder firms against normal firms).** Around the dismissal of a founder CEO, the firm's shares fall behind normal firms: the market, its industry and comparable competitors. The irreplaceable-founder view predicts a fall at the announcement itself. A board that acts as the firm declines predicts that most of the loss comes before it [@jenter2015].

**H2 (growth after a founder dismissal).** After a founder dismissal, the firm's growth slows against its competitor and against its industry.

**Supporting comparison A (dismissals and retirements).** Firms whose board dismisses the CEO decline before the announcement, fall at it and fail more often than firms whose CEO retires [@jenter2015; @weisbach1988].

**Supporting comparison B (reasons for dismissal).** A dismissal over a personal scandal is followed by a smaller fall in the share price than a dismissal over fraud. A fraud reveals that the firm's accounts or conduct were unreliable; a personal scandal concerns one person [@karpoff2008jfqa; @cline2018].

Section 5 reports H1, then the two supporting comparisons, then H2.

## 3. Data and sample

### 3.1 Dismissals

The departures come from the open CEO dismissal database of @gentry2021, which its authors have extended to cover {{db_start}} to {{sample_end}}. It codes the reason for every CEO departure at S&P {{index_size}} firms from press coverage and filings, and an independent recoding agreed with it on {{lit_gentry_agreement_pct}}% of events [@gentry2021]. Codes {{db_code_dismiss_a}} and {{db_code_dismiss_b}}, dismissal for job performance and for legal violations or personal conduct, are dismissals. Code {{db_code_retire}}, voluntary retirement, is the comparison group.

Press releases rarely say that a CEO was dismissed [@gow2017], and how dismissals are classified changes the results [@fee2018]. Like the database, we treat a resignation under board pressure as a dismissal, including one during an investigation, a scandal or an activist campaign.

From the dismissals we remove the {{a.n_criminal_all_dates}} whose main reason is fraud or other legal violation. These cover financial misconduct, a legal or regulatory breach by the firm, and criminal charges against the CEO. They are a comparison group throughout, because there the firm itself is in trouble with the law. A personal scandal is a dismissal over sexual misconduct, a relationship with an employee, conduct at work or another personal failing such as a false degree. There are {{a.n_lr_conduct}} of them, of which {{a.n_lr_founder_personal}} are founders, too few for a test.

We also sort each founder dismissal by why the board acted: fraud, an event, or performance and other reasons (Table 8). An event is either a personal scandal or a boardroom coup. We call a dismissal a coup when its coded main reason is a dispute over strategy or power between the CEO and the board. There are {{fr.founder_coup.n_all}} coups against founders, and each was checked case by case against filings and press. Before computing any group, we fixed that a group with fewer than {{min_reason_cases}} dismissals gets no average; we name its cases instead.

Each departure is linked to the firm's identifier at the Securities and Exchange Commission. Through it we take daily prices from Sharadar's Core US Equities data, which include firms later delisted. That leaves {{a.n_lr_forced}} dismissals and {{a.n_lr_retired}} retirements from {{sample_start}} to {{sample_end}} with share prices. Table IA.3 traces the dismissals from the database to the samples, and Figure IA.1 shows them by year.

### 3.2 Founders, reasons and the case checks

We code who was a founder, and why the board acted, in two steps. First, a language model (DeepSeek, deepseek-chat) reads the database's notes and sources, the 8-K, cited press releases, the CEO's Wikipedia article and New York Times articles. For each departure it records whether the CEO founded the firm, whether the exit was forced and the board's main reason, each with a supporting quote. We call this the evidence-based coding.

A CEO is a founder if he or she founded or co-founded the firm or its direct predecessor. Heirs of founders are not founders, nor are long-serving CEOs who joined after the founding. A first review checked against the sources every founder code on a dismissal and every code of fraud, sexual misconduct, a relationship or other personal conduct. It kept {{code.founder.share_kept}} of the model's founder codes, {{code.fraud.share_kept}} of its fraud codes and {{code.personal.share_kept}} of its personal-conduct codes (Table IA.3). Tables 5 and 8 rest on the reviewed codes.

The evidence-based coding often cannot tell whether an exit was forced. Of the {{car.forced.mm_m1p1.mean|n}} well-dated dismissals with returns (Section 3.3), it reads {{strict.llm_yes.mm_m1p1.mean|n}} as forced, {{strict.llm_no.mm_m1p1.mean|n}} as not forced and {{strict.llm_unclear.mm_m1p1.mean|n}} as unclear, mostly because the sources do not say. The main tests use every well-dated dismissal whatever this reading; Table 5 reports each group separately.

AI research assistants (Anthropic's Claude) then checked every founder departure a second time, case by case, under rules fixed in advance (Internet Appendix A). They found three kinds of error. First, {{fa.n_planned_dropped}} departures were planned successions, in which the founder remained chairman and a designated successor took over on a timetable; we exclude them from every analysis (Table IA.2). Second, some announcement dates were the day the CEO left office rather than the day of the first public report, and we moved them to the first report. Third, four reasons were recoded.

The founder sample therefore narrows in steps. The case check starts from the {{fa.n_checked}} founder departures the database codes as forced and the {{fa.n_forced_resign_added}} forced resignations it codes as retirements. Of these, {{fa.n_kept}} remain after the check, and {{fr.founder_main.n_all}} of these are for reasons other than fraud. Each benchmark needs its own data, so the number of founder firms measured runs from {{fv.founder.pr3.slideann.ret.count}} to {{fv.founder.sp.slideann.ret.count}} (Table 3).

Hired-CEO dismissals enter the results on all dismissals, so a random sample of {{fa.audit.hired.n}} of them was checked with the same rules (Table IA.1). The audit found {{fa.audit.hired.planned}} planned successions and {{fa.audit.hired.redate}} incorrect dates, which are corrected in the same way. The founder results use founder firms only.

Founders the model coded as hired CEOs were not reviewed case by case. As a check, {{fmiss.n_wikidata}} of the {{fmiss.n_hired}} such dismissals are at firms whose founders Wikidata lists. None of those CEOs founded the firm; the {{fmiss.n_surname_match}} who share a founder's surname are heirs. No second human coder has checked either the first review or the case checks. The case files, with every source quoted, are in the replication package so that the codes can be audited. Both language models, and the Wikipedia articles they read, may know later outcomes, so codes of whether and why a CEO was forced could reflect hindsight. The case checks lean on the 8-K and press of the announcement, and founder status, fixed at the founding, is least exposed.

### 3.3 Announcement dates

The three-day test depends on an accurate announcement date. The database gives one for about a third of departures; for the rest it gives only the day the CEO left office, which can come weeks after the news. A second date comes from the firm's 8-K, which a company must file within four business days of a CEO change. Where the database does give a date, the two agree within {{date_agree_days}} days in only {{redate_agree_3d_pct}}% of cases, which is why the announcement tests use only well-dated dismissals.

We call a dismissal well-dated when the database, or a dated source checked case by case, gives its announcement day. Of the {{a.n_lr_forced}} dismissals, {{a.n_forced}} are well-dated, and the announcement tests use only these. Results over months and years use all {{a.n_lr_forced}} dismissals, because an error of a few days matters little over a year or more.

The well-dated dismissals are not a random draw. Compared with the others, they are at larger firms, follow a smaller fall over the prior year, and include more founders and personal scandals (Table IA.13). Those two groups were dated from 8-Ks, press releases and New York Times reports. Every founder dismissed over fraud or in a boardroom coup was also dated this way, before any of their returns was computed. Where a board first put the CEO on leave and removed the CEO later, the date is the announcement of the leave. The announcement fall survives reweighting the well-dated dismissals to resemble every dismissal (Table 5), and it survives a window of trading days {{d_wide0}} to {{d_wide1}} around every dismissal (Table IA.12).

### 3.4 Summary statistics

Table 2 compares firms at the fiscal year-end before the departure. Dismissing firms are smaller and less profitable than retirement firms: the median market value is {{desc.forced.mcap.median}} billion dollars against {{desc.retired.mcap.median}}, and the median return on assets {{desc.forced.roa.median}} against {{desc.retired.roa.median}}. Their shares had also fallen over the preceding year (Table IA.4). These differences motivate the benchmarks of Section 4.

<!-- TABLE:2 -->

## 4. Empirical design

The announcement return is the abnormal return over the three trading days from the day before the announcement (day {{d_ann0}}) to the day after it (day {{d_ann1}}). The abnormal return is the stock's return minus what the market model of equation (1) predicts from the market's return and the stock's own past relation to it.

$$AR_{it} = R_{it} - \hat\alpha_i - \hat\beta_i R_{mt}, \qquad CAR_i = AR_{i,-1} + AR_{i,0} + AR_{i,+1}. \tag{1}$$

Here $R_{it}$ is the stock's total return and $R_{mt}$ the market's. The coefficients come from trading days {{estimation_window_start}} to {{estimation_window_end}} before the announcement. We test the mean with the cross-sectional t and the standardized test of @boehmer1991, and the median with the Wilcoxon signed-rank test [@kothari2007]. For the six weeks before and the three months after, we subtract the market's return instead of using the market model. Shares slide before a dismissal, so a falling stock receives a negative $\hat\alpha$, and subtracting that negative trend afterwards would make ordinary returns look like a recovery.

For the long run, the main measure is the buy-and-hold return from day {{d_post0}} over {{days_1y}}, {{days_3y}} or {{days_5y}} trading days, that is one, three or five years. Equation (2) subtracts the return of the market or of a matched firm:

$$BHAR_i(h) = \prod_{t=2}^{T_h}(1+R_{it}) - \prod_{t=2}^{T_h}(1+R_{bt}). \tag{2}$$

The matched firm is in the same Fama-French industry, within {{matching_rule_pct}}% in market value, with the nearest return on assets. It had no recorded CEO change in the three years before. Matching on prior profitability follows @barber1996, whose tests are well specified only when firms are matched on performance before the event. We also hold a calendar-time portfolio of every firm in its first {{m36}} months after an announcement and regress its excess return on the five Fama-French factors and momentum [@famafrench2015; @lyon1999]. The intercept, the alpha, is the monthly return those risks do not explain.

On the day a firm is delisted, its return is set to zero for a takeover and minus {{delist_bankrupt}} for a bankruptcy. Other delistings get minus {{delist_other}}, close to the average loss on delistings for poor performance [@shumway1997]. Because dismissing firms are smaller, every long-run comparison is also made against a matched firm or within size bands.

### 4.1 Benchmarks for the founder firm

We set each founder firm against five benchmarks of normal firms. The first is the market index, the S&P 500 total return. The second is the industry average, the equal-weighted mean return of the other S&P {{index_size}} firms in the firm's industry. The third and fourth are competitors, and the fifth is the matched firm above, chosen on profitability.

A competitor shares the firm's 4-digit standard industrial classification (SIC) code, else its 3-digit code, else its Sharadar industry. Its market value is within {{size_band}} of the firm's at the fiscal year-end before. It had no recorded CEO change in the three years up to the dismissal. Among those firms, the closest competitor has the nearest buy-and-hold return over trading days {{d_prior0}} to {{d_prior1}}. The three closest competitors are the three nearest by the same rule, averaged.

The main window runs from trading day {{d_entry}} to day {{d_ann1}}, which we call the six-week window. Within it, trading days {{d_slide0}} to {{d_slide1}} measure the slide before the news and days {{d_ann0}} to {{d_ann1}} the announcement.

The dollar change is the firm's return minus the benchmark's, times the firm's market value at the start of the window, in {{dollar_year}} dollars. We test means with a one-sample t test and medians with the Wilcoxon signed-rank test. A Holm adjustment across the five benchmarks of each window was added after review (Table IA.5).

Each benchmark answers a different version of the question. The market index and the industry say what the founder firm lost against the market and against firms in its line of business. They do not adjust for the decline that usually precedes a dismissal, and a typical stock lags an index that a few large winners lift. The competitors adjust for that decline: they had a similar year before the dismissal.

The five benchmarks therefore bracket the answer. The market index and the industry give the loss that a holder of the founder firm suffered against holding the market or the sector instead. The matched benchmarks ask a narrower question: how much worse the founder firm did than firms with a similar recent record. Where they record a smaller loss (Table 3), part of the loss against the market came with a decline that similar firms shared.

The closest competitor is the nearest match on that year, but it is one firm, and its own news moves the comparison. The average of the three closest competitors keeps the adjustment and averages away much of that noise. We therefore lead with it, and report the single competitor beside it throughout. Averages of two, four and five competitors, by the same rule, are in Table IA.31.

Two cautions apply to the average of three. It needs three candidates, so it covers {{fv.founder.pr3.slideann.ret.count}} founder firms against {{fv.founder.pr.slideann.ret.count}} for the single competitor. And the closest competitor did better over the year before: founder firms fell {{fvbal.founder.prior12.firm.mean|abs}} and their closest competitors {{fvbal.founder.prior12.comp.mean|abs}} (Table IA.4). Section 7 reports the same balance for the average of three.

## 5. Results

### 5.1 H1: founder firms against normal firms

H1 is supported against the market, the industry and the three closest competitors (Table 3). The six-week losses against these three benchmarks, {{fv.founder.sp.slideann.ret.mean|abs}}, {{fv.founder.ind.slideann.ret.mean|abs}} and {{fv.founder.pr3.slideann.ret.mean|abs}}, are each statistically significant on their own (Table 3). After the Holm adjustment across the five benchmarks, the p-values are {{fv.founder.sp.slideann.ret.mean.holm5_p}}, {{fv.founder.ind.slideann.ret.mean.holm5_p}} and {{fv.founder.pr3.slideann.ret.mean.holm5_p}} (Table IA.5).

Medians and dollars point the same way. The median founder firm trails its three closest competitors by {{fv.founder.pr3.slideann.ret.median|abs}} and its industry by {{fv.founder.ind.slideann.ret.median|abs}}. In {{dollar_year}} dollars, the median founder firm loses {{fv.founder.pr3.slideann.usd.median|abs}} against its three closest competitors and {{fv.founder.ind.slideann.usd.median|abs}} against its industry (Table 3).

Dollar totals tell the same story but rest on a few firms. Over the six-week window the founder firms lose {{fv.founder.sp.slideann.usd.total_bn|abs}} in all against the market index and {{fv.founder.ind.slideann.usd.total_bn|abs}} against their industry (Table IA.7). A single large firm can account for much of either total, so we read the medians per firm.

Against benchmarks matched on the firm's own record the loss is smaller. Against the firm matched on profitability it is {{fv.founder.roa.slideann.ret.mean|abs}} (p {{fv.founder.roa.slideann.ret.mean|p}}). Against the single closest competitor it is {{fv.founder.pr.slideann.ret.mean|abs}}, which could be chance (p {{fv.founder.pr.slideann.ret.mean|p}}). The median founder firm ends {{fv.founder.pr.slideann.ret.median}} ahead of that competitor, also within chance (p {{fv.founder.pr.slideann.ret.median|p}}).

The slide before the news carries most of the loss. Over trading days {{d_slide0}} to {{d_slide1}}, founder firms lose {{fv.founder.pr3.slide.ret.mean|abs}} against their three closest competitors (p {{fv.founder.pr3.slide.ret.mean|p}}) and {{fv.founder.ind.slide.ret.mean|abs}} against their industry (Table 3).

The announcement adds little that can be told from chance. Over the three days around it, founder firms lose a further {{fv.founder.pr3.ann.ret.mean|abs}} against their three closest competitors (p {{fv.founder.pr3.ann.ret.mean|p}}) and {{fv.founder.sp.ann.ret.mean|abs}} against the market index (p {{fv.founder.sp.ann.ret.mean|p}}). Investors may have anticipated the dismissal, or the slide may be the bad news that prompts it; the design cannot separate the two.

<!-- TABLE:3 -->

Table 4 states the comparison as an investment. Put {{invest_usd}} in the median founder firm six weeks before the announcement, and it is worth {{fvinv.founder.firm_ind.d1.median}} the day after. The same {{invest_usd}} in its industry average is worth {{fvinv.founder.ind.d1.median}}. Each column of Table 4 gives a median, so the two are not the same pair.

<!-- TABLE:4 -->

Over longer horizons the answer depends on the benchmark. Five years after the announcement, the median founder firm trails its industry by {{fv.founder.ind.m60.ret.median|abs}} (p {{fv.founder.ind.m60.ret.median|p}}) and the market index by {{fv.founder.sp.m60.ret.median|abs}} (p {{fv.founder.sp.m60.ret.median|p}}). Against the firm matched on profitability the median gap is {{fv.founder.roa.m60.ret.median}}, which could be chance (Table 3).

For long-run returns the median is the better summary. A typical stock lags an index that a few large winners lift, so index comparisons overstate the typical loss, and means do the opposite. A few founder firms multiplied in value, which lifts the mean five-year gap against the market index to {{fv.founder.sp.m60.ret.mean}} (Table 3). We therefore read the medians, and against the three closest competitors the five-year median gap, {{fv.founder.pr3.m60.ret.median}}, could be chance (p {{fv.founder.pr3.m60.ret.median|p}}).

As a description only, {{exit.forced_founder.bankruptcy_5y}} of founder firms go bankrupt within five years (Table 8). Section 5.2 tests the bankruptcy gap for all dismissals against retirements; the founder figure is not tested on its own.

### 5.2 Dismissals and retirements

Dismissing firms decline before the board acts, fall again at the announcement and fail more often afterwards (Figure 1). In the six weeks before the announcement they lag the market by {{drift.forced.pre_m30m2.mean|abs}}, while retirement firms move with it (Table 1). Over the three trading days around the announcement they fall a further {{car.forced.mm_m1p1.mean|abs}} (Table 5). In the three months that follow they move with the market.

![Figure 1. Prices slide before the dismissal, drop on the news, then stop](/static/reports/founder-ceo/figures/fig1_event_time.png)

*Figure 1. Prices slide before the dismissal, drop on the news, then stop.* Notes. Cumulative return minus the market from trading day {{fig_d0}} to day {{fig_d1}} around the announcement (day 0), well-dated dismissals with every day of the window. Panel (a) shows means, with the {{ci_pct}} confidence band for dismissals; the grey band marks days {{d_ann0}} to {{d_ann1}}. Panel (b) shows medians, so that one firm cannot move a small group's line. The lines sum daily returns, so their end points differ slightly from the window returns of Table 1.

Against their closest competitors, dismissing firms lose {{fv.forced.pr.slideann.ret.mean|abs}} over the six-week window and retirement firms {{fv.retired.pr.slideann.ret.mean|abs}}. The difference is statistically significant (p {{fvdiff.forced_vs_retired.pr.slideann.ret.diff|p}}; Table 1). In {{dollar_year}} dollars the median dismissing firm loses {{fv.forced.pr.slideann.usd.median|abs}} over the six weeks.

<!-- TABLE:5 -->

The modest announcement return comes after a slide and is followed by a high rate of failure. Within five years {{exit.forced.delisted_5y}} of dismissing firms have been delisted, against {{exit.retired.delisted_5y}} after a retirement (Table 7, Figure 2). Most of the difference is bankruptcy: {{exit.forced.bankruptcy_5y}} of dismissing firms go bankrupt, against {{exit.retired.bankruptcy_5y}}.

![Figure 2. Within five years, {{exit.forced.delisted_5y}} of dismissing firms are delisted](/static/reports/founder-ceo/figures/fig3_exits.png)

*Figure 2. Within five years, {{exit.forced.delisted_5y}} of dismissing firms are delisted.* Notes. Cumulative share of firms delisted, by month after the announcement, for firms with a complete {{months_5y}}-month horizon: (a) for any reason, (b) in bankruptcy. Most of the rest are takeovers; Table 7 gives the shares.

Dismissing firms were weaker beforehand, and the difference persists within size bands (Table 6). Controls for size, profitability, debt, distress and the prior year's return reduce the delisting difference to {{reg.exit5c.gone.forced}}, which remains statistically significant (Table 7). A board may dismiss the CEO of a firm it already expects to fail, so this difference does not identify an effect of the dismissal.

<!-- TABLE:6 -->

Against a matched firm of the same industry, size and profitability, the median dismissing firm trails by {{mbhar.forced.1y.median|abs}} after one year (p {{mbhar.forced.1y.median|p}}; Figure 3). At three and five years the median gaps are {{mbhar.forced.3y.median}} and {{mbhar.forced.5y.median}}, with p {{mbhar.forced.3y.median|p}} and {{mbhar.forced.5y.median|pv}} (Table IA.20). So after the first year, prices record no detectable further loss despite the higher rate of failure, which suggests the market had already priced that risk.

### 5.3 Reasons for dismissal

Fraud dismissals fall further than others. Shares fall {{car.criminal.mm_m1p1.mean|abs}} over three days after a dismissal over fraud or another legal violation, and {{car.conduct.mm_m1p1.mean|abs}} after one over a personal scandal (Table 5). The difference of {{cardiff.conduct_vs_criminal.mm_m1p1.diff_mean}} is statistically significant (p {{cardiff.conduct_vs_criminal.mm_m1p1.diff_mean|p}}), as the second supporting comparison predicts.

Against their competitors the contrast is similar: over the three days a scandal dismissal loses {{fv.scandal.pr.ann.ret.mean|abs}} and a fraud dismissal {{fv.fraud.pr.ann.ret.mean|abs}} (p {{fvdiff.scandal_vs_fraud.pr.ann.ret.diff|p}}; Table IA.6). Dismissals over sex or a relationship show no significant fall, {{car.sex_or_relationship.mm_m1p1.mean}} on average (Table 5). On every dated dismissal they fall {{rob.all_dates.sex_vs_fraud.mm_m1p1.diff_mean}} less than fraud dismissals (p {{rob.all_dates.sex_vs_fraud.mm_m1p1.diff_mean|p}}; Table IA.12).

The contrast reflects the fraud more than the scandal. Part of the fall after a fraud dismissal is the news of the fraud itself, often disclosed with the dismissal. Against other dismissals, scandal dismissals show no detectable difference: {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean}}, with a {{ci_pct}} interval from {{equiv.scandal_gap.mm_m1p1.ci95_low}} to {{equiv.scandal_gap.mm_m1p1.ci95_high}} (Internet Appendix E).

Among founders, fraud accounts for {{frmix.founder_fraud.share}} of dismissals and an event, a personal scandal or a boardroom coup, for {{frmix.founder_event.share}} (Table 8). Founders dismissed over fraud are outside the main sample. Against their closest competitor they lose {{fv.founder_fraud.pr.slideann.ret.mean|abs}} over the six-week window (Table IA.6).

<!-- TABLE:7 -->

<!-- TABLE:8 -->

### 5.4 H2: growth after a founder dismissal

Share returns may miss a slow loss of growth, so we test growth directly (Table 9). Growth is measured from as-reported annual statements over fiscal years {{fy_pre}} to {{fy_post5}} around the year of the dismissal. The outcomes are revenue growth, asset growth, market value growth, R&D to sales, capital spending to assets, return on assets and gross margin. The data do not hold employee numbers.

![Figure 3. Against the market the long run looks poor; against a matched firm it does not](/static/reports/founder-ceo/figures/fig2_long_run.png)

*Figure 3. Against the market the long run looks poor; against a matched firm it does not.* Notes. Median buy-and-hold return minus the market, month {{m_first}} to month {{months_5y}} after the announcement, in months of {{trading_days_per_month}} trading days from day {{d_post0}}, all dismissals. Diamonds mark the median return against a matched firm at {{m12}}, {{m36}} and {{m60}} months; Table IA.20 gives the numbers.

Each outcome is a difference-in-differences. We take the firm's change from before the dismissal (years {{fy_pre}} to {{fy_pre1}}) to after it (year {{fy_pre1}} to year {{fy_post3}} or {{fy_post5}}). We then subtract the same change at the closest competitor of Section 4.1, or at the median firm of the industry. A firm that was already slowing before the dismissal is therefore not counted as a new loss.

A firm that went bankrupt, or that a regulator delisted, stays in the sample with revenue growth of {{delist_bankrupt_signed}}, and results are reported with and without those firms. A firm that was taken over leaves at the takeover and is counted (Table IA.28). We test medians with the Wilcoxon signed-rank test.

Against the industry, H2 is supported for revenue. To the third year, the median founder firm's revenue growth slows by {{fg.founder.ind.rev.y3.median|abs}} a year more than its industry's median firm (p {{fg.founder.ind.rev.y3.median|p}}; Table 9). To the fifth year the slowdown is {{fg.founder.ind.rev.y5.median|abs}}, which could be chance (p {{fg.founder.ind.rev.y5.median|p}}).

Against the closest competitor it is not. The median founder firm's revenue growth changes by {{fg.founder.pr.rev.y3.median}} a year against its competitor (p {{fg.founder.pr.rev.y3.median|p}}). Founder firms grew fast before the dismissal, {{fg.founder.firm.rev.y3.pre.median}} a year, and their competitors, chosen on a similar prior year, slowed with them, from {{fg.founder.comp.rev.y3.pre.median}} to {{fg.founder.comp.rev.y3.post.median}} (Table IA.26).

Investment points the same way. Against the industry, the founder firm's capital spending to assets falls by {{fg.founder.ind.capex.y5.median|abs}} by the fifth year (p {{fg.founder.ind.capex.y5.median|p}}). Against the competitor the change is {{fg.founder.pr.capex.y5.median}}, which could be chance (Table 9). The founder tests have little power: only {{fg.founder.pr.rev.y3.count}} founder firms and their competitors both file in the third year.

<!-- TABLE:9 -->

Counting failed firms does not change the result against the competitor. By the fifth year, {{fgatt.founder.p5.bankrupt}} founder firms had gone bankrupt and {{fgatt.founder.p5.acquired}} had been taken over (Table IA.28). With failed firms at growth of {{delist_bankrupt_signed}}, the median founder change to the third year is {{fg.founder.pr.rev_att.y3.median}} (Table 9).

Growth after a scandal dismissal is not detectably weaker than after other dismissals. To the third year, the median firm's revenue growth changes by {{fg.scandal.pr.rev.y3.median}} a year against its competitor (p {{fg.scandal.pr.rev.y3.median|p}}; Table 10). Dismissals over sexual misconduct or a relationship are too few to average; Table IA.30 names each one.

<!-- TABLE:10 -->

### 5.5 When the market prices the news, and what is left for an investor

The question so far is what shareholders lose. An investor also asks when the price moves, and whether anything remains once the news is public. We time each dismissal by the moment its 8-K was accepted by EDGAR, in New York time. The first tradeable day is the announcement day for a release before the close and the next day for a release after it.

For dismissals in general, the market prices the news at the first trade. When the release comes before the open, the shares open {{tm.forced.bycls.before_open.gap.sp.mean|abs}} lower against the S&P 500; when it comes after the close, {{tm.forced.bycls.after_close.gap.sp.mean|abs}} lower (Table IA.33). The rest of that trading day adds {{tm.forced.bycls.before_open.day.sp.mean|abs}} and {{tm.forced.bycls.after_close.day.sp.mean|abs}} more; each of those moves could be chance (p {{tm.forced.bycls.before_open.day.sp.mean|p}}; p {{tm.forced.bycls.after_close.day.sp.mean|p}}).

Minute prices agree: from the first trade after the release to the close, the further move is {{tm.forced.minute.close.mean}} (N = {{tm.forced.minute.close.mean|n}}). A slow drift follows. The next day adds a fall of {{tm.forced.t1.sp.mean|abs}} (Holm p {{tm.forced.t1.sp.mean.holm}}). Six months on, the median dismissing firm trails the S&P 500 by {{tm.forced.p6m.sp.median|abs}} (p {{tm.forced.p6m.sp.median|p}}).

A portfolio holding each dismissing firm for six months after the first tradeable day earns a six-factor alpha of {{tm.forced.ctime.126.ff6}} (p {{tm.forced.ctime.126.ff6|p}}). That is {{tm.forced.ctime.126.ff6.total}} over six months, on about {{tm.forced.ctime.126.ff6.firms}} firms at a time, before the borrowing costs a short seller would pay.

For founders the reaction is front-loaded and uneven. Over the six weeks before the news, founder firms trail the S&P 500 by {{tm.founder.runup.sp.mean|abs}} (p {{tm.founder.runup.sp.mean|p}}). On the first tradeable day the mean fall is {{tm.founder.t0.sp.mean|abs}}, but the median firm moves {{tm.founder.t0.sp.median}}, so a few large falls carry the mean.

No founder trading rule built on the public release survives the correction for testing several rules. Shorting at the first open after the release and holding five days earns {{tm.founder.rule.known.open.5.mean}}, or {{tm.founder.rule.known.open.5.net50}} after a {{cost_bp}} basis point round trip (Holm p {{tm.founder.rule.known.open.5.mean.holm}}; N = {{tm.founder.rule.known.open.5.mean|n}}). The test could detect only an effect of about {{tm.founder.rule.known.open.5.mean.mde}}, so a gain of that size can be neither confirmed nor ruled out.

Founder firms do fall further on days {{d_p2}} to {{d_p5}} (Holm p {{tm.founder.p2_5.sp.mean.holm}}). Almost all of that fall, {{tm.founder.bycls.unknown.p2_5.sp.mean|abs}}, is in dismissals whose release time is unknown (N = {{tm.founder.bycls.unknown.p2_5.sp.mean|n}}). That pattern fits news reaching the market after the recorded date, not a drift an investor could trade.

Over longer holds a founder firm bought after the news ends level with the market. Held twelve months from the day after the announcement, {{invest_usd}} in the median founder firm becomes {{fwd.founder.d1.sp.m12.inv_firm.median}}, against {{fwd.founder.d1.sp.m12.inv_bench.median}} in the S&P 500. A portfolio of founder firms earns a six-factor alpha of {{fwdalpha.founder.d1.ew.ff6.12m}} a month, which could be chance (Holm p {{fwdalpha.founder.d1.ew.ff6.12m.holm}}).

The timing rests on the 8-K acceptance time, the latest moment the news could have been public; some news broke earlier. Of the {{tm.forced.n}} well-dated dismissals, {{tm.forced.cls.unknown}} cannot be timed this way, and minute prices exist only for firms the data vendor still quotes.

## 6. Evidence from the cases

The averages hide wide outcomes. Three years after the announcement, {{fa.outcome.all.gained}} founder firms had beaten their competitor by more than ten percentage points and {{fa.outcome.all.lost}} had trailed it by as much (Table IA.9). Within five years {{fa.outcome.all.taken_over}} had been acquired and {{fa.outcome.all.bankrupt}} had entered bankruptcy.

A few firms at the extremes drive the founder long-run means, which is why the text reads medians; Internet Appendix C names them.

The case check also records how each dismissal happened. On the sources read, {{fa.push.pushed}} of the {{fa.n_kept}} founders were clearly dismissed, by a board vote, a demand to resign or a public disagreement. For the remaining {{fa.push.unclear}} the sources report a resignation without stated pressure.

The founders' later careers vary as widely. Some returned as CEO, some went after the firm, others started new companies; Internet Appendix C names the cases (Table IA.10).

## 7. Robustness

The loss against a single competitor depends on how that competitor is chosen (Table IA.8). With the broad industry match of the earlier design, founder firms trailed their competitor by {{h1v.d34.fv.founder.pr.slideann.ret.mean|abs}} over the six-week window (p {{h1v.d34.fv.founder.pr.slideann.ret.mean|p}}). With the corrected codes the loss was {{h1v.d37old.fv.founder.pr.slideann.ret.mean|abs}} (p {{h1v.d37old.fv.founder.pr.slideann.ret.mean|p}}).

With the narrower match the figures are {{h1v.unc.fv.founder.pr.slideann.ret.mean|abs}} with the original codes and {{h1v.d37.fv.founder.pr.slideann.ret.mean|abs}} with the founder corrections, and both could be chance (Table IA.8). The single closest competitor is therefore the one benchmark under which the founder firm's loss is not detectable.

Checks were added after review (Table IA.31). On founders the case check found clearly forced out, the loss against the closest competitor is {{fvrob.pushed.founder.pr.slideann.ret.mean|abs}} (p {{fvrob.pushed.founder.pr.slideann.ret.mean|p}}). On pairs within the same 4-digit SIC code it is {{fvrob.sic4.founder.pr.slideann.ret.mean|abs}} (p {{fvrob.sic4.founder.pr.slideann.ret.mean|p}}).

The number of competitors averaged does not drive the result. With the two closest competitors the loss is {{fv.founder.pr2.slideann.ret.mean|abs}} (p {{fv.founder.pr2.slideann.ret.mean|p}}). With four it is {{fv.founder.pr4.slideann.ret.mean|abs}} (p {{fv.founder.pr4.slideann.ret.mean|p}}), and with five {{fv.founder.pr5.slideann.ret.mean|abs}} (p {{fv.founder.pr5.slideann.ret.mean|p}}). Only against the single competitor, which carries one firm's own news, is the loss too small to detect (Table IA.31).

The average of the three closest competitors matches the year before the dismissal more closely than the single competitor does. On the firms it covers, founder firms fell {{fvbal3.founder.prior12.firm.mean|abs}} over the year before and the mean of their three closest competitors {{fvbal3.founder.prior12.comp.mean|abs}}. That gap could be chance (p {{fvbal3.founder.prior12.gap|p}}; Table IA.4). The {{fv.founder.pr3.slideann.ret.mean|abs}} loss against them therefore does not mainly carry a slide that the competitors escaped.

A rule-based screen for planned successions, run on every dismissal, finds {{screen.validation.flag.true_positives}} of the {{screen.validation.n_planned}} planned successions among the checked cases, a sensitivity of {{screen.validation.flag.sensitivity}}, below the {{screen_sensitivity_req}} we required. We therefore report it only as a robustness check; with the screen the founder firm trails its closest competitor by {{h1v.scr.fv.founder.pr.slideann.ret.mean|abs}} (Table IA.8).

Winsorising the returns at {{winsor_low}} and {{winsor_high}} changes the six-week means little (Table IA.5). The growth results hold in means: to the third year, the founder firm's revenue growth changes by {{fg.founder.pr.rev.y3.mean}} a year against its competitor on average (Table IA.29).

## 8. Discussion and limitations

The founder firm's loss is mostly a loss before the news. Against the market, the industry and the three closest competitors, founder firms fall far behind over the six-week window, and most of it accrues before the announcement. That fits evidence that boards act after a decline [@jenter2015], and it leaves the announcement itself small and imprecisely measured.

The two founder views make different predictions about the announcement. The irreplaceable-founder view predicts a large fall when the news breaks; against the three closest competitors we find a fall of {{fv.founder.pr3.ann.ret.mean|abs}} that could be chance. Its {{ci_pct}} interval runs from {{fv.founder.pr3.ann.ret.mean.ci_low}} to {{fv.founder.pr3.ann.ret.mean.ci_high}}, so the test can rule out only large effects either way.

Because most of the loss accrues before the news, the announcement return understates what holders of a founder firm lost against normal firms over the whole episode. A study that reads only the three days around the announcement would find a small fall that could be chance. Over the six-week window the same firms trail their industry by {{fv.founder.ind.slideann.ret.mean|abs}} and the market index by {{fv.founder.sp.slideann.ret.mean|abs}} (Table 3).

The evidence describes boards; it does not advise them. A board that removes its founder does so after a decline that comparable firms did not fully share, and the firm's revenue growth then slows against its industry (Table 9). Whether keeping the founder would have done better cannot be read from these comparisons.

Five years on, founder firms trail their industry and the market index by wide margins but not their matched firms. Fast-growing founder firms slowed after the dismissal, and so did competitors with a similar record. The data cannot separate the founder's departure from the slowing of firms that had grown fast.

The study has several limitations. The sample covers S&P {{index_size}} firms, where founders are fewer and hold less control than in smaller firms. We do not observe founders' ownership or voting control. The three-competitor benchmark covers fewer founder firms than the single competitor, although its competitors fell nearly as far over the year before (Table IA.4). Some competitors matched at the broader industry levels are not close rivals (Table IA.23).

The coding has limits too. The case checks were made by AI research assistants, and no second human coder has checked them or the first review. The case files, with every source quoted, are in the replication package so that each code can be audited. Founder dismissals are few, so the founder tests detect only large effects. For {{fa.push.unclear}} of the {{fa.n_kept}} founder exits the sources report no stated board pressure. The growth tests need annual statements for the firm and its competitor years later, which only {{fg.founder.pr.rev.y3.count}} founder pairs have in the third year.

The analysis does not identify what would have happened had the board retained its founder. We record the successor only for founder dismissals (Table IA.9); @cziraki2022 show that most new CEOs are insiders or people the board already knows.

## 9. Conclusion

Founder dismissals at large US firms come after the firm has fallen behind normal firms, and the announcement adds little that the data can tell from chance. Against the market, the industry and the closest competitors the gap is wide and mostly in place before the news. But against a single competitor matched on the prior year, it could be chance (Table 3). What the share price records is the decline that precedes the board's action, not a separate price for the founder's departure.

For dismissals in general the larger fact is failure: dismissing firms go bankrupt far more often than firms whose CEO retires (Table 7). At the announcement, the reason matters when it is fraud; a personal scandal looks like any other dismissal (Table 5). One interpretation is that investors read fraud as news about the firm and a scandal as news about one person; the data do not identify beliefs.

For an investor, much of the move in dismissals in general comes at the first trade, and a slow drift follows before borrowing costs. For founder firms no trading rule based on the public news survives the correction for testing several rules, though the test can detect only large effects (Section 5.5). The census rests on AI-assisted case checks that no second human coder has yet checked; the case files make each code auditable.

## Internet Appendix

### A. Sample construction and the case checks

The case checks are the core of the sample. AI research assistants (Anthropic's Claude), working in five batches under rules fixed in advance, went through every one of the {{fa.n_checked}} founder departures the database codes as forced. No second human coder has yet checked their work. For each case they recorded what happened, whether the departure was forced and when the news first came out. They also recorded why the board acted, who followed and what became of the founder. Each case cites the filings and press read, and the case files are in the replication package.

The check found three kinds of error, all corrected before any corrected result was computed (Table IA.1). Of the departures, {{fa.n_planned_dropped}} were planned successions, not dismissals: the founder stayed on as chairman and a chosen successor took over on a timetable (Table IA.2). Enron in {{case_enron_year}} is one; Kenneth Lay handed the post to Jeffrey Skilling, stayed chairman and returned as CEO after Skilling resigned. These cases leave every analysis and join no comparison group.

The database also codes some forced resignations as retirements. We read the evidence on all {{fa.n_retirements_scanned}} founder departures coded as retirements and checked every one with any sign of pressure. Three were forced. At J.D. Edwards in {{case_jde_year}} the board replaced Ed McVaney with an outsider. At Mednax in {{case_mednax_year}} Roger Medel stepped down under an agreement with the activist Starboard Value. At Cypress Semiconductor in {{case_cypress_year}} the board pressed T.J. Rodgers to make way for new management. They join the sample, and Table IA.32 reports the founder results before and after adding them. Another {{fa.n_forced_resign_unclear}} show pressure but no source says the board forced the exit, and they stay out.

Some dates were wrong. Where day 0 was the day the founder left office, not the day the news broke, the date moved to the first public report the check found. Where no report could be dated, the old date stayed and the case is flagged. A few reasons were recoded: two dismissals to fraud, one from fraud to personal conduct, and one from a boardroom coup to another reason.

Hired-CEO dismissals enter the results on all dismissals, so we drew {{fa.audit.hired.n}} of them at random and checked them with the same rules (Table IA.1). The audit found {{fa.audit.hired.planned}} planned successions and {{fa.audit.hired.redate}} wrong dates among them. Among the {{fa.audit.founder.n}} founders first tested, {{fa.audit.founder.planned}} were planned successions. The audit's fixes are applied as the founder fixes were.

A rule can screen every dismissal for planned successions, founder or hired. It flags a dismissal announced {{screen_days}} days or more before the CEO left office. It also flags one whose notes say the CEO stayed chairman and name the chief operating officer or the president as successor. On the {{screen.validation.n_checked}} checked departures it finds {{screen.validation.flag.true_positives}} of the {{screen.validation.n_planned}} planned successions and flags {{screen.validation.flag.false_positives}} real dismissals.

With a sensitivity of {{screen.validation.flag.sensitivity}}, below the {{screen_sensitivity_req}} we required, the screen is a robustness check, not the main sample (Table IA.8).

<!-- TABLE:IA.1 -->

<!-- TABLE:IA.2 -->

Table IA.3 traces the dismissals from the CEO dismissal database to the samples, and Figure IA.1 counts them by year. Panel B of Table IA.3 shows how often the first review changed the model's codes.

The language model had coded {{b.model_founder_codes}} dismissals as founder removals; the first review confirmed {{b.founders_confirmed}}, rejected {{b.founders_rejected}} and added {{b.founders_added}}. About half of the model's other personal-conduct codes turned out to be pay disputes, unexplained personal reasons or criminal charges.

The first review kept {{code.founder.share_kept}} of founder codes, {{code.fraud.share_kept}} of fraud and legal-violation codes and {{code.personal.share_kept}} of other personal-conduct codes.

![Figure IA.1. Dismissals per year](/static/reports/founder-ceo/figures/fig5_per_year.png)

*Figure IA.1. Dismissals per year.* Notes. Every dismissal in the database by year, {{sample_start}} to {{sample_end}}, by the database's dismissal type, whether or not the firm has share prices, less dismissals over fraud or other legal violation. The bars therefore total more than the paper's {{a.n_lr_forced}} dismissals with prices. The number above each bar counts the founders confirmed by the first review; the founder count in Table IA.3 also includes founders dismissed over fraud. The last year covers part of {{sample_end}}.

<!-- TABLE:IA.3 -->

### B. Competitors, balance and benchmarks

For founders, {{fa.pairs.level.sic4}} competitors share the firm's 4-digit code. A broader match within the {{ff_industries}} Fama-French industries was the competitor of the earlier design and is kept as a robustness row (Table IA.8). The case check found many of its pairs were not real competitors: a broker beside an energy trader, a railcar maker beside a boat builder.

Table IA.4 shows how close the closest competitor is before the dismissal. Founder firms fell {{fvbal.founder.prior12.firm.mean|abs}} over the year before and their closest competitors {{fvbal.founder.prior12.comp.mean|abs}}, while the S&P 500 rose {{fvprior.founder.sp.mean}}. For all dismissals the gap to the competitor is {{fvbal.forced.prior12.gap|abs}} on average (p {{fvbal.forced.prior12.gap|p}}). Retirement firms are matched to firms that rose as they did.

The three closest competitors are closer on the prior year. Founder firms fell {{fvbal3.founder.prior12.firm.mean|abs}} and the mean of their three closest competitors {{fvbal3.founder.prior12.comp.mean|abs}}; the median gap is {{fvbal3.founder.prior12.gap_median}} (p {{fvbal3.founder.prior12.gap_median|p}}). The founder firms are somewhat larger than the average of the three, {{fvbal3.founder.mcap.firm.median_bn}} against {{fvbal3.founder.mcap.comp.median_bn}} billion dollars in median market value, and their profitability is similar (Table IA.4).

Size is matched within half the firm's market value. Profitability is not matched: the median founder firm earns a return on assets of {{fvbal.founder.roa.firm.median}} in the year before, and its competitor {{fvbal.founder.roa.comp.median}}. The matched firm of Section 4 makes the opposite trade, and Table 3 reports the founder firm against both.

<!-- TABLE:IA.4 -->

Table IA.5 gives the mean of Table 3 for every benchmark and window, with its {{ci_pct}} interval and the Holm adjustment across the five benchmarks, which was added after review. Over the six-week window the losses against the market index, the industry, the three closest competitors and the profitability-matched firm remain statistically significant after the adjustment. The loss against the single closest competitor does not (p {{fv.founder.pr.slideann.ret.mean.holm5_p}}).

<!-- TABLE:IA.5 -->

Table IA.6 gives the return gap against the closest competitor for every group of departures, with fraud dismissals shown apart. Retirement firms keep pace with their competitors through the announcement. Dismissals in a boardroom coup lose {{fv.coup.pr.slideann.ret.mean|abs}} against competitors over those six weeks, and dismissals over a personal scandal {{fv.scandal.pr.slideann.ret.mean|abs}}. Fraud dismissals go on losing after the news: their median return gap is {{fv.fraud.pr.m12.ret.median}} at {{months_1y}} months.

<!-- TABLE:IA.6 -->

Table IA.7 gives the dollar change of the founder firm against every benchmark: medians, means and totals. Totals rest on a few very large firms; against the market index the founder total over the six-week window is {{fv.founder.sp.slideann.usd.total_bn}}.

<!-- TABLE:IA.7 -->

Table IA.8 gives the founder firm against its closest competitor under each version of the codes and the competitor, and Table IA.31 three checks added after review. With the broad industry match of the earlier design, founder firms trailed their competitor by {{h1v.d34.fv.founder.pr.slideann.ret.mean|abs}} over the six-week window. With the corrected codes the loss was {{h1v.d37old.fv.founder.pr.slideann.ret.mean|abs}}. With the narrower match the figures are {{h1v.unc.fv.founder.pr.slideann.ret.mean|abs}} and {{h1v.d37.fv.founder.pr.slideann.ret.mean|abs}}.

<!-- TABLE:IA.8 -->

### C. The founder cases

Table IA.9 lists every founder dismissal kept, with the reason, how it happened, who followed, the three-year return against the competitor and what became of the founder. Table IA.10 counts the founders' fates and names the cases in the smaller groups.

<!-- TABLE:IA.9 -->

<!-- TABLE:IA.10 -->

The extremes are large. Jazz Pharmaceuticals and Chipotle Mexican Grill beat their competitors by the widest margins in the three years after their founders left. Calpine filed for bankruptcy weeks after the board removed Peter Cartwright, and Chesapeake Energy trailed its competitor after Aubrey McClendon's exit (Tables IA.9 and IA.17). A few such firms drive the founder long-run means, which is why the text reads medians.

Personal scandals divide the same way. Wynn Resorts' shares rose {{frcase.8761.car_m1p1}} when Steve Wynn resigned after published allegations of sexual misconduct. World Wrestling Entertainment's shares fell {{frcase.8370.car_m1p1|abs}} when Vince McMahon stepped back during the board's investigation, news that came with the first reports of the payments (Table IA.16). Papa John's shares fell {{frcase.6523.car_m1p1|abs}} when John Schnatter stepped down (Internet Appendix D). Three cases test nothing; Table IA.9 lists every founder dismissal.

Some founders do not stay gone. Jerry Moyes at Swift Transportation, Robert Rucker at Tile Shop and Michael Reger at Northern Oil & Gas each returned as CEO of the same firm within five years. Moyes did so by taking Swift private. In all, {{fa.fate.went_after_the_firm}} founders, Moyes among them, went after the firm through a proxy fight, a bid or a buyout (Table IA.10).

Others moved on: {{fa.fate.started_or_led_a_new_firm}} started or led a new company, among them David Neeleman, who founded Azul after JetBlue, and McClendon, who founded American Energy Partners. Of the founders, {{fa.fate.stayed_on_the_board}} kept a board seat or the chair for some time after the exit, and legal action named {{fa.fate.legal_action_naming_the_founder}}, most of them dismissed over fraud (Table IA.10).

### D. Founder dismissals by why the board acted

Table 8 sorts founder dismissals by why the board acted. Fraud or other legal violation accounts for {{frmix.founder_fraud.share}} of them and an event, a personal scandal or a boardroom coup, for {{frmix.founder_event.share}}. Most founders, {{fr.founder_other.n_all}} of the {{fr.founder_all.n_all}}, were dismissed over performance or another reason.

Founders dismissed over fraud are outside the main sample. Over the three announcement days their shares fall {{fr.founder_fraud.mm_m1p1.mean|abs}} (Table 8), a figure that carries the news of the fraud as well as the news that the founder is gone.

It also understates one case. Trading in HealthSouth's shares was halted around the board's decision to put Richard Scrushy on leave in {{case_healthsouth_year}}. The Securities and Exchange Commission had charged the firm with inflating its earnings. The three days therefore record almost no fall, and the shares lost most of their value when trading resumed.

Against their closest competitor, founders dismissed over fraud lose {{fv.founder_fraud.pr.slideann.ret.mean|abs}} over the six-week window, a median {{fv.founder_fraud.pr.slideann.usd.median|abs}} per firm (Table IA.6). Of the {{fr.founder_fraud.n5}} followed for five years, {{fr.founder_fraud.delisted_5y}} were delisted and {{fr.founder_fraud.bankruptcy_5y.count}} went bankrupt, WorldCom among them.

The {{fr.founder_event.n_all}} founders dismissed over an event are {{fr.founder_scandal.n_all}} personal scandals and {{fr.founder_coup.n_all}} boardroom coups. Papa John's shares fell {{frcase.6523.car_m1p1|abs}} when John Schnatter stepped down after criticism of his public remarks. Wynn Resorts' shares rose {{frcase.8761.car_m1p1}} when Steve Wynn resigned after published allegations of sexual misconduct. World Wrestling Entertainment's (WWE) fell {{frcase.8370.car_m1p1|abs}} when Vince McMahon stepped back during the board's investigation.

The fourth scandal case came from the case check, which moved it from fraud to personal conduct. AdaptHealth's shares fell {{frcase.10360.car_m1p1|abs}} when the board put Luke McGee on unpaid leave in {{case_adapthealth_year}} (Table IA.9).

After the coups against founders, the shares fell {{frcase.7374.car_m1p1|abs}} at PRG-Schultz. They rose {{frcase.7230.car_m1p1}} at RadiSys and {{frcase.9699.car_m1p1}} at Cara Therapeutics, and barely moved at Inter-Tel ({{frcase.1862.car_m1p1}}) and LCA-Vision ({{frcase.7327.car_m1p1}}). The case check moved AXT's case out of the coups: the sources point to an internal compliance review.

There are fewer event dismissals than the {{min_reason_cases}} we set, before computing any group, as the least that supports an average. We report no average for them, and their returns fall on both sides of zero.

The founders who left over a personal scandal went different ways against their competitors. Over the six weeks through the announcement Papa John's lost {{fvcase.6523.slideann.usd|abs}} and AdaptHealth {{fvcase.10360.slideann.usd|abs}}. Wynn Resorts gained {{fvcase.8761.slideann.usd}}.

Leaving fraud aside, {{exit.forced_founder.delisted_5y}} of founder firms are delisted within five years and {{exit.forced_founder.bankruptcy_5y}} go bankrupt (Table 8). Only {{exit.forced_founder.n5}} founder dismissals can be followed for five years. Of the {{fr.founder_event.n5}} event dismissals followed that long, {{fr.founder_event.delisted_5y.count}} firm was delisted, Inter-Tel in a takeover, and none went bankrupt. Papa John's and Wynn Resorts were still listed five years on.

### E. The announcement

The fall does not come from how dismissals are defined (Table 5, Panel C). Where the evidence-based coding agrees the exit was forced, the fall is {{strict.llm_yes.mm_m1p1.mean|abs}} (p {{strict.llm_yes.mm_m1p1.mean|p}}); where it is unclear, {{strict.llm_unclear.mm_m1p1.mean|abs}}; where it reads the exit as not forced, {{strict.llm_no.mm_m1p1.mean|abs}}. Reweighting the well-dated dismissals to resemble every dismissal gives {{dsel.ipw.mm_m1p1.mean|abs}}, and the five-factor model {{car.forced.ff5_m1p1.mean|abs}}.

Dating matters only because a late day 0 puts the news outside the three-day window. Over every dismissal, whatever its date source, the three-day fall is only {{rob.all_dates.forced.mm_m1p1.mean|abs}}. Widen the window to trading days {{d_wide0}} to {{d_wide1}} and every dismissal falls {{dsel.window.all.mm_m5p5.mean|abs}} (p {{dsel.window.all.mm_m5p5.mean|p}}), close to the well-dated dismissals' {{dsel.window.dated.mm_m5p5.mean|abs}} (Table IA.12).

After a dismissal over a personal scandal the shares fall {{car.conduct.mm_m1p1.mean|abs}} over the three days, against {{car.performance.mm_m1p1.mean|abs}} after other dismissals (Table 5). On its own, the fall across {{car.conduct.mm_m1p1.mean|n}} scandal dismissals is {{car.conduct.mm_m1p1.mean|sig}} (p {{car.conduct.mm_m1p1.mean|p}}). With size, the prior year's return and the year held constant, the gap between the two is {{regc.car_m1p1.conduct}} (Table IA.12).

Too few scandal dismissals are dated to tell the two falls apart with confidence. The raw gap of {{equiv.scandal_gap.mm_m1p1.diff}} is {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean|sig}} (p {{cardiff.conduct_vs_performance.mm_m1p1.diff_mean|p}}). Its {{ci_pct}} interval runs from {{equiv.scandal_gap.mm_m1p1.ci95_low}} to {{equiv.scandal_gap.mm_m1p1.ci95_high}}, and the test would detect only gaps of about {{equiv.scandal_gap.mm_m1p1.mde}}.

After a dismissal over fraud or other legal violation the shares fall {{car.criminal.mm_m1p1.mean|abs}}, {{cardiff.conduct_vs_criminal.mm_m1p1.diff_mean}} more than after a personal scandal (p {{cardiff.conduct_vs_criminal.mm_m1p1.diff_mean|p}}, n = {{cardiff.conduct_vs_criminal.mm_m1p1.diff_mean|n}}). That fall measures more than the dismissal, because a fraud dismissal is often announced with the fraud itself. Its three-day fall carries the news that the accounts or the business were wrong, as well as the news that the CEO is gone.

A scandal dismissal may be followed by little because the market priced the scandal when it first broke. To check, we searched the New York Times Archive for personal misconduct by sitting CEOs of the sample's firms and checked each report against the article (Table IA.16). The search finds {{scandal.n_events}} scandals. In {{scandal.n_departed}} the CEO left within a year; in {{scandal.n_kept}} the board kept them, among them Jeff Bezos at Amazon and Bobby Kotick at Activision Blizzard.

Over the three trading days around the first press report, the shares of the {{scandal.all.first_report.car_m1p1.mean|n}} scandal firms with prices fell {{scandal.all.first_report.car_m1p1.mean|abs}} against the market. They fell {{scandal.departed.first_report.car_m1p1.mean|abs}} where the CEO later left and {{scandal.kept.first_report.car_m1p1.mean|abs}} where the board kept them, too few cases to tell apart. The search finds only {{scandal.n_known_firings_found}} of the database's dismissals over a personal scandal, mostly at the largest firms. These cases describe prominent scandals and are too few and too unusual for a test.

Against competitors the contrast is the same. Over the three days a scandal dismissal loses {{fv.scandal.pr.ann.ret.mean|abs}} and a fraud dismissal {{fv.fraud.pr.ann.ret.mean|abs}}. The gap of {{fvdiff.scandal_vs_fraud.pr.ann.ret.diff}} is statistically significant (p {{fvdiff.scandal_vs_fraud.pr.ann.ret.diff|p}}; Table IA.6). Over the six weeks through the announcement a fraud dismissal loses {{fv.fraud.pr.slideann.ret.mean|abs}}, or {{fv.fraud.pr.slideann.usd.median|abs}} at the median firm.

Table IA.11 gives the founder firm's abnormal return over three announcement windows. Over days {{d_ann0}} to {{d_ann1}} it is {{car.forced_founder.mm_m1p1.mean}} (p {{car.forced_founder.mm_m1p1.mean|p}}), against {{car.forced.mm_m1p1.mean}} for every dismissal.

<!-- TABLE:IA.11 -->

Table IA.12 changes one thing at a time against the main tables. With the five-factor model plus momentum, the personal-scandal gap is {{rob.conduct_vs_performance_ff5.m1p1.diff_mean}}. Returns minus the market, with no estimated model, give {{rob.forced.ma_m1p1.mean}} over the three days. Using every dismissal, whatever its date source, gives {{rob.all_dates.forced.mm_m1p1.mean}}.

Table 5, Panel C, already splits the dismissals by how the evidence-based coding reads them. Excluding {{crisis_y0}} and {{crisis_y1}} gives {{rob.forced_excl_crisis.mm_m1p1.mean}}, and dropping dismissals coded as leaving for a new job gives {{rob.forced_excl_newopp.mm_m1p1.mean}}.

The long-run results do not depend on how delisting returns are set. With every delisting return at zero, the median three-year return against the market is {{rob.bhar_dl0.forced.3y.median}}, and setting every delisting that is not a takeover to minus {{delist_worst}} gives {{rob.bhar_dlworst.forced.3y.median}}. When no firm meets the size band the nearest firm in size is the match ({{h.relaxed_matches}} matches); using only matches within the band, the median three-year matched return is {{rob.mbhar_strict_matches.3y.median}}.

For departures from {{pre_start}} to {{pre_end}}, before daily prices for delisted firms exist, we use the five-year return graphs that firms print in their proxy statements. Of these departures, {{pre.events_with_tsr}} have a usable graph, including {{pre.n_forced}} dismissals. The median three-year return against the firm's own reported index is {{pre.forced.abn_tsr_3y.median}} after dismissals and {{pre.retired.abn_tsr_3y.median}} after retirements. Only firms still filing three years later enter this check.

<!-- TABLE:IA.12 -->

Table IA.13 compares the well-dated dismissals with the others. The well-dated firms are larger, with a median market value of {{dsel.mcap_m1.dated}} billion dollars against {{dsel.mcap_m1.undated}}, and fell less over the prior year. They are also more recent, with a median year of {{dsel.year.dated}} against {{dsel.year.undated}}, and fewer of them are delisted within five years. Reweighting them to resemble every dismissal leaves the announcement return almost unchanged (Table 5).

<!-- TABLE:IA.13 -->

Table IA.14 gives the return before, at and after the announcement for each group of departures.

<!-- TABLE:IA.14 -->

Table IA.15 and Figure IA.2 split the dismissals by the reason coded for them. After a Holm correction for testing every reason, two falls remain statistically significant (Table IA.15). Where a push was described as a retirement or ill health the fall is {{car.reason.retirement_or_health.mm_m1p1.mean|abs}} (Holm p = {{car.reason.retirement_or_health.mm_m1p1.holm_p}}). Where the CEO was coded as leaving for a new job it is {{car.reason.new_opportunity.mm_m1p1.mean|abs}} (Holm p = {{car.reason.new_opportunity.mm_m1p1.holm_p}}). After other personal conduct it is {{car.reason.other_personal_conduct.mm_m1p1.mean|abs}} (Holm p = {{car.reason.other_personal_conduct.mm_m1p1.holm_p}}), short of significance; performance and the other reasons do not survive the correction either.

<!-- TABLE:IA.15 -->

![Figure IA.2. The announcement return by the reason the board acted](/static/reports/founder-ceo/figures/fig4_reasons.png)

*Figure IA.2. The announcement return by the reason the board acted.* Notes. Mean abnormal return over trading days {{d_ann0}} to {{d_ann1}} by the coded reason, well-dated dismissals, with {{ci_level}}% intervals; reasons with at least {{min_reason_cases}} dismissals. Table IA.15 gives the numbers.

Table IA.16 lists each scandal the New York Times search found, grouped by whether the board kept its CEO, with the return around the first report. The boards that kept their CEO include News Corp, Goldman Sachs, Amazon and Activision Blizzard; those whose CEO left include Boeing, Hewlett-Packard, Intel and McDonald's. Sexual relationships and harassment allegations appear on both sides. Table IA.17 lists the largest founders dismissed, with the return at the announcement and what became of the firm.

<!-- TABLE:IA.16 -->

<!-- TABLE:IA.17 -->

### F. Survival, returns, profits and the board

After a retirement, {{exit.retired.delisted_5y}} of firms are delisted: {{exit.retired.acquired_5y}} are taken over and {{exit.retired.bankruptcy_5y}} go bankrupt. So most of the gap between the two groups is bankruptcy. Takeovers are the larger share in both groups, which fits the view that board removal and takeover are two routes to a change of control [@morck1989].

Small firms fail more often, and dismissing firms are smaller, so Table 6 compares firms of similar size. In the smallest band, under {{size_small_usd}} in market value, {{exit.forced.size_small.bankruptcy_5y}} of dismissing firms go bankrupt within five years, against {{exit.retired.size_small.bankruptcy_5y}} of retirement firms. Above {{size_mega_usd}} the bankrupt shares are {{exit.forced.size_mega.bankruptcy_5y}} and {{exit.retired.size_mega.bankruptcy_5y}}. Dismissing firms are delisted more often in every band (Table 6).

Some firms were already failing when the CEO left: for {{exit.forced.early_bankruptcy_n}} of them a bankruptcy was recorded within {{early_bankrupt_days}} days of the announcement, as at Sears and Dana. Setting those aside, {{exit.forced.after.delisted_5y}} of dismissing firms are delisted within five years and {{exit.forced.after.bankruptcy_5y}} go bankrupt.

Much of the gap goes with weakness that was there before the dismissal. With controls for size and profitability, dismissing firms are {{reg.exit5.gone.forced}} more likely than retirement firms to be delisted within five years (Table 7). Adding the prior year's return, debt, book-to-market, a distress score and a loss flag lowers the gap to {{reg.exit5c.gone.forced}} (p {{reg.exit5c.gone.forced|p}}). Of that gap, {{reg.exit5c.bankrupt.forced}} is bankruptcy. Debt is the strongest predictor among these controls (Table IA.18). The dismissal need not cause what remains: a board may fire the CEO of a firm it already expects to struggle.

The remaining gap survives three further checks (Table IA.18). A survival model counts every month a firm is followed, including firms followed for less than five years. With every control, the model's hazard ratio is {{cox.gone.full.forced_hr}} (p {{cox.gone.full.forced_hr|p}}): the monthly rate at which dismissing firms leave the market, divided by the rate for retirement firms. Where the evidence-based coding agrees the exit was forced, the controlled gap is {{strict.reg.gone.yes}} (p {{strict.reg.gone.yes|p}}). Against their own matched firms it is {{exitdiff.forced_vs_ctrl.delisted_5y}}.

Against its matched firm, the median dismissal firm's buy-and-hold return is {{mbhar.forced.1y.median}} after one year (p {{mbhar.forced.1y.median|p}}). After three and five years it is {{mbhar.forced.3y.median}} and {{mbhar.forced.5y.median}}, neither significant (Table IA.20).

The mean returns against the matched firm at three and five years are {{mbhar.forced.3y.mean}} and {{mbhar.forced.5y.mean}}. Neither is statistically significant with the skewness-adjusted t test (Table IA.20). A few large winners pull the mean above the median, so the median and a risk-adjusted portfolio return are the measures we read.

A risk-adjusted portfolio finds no extra loss over the first three years (Table IA.19). An alpha is the monthly return that market, size, value, profitability, investment and momentum risks do not explain. A portfolio holding every firm in its first three years after a dismissal earns an alpha of {{alpha.forced.ew.36m}} a month. Its {{ci_pct}} interval runs from {{alpha.forced.ew.36m.ci_low}} to {{alpha.forced.ew.36m.ci_high}} a month. Against a portfolio of retirement firms the difference is {{alphadiff.forced_vs_retired.ew.36m}} a month (p {{alphadiff.forced_vs_retired.ew.36m|p}}).

The personal-scandal portfolio earns {{alpha.conduct.ew.36m}} a month, but it holds about a dozen firms at a time, so one or two firms can drive it. We do not read it as evidence that scandal firms do better.

Profits fall in the year of the dismissal and then recover. In the fiscal year of the departure, return on assets falls {{roa.forced.abn_d_0.median|abs}} percentage points against the matched firm (p {{roa.forced.abn_d_0.median|p}}; Table IA.21 and Figure IA.3). By fiscal year {{fy_plus2}} the median gap is {{roa.forced.abn_d_2.median}} percentage points, on the firms still filing.

A dismissal may come with a wider change in who governs the firm, which would appear on the board. The proxy statement, the annual filing that lists the directors standing for election, records the board before and after a dismissal. Of the directors named in the last proxy statement before a dismissal, {{board.forced.director_turnover.mean}} are missing from the first one filed about two years later. After a retirement the share is {{board.retired.director_turnover.mean}} (Table IA.22). The measure counts every director who disappears, matched on surname and first initial; a proxy does not say whether a director resigned, was not nominated again or lost a vote.

Two years later a dismissed founder is still a director at {{board.forced_founder.founder_stays.mean}} of the {{board.forced_founder.founder_stays.mean|n}} firms with both proxy statements, against {{board.retired.ceo_stays_director.mean}} for a retired CEO (Table IA.22). These results cover the {{g.events_with_board_data}} departures whose firms filed a proxy statement both before and about two years after.

<!-- TABLE:IA.18 -->

<!-- TABLE:IA.19 -->

<!-- TABLE:IA.20 -->

<!-- TABLE:IA.21 -->

![Figure IA.3. Profits and the board after the dismissal](/static/reports/founder-ceo/figures/fig6_roa_board.png)

*Figure IA.3. Profits and the board after the dismissal.* Notes. (a) Median change in return on assets from fiscal year {{fy_minus1_ascii}}, minus the same change at the matched firm, in percentage points, fiscal years {{fy_zero}} to {{fy_post3}}. (b) About two years after the departure, three shares: pre-departure directors not named in the later proxy, firms with a separate chair and CEO, and firms where the departing CEO is still a director. Dismissals are red and retirements grey; the diamond marks dismissed founders.

<!-- TABLE:IA.22 -->

### G. Founder firms and their competitors

Table IA.23 lists each founder dismissal with its closest competitor, the industry of each and the level at which they match. Of the {{fa.n_kept}} founder dismissals, {{fa.pairs.level.sic4}} are matched within the same 4-digit industry and {{fa.pairs.level.none}} have no competitor.

<!-- TABLE:IA.23 -->

### H. Growth after the dismissal

Tables IA.24 and IA.25 report every outcome and horizon behind Tables 9 and 10. For founders, Table IA.24 sets each against the competitor and against the industry median.

<!-- TABLE:IA.24 -->

Against the industry, founder firms slow on revenue, capital spending and assets. Their market value recovers from its earlier fall: to the third year it grows {{fg.founder.ind.mcap.y3.median}} a year faster than the industry's median firm (Table IA.24). Against the closest competitor no outcome moves detectably. The difference between the two benchmarks is the one Section 5.4 describes: the competitor had a similar record before the dismissal, and the industry did not.

Table IA.25 gives the same tests for dismissals over a personal scandal against other dismissals, every outcome against the competitor and the industry median. After a scandal dismissal, the median firm's revenue growth to the third year changes by {{fg.scandal.pr.rev.y3.median}} a year against its competitor and {{fg.scandal.ind.rev.y3.median}} against its industry. After other dismissals the two changes are {{fg.nonscandal.pr.rev.y3.median}} and {{fg.nonscandal.ind.rev.y3.median}}.

Against the competitor the gap in medians between the two groups is {{fgdiff.scandal_vs_nonscandal.pr.rev.y3.diff_median}}, which could be chance (p {{fgdiff.scandal_vs_nonscandal.pr.rev.y3.diff_median|p}}). Against the industry it is {{fgdiff.scandal_vs_nonscandal.ind.rev.y3.diff_median}}, which could also be chance (p {{fgdiff.scandal_vs_nonscandal.ind.rev.y3.diff_median|p}}). Scandal firms, like founder firms, slow against their industry more than against a competitor with a similar recent record.

<!-- TABLE:IA.25 -->

Table IA.26 gives the levels behind these tests: each outcome before and after the dismissal, for the firm and for its competitor. Founder firms grew {{fg.founder.firm.rev.y3.pre.median}} a year before the dismissal and {{fg.founder.firm.rev.y3.post.median}} after it, while their competitors grew {{fg.founder.comp.rev.y3.pre.median}} and {{fg.founder.comp.rev.y3.post.median}}. The tests compare changes, not levels, so a firm already slowing is not counted as a new loss.

<!-- TABLE:IA.26 -->

Table IA.27 shows the same pattern year by year. With revenue set to {{index_base}} in the year before the dismissal, the median founder firm stands at {{fgpath.founder.firm.p5.median}} in the fifth year and its competitor at {{fgpath.founder.comp.p5.median}}. Each year uses the pairs that both file in it, so later years hold fewer and stronger firms.

<!-- TABLE:IA.27 -->

Table IA.28 counts what became of the firms. Of the {{fg.founder.n_base}} founder firms with revenue in the year before the dismissal, {{fgatt.founder.p5.filing}} still file in the fifth year. By then {{fgatt.founder.p5.bankrupt}} have gone bankrupt and {{fgatt.founder.p5.acquired}} have been taken over.

<!-- TABLE:IA.28 -->

Table IA.29 reports every outcome in means: for founders, the change against the competitor with its interval; for personal scandals, the difference from other dismissals, with the coefficient with controls. Raw means of the ratios are moved by a few firms with very small sales or assets, so the text reads medians and the winsorised columns.

<!-- TABLE:IA.29 -->

Table IA.30 names the dismissals over sexual misconduct or a relationship, which are too few for an average.

<!-- TABLE:IA.30 -->

### I. Checks added after review

The three checks of Table IA.31 were added after the main results were known. On founders clearly forced out, the loss against the closest competitor over the six-week window is {{fvrob.pushed.founder.pr.slideann.ret.mean|abs}} (p {{fvrob.pushed.founder.pr.slideann.ret.mean|p}}), on {{fvrob.pushed.founder.pr.slideann.ret.count}} firms. Against the average of the three closest competitors it is {{fv.founder.pr3.slideann.ret.mean|abs}}, the figure of Table 3.

<!-- TABLE:IA.31 -->

Table IA.32 compares the founder results before and after the {{fa.n_forced_resign_added}} forced resignations that the database codes as retirements join the sample.

<!-- TABLE:IA.32 -->

### J. When the market prices the news

Table IA.33 splits the return around each dismissal into windows. They run from the run-up, through the overnight gap and the trading day of the first tradeable day, to the months after. It also reports the release-time classes, the trading rules that use only public release times and the calendar-time alphas of Section 5.5.

<!-- TABLE:IA.33 -->

## References
