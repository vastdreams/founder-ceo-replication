"""Extract board composition from two proxies per event: the last DEF 14A before the departure and the
first DEF 14A filed at least 600 days after it (about year t+2). The model lists directors; code computes
every outcome (board_outcomes.py). Forced exits first, then retirements.

Output: analysis/out/board_raw.jsonl  {event_id, which: pre|post, accession, data:{directors:[...], chair, ceo}}
"""

import asyncio
import gzip
import json
import os
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path.home()))
sys.path.insert(0, str(pathlib.Path.home() / "world_raw"))
import fce_db  # noqa: E402
from extract_docs import cut, text_of  # noqa: E402

HERE = pathlib.Path(__file__).parent / "out"
DOCS = pathlib.Path.home() / "world_raw/sec/docs/DEF14A"
OUTF = HERE / "board_raw.jsonl"
PROMPT = """From this proxy statement excerpt (director election / board section), return JSON only:
{"directors": [{"name": str, "independent": true|false|null, "is_chair": true|false, "is_ceo": true|false,
   "director_since": int|null, "age": int|null, "is_founder": true|false|null}],
 "chair_name": str|null, "ceo_name": str|null, "lead_independent_director": str|null}
List every director or nominee named. Use null when the text does not say. Do not guess."""


def main_sync():
    con = fce_db.connect()
    pairs = pd.read_sql(
        """
      with ev as (select g.dismissal_dataset_id event_id, g.departure_code code, c.cik,
                         coalesce(g.date_departure_announced, g.left_ceo_office) d
                  from world.ceo_turnover_gentry g join world.gvkey_cik c using(gvkey)
                  where g.departure_code in (3,4,5) and coalesce(g.date_departure_announced, g.left_ceo_office) >= '1998-01-01')
      select ev.event_id, ev.code,
        (select f.cik||'_'||f.accession from world.sec_filings f where f.cik=ev.cik and f.form='DEF 14A' and f.filing_date < ev.d order by f.filing_date desc limit 1) pre,
        (select f.cik||'_'||f.accession from world.sec_filings f where f.cik=ev.cik and f.form='DEF 14A' and f.filing_date >= ev.d + 600 order by f.filing_date limit 1) post
      from ev""",
        con,
    )
    pairs["prio"] = pairs["code"].isin([3, 4]).map({True: 0, False: 1})
    return pairs.sort_values("prio")


async def main():
    import aiohttp

    env = dict(x.strip().split("=", 1) for x in open(os.path.expanduser("~/.config/research-keys.env")) if "=" in x)
    key = env["DEEPSEEK_API_KEY"].strip('"')
    pairs = main_sync()
    seen = {(json.loads(x)["event_id"], json.loads(x)["which"]) for x in open(OUTF)} if OUTF.exists() else set()
    jobs = [
        (int(r.event_id), w, getattr(r, w))
        for r in pairs.itertuples()
        for w in ("pre", "post")
        if isinstance(getattr(r, w), str)
        and (int(r.event_id), w) not in seen
        and (DOCS / f"{getattr(r, w)}.gz").exists()
    ]
    sem, fh, tok = asyncio.Semaphore(32), open(OUTF, "a"), [0, 0]

    async def one(session, eid, which, doc):
        t = text_of(gzip.decompress((DOCS / f"{doc}.gz").read_bytes()))
        sec = cut(
            t,
            [
                r"(?i)election\s+of\s+directors",
                r"(?i)nominees\s+for\s+(election|director)",
                r"(?i)board\s+of\s+directors\s+and\s+committees",
                r"(?i)information\s+(about|concerning)\s+(the\s+)?(directors|nominees)",
            ],
            [r"(?i)\n\s*(executive\s+compensation|compensation\s+discussion|security\s+ownership)"],
            16000,
        )
        rec = {"event_id": eid, "which": which, "accession": doc, "section_chars": len(sec or "")}
        if sec:
            body = {
                "model": "deepseek-chat",
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [{"role": "system", "content": PROMPT}, {"role": "user", "content": sec}],
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
                            rec["data"] = json.loads(d["choices"][0]["message"]["content"])
                            u = d.get("usage", {})
                            tok[0] += u.get("prompt_tokens", 0)
                            tok[1] += u.get("completion_tokens", 0)
                            break
                    except Exception:
                        await asyncio.sleep(5 * (i + 1))
        fh.write(json.dumps(rec) + "\n")
        fh.flush()

    async with aiohttp.ClientSession() as s:
        await asyncio.gather(*(one(s, *j) for j in jobs))
    print(
        "board docs",
        len(jobs),
        "tokens",
        tok,
        "pairs",
        len(pairs),
        "missing pre",
        pairs["pre"].isna().sum(),
        "missing post",
        pairs["post"].isna().sum(),
    )


if __name__ == "__main__":
    asyncio.run(main())
