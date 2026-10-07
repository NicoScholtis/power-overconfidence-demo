# Power & Overconfidence — demo study

A small, end-to-end behavioral experiment built as a learning exercise with Claude Code:
a browser experiment, a simulated dataset, an analysis pipeline, and a one-page report.

> **The data in this project are simulated.** They were generated to build and test the
> analysis before any real data collection, and are not empirical findings.

## Research question
Does recalling an experience of power increase overconfidence in one's own judgments?

## Contents
| Folder | What it contains |
|---|---|
| `experiment/index.html` | The experiment (jsPsych 7): consent → power recall (high vs. low, random) → 10 general-knowledge questions with confidence ratings, plus an attention check in the middle → estimate of own score → manipulation check → demographics → suspicion probe → debriefing. Saves a CSV at the end. |
| `analysis/simulate_data.py` | Generates 120 simulated participants (fixed seed = reproducible). |
| `analysis/process_raw.py` | For real data: combines the jsPsych CSVs in `data/raw/` into one row per participant (same columns as `simulated_data.csv`) and applies the pre-specified exclusions (see below). |
| `analysis/analysis.py` | Manipulation check, overall overconfidence, high vs. low power (Welch's t-test, Cohen's d, 95% CI), accuracy check, figure. |
| `analysis/build_report.py` | Builds `report/report.pdf` from the analysis results. |
| `data/simulated_data.csv` | The simulated dataset. |
| `figures/` | Output figure. |
| `report/report.pdf` | One-page summary. |

## How to run
**Experiment:** double-click `experiment/index.html` (needs an internet connection to load jsPsych).
No data is sent anywhere — responses are downloaded as a CSV to your own computer at the end.

**Analysis** (Python 3 with pandas, SciPy, matplotlib):
```
python3 analysis/simulate_data.py
python3 analysis/analysis.py
python3 analysis/build_report.py   # needs Google Chrome to create the PDF
```

**Real data:** put each participant's CSV (the file downloaded at the end of the experiment)
in `data/raw/`, then run:
```
python3 analysis/process_raw.py
```
This writes `data/processed_data.csv` (included participants) and `data/exclusions_log.csv`
(every participant, with the reason for any exclusion).

## Data quality measures and pre-specified exclusions
Built into the experiment:
- **Recall text:** cannot be left empty (no minimum length). The word count is saved as
  `recall_words` for inspection.
- **Confidence slider:** starts with no value; participants must move it before continuing
  (prevents leaving the default value).
- **Attention check:** shown among the general-knowledge questions — participants are asked to
  select "Banana" and set confidence to 100%. It is not counted in accuracy or confidence.
- **Suspicion probe:** "What do you think this study was about?", asked before the debriefing.
  Responses are kept in `exclusions_log.csv` for inspection; they are **not** used for exclusion.

Exclusion rules applied by `process_raw.py` (decided before data collection):
1. **Failed attention check:** did not select "Banana" *and* set confidence to 100%.
2. **Incomplete session:** the file does not contain all 10 questions and the debriefing.

## Variables (`data/simulated_data.csv`)
- `condition`: `high_power` / `low_power`
- `n_correct`, `accuracy_pct`: correct answers out of 10, and as a percentage
- `mean_confidence`: mean confidence across the 10 items (50–100)
- `estimated_correct`: participant's own estimate of their score (0–10)
- `felt_power`: manipulation check (1–7)
- `age`

Overconfidence = `mean_confidence` − `accuracy_pct`.

## Reference
Galinsky, A. D., Gruenfeld, D. H., & Magee, J. C. (2003). From power to action.
*Journal of Personality and Social Psychology, 85*(3), 453–466.
