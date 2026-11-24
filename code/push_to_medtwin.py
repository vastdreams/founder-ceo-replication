"""Push the founder-CEO paper into MedTwin through the product API.

Steps (each idempotent):
  1. find or create the project (domain finance)
  2. POST statistics/load with outputs/combined_results.json (rule set founder_ceo_jfe)
  3. PUT the bibliography from literature/references.bib, then upload each held PDF
  4. create the paper from paper/main.local.md if absent, else PUT each '## ' section by title
  5. GET the integrity gate; on PASS save and pin a version, else print the failures
Usage: AUTH_TOKEN=... API_BASE=https://research.medtwin.ai/api/v1 python analysis/push_to_medtwin.py [--only stats|bib|paper]
"""

import json
import os
import re
import sys
import time
from datetime import date
from pathlib import Path

import requests

PACK = Path(__file__).resolve().parents[1]
REPO = PACK.parents[1]
BASE = os.environ.get("API_BASE", "https://research.medtwin.ai/api/v1")
PROJECT = "Firing the Founder: CEO removals at US firms"
TITLE = "Sacked: Sex, Fraud, and the Fate of Firms That Fire Their Founder CEO"
OLD_TITLES = (
    "Sacked: Sex, Fraud, Founders, and the Fate of Firms That Fire Their CEO",
    "Sacked: Founders, Sex Scandals, and the Fate of Firms That Fire Their CEO",
    "Sacked: Share Prices and Survival After Boards Fire Their CEO",
    "Sacked: Scandal, Founders, and the Fate of Firms That Fire Their CEO",
    "Firing the Founder: What Happens After US Boards Remove Their CEO",
)
JOURNAL = "Journal of Corporate Finance"
RENAMED_SECTIONS = (
    "8. Discussion",  # D-41: became "8. Discussion and limitations"
    "3. Announcement returns",
    "4. Long-run returns and operating performance",
    "5. Survival, takeover, and delisting",
    "6. The board after the founder",
    # the 20 Nov rewrite (D-18, D-19)
    "2. Data and sample",
    "3. The market's verdict",
    "4. After the dust settles: long-run returns and profits",
    "5. Sold, bankrupt, or still standing",
    "6. Who stays on the board",
    "7. Conclusion",
    # moved to the disclosure page (export settings), as in the cost-of-living paper
    "Data and code",
    "Use of AI tools",
    # platform review r3 (D-24): Section 7 became the discussion
    "7. Firings over fraud and legal violations",
    # D-34: the founder section leads the results and the later sections move down one
    "4. The stock around the announcement",
    "5. Which firms are delisted",
    "6. Returns, profits and the board over five years",
    "7. Discussion",
    "8. Conclusion",
    # D-39: the story in the main text, method and selection in the Internet Appendix
    "3. Data and design",
    "4. The founder CEO: what shareholders lose against competitors",
    "5. Every firing: the stock around the announcement",
    "6. Which firms are delisted",
    "7. Returns, profits and the board over five years",
    "2. Related work",
    "3. Data and method",
    "4. The founder CEO against competitors",
    "5. What the cases show",
    "6. Every firing: shares and survival",
    "7. Why the board acted",
)
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None


def session():
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {os.environ['AUTH_TOKEN']}"
    return s


def ok(r, what):
    if r.status_code >= 300:
        raise SystemExit(f"{what}: {r.status_code} {r.text[:800]}")
    return r.json() if r.text else {}


def project_id(s):
    rows = ok(s.get(f"{BASE}/projects/", timeout=60), "list projects")
    rows = rows.get("projects", rows) if isinstance(rows, dict) else rows
    for p in rows:
        if p.get("name") == PROJECT:
            return p["id"]
    p = ok(
        s.post(
            f"{BASE}/projects/",
            json={
                "name": PROJECT,
                "domain": "finance",
                "description": "What happens after a US board removes its CEO, with founders and conduct in focus.",
            },
            timeout=60,
        ),
        "create project",
    )
    return p["id"]


def load_stats(s, pid):
    payload = json.loads((PACK / "outputs" / "combined_results.json").read_text())
    r = ok(s.post(f"{BASE}/projects/{pid}/statistics/load", json=payload, timeout=300), "statistics/load")
    print("statistics loaded:", {k: r[k] for k in list(r)[:6]})


def bib_entries():
    sys.path.insert(0, str(REPO))
    from backend.scripts.bibtex_import import parse_bibtex

    out = {}
    for e in parse_bibtex((PACK / "literature" / "references.bib").read_text(encoding="utf-8")):
        year = e.get("year")
        out[e["key"]] = {
            "title": e["title"],
            "authors": [a.strip() for a in (e.get("author") or "").split(" and ") if a.strip()],
            "journal": e.get("journal"),
            "year": int(year) if year and str(year).isdigit() else None,
            "doi": e.get("doi"),
            "entry_type": e.get("entry_type", "article"),
            "volume": e.get("volume"),
            "number": e.get("number"),
            "pages": e.get("pages"),
            "publisher": e.get("publisher"),
            "booktitle": e.get("booktitle"),
            "url": e.get("url"),
            "note": e.get("note"),
            "cited": True,
        }
    return out


