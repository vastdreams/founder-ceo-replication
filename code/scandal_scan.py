"""Personal-scandal reports about sitting CEOs of S&P 1500 firms, 1998-2023, from NYT Archive metadata, with whether
the CEO left within 12 months. The comparison group for the conduct firings: CEOs with a sex, relationship, harassment
or other personal-conduct report who were NOT fired.

Stages (python scandal_scan.py scan|extract|build|all):
  scan     stream ~/world_raw/news/nyt_archive/YYYY-MM.json.gz one month at a time (1998-01..2024-12) and keep articles
           whose headline + abstract + snippet + lead paragraph name an executive role (chief executive, C.E.O., CEO,
           chairman, founder, top executive, mogul) together with a personal-conduct term (CONDUCT below).
           -> out/scandal_candidates.jsonl
  extract  DeepSeek (deepseek-chat, temperature 0, 8 concurrent) reads each candidate's metadata and returns every CEO
           who is personally the subject of a personal-conduct issue, typed; cached and resumable.
           -> out/scandal_extract.jsonl
  build    drop financial / criminal items, CEOs already gone, subsidiary heads; match the firm to a Gentry et al. firm
           (Gentry conames + SEC former names, fuzzy, plus NYT keywords) and the person to a Gentry CEO surname; one event
           per CEO and scandal (first report date); departure within 12 months from Gentry (any code); founder flag;
           recall against the 51 coded personal-conduct firings.
           -> out/scandal_events.parquet, out/scandal_review.csv, out/scandal_recall.csv

NYT terms forbid republishing archive text: the <=25-word quotes are for internal hand review only.
"""

from __future__ import annotations

import asyncio
import difflib
import gzip
import hashlib
import json
import pathlib
import re
import sys
import unicodedata

import pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
ARCHIVE = pathlib.Path.home() / "world_raw/news/nyt_archive"
CAND = OUT / "scandal_candidates.jsonl"
EXTR = OUT / "scandal_extract.jsonl"
FIRST_MONTH, LAST_MONTH = (1998, 1), (2024, 12)
EVENT_START, EVENT_END = pd.Timestamp("1998-01-01"), pd.Timestamp("2023-12-31")
# Gentry departures per year are ~290-345 through 2020, then 226 (2021), 173 (2022), 22 (2023): the database is
# complete through 2020 and thins after, so a 12-month window ending later is only partly observed.
FULL_COVERAGE_END, PARTIAL_COVERAGE_END = pd.Timestamp("2020-12-31"), pd.Timestamp("2022-12-31")
TOL = 14  # days
AGENT_NOTES = {
    ("michaels", 2010): "departed: NYT 2010-10-22 'Michaels Out at Tribune'; no Gentry record (Tribune in bankruptcy)",
    ("thompson", 2012): "departed: resigned as Yahoo CEO 13 May 2012 over the resume; no Gentry record",
    ("kubasik", 2012): "not a sitting CEO: CEO-elect (president/COO) forced out before taking office",
    ("redstone", 2002): "not a scandal: first article is his engagement",
    ("scudamore", 2014): "wrong firm: English Premier League, not Premier Inc",
    ("black", 2020): "wrong firm: Apollo Global Management, not Apollo Education Group",
    ("rivera", 2021): "wrong firm: a Bronx nonprofit, not Promus Hotel",
    ("paulson", 2003): "weak: an insensitive remark about layoffs",
}
KNOWN_51 = {
    7238, 1732, 3557, 3751, 13, 3311, 6254, 498, 3495, 7763, 2043, 3360, 1759, 7852, 4759, 1734, 6466, 1713, 307, 3407,
    443, 7665, 8547, 3749, 8486, 8257, 8205, 6347, 6523, 8517, 10500, 8761, 6390, 8664, 1857, 7747, 6628, 3563, 8500,
    2103, 6209, 2301, 1869, 6325, 8540, 9072, 9399, 5475, 8370, 6239, 10213,
}  # fmt: skip
CONDUCT_REASONS = [
    "relationship_with_employee",
    "other_sexual_misconduct",
    "relationship_other",
    "other_personal_conduct",
]
CODE_LABEL = {
    1: "death",
    2: "illness",
    3: "dismissed_performance",
    4: "dismissed_legal_or_conduct",
    5: "retired",
    6: "new_opportunity",
    7: "other",
    8: "missing",
    9: "execucomp_error",
}

