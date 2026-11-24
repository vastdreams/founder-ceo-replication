# Founders who came back

Operator, 24 Nov 2026: "as there are so few who actually bring back their founders, what happened in between and so on".
Eleven founders among the pack's 103 founder departures came back to run the same firm as CEO or executive chairman.
The data are in `boomerangs.csv`, one row per return, with a source for each fact.

## How the numbers were made

- **Returns:** buy-and-hold from Alpha Vantage adjusted closes, firm against the S&P 500 (SPY), in percent.
  - **Absence:** from the close before the founder's exit to the close before the return was announced.
  - **Return announcement:** the close two trading days before the announcement to the close one day after it, so trading days −1 to +1.
  - **After the return:** from the close one day after the announcement, over 252 and 756 trading days (1 and 3 years).
- **WWE:** after the September 2023 merger, the series continues in TKO shares, one for one.
- **Not computed:**
  - **Pack data:** industry returns and revenue from SF1 were not computed, because the Persona server could not be reached (SSH timed out). Its firewall admits listed IP addresses only, and this machine's address has changed. The firewall was left alone.
  - **Enron and the 2005–07 Swift:** there is no price series for either. Swift was private from 2007 to 2010.
- **Small numbers:** with 11 cases there are no averages, only counts and names.

## Summary

| Founder, firm | Out | Back | Gone | Firm vs S&P 500 while gone | Return announced, 3 days, firm vs S&P | 1 year after, firm vs S&P | 3 years after, firm vs S&P |
|---|---|---|---|---|---|---|---|
| Kenneth Lay, Enron | Feb 2001 | Aug 2001 | 0.5 yr | n/a | $42.93 to $40.25 (OGJ) | bankrupt Dec 2001 | bankrupt |
| John Schnatter, Papa John's | Apr 2005 | Dec 2008 | 3.7 yr | +4.3% vs −21.0% | −3.4% vs +3.1% | +36.0% vs +29.3% | +125.4% vs +53.2% |
| Jerry Moyes, Swift | Oct 2005 | May 2007 | 1.5 yr | n/a (bought out at $31.55) | n/a | private | private |
| Morris Young, AXT | May 2004 | Jul 2009 | 5.2 yr | −23.1% vs −4.7% | −4.4% vs +2.6% | +205.3% vs +14.2% | +149.3% vs +53.0% |
| Mark Speese, Rent-A-Center | Feb 2014 | Jan 2017 | 2.9 yr | −52.4% vs +35.6% | −3.3% vs 0.0% | +3.8% vs +23.4% | +184.4% vs +53.3% (he left after 1 yr) |
| Stephen Waldis, Synchronoss | Jan 2017 | Apr 2017 | 0.3 yr | −35.1% vs +5.6% | −35.1% vs −0.2% (with a profit miss) | −30.0% vs +13.2% | −78.4% vs +29.4% |
| Robert Rucker, Tile Shop | Oct 2014 | Oct 2017 | 3.0 yr | +12.1% vs +39.7% | −8.5% vs +0.6% | −21.6% vs +7.2% | −45.1% vs +36.0% |
| Ajay Shah, SMART Global | 2000 | Mar 2018 | ~18 yr | n/a (different listed firm) | +5.7% vs −1.3% | −41.2% vs +5.1% | +12.5% vs +52.9% |
| Michael Reger, Northern Oil & Gas | Aug 2016 | May 2018 | 1.8 yr | −32.4% vs +29.1% | +3.8% vs −0.2% | −22.0% vs +4.2% | −33.6% vs +62.9% |
| Mark Dankberg, ViaSat | Nov 2020 | Jun 2022 | 1.6 yr | −2.5% vs +13.6% | −1.8% vs −2.9% | +35.8% vs +19.6% | −48.0% vs +71.6% |
| Vince McMahon, WWE (exec chair) | Jun 2022 | Jan 2023 | 0.6 yr | +11.4% vs +4.8% | +24.7% vs +1.1% | −4.9% vs +24.7% | +146.4% vs +85.7% (as TKO) |

**How many, and how they left.**

- Eleven of 103 founder departures were followed by a return to the same firm, at any distance.
- Four of the eleven had been forced out: Young, Moyes, Reger and McMahon.
- The other seven had handed over: Lay, Schnatter, Speese, Waldis, Dankberg and Shah by plan or deal, and Rucker in a step-down with no stated pressure.
- Two of the eleven, Lay and Dankberg, were left out of the paper's firing sample as planned successions (D-37).

**How long they were gone.**

- **Under a year:** Waldis (3 months), Lay (6 months) and McMahon (7 months).
- **One to four years:** Dankberg, Moyes, Reger, Speese, Rucker and Schnatter.
- **More than five years:** Young (5 years 2 months) and Shah (about 18 years, across a change of corporate shell).

**What happened in between.**

- **Successor stumbled (6):** Lay (Skilling quit as the stock halved), Speese (falling results and an activist), Waldis (successor and CFO quit with a profit miss), Rucker (successor's "mutually decided" exit), Young (successor resigned abruptly in 2009), and Dankberg (no reason given; shares down 41% from the June 2021 level, per one outlet).
- **Successor left for another opportunity (1):** Schnatter, after Travis left Papa John's.
- **The founder's money brought him back (3):**
  - Moyes bought the company.
  - McMahon used his majority vote.
  - Reger was recruited by a new large holder who became chairman.
- **Shah's return** followed his successor's own choice to step back.

**Shareholders while the founder was gone.**

- Six of the eight firms with prices trailed the S&P 500: AXT, Rent-A-Center, Synchronoss, Tile Shop, Northern Oil & Gas and ViaSat.
- Two beat it: Papa John's and WWE.

**Shareholders after the return.**

- **The news itself:** shares fell at six of the nine return announcements with prices. They rose at WWE (+24.7%), Northern Oil & Gas (+3.8%) and SMART (+5.7%).
- **One year on:** three firms beat the S&P 500 (AXT, ViaSat, Papa John's) and six trailed it.
- **Three years on:** four beat it (AXT, Papa John's, Rent-A-Center, WWE) and five trailed it.
- **Rent-A-Center's three-year gain** came after Speese had left again.

## Striking facts, each sourced in the CSV

1. **Second acts are short.**
   - Lay ran Enron for under four months before the bankruptcy.
   - Waldis was out again within seven months.
   - Speese lasted under a year and lost the chair to an activist.
   - Reger was CEO for about six weeks before the titles were swapped.
2. **Two founders came back for nothing.** Rucker returned to Tile Shop with no salary, and Reger to Northern Oil & Gas for $1 a year plus shares.
3. **The biggest return-day gain was a founder using his votes to sell.** WWE rose 24.7% over three days when McMahon came back as executive chairman to push a sale, and it was merged into TKO within nine months.
4. **Moyes did not wait to be asked.** He bought Swift back at $31.55 a share, about $2.74 billion with debt, 18 months after the SEC case pushed him out.
5. **The one clear turnaround was AXT.** Young was removed after a product-testing investigation and reappointed five years later at the 2009 low. The shares rose 205% in his first year back, against 14% for the S&P 500.

## Gaps

- Industry-relative returns and SF1 revenue or margin direction are not filled; they need the Persona server.
- The Enron price on 12 February 2001 and Swift's price at the October 2005 exit are not held.
- The Rent-A-Center exit date (3 February 2014) and the Tile Shop return date (30 October 2017) are effective or first-trading dates; the exact announcement dates are unverified.
- Northern Oil & Gas uses the 24 May 2018 effective date from the 8-K filed on 31 May.
- Several gap facts come from search summaries of the cited pages, not full reads.
