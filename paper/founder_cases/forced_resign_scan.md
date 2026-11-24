# Founder CEOs forced to resign but coded as voluntary: scan (24 Nov 2026)

Operator, 24 Nov 2026: "remember to capture the ones where founder was forced to resign, that counts too." D-01
already treats a resignation under board pressure as a dismissal, but the sample takes only departures the CEO
dismissal database codes as dismissals (codes 3 and 4). This scan looks for founder departures the database codes as
voluntary that were in fact forced. Nothing here changes the sample; `forced_resign_scan.csv` holds every row.

## Data and limits

- Event file: the replication copy (`founder-ceo-replication.nosync/data/events/`, 21 Nov), because the Persona
  server refused connections (this machine's IP changed; the security group was not changed without the operator's
  word). The event file holds codes 3, 4 and 5 only; codes 6 to 9 were removed upstream, so they are not scanned.
- Founder flag: the founder code on the file. For retirements (code 5) it is the language model's code, not
  hand-checked, so some "founders" below may not be founders (Citigroup's Weill is doubtful).
- Sources read: the database's notes and quotes, the model's quoted evidence, and source titles. Web checks:
  Computer Weekly (403), Business Wire (timed out), MarketWatch (401) and Cutera's release (redirected to an
  unrelated page) could not be read; no workaround was tried. Mercury News loaded only page chrome. So every
  classification rests on evidence already held, and the quotes are second-hand where marked.

## Counts

| Step | N |
|---|---|
| Founder departures coded 5 (retirement), 1998–2023 | 448 |
| No sign of pressure in the evidence held | 237 |
| Weak signal: the model coded "forced" as unclear, no pressure words | 145 (not read by hand) |
| Pressure words in notes or quotes (activist, investigation, interim, abrupt, ...) | 29 read by hand |
| Strong signal: model coded forced, or reason is activist, performance, legal, conduct or power dispute | 37 read by hand |
| Classified forced resignation | 3 |
| Unclear | 13 |

## Forced resignations found

| Firm | Founder | Date | Evidence | Dating |
|---|---|---|---|---|
| J.D. Edwards | C. Edward McVaney | 4 Jan 2002 | "its board decided to swap long-term chief executive officer Ed McVaney for Robert Dutkowsky" (Computer Weekly, as quoted in the database note) | database announcement date; well-dated |
| Mednax | Roger J. Medel | 13 Jul 2020 | "pursuant to an agreement that Mednax has reached with Starboard Value LP ... which owns approximately 9.9%" (Business Wire, as quoted in the database note) | data day 0 is 12 Jul (left office); needs redating to 13 Jul |
| Cypress Semiconductor | T.J. Rodgers | Apr 2016 | database coder: "the board of directors pressured Mr. Rodgers to make way for new blood"; MarketWatch title "Burning Cypress: ousted CEO wages bruising battle with company he built" | data day 0 is 1 Apr (left office); Mercury News report dated 28 Apr; needs redating |

All three have prices. Medel and Rodgers kept a board role or fought the board afterwards (Rodgers later ran a proxy
fight against his successor's chairman).

## Unclear (pressure possible, no quote that shows it)

Cutera (Connors, 2016: abrupt exit, interim CEO), L Brands (Wexner, 2020: Epstein controversy and weak results),
Group 1 Automotive (Hollingsworth, 2005), Perry Ellis (Feldenkreis, 2015: activists pressing, handover to his son),
Citigroup (Weill, 2003: board members "agitated for a succession plan"; founder status doubtful), Siebel Systems
(2004), Safeguard Scientifics (Musser, 2001), Ariba (2001: the held evidence describes Mueller, not Krach), Grand
Canyon (2008: pre-IPO, no prices), Power Integrations (2002), Visual Networks (2001), Rent-A-Center (Speese, 2013),
Mercury Systems (2007).

## The 12 excluded planned successions (D-37), re-checked

None shows a forced resignation on the sources read. Ten are planned successions with the founder staying chairman
or executive chairman. Two are unclear: Datascope (2009: activist Ramius raised ethics concerns about the founder in
2007, but he left when the firm was sold) and KLX Energy (2020: "family health reasons", no source of pressure).

## Recommendation

Three forced founder resignations are missing from the sample, all priced, two needing redating; up to 13 more are
unclear. Adding them would raise the founder firings by about 5%. It would change the sample after the results were
seen, so it must be recorded as a correction in DECISIONS (with this file as its source) and every founder number
re-run, with the before-and-after shown. A second pass should read the 145 weak-signal rows and the unclear 13 from
the original filings once the server is reachable.

## Second pass (24 Nov 2026)

Operator, 24 Nov 2026: "add forced resignations". The second pass read the held evidence (database notes, the model's
quotes) for all 145 weak-signal rows and the 13 unclear rows, and searched the web for the cases with any sign of
pressure (search summaries of: eWeek, California HealthLine, San Fernando Valley Business
Journal, Fortune, Computerworld, SEC filings). The Persona server's 8-K cache could not be read (its command channel
was queued behind another run), and codes 6 to 9 were not scanned for the same reason; both are open.

| Result | N |
|---|---|
| Forced resignation, confirmed (join the sample) | 3 |
| Unclear after the second pass (stay out; pressure reported but no source says the board forced the exit) | 11 |
| Voluntary or planned | 145 |
| Outside the sample (no prices) or founder status doubtful | 2 |

No weak-signal row became a forced resignation. The unclear cases that come closest: Foundation Health Systems
(Hasan, 1998: critics said the board pushed him, the board denied it), BofI (Evans, 2007: relinquished the CEO role
but stayed president), Group 1 Automotive (Hollingsworth, 2005: left the board within a month), Cutera (Connors, 2016:
abrupt exit, no reason given), Perry Ellis (2015: handover to his son during an activist campaign) and L Brands
(Wexner, 2020: exit with a sale after an activist campaign).

Two of the three confirmed cases are also returning founders: McVaney had returned as J.D. Edwards' CEO before the
2002 exit, and Medel had returned as Mednax's CEO in 2003.
