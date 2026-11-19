"""Code each CEO departure: founder status, why the board acted, and relationship details.

The model reads text (dataset notes and sources, and from v2 the collected news) and returns labels with
a supporting quote. It never produces a statistic: counts and tests come from stats_*.py.
Taxonomy follows paper/RESEARCH_PLAN.md (D-02). A 10% random sample is hand-checked before use.

Input : analysis/out/events.parquet; optional ~/world_raw/news/{nyt,guardian}.jsonl
Output: analysis/out/event_coding_{version}.jsonl (resumable)
Usage : python code_events.py v1            (notes only, all events)
        python code_events.py v2 --news     (forced events, notes plus news)
"""

import asyncio
import json
import os
import pathlib
import sys

import pandas as pd

HERE = pathlib.Path(__file__).parent / "out"
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v1"
USE_NEWS = "--news" in sys.argv
OUTF = HERE / f"event_coding_{VERSION}.jsonl"

PROMPT = """You code why a US public company's CEO left office. Use only the text given. Return JSON only:
{
 "ceo_is_founder": "yes" | "no" | "unclear",          // founded or co-founded this company (or its predecessor)
 "founder_family": "yes" | "no" | "unclear",          // child or close relative of the founder, not a founder
 "founder_evidence": "short quote or null",
 "forced": "yes" | "no" | "unclear",                   // board fired or pushed the CEO out, incl. a resignation under pressure
 "primary_reason": one of ["relationship_with_employee","other_sexual_misconduct","other_personal_conduct",
     "financial_misconduct","performance","strategy_or_power_dispute","activist_or_shareholder_pressure",
     "legal_or_regulatory","merger_or_restructuring","retirement_or_health","new_opportunity","unclear"],
 "secondary_reasons": [same labels],
 "relationship": null or {"consensual": "yes"|"no"|"alleged_nonconsensual"|"unclear",
     "counterparty_role": "direct_report"|"other_employee"|"contractor"|"unclear",
     "policy_breach_cited": "yes"|"no"|"unclear", "concealed_from_board": "yes"|"no"|"unclear",
     "how_revealed": "investigation"|"whistleblower"|"press"|"self_disclosed"|"unclear"},
 "reason_evidence": "short quote",
 "confidence": "high" | "medium" | "low"
}"""


_NEWS: dict = {}


def news_for(eid, cache=None):
    cache = _NEWS if cache is None else cache
    if not cache:
        for name in ("nyt", "guardian", "nyt_archive_matched"):
            p = pathlib.Path.home() / f"world_raw/news/{name}.jsonl"
            if p.exists():
                for line in open(p):
                    r = json.loads(line)
                    cache.setdefault(str(r["event_id"]), []).extend(
                        f"[{name} {(d.get('pub_date') or '')[:10]}] {d.get('headline') or ''}. {d.get('abstract') or d.get('trail') or ''} "
                        f"{d.get('lead_paragraph') or ''} {(d.get('body') or '')[:2500]}"
                        for d in r.get("docs", [])
                    )
    return "\n".join(cache.get(str(eid), [])[:8])


async def main():
    import aiohttp

    env = dict(
        line_.strip().split("=", 1) for line_ in open(os.path.expanduser("~/.config/research-keys.env")) if "=" in line_
    )
    key = env["DEEPSEEK_API_KEY"].strip('"')
    ev = pd.read_parquet(HERE / "events.parquet")
    if USE_NEWS:
        ev = ev[ev["forced"] == 1]
    seen = {json.loads(line_)["event_id"] for line_ in open(OUTF)} if OUTF.exists() else set()
    ev = ev[~ev["event_id"].isin(seen)]
    sem, fh, tok = asyncio.Semaphore(32), open(OUTF, "a"), [0, 0]

    async def one(session, e):
        text = (
            f"Company: {e['coname']}\nCEO: {e['exec_fullname']}\nFiscal year: {e['fyear']}\n"
            f"Departure announced: {e['event_date']}\nDataset reason code: {e['code']}\n"
            f"Dataset notes: {e['notes'] or ''}\nSources: {(e['sources'] or '')[:1500]}"
        )
        if USE_NEWS:
            text += "\nNews coverage:\n" + news_for(e["event_id"])
        body = {
            "model": "deepseek-chat",
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": PROMPT}, {"role": "user", "content": text[:20000]}],
        }
        async with sem:
            for i in range(5):
                try:
                    async with session.post(
                        "https://api.deepseek.com/chat/completions",
                        json=body,
                        headers={"Authorization": f"Bearer {key}"},
                        timeout=aiohttp.ClientTimeout(total=180),
                    ) as r:
                        if r.status == 429:
                            await asyncio.sleep(10 * (i + 1))
                            continue
                        d = await r.json()
                        out = json.loads(d["choices"][0]["message"]["content"])
                        u = d.get("usage", {})
                        tok[0] += u.get("prompt_tokens", 0)
                        tok[1] += u.get("completion_tokens", 0)
                        break
                except Exception:
                    await asyncio.sleep(5 * (i + 1))
            else:
                out = {"error": "failed"}
        fh.write(json.dumps({"event_id": int(e["event_id"]), "version": VERSION, **out}) + "\n")
        fh.flush()

    async with aiohttp.ClientSession() as s:
        await asyncio.gather(*(one(s, e) for _, e in ev.iterrows()))
    print("coded", len(ev), "tokens", tok)


if __name__ == "__main__":
    asyncio.run(main())
