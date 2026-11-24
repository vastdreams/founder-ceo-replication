"""Fill paper/template.md from outputs/combined_results.json and write paper/main.local.md.

Placeholders:
  {{stat_id}}        the statistic's formatted value
  {{stat_id|abs}}    formatted absolute value (for "fell by X")
  {{stat_id|p}}      its p-value as "< 0.001" or "= 0.123" (write "p {{x|p}}")
  {{stat_id|pv}}     its bare p-value, "<0.001" or "0.123", for table cells
  {{stat_id|t}}      its t-statistic, two decimals
  {{stat_id|n}}      its N with thousands separators
  {{stat_id|sig}}    "statistically significant" (p < 0.05) or "not statistically significant"
  <!-- TABLES:X -->   every table of payload section X
  <!-- TABLE:7 -->     the table whose title starts "Table 7." ("IA.1" for "Table IA.1.")
Inside a pipe table write "!" for "|" ({{stat_id!n}}), so the modifier is not read as a column break.
A placeholder that does not resolve stops the build, so no number can be typed by hand.
"""

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PAY = json.loads((ROOT / "outputs" / "combined_results.json").read_text())
STATS = {s["stat_id"]: s for sec in PAY["sections"] for s in sec["statistics"]}
CONST = {c["name"]: c["value"] for c in PAY["constants"]}
CONST_SRC = {c["name"]: c.get("source") for c in PAY["constants"]}
PROV_REQUIRED = ("results_file", "key", "script", "function", "inputs", "window", "formula")
PRINTED = []  # one row per printed number, written to paper/PROVENANCE.csv


def provenance_row(placeholder, key, printed):
    """Record a printed number with its provenance; stop the build if any part is missing."""
    if key in CONST:
        if not CONST_SRC.get(key):
            raise KeyError(f"constant {key} has no source")
        PRINTED.append(
            {
                "placeholder": placeholder,
                "printed": printed,
                "kind": "constant",
                "id": key,
                "results_file": "analysis/constants.py",
                "script": "",
                "function": "",
                "inputs": "",
                "window": "",
                "n": "",
                "formula": "",
                "source": CONST_SRC[key],
            }
        )
        return
    pv = STATS[key].get("provenance") or {}
    missing = [f for f in PROV_REQUIRED if not pv.get(f)]
    if missing:
        raise KeyError(f"statistic {key} lacks provenance fields {missing}")
    PRINTED.append(
        {
            "placeholder": placeholder,
            "printed": printed,
            "kind": "statistic",
            "id": key,
            "results_file": pv["results_file"],
            "script": pv["script"],
            "function": pv["function"],
            "inputs": "; ".join(pv["inputs"]),
            "window": pv["window"],
            "n": pv.get("n") or "",
            "formula": pv["formula"],
            "source": f"{pv['results_file']}#{pv['key']}",
        }
    )


CELLS = json.loads((ROOT / "outputs" / "table_cell_sources.json").read_text())


def table_provenance(num, t):
    """Every number a printed table shows, with the results file, key and field it was read from."""
    sys.path.insert(0, str(ROOT / "analysis"))
    import provenance as P  # noqa: E402

    for c in CELLS.get(t["title"], []):
        if not c["file"]:
            raise KeyError(f"Table {num}: {c['printed']} in row {c['row']!r} has no source")
        if c["field"] == "constant":
            provenance_row(f"[Table {num}] {c['row']}", c["key"], c["printed"])
            continue
        script, inputs = P.PRODUCERS.get(c["file"], (None, None))
        if not script:
            raise KeyError(f"Table {num}: {c['file']} has no declared producer")
        PRINTED.append(
            {
                "placeholder": f"[Table {num}] {c['row']} | {c['col']}",
                "printed": c["printed"],
                "kind": f"table cell ({c['field']})",
                "id": c["key"],
                "results_file": f"outputs/{c['file']}",
                "script": f"analysis/{script}",
                "function": P.producer_function(script, c["file"]),
                "inputs": "; ".join(inputs),
                "window": f"as stated in Table {num}",
                "n": "",
                "formula": P.formula(c["key"], "", ""),
                "source": f"outputs/{c['file']}#{c['key']}",
            }
        )


def render(m):
    out = _render(m)
    key = m.group(1).replace("!", "|").partition("|")[0]
    provenance_row(m.group(0), key, out)
    return out


def _render(m):
    key, _, mod = m.group(1).replace("!", "|").partition("|")
    if key in CONST and not mod:
        return str(CONST[key])
    s = STATS.get(key)
    if s is None:
        raise KeyError(f"unknown statistic {key}")
    if mod == "p":
        p = s.get("p")
        return "< 0.001" if p is not None and p < 0.001 else f"= {p:.3f}"
    if mod == "pv":
        p = s.get("p")
        return "n/a" if p is None else ("<0.001" if p < 0.001 else f"{p:.3f}")
    if mod == "t":
        return f"{s['t']:.2f}"
    if mod == "n":
        return f"{s['n']:,}" if s.get("n") is not None else s["formatted"]
    if mod == "sig":
        p = s.get("p")
        return "statistically significant" if p is not None and p < 0.05 else "not statistically significant"
    if mod == "abs":
        return s["formatted"].lstrip("-")
    return s["formatted"]


def main():
    tpl = (ROOT / "paper" / "template.md").read_text()
    out = re.sub(r"\{\{([a-z0-9_.:|!-]+)\}\}", render, tpl)

    def render_tables(sec):
        out = []
        for t in sec["tables"]:
            head = "| " + " | ".join(t["columns"]) + " |\n|" + "---|" * len(t["columns"]) + "\n"
            body = "".join("| " + " | ".join(r) + " |\n" for r in t["rows"])
            out.append(f"### {t['title']}\n\n{head}{body}\n*Notes.* {t['notes']}\n")
        return "\n".join(out)

    for sec in PAY["sections"]:
        out = out.replace(f"<!-- TABLES:{sec['section_id']} -->", render_tables(sec))
        for t in sec["tables"]:
            num = (
                t["title"].split(".")[0].replace("Table ", "")
                if not t["title"].startswith("Table IA")
                else "IA." + t["title"].split(".")[1]
            )
            if f"<!-- TABLE:{num} -->" in out:
                table_provenance(num, t)
            out = out.replace(f"<!-- TABLE:{num} -->", render_tables({"tables": [t]}))
    if re.search(r"<!-- TABLES", out):
        raise KeyError("a table marker names a section with no tables")
    (ROOT / "paper" / "main.local.md").write_text(out)
    import csv

    cols = [
        "placeholder",
        "printed",
        "kind",
        "id",
        "results_file",
        "script",
        "function",
        "inputs",
        "window",
        "n",
        "formula",
        "source",
    ]
    with open(ROOT / "paper" / "PROVENANCE.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(PRINTED)
    print("wrote paper/PROVENANCE.csv", len(PRINTED), "printed numbers, all with provenance")
    print("wrote paper/main.local.md", len(out.split()), "words")


if __name__ == "__main__":
    sys.exit(main())
