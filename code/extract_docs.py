"""Extract pre-2010 fundamentals, stock price ranges, proxy TSR graphs and merger prices from SEC documents.

Inputs: ~/world_raw/sec/docs/{10-K,10-K405,DEF14A,DEFM14A}/<cik>_<accession>.gz
Output: ~/world_raw/sec/extract/<form>.jsonl (one JSON line per document; resumable)
- EX-27 financial data schedules (1997-2001) are parsed with regex, no model.
- Short sections (10-K Items 5-6, proxy performance graph, merger consideration) go to DeepSeek
  (DEEPSEEK_API_KEY, see keys.py), 16 requests in flight. Documents are EDGAR filings you download first
  (FCE_SEC_ROOT, default ~/world_raw/sec, holds docs/<form>/<cik>_<accession>.gz).
Usage: python3 extract_docs.py [--dry N]   (--dry: cut sections for N docs and print sizes, no model calls)
"""
import asyncio, gzip, html, json, os, pathlib, re, sys
ROOT = pathlib.Path(os.environ.get("FCE_SEC_ROOT") or pathlib.Path.home() / "world_raw/sec")
OUT = ROOT / "extract"; OUT.mkdir(exist_ok=True)

def text_of(raw: bytes) -> str:
    t = raw.decode("latin1", "ignore")
    t = re.sub(r"(?is)<(script|style).*?</\1>", " ", t)
    t = re.sub(r"(?i)<br\s*/?>|</(p|div|tr|li|h\d)>", "\n", t)
    t = re.sub(r"(?i)</t[dh]>", " | ", t)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t\xa0]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n", t)

EX27_TAGS = ["MULTIPLIER", "FISCAL-YEAR-END", "PERIOD-END", "TOTAL-REVENUES", "SALES", "NET-INCOME", "TOTAL-ASSETS",
             "BONDS", "COMMON", "TOTAL-LIABILITY-AND-EQUITY", "EPS-PRIMARY", "EPS-DILUTED", "EPS-BASIC", "INCOME-PRETAX"]
def ex27(t: str):
    m = re.search(r"(?is)<TYPE>EX-27.*?(</DOCUMENT>|$)", t)
    if not m: return None
    blk = m.group(0); out = {}
    for tag in EX27_TAGS:
        v = re.search(rf"<{tag}>\s*([^\s<]+)", blk)
        if v: out[tag.lower()] = v.group(1)
    return out or None

def cut(t, start_pats, end_pats, maxlen):
    s = None
    for p in start_pats:
        ms = [m.start() for m in re.finditer(p, t)]
        # skip the table of contents: take the last start that is followed by real text
        ms = [x for x in ms if len(t) - x > 2000]
        if ms: s = ms[-1] if len(ms) > 1 and ms[0] < len(t) * 0.05 else ms[0]; break
    if s is None: return None
    e = len(t)
    for p in end_pats:
        m = re.search(p, t[s + 200:])
        if m: e = min(e, s + 200 + m.start())
    return t[s:min(e, s + maxlen)]

def sections(form, t):
    if form.startswith("10-K"):
        sec = cut(t, [r"(?i)item\s*5\.?\s*market\s+for", r"(?i)market\s+for\s+(the\s+)?registrant'?s\s+common"],
                  [r"(?i)item\s*7\.?\s*management'?s\s+discussion", r"(?i)item\s*7\.?\s"], 24000)
        if not sec or len(sec) < 3000:
            extra = [cut(t, [r"(?i)selected\s+(consolidated\s+)?financial\s+data", r"(?i)(five|ten|eleven)[- ]year\s+(financial\s+)?summary"], [r"(?i)management'?s\s+discussion"], 12000),
                     cut(t, [r"(?i)(quarterly|common)\s+(stock\s+)?(market\s+)?(price|data|information)", r"(?i)market\s+price\s+of\s+common"], [], 5000)]
            sec = "\n\n".join(x for x in [sec] + extra if x) or None
        emp = re.search(r"(?i)[^.]{0,120}\b(approximately|about)?\s*[\d,]{3,}\s+(full[- ]time\s+)?employees[^.]{0,300}\.", t)
        return {"items56": sec, "employees_sentence": emp.group(0).strip() if emp else None, "ex27": ex27(t)}
    if form == "DEF14A":
        return {"perf": cut(t, [r"(?i)performance\s+graph", r"(?i)cumulative\s+total\s+(shareholder|stockholder)?\s*return"],
                        [r"(?i)\n\s*(certain\s+relationships|section\s+16|proposal\s+(no\.?\s*)?\d|other\s+matters|compensation\s+committee\s+interlocks)"], 7000)}
    if form == "DEFM14A":
        return {"deal": cut(t, [r"(?i)merger\s+consideration", r"(?i)(will|shall)\s+be\s+converted\s+into\s+the\s+right\s+to\s+receive", r"(?i)per\s+share\s+in\s+cash", r"(?i)each\s+(issued\s+and\s+)?outstanding\s+share", r"(?i)what\s+(will\s+)?(i|you|shareholders|stockholders)\s+(will\s+)?receive"],
                        [r"(?i)\n\s*(risk\s+factors|background\s+of\s+the\s+merger)"], 6000)}
    return {}

