"""
PATH: data/founder_ceo_exits/analysis/local_gates.py
PURPOSE: Run MedTwin's manuscript gates on paper/main.local.md before a push: number integrity under the founder_ceo_jfe
         rule set, the prose style audit, the affirmative-causal sentence check, the reading gate, the headline gate,
         the claim-scope gate (a number's sentence must name the group and horizon it was measured on), and the
         horizon/N gate already enforced in combine_results.py.
WHY: The same gates run in production; this paper's earlier siblings went through several review rounds for exactly
     these failures (jargon, causal overreach, unscoped numbers), so they are checked before anyone reads the draft.
Usage: python data/founder_ceo_exits/analysis/local_gates.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))

from backend.schemas.lettered_report import LetteredReportPayload  # noqa: E402
from backend.services.gates.causal import _is_affirmative_causal, _sentences  # noqa: E402
from backend.services.gates.claim_scope import claim_section_failures  # noqa: E402
from backend.services.gates.reading import ReadingLimits, audit_manuscript  # noqa: E402
from backend.services.gates.style import audit, audit_title  # noqa: E402
from backend.services.paper_integrity import check_sections, ledger_values, markdown_to_sections  # noqa: E402
from backend.services.paper_rulesets.founder_ceo_jfe import FOUNDER_CEO_JFE as RULES  # noqa: E402
from backend.services.statistics_load import payload_to_report_sections  # noqa: E402

PACK = HERE.parent


def main() -> int:
    payload = LetteredReportPayload.model_validate(json.loads((PACK / "outputs" / "combined_results.json").read_text()))
    ledger = ledger_values(payload_to_report_sections(payload), [c.model_dump() for c in payload.constants])
    text = (PACK / "paper" / "main.local.md").read_text()
    title = text.splitlines()[0].lstrip("# ").strip()
    sections = [s for s in markdown_to_sections(text) if s["title"] not in ("References", title)]
    keys = {
        line.split("{", 1)[1].split(",", 1)[0]
        for line in (PACK / "literature" / "references.bib").read_text().splitlines()
        if line.startswith("@")
    }
    result = check_sections(
        sections,
        ledger,
        keys,
        abstract_max_words=RULES.abstract_max_words,
        table_max_columns=RULES.table_max_columns,
        roadmap_pattern=RULES.roadmap_pattern,
    )
    print("integrity:", "PASS" if result["passed"] else "FAIL")
    for k, val in result.items():
        if k != "passed" and val:
            print("  ", k, json.dumps(val, default=str)[:500])
    style = [(s["title"][:28], hit) for s in sections for hit in audit(s["content"])]
    style += [("title", hit) for hit in audit_title(title)]
    causal = [
        (s["title"][:28], x[:150]) for s in sections for x in _sentences(s["content"]) if _is_affirmative_causal(x)
    ]
    reading = audit_manuscript(sections, ReadingLimits(exempt_prefixes=RULES.reading_exempt))
    stats = [s.model_dump() for sec in payload.sections for s in sec.statistics]
    scope = claim_section_failures(sections, stats)
    for name, rows in (("style", style), ("causal", causal), ("scope", scope)):
        print(f"{name}: {len(rows)}")
        for r in rows[:40]:
            print("   ", r)
    print(f"reading: {len(reading)}")
    for f in reading[:60]:
        print(f"    [{f['section'][:22]}] {f['detail']}: {f['text'][:120]}")
    print("words:", sum(len(s["content"].split()) for s in sections))
    # The four production quality gates (house style, causal claims, statistics, exhibits), as the integrity
    # endpoint runs them, without the parts that need the database (bindings, the last pinned version, the edition).
    from backend.services.gates.quality import run_quality_gates, summary_line  # noqa: E402

    quality = run_quality_gates(
        sections,
        title=title,
        report_sections=payload_to_report_sections(payload),
        ruleset=RULES,
        legacy_sections=result.get("sections") or [],
    )
    print(summary_line(quality))
    for f in quality.get("failures", [])[:60]:
        print("   ", str(f)[:330])
    return 0 if result["passed"] and quality["passed"] and not (style or causal or reading or scope) else 1


if __name__ == "__main__":
    raise SystemExit(main())
