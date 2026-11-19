"""Final founder flag: the hand review in paper/founder_review.csv decides every forced exit it covers
(all model 'yes' codes plus notes-based candidates). Forced exits not in the review are non-founders.
Retirements keep the model code (used only as a comparison group). Output: analysis/out/founder_final.parquet"""

import json
import pathlib

import pandas as pd

HERE = pathlib.Path(__file__).parent


def main():
    ev = pd.read_parquet(HERE / "out" / "events.parquet")[["event_id", "code"]]
    c = pd.DataFrame([json.loads(x) for x in open(HERE / "out" / "event_coding_final.jsonl")])[
        ["event_id", "ceo_is_founder"]
    ]
    rv = pd.read_csv(HERE.parent / "paper" / "founder_review.csv")[["event_id", "decision"]]
    d = ev.merge(c, on="event_id", how="left").merge(rv, on="event_id", how="left")
    forced = d["code"].isin([3, 4])
    d["founder"] = 0
    d.loc[forced, "founder"] = (d.loc[forced, "decision"] == "yes").astype(int)
    d.loc[~forced, "founder"] = (d.loc[~forced, "ceo_is_founder"] == "yes").astype(int)
    d["founder_reviewed"] = d["decision"].notna().astype(int)
    d[["event_id", "founder", "founder_reviewed"]].to_parquet(HERE / "out" / "founder_final.parquet", index=False)
    rvf = pd.read_csv(HERE.parent / "paper" / "founder_review.csv")
    stats = {
        "b.founders_reviewed": {"value": float(len(rvf))},
        "b.founders_confirmed": {"value": float(((rvf["decision"] == "yes") & (rvf["model_code"] == "yes")).sum())},
        "b.founders_added": {"value": float(((rvf["decision"] == "yes") & (rvf["model_code"] != "yes")).sum())},
        "b.founders_rejected": {"value": float(((rvf["decision"] == "no") & (rvf["model_code"] == "yes")).sum())},
        "b.model_founder_codes": {"value": float((rvf["model_code"] == "yes").sum())},
        "b.model_error_rate": {
            "value": float(
                ((rvf["decision"] == "no") & (rvf["model_code"] == "yes")).sum() / (rvf["model_code"] == "yes").sum()
            )
        },
        "b.forced_founders_all_years": {"value": float(d.loc[forced, "founder"].sum())},
    }
    out = HERE.parent / "outputs"
    out.mkdir(exist_ok=True)
    (out / "coding_stats.json").write_text(json.dumps(stats, indent=1))
    print("forced founders", int(d.loc[forced, "founder"].sum()), "reviewed", int(d["founder_reviewed"].sum()))


if __name__ == "__main__":
    main()
