"""Board outcomes computed from director lists (extract_board.py). All numbers are computed here.

Per event with both a pre and a post proxy:
  director_turnover   share of pre-departure directors absent from the post-departure list
  board_size_change   post minus pre number of directors
  indep_share_change  change in the share of independent directors
  split_before/after  chair and CEO are different people (before / after)
  outside_chair_after chair after is independent
  founder_stays       for founder removals: the removed CEO is still a director in the post proxy
  ceo_stays_director  for all removals: the removed CEO is still a director
Names match on surname plus first initial, case-insensitive.
Output: outputs/board_stats.json
"""

import json
import pathlib
import re

import pandas as pd
from stats_returns import R, one_group, put, two_group

HERE = pathlib.Path(__file__).parent
OUT = HERE.parent / "outputs"


def key(n):
    p = [
        x
        for x in re.sub(r"[^A-Za-z ]", " ", n or "").split()
        if x.lower() not in ("jr", "sr", "ii", "iii", "iv", "dr", "mr", "ms", "mrs")
    ]
    return (p[-1].lower(), p[0][0].lower()) if len(p) >= 2 else (p[0].lower(), "") if p else ("", "")


def main():
    R.clear()
    raw = [json.loads(x) for x in open(HERE / "out" / "board_raw.jsonl")]
    ev = pd.read_parquet(HERE / "out" / "events.parquet")
    c = pd.DataFrame([json.loads(x) for x in open(HERE / "out" / "event_coding_final.jsonl")])
    ev = ev.merge(c[["event_id", "ceo_is_founder"]], on="event_id", how="left")
    ff = HERE / "out" / "founder_final.parquet"
    if ff.exists():  # hand-reviewed founder flag
        ev = ev.merge(pd.read_parquet(ff)[["event_id", "founder"]], on="event_id", how="left")
        ev["ceo_is_founder"] = ev["founder"].fillna(0).map({1: "yes", 0: "no"})
    by = {}
    for r in raw:
        d = r.get("data") or {}
        if d.get("directors"):
            by.setdefault(r["event_id"], {})[r["which"]] = d
    rows = []
    for _, e in ev.iterrows():
        b = by.get(int(e["event_id"]))
        if not b or "pre" not in b or "post" not in b:
            continue
        pre, post = b["pre"]["directors"], b["post"]["directors"]
        kp, kq = {key(x.get("name")) for x in pre}, {key(x.get("name")) for x in post}
        ceo = key(e["exec_fullname"])

        def split(d):
            ch, ce = key(d.get("chair_name")), key(d.get("ceo_name"))
            return None if not ch[0] or not ce[0] else int(ch != ce)

        def indep(ds):
            v = [x.get("independent") for x in ds if x.get("independent") is not None]
            return sum(v) / len(v) if v else None

        chair_after = next((x for x in post if x.get("is_chair")), None)
        ip, iq = indep(pre), indep(post)
        rows.append(
            {
                "event_id": int(e["event_id"]),
                "forced": int(e["forced"]),
                "conduct": int(e["conduct"]),
                "founder": int(e["ceo_is_founder"] == "yes"),
                "director_turnover": len(kp - kq) / len(kp) if kp else None,
                "board_size_change": len(post) - len(pre),
                "indep_share_change": None if ip is None or iq is None else iq - ip,
                "split_before": split(b["pre"]),
                "split_after": split(b["post"]),
                "outside_chair_after": (
                    None
                    if chair_after is None or chair_after.get("independent") is None
                    else int(chair_after["independent"])
                ),
                "ceo_stays_director": int(ceo in kq),
            }
        )
    d = pd.DataFrame(rows)
    d.to_parquet(HERE / "out" / "board_outcomes.parquet", index=False)
    f, r = d[d.forced == 1], d[d.forced == 0]
    groups = {
        "forced": f,
        "retired": r,
        "forced_founder": f[f.founder == 1],
        "forced_nonfounder": f[f.founder == 0],
        "conduct": f[f.conduct == 1],
        "performance": f[f.conduct == 0],
    }
    put("g.events_with_board_data", len(d))
    for g, x in groups.items():
        put(f"g.n_{g}", len(x))
        for m in (
            "director_turnover",
            "board_size_change",
            "indep_share_change",
            "split_before",
            "split_after",
            "outside_chair_after",
            "ceo_stays_director",
        ):
            s = x[m].dropna().astype(float)
            put(f"board.{g}.{m}.mean", s.mean() if len(s) else None, n=len(s))
            one_group(f"board.{g}.{m}", s)
    put(
        "board.forced_founder.founder_stays.mean",
        groups["forced_founder"]["ceo_stays_director"].mean() if len(groups["forced_founder"]) else None,
        n=len(groups["forced_founder"]),
    )
    for a, b in [("forced", "retired"), ("forced_founder", "forced_nonfounder"), ("conduct", "performance")]:
        for m in ("director_turnover", "split_after", "ceo_stays_director", "indep_share_change"):
            two_group(f"boarddiff.{a}_vs_{b}.{m}", groups[a][m], groups[b][m])
    (OUT / "board_stats.json").write_text(json.dumps(R, indent=1))
    for k in [
        "g.events_with_board_data",
        "g.n_forced",
        "g.n_forced_founder",
        "board.forced.director_turnover.mean",
        "board.retired.director_turnover.mean",
        "boarddiff.forced_vs_retired.director_turnover.diff_mean",
        "board.forced.split_after.mean",
        "board.retired.split_after.mean",
        "board.forced_founder.founder_stays.mean",
        "board.forced_nonfounder.ceo_stays_director.mean",
        "board.retired.ceo_stays_director.mean",
    ]:
        v = R.get(k, {})
        print(f"{k:60s} {v.get('value')!s:>22} n={v.get('n')} p={v.get('p')}")


if __name__ == "__main__":
    main()
