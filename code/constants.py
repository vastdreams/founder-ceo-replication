"""Every constant the paper prints, in one place, with its source (operator, 25 Nov 2026: every number has provenance).

Each entry is (name, value as printed, source). The template refers to a constant as {{name}}; draft_paper.py fills it
from combined_results.json, which carries this list. Values that the analysis also uses are read from here by the
analysis scripts where they are shared; the source names the script or document that fixes each one.
"""

M = "−"  # the minus sign the paper prints

CONSTANTS = (
    # sample and units
    (
        "sample_start",
        "1998",
        "build_events.py: first year of the main sample (Gentry et al. 2021 coverage with prices)",
    ),
    ("sample_end", "2023", "build_events.py: last announcement year in the dismissal database"),
    ("db_start", "1992", "Gentry et al. (2021) open CEO dismissal database: first year covered"),
    ("dollar_year", "2023", "founder_value.py: CPI-U deflator base year (analysis/cpi_u.csv)"),
    ("invest_usd", "$100", "founder_value.py INVEST: the $100 investment line (D-34 addendum)"),
    ("ci_pct", "95%", "convention: two-sided 95% intervals (stats_ops.py, founder_value.py)"),
    ("db_code_dismiss_a", "3", "Gentry et al. (2021) departure code 3: dismissal for job performance"),
    ("db_code_dismiss_b", "4", "Gentry et al. (2021) departure code 4: dismissal for legal violations or concerns"),
    ("db_code_retire", "5", "Gentry et al. (2021) departure code 5: voluntary retirement"),
    ("date_agree_days", "3", "describe.py: database date against 8-K date, agreement window in days"),
    ("ff_industries", "48", "Fama-French 48-industry classification (D-34 broad match)"),
    # event windows, trading days relative to the announcement (day 0)
    ("d_slide0", f"{M}30", "event_study.py / founder_value.py WINDOWS: start of the slide window"),
    ("d_slide1", f"{M}2", "event_study.py / founder_value.py WINDOWS: end of the slide window"),
    ("d_ann0", f"{M}1", "event_study.py: start of the announcement window"),
    ("d_ann1", "+1", "event_study.py: end of the announcement window"),
    ("d_post0", "+2", "event_study.py: start of the post-announcement window"),
    ("d_post1", "+60", "event_study.py: end of the post-announcement window"),
    ("d_wide0", f"{M}5", "referee_checks.py: start of the wide window"),
    ("d_wide1", "+5", "referee_checks.py: end of the wide window"),
    ("d_entry", f"{M}31", "founder_value.py: the close of day -31 starts the six-week window"),
    ("d_prior0", f"{M}282", "founder_value.py PRIOR: start of the prior-year return used for matching"),
    ("d_prior1", f"{M}31", "founder_value.py PRIOR: end of the prior-year return used for matching"),
    ("fig_d0", "-30", "figures.py: Figure 1 first day"),
    ("fig_d1", "+60", "figures.py: Figure 1 last day"),
    ("d_p2", "+2", "founder_timing.py: start of days +2 to +5"),
    ("d_p5", "+5", "founder_timing.py: end of days +2 to +5"),
    ("m_first", "1", "calendar_alpha.py / figures.py: first month after the announcement"),
    ("m12", "12", "founder_value.py / ops_matched.py: one-year horizon in months"),
    ("m36", "36", "founder_value.py / calendar_alpha.py: three-year horizon in months"),
    ("m60", "60", "founder_value.py: five-year horizon in months"),
    ("fy_pre", f"{M}3", "founder_growth.py: first fiscal year before the dismissal"),
    ("fy_pre1", f"{M}1", "founder_growth.py: last fiscal year before the dismissal"),
    ("fy_post3", "+3", "founder_growth.py: three years after"),
    ("fy_post5", "+5", "founder_growth.py: five years after"),
    ("fy_plus1", "+1", "ops_matched.py: fiscal year +1"),
    # rules and thresholds
    ("delist_bankrupt", "100%", "event_study.py: delisting return for a bankruptcy (minus 100%)"),
    ("delist_bankrupt_signed", f"{M}100%", "founder_growth.py: revenue growth assigned to a failed firm"),
    ("delist_other", "30%", "event_study.py shumway_delist_return: other delistings (minus 30%, Shumway 1997)"),
    ("size_band", "50%", "founder_value.py NEW_BAND: competitor market value within 50% (D-37 item 4)"),
    ("screen_sensitivity_req", "70%", "DECISIONS.md D-38: required sensitivity of the succession screen"),
    ("screen_days", "90", "DECISIONS.md D-38: succession screen, days between announcement and exit"),
    ("winsor_low", "1%", "stats_ops.py: winsorising, lower tail"),
    ("winsor_high", "99%", "stats_ops.py: winsorising, upper tail"),
    ("cost_bp", "50", "founder_timing.py: round-trip trading cost in basis points (D-46)"),
    ("crisis_y0", "2008", "referee_checks.py: robustness excludes the financial-crisis years"),
    ("crisis_y1", "2009", "referee_checks.py: robustness excludes the financial-crisis years"),
    ("delist_worst", "100%", "referee_checks.py: every non-takeover delisting set to minus 100%"),
    ("pre_start", "1992", "pre1998_tsr.py: first year of the pre-sample proxy-graph check"),
    ("pre_end", "1997", "pre1998_tsr.py: last year of the pre-sample proxy-graph check"),
    ("size_small_usd", "$300 million", "stats_ops.py SIZE_BANDS: upper edge of the smallest size band"),
    ("size_mega_usd", "$5 billion", "stats_ops.py SIZE_BANDS: lower edge of the largest size band"),
    ("early_bankrupt_days", "180", "stats_ops.py: bankruptcy recorded within 180 days marks a firm already failing"),
    ("fy_plus2", "+2", "ops_matched.py: fiscal year +2"),
    ("fy_minus1_ascii", "-1", "ops_matched.py: base fiscal year -1"),
    ("fy_zero", "0", "ops_matched.py: fiscal year of the departure"),
    ("index_base", "100", "founder_growth.py: revenue index base in the year before the dismissal"),
    ("days_12m", "252", "12 months x 21 trading days (founder_value.py, stats_returns.py)"),
    ("days_36m", "756", "36 months x 21 trading days"),
    ("days_60m", "1,260", "60 months x 21 trading days"),
    # dated events named in the text, each from the case files or a cited source
    ("hook_month", "November 2026", "NVIDIA 8-K and newsroom (nvidia2026form8k, nvidia2026reinstate)"),
    ("metoo_year", "2017", "Baharad et al. (2026), cited in the text"),
    ("case_enron_year", "2000", "paper/founder_cases/founder_cases.csv, event 1923 (Enron, 13 Dec 2000)"),
    ("case_jde_year", "2002", "paper/d44_corrections.csv, event 7861 (J.D. Edwards, 4 Jan 2002)"),
    ("case_mednax_year", "2020", "paper/d44_corrections.csv, event 7188 (Mednax, 13 Jul 2020)"),
    ("case_cypress_year", "2016", "paper/d44_corrections.csv, event 4161 (Cypress Semiconductor, 28 Apr 2016)"),
    ("case_healthsouth_year", "2003", "paper/date_corrections.csv, event 10421 (HealthSouth, 20 Mar 2003)"),
    ("case_adapthealth_year", "2021", "paper/date_corrections.csv, event 10360 (AdaptHealth, 13 Apr 2021)"),
)


def as_payload():
    """The constants as the payload lists them: name, value, source."""
    return [{"name": n, "value": v, "source": s} for n, v, s in CONSTANTS]