ROLE = re.compile(
    r"chief executive|\bC\.E\.O\.?|\bCEOs?\b|chief exec\b|chairman|chairwoman|\bfounder|top executive|\bmogul", re.I
)
CONDUCT = re.compile(
    r"\baffair\b|extramarital|love affair|affairs? with|romantic(?:ally)?\b"
    r"|relationship with (?:an? |his |her )?(?:former )?(?:employee|subordinate|staff|worker|colleague|co-?worker|executive|woman|man|contractor|consultant)"
    r"|consensual|intimate relationship|personal relationship|improper relationship|inappropriate relationship|sexual relationship"
    r"|sexual(?:ly)? harass|harass(?:ment|ed|ing)?\b|sexual misconduct|sexual assault|sexual(?:ly)? (?:abuse|explicit|advances|encounter|impropriety)"
    r"|inappropriate (?:conduct|behavio|comment|remark|text|message|touch|personal)|improper (?:conduct|behavio)"
    r"|personal conduct|personal behavio|personal misconduct|#?me ?too\b|misconduct|code of conduct|ethics (?:code|policy|violation)"
    r"|fraterniz|lapses? (?:of|in) judgment|girlfriend|mistress|paramour|lover\b"
    r"|racial slur|racist|lewd|sexis[mt]|hostile work environment|womaniz|grop|adulter|infidelity|sex scandal|scandal"
    # second pass (recall check on the coded firings): behavior, policy violations, résumé lies, remarks, other conduct
    r"|behaviou?r\b|standards? of conduct|business conduct|conduct (?:policy|policies|standards|investigation|inquiry|review)"
    r"|violat\w* (?:[\w\u2019'-]+ ){0,4}polic(?:y|ies)|company[\u2019']?s? polic(?:y|ies)|internal polic"
    r"|r[e\u00e9]sum[e\u00e9]|educational background|academic (?:record|credentials)|lied about"
    r"|\bslur|n-word|offensive|insensitive|racially|derogatory|homophobic|anti-?gay|anti-?semit|bigot"
    r"|\bsex(?:ual|ually)?\b|\bdating\b|\bromance\b|escort|prostitut|strip club|pornograph|\bnude|drunk|intoxicat|cocaine|epstein"
    r"|misbehav|indiscretion|impropriet|unprofessional|bully|abusive|tirade|outburst|toxic (?:culture|workplace|work)"
    r"|allegations? of|accus(?:ed|ations?|er|ers)\b|complaints? (?:of|against|by)",
    re.I,
)


def months():
    y, m = FIRST_MONTH
    while (y, m) <= LAST_MONTH:
        yield f"{y}-{m:02d}"
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def doc_text(x) -> str:
    parts = [x.get("headline"), x.get("abstract"), x.get("snippet"), x.get("lead_paragraph")]
    return " | ".join(dict.fromkeys(p.strip() for p in parts if isinstance(p, str) and p.strip()))


# ---------------------------------------------------------------- scan
def scan():
    seen, n_docs, n_role = set(), 0, 0
    with open(CAND, "w") as fh:
        for ym in months():
            f = ARCHIVE / f"{ym}.json.gz"
            if not f.exists():
                print("missing", ym, flush=True)
                continue
            with gzip.open(f) as g:
                docs = json.load(g)  # one month in memory at a time
            k = 0
            for x in docs:
                n_docs += 1
                t = doc_text(x)
                if not ROLE.search(t):
                    continue
                n_role += 1
                terms = sorted({m.group(0).lower() for m in CONDUCT.finditer(t)})
                url = x.get("web_url") or ""
                if not terms or url in seen:
                    continue
                seen.add(url)
                k += 1
                fh.write(
                    json.dumps(
                        {
                            "cid": hashlib.sha1(url.encode(), usedforsecurity=False).hexdigest()[:16],
                            "pub_date": (x.get("pub_date") or "")[:10],
                            "web_url": url,
                            "section": x.get("section_name"),
                            "type_of_material": x.get("type_of_material"),
                            "headline": x.get("headline"),
                            "text": t,
                            "keywords": x.get("keywords") or [],
                            "terms": terms,
                        }
                    )
                    + "\n"
                )
            del docs
            print(ym, k, flush=True)
    print(f"scan: {n_docs} articles, {n_role} name an executive role, {len(seen)} candidates")


# ---------------------------------------------------------------- extract
PROMPT = """You read New York Times article metadata (headline, abstract, snippet, lead paragraph, index keywords).
List every person the text reports as the chief executive (CEO) of a company who is PERSONALLY the subject of a
personal-conduct issue: an affair; a romantic or sexual relationship (with an employee, subordinate or anyone else,
consensual or not); allegations, complaints, lawsuits or investigations of sexual harassment, sexual misconduct or
other harassment by them; offensive remarks (racist, sexist) or inappropriate personal behavior; a personal-conduct or
code-of-conduct violation; any other personal scandal. Also list CEOs accused of financial misconduct or crimes, labelled
as such so they can be filtered out.
Do NOT list: people who are not the CEO of a company (politicians, government officials, celebrities, athletes, heads of
nonprofits, universities, unions or sports leagues, journalists) unless they are a company's CEO; CEOs who only comment on,
investigate, settle or handle someone else's misconduct, or whose company is accused without the CEO being accused personally;
fictional characters (reviews or summaries of films, plays, novels, TV).
Return JSON {"events": [...]}, each item:
 "company": the company as written,
 "parent_company": if that company is a division, unit or subsidiary of a larger company, the parent's name, else null,
 "ceo_name": the person's full name (as written; if the text gives only the role, the name only if you are certain),
 "role_text": the role words in the text (e.g. "chief executive", "founder and chairman"),
 "ceo_at_time": "yes" if the person is the company's CEO when this issue is being reported (including a CEO who resigns or is
    fired over it in this article), "former" if the person had left the CEO post before the issue was reported, "no" if the
    person is not and was not CEO (e.g. chairman only, another executive), "unclear",
 "founder": "yes" if the text says the person founded or co-founded the company, else "no",
 "scandal_type": one of
    "sexual_relationship" (affair, romantic or sexual relationship, relationship with an employee or subordinate),
    "harassment_allegation" (allegations, complaints, lawsuits or investigations of sexual harassment, sexual misconduct or
        sexual assault without criminal charges; other harassment allegations against the person),
    "other_personal_conduct" (offensive remarks, slurs, inappropriate behavior, lying about personal matters, personal or
        code-of-conduct violations not about money),
    "financial_or_criminal" (fraud, accounting, insider trading, bribery, theft, embezzlement, expense or perk abuse, misuse of
        company money, or any criminal charge, arrest or conviction, e.g. DUI, drugs, assault, domestic violence, sex crimes),
 "report_kind": "new" if the article reports the issue as current news (first disclosure, ongoing allegations, an
    investigation, a departure over it), "retrospective" if it only recalls an issue from an earlier year,
 "event_year": the year the issue first became public if stated or clear from the text, else null,
 "departure_in_text": "fired", "resigned", "none" or "unclear": does the text report the CEO leaving over the issue,
 "quote": an exact excerpt of the text, at most 25 words, that shows the issue.
Return {"events": []} if there is no such person."""


