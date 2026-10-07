"""
Process REAL participant data from the jsPsych experiment.

Reads every jsPsych CSV in data/raw/ (one file per participant, trial-level),
converts each to one row per participant with the same columns as
data/simulated_data.csv, and applies the pre-specified exclusion rules:

  1. Failed attention check (did not select "Banana" with 100% confidence).
  2. Incomplete session (file does not contain all 10 questions and the debriefing).

The length of the recall text (recall_words) is kept in the log for inspection
but is NOT used for exclusion.

Outputs:
  data/processed_data.csv  - included participants only (same columns as simulated_data.csv)
  data/exclusions_log.csv  - every participant, with exclusion flags and reasons
"""
from pathlib import Path

import pandas as pd

N_ITEMS = 10
COLUMNS = ["participant_id", "condition", "n_correct", "accuracy_pct",
           "mean_confidence", "estimated_correct", "felt_power", "age"]

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"


def first_value(trials, task, column):
    """Value of `column` in the first trial of a given task (None if missing)."""
    rows = trials.loc[trials["task"] == task, column] if column in trials else pd.Series(dtype=object)
    rows = rows.dropna()
    return rows.iloc[0] if len(rows) else None


def summarise(path):
    trials = pd.read_csv(path)
    quiz = trials[trials["task"] == "quiz"]
    pid = trials["participant_id"].dropna().iloc[0] if "participant_id" in trials else path.stem

    complete = len(quiz) == N_ITEMS and (trials["task"] == "debrief").any()
    if not complete:
        return {"participant_id": pid, "source_file": path.name, "incomplete": True}

    n_correct = int(quiz["correct"].sum())
    recall_words = first_value(trials, "power_recall", "recall_words")
    attention = first_value(trials, "attention_check", "attention_passed")
    return {
        "participant_id": pid,
        "condition": trials["condition"].dropna().iloc[0],
        "n_correct": n_correct,
        "accuracy_pct": n_correct / N_ITEMS * 100,
        "mean_confidence": round(quiz["confidence"].astype(float).mean(), 1),
        "estimated_correct": first_value(trials, "estimate", "estimated_correct"),
        "felt_power": first_value(trials, "manipulation_check", "felt_power"),
        "age": first_value(trials, "demographics", "age"),
        "recall_words": recall_words,
        "attention_passed": attention,
        "suspicion": first_value(trials, "suspicion_probe", "suspicion"),
        "source_file": path.name,
        "incomplete": False,
    }


def exclusion_reasons(row):
    if row["incomplete"]:
        return "incomplete"
    if row["attention_passed"] != 1:
        return "failed attention check"
    return ""


def main():
    files = sorted(RAW_DIR.glob("*.csv"))
    if not files:
        print(f"No CSV files found in {RAW_DIR}. Put the jsPsych output files there and run again.")
        return

    log = pd.DataFrame([summarise(f) for f in files])
    log["exclusion_reason"] = log.apply(exclusion_reasons, axis=1)
    log["excluded"] = log["exclusion_reason"] != ""

    dupes = log["participant_id"].duplicated(keep=False)
    if dupes.any():
        print("WARNING: duplicate participant IDs:", sorted(log.loc[dupes, "participant_id"].unique()))

    included = log.loc[~log["excluded"], COLUMNS].copy()
    for col in ["n_correct", "estimated_correct", "felt_power", "age"]:
        included[col] = included[col].astype("Int64")
    included.to_csv(ROOT / "data" / "processed_data.csv", index=False)
    log.to_csv(ROOT / "data" / "exclusions_log.csv", index=False)

    print(f"Raw files read:  {len(log)}")
    print(f"Excluded:        {log['excluded'].sum()}")
    for reason, n in log.loc[log["excluded"], "exclusion_reason"].value_counts().items():
        print(f"  - {reason}: {n}")
    print(f"Included:        {len(included)}")
    if len(included):
        print(included.groupby("condition").size().rename("n per condition").to_string())
    print("\nSaved data/processed_data.csv and data/exclusions_log.csv")


if __name__ == "__main__":
    main()