PROMPTS = {
 "10-K": """From this 10-K excerpt (Items 5 and 6), return JSON only:
{"units": "as stated, e.g. thousands or millions", "fiscal_year_end": "MM-DD or null",
 "selected_data": [{"fiscal_year": int, "revenue": num|null, "net_income": num|null, "total_assets": num|null,
   "long_term_debt": num|null, "shareholders_equity": num|null, "eps_diluted": num|null, "dividends_per_share": num|null}],
 "price_ranges": [{"fiscal_year": int, "quarter": 1-4, "high": num, "low": num}],
 "exchange": "NYSE/Nasdaq/AMEX/other or null"}
Copy numbers exactly as printed in the stated units (negative for losses). Use null when absent. Do not compute or guess.""",
 "DEF14A": """From this proxy excerpt (stock performance graph), return JSON only:
{"base_year": int|null, "points": [{"date_or_year": "as printed", "company": num, "index_1": num|null, "index_2": num|null}],
 "index_1_name": str|null, "index_2_name": str|null}
Values are the cumulative total return of $100 invested, as printed. Use an empty list when there is no table of values.""",
 "DEFM14A": """From this merger proxy excerpt, return JSON only:
{"cash_per_share": num|null, "stock_exchange_ratio": num|null, "acquirer": str|null, "acquirer_ticker": str|null,
 "consideration_text": "the sentence that states what each share receives"}
Use null when not stated. Do not guess."""}

async def call(session, key, form, payload):
    import aiohttp
    body = {"model": "deepseek-chat", "temperature": 0, "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": PROMPTS[form]}, {"role": "user", "content": payload[:24000]}]}
    for i in range(5):
        try:
            async with session.post("https://api.deepseek.com/chat/completions", json=body,
                                    headers={"Authorization": f"Bearer {key}"}, timeout=aiohttp.ClientTimeout(total=180)) as r:
                if r.status == 429: await asyncio.sleep(10 * (i + 1)); continue
                d = await r.json()
                return json.loads(d["choices"][0]["message"]["content"]), d.get("usage", {})
        except Exception as e:
            err = str(e); await asyncio.sleep(5 * (i + 1))
    return {"error": "failed"}, {}

async def main():
    dry = int(sys.argv[sys.argv.index("--dry") + 1]) if "--dry" in sys.argv else 0
    import keys
    key = keys.get("DEEPSEEK_API_KEY")
    import aiohttp
    sem = asyncio.Semaphore(int(os.environ.get('CONC', 48)))
    async with aiohttp.ClientSession() as session:
        for folder in os.environ.get("FOLDERS", "DEFM14A,10-K405,10-K,DEF14A").split(","):
            form = "10-K" if folder.startswith("10-K") else folder
            outf = OUT / f"{folder}.jsonl"
            seen = {json.loads(l)["file"] for l in open(outf)} if outf.exists() else set()
            files = sorted((ROOT / "docs" / folder).glob("*.gz")) if (ROOT / "docs" / folder).exists() else []
            import datasource
            import pandas as _pd
            _g = datasource.gentry()
            _g = _g[_pd.to_numeric(_g["departure_code"], errors="coerce").isin([3, 4])]
            forced = {str(int(c)) for c in _g.merge(datasource.gvkey_cik(), on="gvkey")["cik"].dropna()}
            only = os.environ.get("ONLY_FORCED") == "1"
            files = [f for f in files if f.name not in seen and (not only or f.name.split("_")[0] in forced)]
            files.sort(key=lambda f: f.name.split("_")[0] not in forced)
            if os.environ.get("ONLY_CIKS"):  # restrict to a CIK list and to filings up to a year
                keep = set(open(os.environ["ONLY_CIKS"]).read().split())
                maxyy = int(os.environ.get("MAX_YEAR", "2004"))
                def _yr(f):
                    yy = int(f.name.split("_")[1].split("-")[1])
                    return 1900 + yy if yy > 50 else 2000 + yy
                files = [f for f in files if f.name.split("_")[0] in keep and _yr(f) <= maxyy]
            if os.environ.get("SHARD"):  # SHARD=i/n splits the work across processes
                i, n = map(int, os.environ["SHARD"].split("/"))
                files = [f for k, f in enumerate(files) if k % n == i]
            if os.environ.get("OUT_SUFFIX"):
                outf = OUT / f"{folder}{os.environ['OUT_SUFFIX']}.jsonl"
                seen |= {json.loads(x)["file"] for x in open(outf)} if outf.exists() else set()
                fh = open(outf, "a")
            files = files[: int(os.environ.get("LIMIT", 0)) or dry or None]
            fh = fh if os.environ.get("OUT_SUFFIX") else open(outf, "a"); tok = [0, 0]
            async def one(f):
                async with sem:
                    t = text_of(gzip.decompress(f.read_bytes()))
                    sec = sections(folder if folder != "10-K405" else "10-K", t)
                    payload = sec.get("items56") or sec.get("perf") or sec.get("deal")
                    rec = {"file": f.name, "cik": f.name.split("_")[0], "accession": f.name.split("_")[1][:-3],
                           "ex27": sec.get("ex27"), "employees_sentence": sec.get("employees_sentence"),
                           "section_chars": len(payload or "")}
                    if dry: print(folder, rec); return
                    if payload and key:
                        rec["data"], use = await call(session, key, form, payload)
                        tok[0] += use.get("prompt_tokens", 0); tok[1] += use.get("completion_tokens", 0)
                    fh.write(json.dumps(rec) + "\n"); fh.flush()
            await asyncio.gather(*(one(f) for f in files))
            print(folder, "done", len(files), "tokens in/out", tok, flush=True)

if __name__ == "__main__":
    asyncio.run(main())