def user_msg(c) -> str:
    return (
        f"Published: {c['pub_date']}\nSection: {c.get('section')}\nType: {c.get('type_of_material')}\n"
        f"Text: {c['text'][:6000]}\nKeywords: {'; '.join(c.get('keywords') or [])[:1500]}"
    )


async def _extract():
    import aiohttp

    sys.path.insert(0, str(HERE))
    import keys

    key = keys.get("DEEPSEEK_API_KEY")
    cands = [json.loads(line) for line in open(CAND)]
    done = set()
    if EXTR.exists():
        for line in open(EXTR):
            r = json.loads(line)
            if "error" not in r:
                done.add(r["cid"])
    todo = [c for c in cands if c["cid"] not in done]
    print(f"extract: {len(cands)} candidates, {len(done)} cached, {len(todo)} to do", flush=True)
    sem, tok, n = asyncio.Semaphore(8), [0, 0], [0]
    fh = open(EXTR, "a")

    async def one(session, c):
        body = {
            "model": "deepseek-chat",
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [{"role": "system", "content": PROMPT}, {"role": "user", "content": user_msg(c)}],
        }
        out = {"error": "failed"}
        async with sem:
            for i in range(6):
                try:
                    async with session.post(
                        "https://api.deepseek.com/chat/completions",
                        json=body,
                        headers={"Authorization": f"Bearer {key}"},
                        timeout=aiohttp.ClientTimeout(total=180),
                    ) as r:
                        if r.status == 429 or r.status >= 500:
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
        fh.write(json.dumps({"cid": c["cid"], **out}) + "\n")
        fh.flush()
        n[0] += 1
        if n[0] % 200 == 0:
            print("done", n[0], "tokens", tok, flush=True)

    async with aiohttp.ClientSession() as s:
        await asyncio.gather(*(one(s, c) for c in todo))
    fh.close()
    print("extract: coded", len(todo), "tokens", tok, flush=True)


def extract():
    asyncio.run(_extract())


# ---------------------------------------------------------------- matching helpers
SUFFIX = {
    "inc", "corp", "corporation", "co", "company", "companies", "ltd", "limited", "plc", "llc", "lp", "holdings",
    "holding", "group", "the", "incorporated", "sa", "nv", "ag", "se", "cl", "a", "b", "old", "new", "del", "de",
    "trust", "bancorp", "intl",
}  # fmt: skip


def ascii_(s: str) -> str:
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()


def norm_co(s: str) -> str:
    s = ascii_(s).lower().replace("&", " and ").replace("'", "").replace("’", "")
    s = re.sub(r"\s-\s*cl\s+[a-z]\b|\s-old\b|\s-new\b|\(the\)", " ", s)
    toks = [t for t in re.sub(r"[^a-z0-9]+", " ", s).split() if t not in SUFFIX]
    return " ".join(toks)