def sync_bib(s, pid):
    entries = bib_entries()
    ok(s.put(f"{BASE}/literature/{pid}/bibliography", json=entries, timeout=300), "bibliography")
    rows = ok(s.get(f"{BASE}/literature/{pid}", params={"limit": 500}, timeout=120), "literature list")["papers"]
    ids = {r.get("bibtex_key"): r["id"] for r in rows if r.get("bibtex_key")}
    status = {r.get("bibtex_key"): r.get("full_text_status") for r in rows}
    up, failed = 0, []
    for key in entries:
        pdf = PACK / "literature" / "pdfs" / f"{key}.pdf"
        if key in ids and pdf.exists() and status.get(key) not in ("parsed", "available"):
            for attempt in range(3):
                with pdf.open("rb") as fh:
                    r = s.post(
                        f"{BASE}/literature/{pid}/{ids[key]}/document/upload",
                        files={"file": (pdf.name, fh, "application/pdf")},
                        timeout=900,
                    )
                if r.status_code < 300:
                    break
                time.sleep(20 * (attempt + 1))
            else:
                failed.append(f"{key} ({r.status_code})")
                continue
            up += 1
    print(f"bibliography: {len(entries)} entries, {up} PDFs uploaded, failed: {failed}")


def sections_of(md):
    parts = re.split(r"^## ", md, flags=re.M)
    out = []
    for part in parts[1:]:
        title, _, body = part.partition("\n")
        out.append((title.strip(), body.strip() + "\n"))
    return out


def filled(settings):
    """Export settings with their {{stat}} placeholders filled from the results, as draft_paper.py fills the
    manuscript, so the cover's standfirst and chart labels can never carry a number typed by hand."""
    sys.path.insert(0, str(PACK / "analysis"))
    from draft_paper import render

    def fill(value):
        if isinstance(value, str):
            return re.sub(r"\{\{([a-z0-9_.:|!-]+)\}\}", render, value)
        if isinstance(value, list):
            return [fill(v) for v in value]
        if isinstance(value, dict):
            return {k: fill(v) for k, v in value.items()}
        return value

    return fill(settings)


def push_paper(s, pid):
    md = (PACK / "paper" / "main.local.md").read_text()
    papers = ok(s.get(f"{BASE}/papers/", params={"project_id": pid}, timeout=60), "list papers")
    papers = papers.get("papers", papers) if isinstance(papers, dict) else papers
    paper = next((p for p in papers if p.get("title") in (TITLE, *OLD_TITLES)), None)
    if paper is None:
        paper = ok(
            s.post(
                f"{BASE}/papers/import-from-markdown",
                json={
                    "project_id": pid,
                    "title": TITLE,
                    "md_text": md,
                    "target_journal": JOURNAL,
                },
                timeout=300,
            ),
            "import",
        )
        paper = paper.get("paper", paper)
        print("paper created", paper["id"])
    paper_id = paper["id"]
    settings = PACK / "paper" / "export_settings.json"  # title page, keywords, JEL and disclosures, kept in the repo
    body = {"title": TITLE, "target_journal": JOURNAL}
    if settings.exists():
        body.update(filled(json.loads(settings.read_text())))
    ok(s.put(f"{BASE}/papers/{paper_id}", json=body, timeout=60), "title and export settings")
    saved = ok(s.get(f"{BASE}/papers/{paper_id}/sections", timeout=60), "sections")
    saved = saved.get("sections", saved) if isinstance(saved, dict) else saved
    by_title = {str(x.get("title")).strip(): str(x.get("id") or x.get("section_id")) for x in saved}
    for order, (title, body) in enumerate(sections_of(md)):
        if title in by_title:
            ok(
                s.put(
                    f"{BASE}/papers/{paper_id}/sections/{by_title[title]}",
                    json={"title": title, "content": body, "order": order},
                    timeout=120,
                ),
                title,
            )
        else:
            ok(
                s.post(
                    f"{BASE}/papers/{paper_id}/sections",
                    json={"title": title, "content": body, "order": order},
                    timeout=120,
                ),
                title,
            )
    for title, sid in by_title.items():
        if title in RENAMED_SECTIONS:  # renamed in the template; sections the platform wrote are left alone
            r = s.delete(f"{BASE}/papers/{paper_id}/sections/{sid}", timeout=60)
            print("removed stale section", title, r.status_code)
    rep = ok(s.get(f"{BASE}/papers/{paper_id}/integrity", timeout=180), "integrity")
    status = rep.get("status") or rep.get("verdict") or ("PASS" if rep.get("passed") else "FAIL")
    failures = rep.get("failures") or rep.get("issues") or []
    print(f"integrity: {status}; {len(failures)} failures")
    for f in failures[:40]:
        print("   ", json.dumps(f)[:300])
    if str(status).upper() == "PASS":
        v = ok(
            s.post(
                f"{BASE}/papers/{paper_id}/versions",
                json={
                    "note": os.environ.get("VERSION_NOTE") or f"Draft for review, {date.today():%-d %B %Y}",
                    "auto_save": False,
                },
                timeout=120,
            ),
            "version",
        )
        ok(s.patch(f"{BASE}/papers/{paper_id}/versions/{v['id']}/pin", json={"pinned": True}, timeout=60), "pin")
        print("pinned version", v["id"])
    return paper_id


def main():
    s = session()
    pid = project_id(s)
    print("project", pid)
    if ONLY in (None, "stats"):
        load_stats(s, pid)
    if ONLY in (None, "bib"):
        sync_bib(s, pid)
    if ONLY in (None, "paper"):
        print("paper", push_paper(s, pid))


if __name__ == "__main__":
    main()
