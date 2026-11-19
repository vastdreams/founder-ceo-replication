"""Extract board composition from two proxies per event: the last DEF 14A before the departure and the
first DEF 14A filed at least 600 days after it (about year t+2). The model lists directors; code computes
every outcome (board_outcomes.py). Forced exits first, then retirements.

Output: analysis/out/board_raw.jsonl  {event_id, which: pre|post, accession, data:{directors:[...], chair, ceo}}
"""

import asyncio
import gzip
import json
import pathlib
import sys

import pandas as pd

sys.path.insert(0, str(pathlib.Path.home() / "world_raw"))
import datasource  # noqa: E402
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
    g = datasource.gentry()
    g["d"] = g["date_departure_announced"].fillna(g["left_ceo_office"])
    g["code"] = pd.to_numeric(g["departure_code"], errors="coerce")
    g = g[g["code"].isin([3, 4, 5]) & (g["d"] >= "1998-01-01")]
    ev = g.merge(datasource.gvkey_cik()[["gvkey", "cik"]], on="gvkey")[["dismissal_dataset_id", "code", "cik", "d"]]
    ev = ev.rename(columns={"dismissal_dataset_id": "event_id"})
    px = datasource.sec_filings(["DEF 14A"]).sort_values("filing_date")
    px["key"] = px["cik"].astype(str) + "_" + px["accession"]
    by = dict(list(px.groupby("cik")))
    rows = []
    for e in ev.itertuples():
        f = by.get(e.cik)
        before = f[f["filing_date"] < e.d] if f is not None else None
        after = f[f["filing_date"] >= e.d + pd.Timedelta(days=600)] if f is not None else None
        rows.append(
            {
                "event_id": e.event_id,
                "code": e.code,
                "pre": before["key"].iloc[-1] if before is not None and len(before) else None,
                "post": after["key"].iloc[0] if after is not None and len(after) else None,
            }
        )
    pairs = pd.DataFrame(rows)
    pairs["prio"] = pairs["code"].isin([3, 4]).map({True: 0, False: 1})
    return pairs.sort_values("prio")


async def main():
    import aiohttp

    import keys

    key = keys.get("DEEPSEEK_API_KEY")
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