def co_sim(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    ta, tb = a.split(), b.split()
    short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    if long_[: len(short)] == short and len(short) >= 2:
        return 0.93
    if long_[: len(short)] == short and len(short[0]) >= 4:
        return 0.9  # "Wynn" ~ "wynn resorts", but also "apollo" ~ "apollo global management": needs the CEO to match
    r = difflib.SequenceMatcher(None, a, b).ratio()
    # "Disney" ~ "walt disney": one distinctive word inside the longer name; weak on its own (needs the CEO to match)
    if len(short) == 1 and len(short[0]) >= 5 and short[0] in long_ and short[0] not in GENERIC:
        r = max(r, 0.88)
    return r


GENERIC = {
    "american", "national", "general", "international", "united", "first", "financial", "energy", "services", "systems",
    "technologies", "technology", "resources", "industries", "capital", "global", "pacific", "southern", "northern",
    "western", "eastern", "communications", "entertainment", "health", "healthcare", "insurance", "airlines", "motors",
    "media", "foods", "brands", "partners", "properties", "realty", "investment", "investments", "networks", "software",
    "pharmaceuticals", "electric", "power", "petroleum", "chemical", "steel", "stores", "restaurants", "hotels",
}  # fmt: skip

NAME_JUNK = {
    "jr",
    "sr",
    "ii",
    "iii",
    "iv",
    "phd",
    "md",
    "dr",
    "mr",
    "ms",
    "mrs",
    "esq",
    "cpa",
    "dipl",
    "kfm",
    "rer",
    "pol",
}


def name_tokens(n: str):
    n = ascii_(n).lower().strip()
    if "," in n:
        head, tail = n.split(",", 1)
        tail_toks = [t for t in re.sub(r"[^a-z\-' ]+", " ", tail).split() if t not in NAME_JUNK and len(t) > 1]
        # "Krzanich, Brian M" (NYT keyword style) -> Brian M Krzanich; "Leslie Moonves, II" -> Leslie Moonves
        n = f"{tail} {head}" if len(head.split()) == 1 and tail_toks else head
    toks = re.sub(r"[^a-z\-' ]+", " ", n).replace("'", "").split()
    return [t.strip("-") for t in toks if t.strip("-") not in NAME_JUNK and len(t.strip("-")) > 1]


def surname(n: str) -> str:
    t = name_tokens(n)
    return t[-1] if t else ""


def same_person(a: str, b: str) -> bool:
    """a: name from the article, b: Gentry exec_fullname. Surname equal (or a hyphen/compound part of it)."""
    sa, tb = surname(a), name_tokens(b)
    if not sa or not tb:
        return False
    sb = tb[-1]
    return sa == sb or sa in sb.split("-") or sb in sa.split("-") or (len(sa) >= 4 and sa in tb[1:])


def load_gentry():
    sys.path.insert(0, str(HERE))
    import warnings

    warnings.filterwarnings("ignore")
    import datasource as ds

    g = ds.gentry()
    g = g[g["gvkey"].notna()].copy()
    g["gvkey"] = g["gvkey"].astype(int)
    g["dep_date"] = g[["date_departure_announced", "left_ceo_office"]].min(axis=1)
    # every name the firm has had: Gentry conames + SEC former names through the gvkey-CIK link
    names = {}
    for gv, cn in zip(g["gvkey"], g["coname"]):
        names.setdefault(gv, set()).add(norm_co(cn))
    try:
        con = ds._con()
        sec = pd.read_sql(
            "select l.gvkey, n.name from world.gvkey_cik l join world.sec_cik_names n on n.cik = l.cik", con
        )
        for gv, nm in zip(sec["gvkey"].astype(int), sec["name"]):
            if gv in names:
                names[gv].add(norm_co(nm))
    except Exception as e:  # files backend without SEC names: Gentry conames only
        print("no SEC former names:", e)
    names = {gv: {n for n in s if n} for gv, s in names.items()}
    return g, names


def match_firm(orgs, names, first_tok_idx):
    """orgs: [(normalized name, weight)] -> {gvkey: best similarity}"""
    best = {}
    for o, w in orgs:
        if not o:
            continue
        pool = set()
        for t in o.split():
            pool |= first_tok_idx.get(t, set())
        for gv in pool:
            s = max(co_sim(o, n) for n in names[gv]) * w
            if s > best.get(gv, 0):
                best[gv] = s
    return best


def looks_like_person_kw(k: str) -> bool:
    return bool(re.match(r"^[A-Z][A-Za-z'\-]+, [A-Z]", k or ""))


EXIT = re.compile(
    r"resign|step(?:s|ped|ping)? down|stepping aside|oust|\bfired\b|dismiss|departure|depart|successor|succeed|replac|retir|\bquit|leav(?:e|es|ing) (?:the|his|her)",
    re.I,
)


def nyt_exit_check(ev):
    """Gentry can miss a departure (e.g. a firm out of the index that year). For every event with no Gentry departure
    within 12 months, stream the next 12 months of NYT metadata for an article naming the CEO's surname, the firm and
    an exit word. Hits are flagged for hand review; the kept group is the events with none."""
    ev["nyt_exit_hits"], ev["nyt_exit_first"] = 0, None
    todo = ev.index[ev["departed_12m"] == 0]
    want = {}
    for i in todo:
        t0 = ev.at[i, "first_report_date"]
        for p in pd.period_range(t0, t0 + pd.Timedelta(days=365), freq="M"):
            want.setdefault(f"{p.year}-{p.month:02d}", []).append(i)
    pats = {}
    for i in todo:
        co = [
            t
            for t in (norm_co(ev.at[i, "company"]).split()[:1] + norm_co(ev.at[i, "gentry_coname"]).split()[:1])
            if len(t) >= 3
        ]
        pats[i] = (
            re.compile(rf"\b{re.escape(surname(ev.at[i, 'ceo_name']))}\b", re.I),
            [re.compile(rf"\b{re.escape(c)}", re.I) for c in co],
        )
    hits = {i: [] for i in todo}
    for ym in sorted(want):
        f = ARCHIVE / f"{ym}.json.gz"
        if not f.exists():
            continue
        with gzip.open(f) as g:
            docs = json.load(g)
        for x in docs:
            t = ascii_(doc_text(x)).replace("'", "")
            d = pd.Timestamp((x.get("pub_date") or "")[:10])
            for i in want[ym]:
                t0 = ev.at[i, "first_report_date"]
                if not (t0 <= d <= t0 + pd.Timedelta(days=365)):
                    continue
                sp, cps = pats[i]
                if sp.search(t) and any(c.search(t) for c in cps) and EXIT.search(t):
                    hits[i].append(f"{d:%Y-%m-%d} {x.get('headline')} <{x.get('web_url')}>")
        del docs
    for i, h in hits.items():
        ev.at[i, "nyt_exit_hits"] = len(h)
        ev.at[i, "nyt_exit_first"] = h[0] if h else None
    ev["outcome"] = "departed_12m"
    ev.loc[(ev["departed_12m"] == 0) & (ev["nyt_exit_hits"] == 0), "outcome"] = "kept"
    ev.loc[(ev["departed_12m"] == 0) & (ev["nyt_exit_hits"] > 0), "outcome"] = "kept_per_gentry_but_nyt_exit_words"


# ---------------------------------------------------------------- build
def build():
    cands = {c["cid"]: c for c in map(json.loads, open(CAND))}
    ext = {}
    for line in open(EXTR):
        r = json.loads(line)
        if "error" not in r:
            ext[r["cid"]] = r
    n_err = len({json.loads(line)["cid"] for line in open(EXTR)} - set(ext))
    rows = []
    for cid, r in ext.items():
        c = cands.get(cid)
        if c is None:
            continue
        for i, e in enumerate(r.get("events") or []):
            if not isinstance(e, dict):
                continue
            q = " ".join(str(e.get("quote") or "").split()[:25])
            rows.append(
                {
                    "cid": cid,
                    "k": i,
                    "pub_date": pd.Timestamp(c["pub_date"]),
                    "web_url": c["web_url"],
                    "headline": c["headline"],
                    "keywords": c["keywords"],
                    "company": str(e.get("company") or "").strip(),
                    "parent_company": e.get("parent_company"),
                    "ceo_name": str(e.get("ceo_name") or "").strip(),
                    "role_text": e.get("role_text"),
                    "ceo_at_time": str(e.get("ceo_at_time") or "unclear").lower(),
                    "founder_text": str(e.get("founder") or "no").lower(),
                    "scandal_type": str(e.get("scandal_type") or "").lower(),
                    "report_kind": str(e.get("report_kind") or "new").lower(),
                    "event_year": pd.to_numeric(e.get("event_year"), errors="coerce"),
                    "departure_in_text": e.get("departure_in_text"),
                    "quote": q,
                }
            )
    a = pd.DataFrame(rows)
    S = {"candidates": len(cands), "extracted_ok": len(ext), "extract_failed": n_err, "llm_items": len(a)}
    S["llm_items_by_type"] = a["scandal_type"].value_counts().to_dict()
    PERSONAL = {"sexual_relationship", "harassment_allegation", "other_personal_conduct"}
    a = a[a["scandal_type"].isin(PERSONAL)]
    S["personal_items"] = len(a)
    S["personal_items_by_ceo_at_time"] = a["ceo_at_time"].value_counts().to_dict()
    # every CEO-status label goes on to matching; "former"/"no" items survive only if Gentry shows the person as the
    # firm's CEO on the report date (checked after the outcome lookup below)
    a = a[a["ceo_name"].str.len() > 0]
    sub = a["parent_company"].notna() & (
        ~a["parent_company"].astype(str).str.strip().str.lower().isin(["", "null", "none"])
    )  # noqa: E712
    S["dropped_subsidiary_heads"] = int(sub.sum())
    a = a[~sub].copy()
    S["extracted_events"] = len(a)  # article x CEO items: personal conduct, any CEO-status label, not a subsidiary head
    S["extracted_events_by_ceo_at_time"] = a["ceo_at_time"].value_counts().to_dict()

    g, names = load_gentry()
    first_tok_idx = {}
    for gv, s in names.items():
        for n in s:
            for t in n.split():
                if len(t) >= 2 and t not in GENERIC:
                    first_tok_idx.setdefault(t, set()).add(gv)
    by_gv = dict(list(g.groupby("gvkey")))
    by_surname = {}
    for _, r in g.iterrows():
        by_surname.setdefault(surname(r["exec_fullname"]), []).append(r)

    out, unmatched = [], []
    for _, r in a.iterrows():
        orgs = [(norm_co(r["company"]), 1.0)]
        kw_orgs = [norm_co(k) for k in r["keywords"] if not looks_like_person_kw(k)]
        sims = match_firm(orgs, names, first_tok_idx)
        kw_sims = match_firm([(k, 1.0) for k in kw_orgs], names, first_tok_idx)
        person_kws = [k for k in r["keywords"] if looks_like_person_kw(k)]
        best = None
        for gv in set(sims) | set(kw_sims):
            s_llm, s_kw = sims.get(gv, 0.0), kw_sims.get(gv, 0.0)
            s = s_llm
            gd = by_gv[gv]
            pm = gd[[same_person(r["ceo_name"], x) for x in gd["exec_fullname"]]]
            if s_kw >= 0.93:
                # an NYT organization keyword names the firm: full match when the LLM's company agrees or the person
                # is that firm's Gentry CEO; a keyword alone (places, topics, other firms in the story) is not enough
                if s_llm >= 0.6 or len(pm):
                    s = max(s, 0.93)
            if s < 0.85:
                continue
            key = (len(pm) > 0, s)
            if best is None or key > best[0]:
                best = (key, gv, s, pm, "firm")
        if best is None or not best[0][0]:
            # name route: a Gentry CEO with this surname and first initial whose firm loosely matches
            tn = name_tokens(r["ceo_name"])
            for gr in by_surname.get(surname(r["ceo_name"]), []):
                gt = name_tokens(gr["exec_fullname"])
                if not tn or not gt or tn[0][:3] != gt[0][:3]:
                    continue
                s = (
                    max(co_sim(o, n) for o, _ in orgs + [(k, 1) for k in kw_orgs] for n in names[gr["gvkey"]])
                    if names.get(gr["gvkey"])
                    else 0
                )
                if s >= 0.7 and (best is None or s > best[2] - 0.2):
                    pm = by_gv[gr["gvkey"]]
                    pm = pm[[same_person(r["ceo_name"], x) for x in pm["exec_fullname"]]]
                    best = (((True, s)), gr["gvkey"], s, pm, "name")
                    break
        if best is None:
            unmatched.append(
                {k: r[k] for k in ("pub_date", "company", "ceo_name", "ceo_at_time", "scandal_type", "web_url")}
            )
            continue
        _, gv, s, pm, how = best
        out.append({**r.to_dict(), "gvkey": int(gv), "firm_sim": round(float(s), 3), "match_route": how,
                    "person_in_gentry": int(len(pm) > 0), "person_kw": "; ".join(person_kws)})  # fmt: skip
    m = pd.DataFrame(out)
    S["matched_items"] = len(m)
    pd.DataFrame(unmatched).to_csv(OUT / "scandal_unmatched.csv", index=False)  # items with no Gentry firm, for review

    # one event per CEO and scandal: cluster a CEO's articles; a gap of more than 365 days starts a new scandal
    m["pkey"] = m["gvkey"].astype(str) + "|" + m["ceo_name"].map(surname)
    m = m.sort_values(["pkey", "pub_date", "cid"])
    ev_rows, n_retro_only = [], [0]
    for pk, d in m.groupby("pkey", sort=False):
        d = d.reset_index(drop=True)
        cl, last = 0, None
        for i in range(len(d)):
            if last is not None and (d.loc[i, "pub_date"] - last).days > 365:
                cl += 1
            last = d.loc[i, "pub_date"]
            d.loc[i, "cluster"] = cl
        for c, dd in d.groupby("cluster"):
            if not (dd["report_kind"] == "new").any():
                n_retro_only[0] += 1  # only recaps of an earlier issue: not a new report
                continue
            f = first = dd.iloc[0]
            pri = {"sexual_relationship": 0, "harassment_allegation": 1, "other_personal_conduct": 2}
            types = sorted(set(dd["scandal_type"]), key=pri.get)
            date_flag = ""
            if first["report_kind"] == "retrospective":
                ey = dd["event_year"].dropna()
                if len(ey) and ey.min() < first["pub_date"].year:
                    date_flag = f"first article is retrospective; event_year {int(ey.min())}"
                else:
                    date_flag = "first article is retrospective"
            ev_rows.append({
                "pkey": pk, "repeat_scandal": int(c > 0), "gvkey": first["gvkey"],
                "company": f["company"], "ceo_name": max(dd["ceo_name"], key=len),
                "first_report_date": first["pub_date"], "scandal_type": types[0], "all_types": ";".join(types),
                "quote": f["quote"], "nyt_url": f["web_url"], "headline": f["headline"],
                "first_url": first["web_url"], "n_articles": int(dd["cid"].nunique()),
                "ceo_at_time_llm": next((v for v in ("yes", "unclear", "former", "no") if (dd["ceo_at_time"] == v).any()), "unclear"),
                "founder_text": int((dd["founder_text"] == "yes").any()),
                "departure_in_text": ";".join(sorted(set(map(str, dd["departure_in_text"])))),
                "firm_sim": dd["firm_sim"].max(), "match_route": first["match_route"],
                "person_in_gentry": int(dd["person_in_gentry"].max()), "date_flag": date_flag,
                "event_year_llm": dd["event_year"].min(),
            })  # fmt: skip
    ev = pd.DataFrame(ev_rows)
    S["dropped_retrospective_only_clusters"] = n_retro_only[0]
    S["events_all_dates"] = len(ev)
    ev = ev[(ev["first_report_date"] >= EVENT_START) & (ev["first_report_date"] <= EVENT_END)]
    S["events_1998_2023"] = len(ev)
    # recaps first seen after an earlier stated year: the scandal began before 1998 when event_year says so
    pre = ev["event_year_llm"].notna() & (ev["event_year_llm"] < 1998) & ev["date_flag"].ne("")
    S["dropped_pre1998_retrospective"] = int(pre.sum())
    ev = ev[~pre]

    # outcome from Gentry, matched by gvkey and CEO surname
    founder_final = pd.read_parquet(OUT / "founder_final.parquet")
    ff = dict(zip(founder_final["event_id"], founder_final["founder"]))
    res = []
    for _, e in ev.iterrows():
        gd = by_gv[e["gvkey"]]
        t0 = e["first_report_date"]
        pm = gd[[same_person(e["ceo_name"], x) for x in gd["exec_fullname"]]].sort_values("dep_date")
        pmd = pm[pm["dep_date"].notna()]
        # a report up to 14 days after the departure announcement still counts (the scandal surfaced with the exit)
        after = pmd[pmd["dep_date"] >= t0 - pd.Timedelta(days=TOL)]
        before = pmd[pmd["dep_date"] < t0 - pd.Timedelta(days=TOL)]
        o = {"gentry_exec_fullname": None, "dismissal_dataset_id": None, "departed_12m": 0, "departure_code": None,
             "departure_reason": None, "departure_date": None, "later_departure_date": None, "later_departure_code": None,
             "sitting": "yes"}  # fmt: skip
        o["gentry_conflict"] = None
        if len(before) and not len(after):
            if e["ceo_at_time_llm"] == "yes" and before.iloc[-1]["dep_date"] < t0 - pd.Timedelta(days=365):
                # the text says sitting CEO; Gentry's earlier exit may be a merger re-filing (Kotick, Activision 2008,
                # code 7) or a return to the post (Schnatter): keep, flag for review
                o["gentry_conflict"] = (
                    f"Gentry exit {before.iloc[-1]['dep_date']:%Y-%m-%d} (code {before.iloc[-1]['departure_code']}) before the report; text says sitting CEO"
                )
            else:
                o["sitting"] = "no: Gentry has this CEO leaving before the report"
        # Gentry tenure check: the person's next Gentry departure is on/after the report and no other CEO of the firm
        # left between the report and it (otherwise someone else held the post on the report date)
        o["gentry_ceo_on_report_date"] = 0
        if len(after):
            nxt = after.iloc[0]["dep_date"]
            between = gd[(gd["dep_date"] > t0 + pd.Timedelta(days=TOL)) & (gd["dep_date"] < nxt)]
            between = between[[not same_person(e["ceo_name"], x) for x in between["exec_fullname"]]]
            o["gentry_ceo_on_report_date"] = int(between.empty)
        if e["ceo_at_time_llm"] in ("former", "no") and not o["gentry_ceo_on_report_date"]:
            o["sitting"] = "no: text says former/not CEO and Gentry does not show this CEO in post on the report date"
        if len(after):
            x = after.iloc[0]
            o["gentry_exec_fullname"], o["dismissal_dataset_id"] = x["exec_fullname"], int(x["dismissal_dataset_id"])
            code = None if pd.isna(x["departure_code"]) else int(x["departure_code"])
            if pd.notna(x["dep_date"]) and x["dep_date"] <= t0 + pd.Timedelta(days=365):
                o.update(
                    departed_12m=1,
                    departure_code=code,
                    departure_reason=CODE_LABEL.get(code),
                    departure_date=x["dep_date"],
                )
            else:
                o.update(later_departure_date=x["dep_date"], later_departure_code=code)
        elif len(before):
            x = before.iloc[-1]
            o["gentry_exec_fullname"], o["dismissal_dataset_id"] = x["exec_fullname"], int(x["dismissal_dataset_id"])
        # another CEO at the firm leaving in the window: a name mismatch, or the scandal CEO was not the firm's CEO
        oth = gd[(gd["dep_date"] >= t0 - pd.Timedelta(days=TOL)) & (gd["dep_date"] <= t0 + pd.Timedelta(days=365))]
        oth = oth[[not same_person(e["ceo_name"], x) for x in oth["exec_fullname"]]]
        o["other_ceo_departure_12m"] = "; ".join(
            f"{x['exec_fullname']} ({x['dep_date']:%Y-%m-%d}, code {x['departure_code']:.0f})"
            for _, x in oth.iterrows()
            if pd.notna(x["dep_date"]) and pd.notna(x["departure_code"])
        )
        # the firm's previous CEO departure: this CEO's tenure starts after it
        notme = pd.Series([not same_person(e["ceo_name"], x) for x in gd["exec_fullname"]], index=gd.index)
        prev = gd[(gd["dep_date"] < t0) & notme]
        o["prev_ceo_departure"] = None if prev.empty else prev["dep_date"].max()
        end = t0 + pd.Timedelta(days=365)
        o["outcome_coverage"] = (
            "full" if end <= FULL_COVERAGE_END else "partial" if end <= PARTIAL_COVERAGE_END else "thin"
        )
        if o["departed_12m"]:
            o["kept_evidence"] = None
        elif o["later_departure_date"] is not None and pd.notna(o["later_departure_date"]):
            o["kept_evidence"] = "Gentry records this CEO leaving later"
        else:
            o["kept_evidence"] = "no Gentry departure for this CEO after the report"
        # founder: coded founder flag for departures (founder_final), Gentry notes, or the article itself
        src = []
        if any(ff.get(int(i)) == 1 for i in pm["dismissal_dataset_id"]):
            src.append("founder_final")
        if any(
            re.search(r"\b(co-?)?found(er|ed|ing)\b", str(nt), re.I)
            and surname(e["ceo_name"]) in ascii_(str(nt)).lower()
            for nt in pm["notes"]
        ):
            src.append("gentry_notes")
        if e["founder_text"]:
            src.append("nyt_text")
        o["founder_flag"], o["founder_source"] = int(bool(src)), ";".join(src)
        o["gentry_coname"] = gd["coname"].iloc[-1]
        res.append(o)
    ev = pd.concat([ev.reset_index(drop=True), pd.DataFrame(res)], axis=1)
    S["dropped_not_sitting_per_gentry"] = int(ev["sitting"].str.startswith("no: Gentry").sum())
    S["dropped_former_not_confirmed"] = int(ev["sitting"].str.startswith("no: text").sum())
    S["kept_former_or_no_confirmed_by_gentry"] = int(
        ((ev["sitting"] == "yes") & ev["ceo_at_time_llm"].isin(["former", "no"])).sum()
    )
    ev = ev[ev["sitting"] == "yes"].drop(columns="sitting")

    def conf(e):
        if (
            e["person_in_gentry"]
            and e["firm_sim"] >= 0.93
            and e["ceo_at_time_llm"] == "yes"
            and e["match_route"] == "firm"
        ):
            return "high"
        if (e["person_in_gentry"] or e["firm_sim"] >= 0.93) and (
            e["ceo_at_time_llm"] == "yes" or e["gentry_ceo_on_report_date"]
        ):
            return "medium"
        return "low"

    ev["match_confidence"] = ev.apply(conf, axis=1)
    # agent hand check of the automated rows (20 Nov 2026), from the NYT metadata already in the row; the operator's
    # review overrides these. The automated columns are left as computed.
    ev["agent_note"] = [AGENT_NOTES.get((surname(n), d.year)) for n, d in zip(ev["ceo_name"], ev["first_report_date"])]
    ev = ev.sort_values(["first_report_date", "gvkey"]).reset_index(drop=True)
    ev.insert(0, "event_id", [f"S{i + 1:04d}" for i in range(len(ev))])

    # recall against the coded personal-conduct firings
    sys.path.insert(0, str(HERE))
    import stats_returns

    d = stats_returns.load_labelled()
    current = set(d.loc[(d["forced"] == 1) & d["primary_reason"].isin(CONDUCT_REASONS), "event_id"].astype(int))
    # the recall set is the 51 forced personal-conduct exits as labelled on 20 Nov 2026 before
    # paper/personal_conduct_review.csv; in_current_set marks the ones the labelled data still codes that way
    evp = pd.read_parquet(OUT / "events.parquet")
    pr = pd.DataFrame([json.loads(x) for x in open(OUT / "event_coding_final.jsonl")])[["event_id", "primary_reason"]]
    known = (
        evp[evp["event_id"].isin(KNOWN_51 | current)]
        .merge(pr, on="event_id", how="left")[
            ["event_id", "gvkey", "coname", "exec_fullname", "code", "event_date", "primary_reason"]
        ]
        .copy()
    )
    known["in_known_51"] = known["event_id"].isin(KNOWN_51).astype(int)
    known["in_current_set"] = known["event_id"].isin(current).astype(int)
    known["event_date"] = pd.to_datetime(known["event_date"])
    rec = []
    allm = m.copy()
    for _, k in known.iterrows():
        sn = surname(k["exec_fullname"])
        lo, hi = k["event_date"] - pd.Timedelta(days=400), k["event_date"] + pd.Timedelta(days=60)
        hit = ev[(ev["gvkey"] == k["gvkey"]) & ev["ceo_name"].map(lambda n, k=k: same_person(n, k["exec_fullname"]))
                 & ev["first_report_date"].between(lo, hi)]  # fmt: skip
        cand_hit = [
            c
            for c in cands.values()
            if lo <= pd.Timestamp(c["pub_date"]) <= hi and re.search(rf"\b{re.escape(sn)}\b", ascii_(c["text"]), re.I)
        ]
        ext_hit = a[
            a["ceo_name"].map(lambda n, k=k: same_person(n, k["exec_fullname"])) & a["pub_date"].between(lo, hi)
        ]
        raw_hit = [cid for c in cand_hit for cid in [c["cid"]] if cid in ext]
        raw_types = [e.get("scandal_type") + "/" + str(e.get("ceo_at_time")) for cid in raw_hit for e in (ext[cid].get("events") or [])
                     if isinstance(e, dict) and same_person(str(e.get("ceo_name") or ""), k["exec_fullname"])]  # fmt: skip
        mm = allm[(allm["gvkey"] == k["gvkey"]) & allm["pub_date"].between(lo, hi)]
        if len(hit):
            stage, why = "found", ""
        elif not cand_hit:
            stage, why = "no_candidate", ""
        elif not raw_types:
            stage, why = "llm_no_item", ""
        elif not len(ext_hit):
            stage, why = "llm_filtered", ",".join(sorted(set(raw_types)))
        elif not len(mm):
            stage, why = "not_matched_to_firm", ",".join(sorted(set(ext_hit["company"])))
        else:
            stage, why = "dropped_after_match", ""
        rec.append({"event_id": int(k["event_id"]), "in_known_51": k["in_known_51"], "in_current_set": k["in_current_set"],
                    "coname": k["coname"], "exec_fullname": k["exec_fullname"],
                    "event_date": k["event_date"].date(), "primary_reason": k["primary_reason"], "stage": stage,
                    "detail": why, "n_candidate_articles": len(cand_hit),
                    "scandal_event_id": hit["event_id"].iloc[0] if len(hit) else None})  # fmt: skip
    rec = pd.DataFrame(rec)
    ev["in_known_conduct_firings"] = ev["event_id"].isin(rec["scandal_event_id"].dropna()).astype(int)

    nyt_exit_check(ev)
    ev.to_parquet(OUT / "scandal_events.parquet", index=False)
    cols = ["event_id", "company", "gentry_coname", "gvkey", "ceo_name", "gentry_exec_fullname", "first_report_date",
            "scandal_type", "all_types", "quote", "nyt_url", "headline", "n_articles", "departed_12m", "departure_code",
            "departure_reason", "departure_date", "later_departure_date", "later_departure_code", "kept_evidence",
            "outcome_coverage", "outcome", "nyt_exit_hits", "nyt_exit_first", "founder_flag", "founder_source", "match_confidence", "match_route", "firm_sim",
            "person_in_gentry", "gentry_ceo_on_report_date", "ceo_at_time_llm", "departure_in_text", "other_ceo_departure_12m", "prev_ceo_departure", "gentry_conflict",
            "repeat_scandal", "date_flag", "agent_note", "in_known_conduct_firings"]  # fmt: skip
    ev[cols].to_csv(OUT / "scandal_review.csv", index=False)
    rec.to_csv(OUT / "scandal_recall.csv", index=False)

    S["events"] = len(ev)
    S["events_by_confidence"] = ev["match_confidence"].value_counts().to_dict()
    S["departed_12m"] = int(ev["departed_12m"].sum())
    S["kept"] = int((ev["departed_12m"] == 0).sum())
    S["outcome"] = ev["outcome"].value_counts().to_dict()
    hm = ev[ev["match_confidence"].isin(["high", "medium"])]
    S["high_medium_events"] = len(hm)
    S["high_medium_outcome"] = hm["outcome"].value_counts().to_dict()
    S["high_medium_outcome_by_coverage"] = {
        f"{a}|{b}": int(n) for (a, b), n in hm.groupby(["outcome_coverage", "outcome"]).size().items()
    }
    S["by_coverage"] = ev.groupby("outcome_coverage")["departed_12m"].agg(["size", "sum"]).to_dict("index")
    S["departure_codes_12m"] = ev.loc[ev["departed_12m"] == 1, "departure_code"].value_counts().to_dict()
    S["recall_known_51"] = rec.loc[rec["in_known_51"] == 1, "stage"].value_counts().to_dict()
    S["recall_current_set"] = rec.loc[rec["in_current_set"] == 1, "stage"].value_counts().to_dict()
    S["founder_events"] = int(ev["founder_flag"].sum())
    json.dump(S, open(OUT / "scandal_summary.json", "w"), indent=1, default=str)
    print(json.dumps(S, indent=1, default=str))


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("scan", "all"):
        scan()
    if stage in ("extract", "all"):
        extract()
    if stage in ("build", "all"):
        build()
