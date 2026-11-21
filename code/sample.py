"""The paper's sample, in one place: which firings count, and which are personal scandals.

The question is what happens when a board fires its CEO, above all a founder, for something other than a crime: a
personal scandal (sex, a relationship, other personal conduct), a strategy or power dispute, activist pressure, poor
performance. Firings for financial misconduct or legal and regulatory violations (fraud, bribery, accounting, other
crimes) are a different event: the firm itself is in trouble with the law. They leave the main sample and are
reported only as a comparison in the discussion (operator, 20 Nov 2026; paper/DECISIONS.md D-18).

The reason is the final code: the evidence-based coding (event_coding_final.jsonl) after the hand reviews of every
financial-misconduct code (paper/fraud_review.csv), every sexual-conduct and relationship code (paper/conduct_review.csv) and every
other-personal-conduct code (paper/personal_conduct_review.csv; criminal charges there become personal_crime).
"""

import json
import pathlib

import pandas as pd

HERE = pathlib.Path(__file__).parent
CRIMINAL = frozenset({"financial_misconduct", "legal_or_regulatory", "personal_crime"})
PERSONAL = frozenset(
    {"relationship_with_employee", "relationship_other", "other_sexual_misconduct", "other_personal_conduct"}
)
SEX_OR_RELATIONSHIP = frozenset({"relationship_with_employee", "relationship_other", "other_sexual_misconduct"})


def final_reasons() -> pd.Series:
    """event_id -> the board's main reason after the hand reviews (NaN where the coding has none)."""
    coding = HERE / "out" / "event_coding_final.jsonl"
    c = pd.DataFrame([json.loads(x) for x in open(coding)])[["event_id", "primary_reason"]]
    for name in ("fraud_review.csv", "conduct_review.csv", "personal_conduct_review.csv"):
        f = HERE.parent / "paper" / name
        if f.exists():
            rv = pd.read_csv(f)[["event_id", "decision"]]
            c = c.merge(rv, on="event_id", how="left")
            c["primary_reason"] = c["decision"].fillna(c["primary_reason"])
            c = c.drop(columns=["decision"])
    return c.set_index("event_id")["primary_reason"]


def criminal_ids(events: pd.DataFrame) -> set:
    """Firings (forced == 1) whose final reason is financial misconduct or a legal or regulatory violation."""
    reason = events["event_id"].map(final_reasons())
    return set(events.loc[(events["forced"] == 1) & reason.isin(CRIMINAL), "event_id"].astype(int))


def apply(events: pd.DataFrame, include_criminal: bool = False) -> pd.DataFrame:
    """The paper's sample: criminal firings dropped (unless asked for), `reason` set to the final code, and
    `conduct` redefined as a firing over a personal scandal, so every script's conduct/performance split reads
    personal scandal against every other non-criminal reason."""
    d = events.copy()
    d["reason"] = d["event_id"].map(final_reasons())
    if "primary_reason" in d:  # every script reads the reviewed reason
        d["primary_reason"] = d["reason"].fillna(d["primary_reason"])
    d["criminal"] = ((d["forced"] == 1) & d["reason"].isin(CRIMINAL)).astype(int)
    if not include_criminal:
        d = d[d["criminal"] == 0].copy()
    d["conduct"] = ((d["forced"] == 1) & d["reason"].isin(PERSONAL)).astype(int)
    return d
