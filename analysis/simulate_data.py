"""
Simulate participant-level data for the power & overconfidence demo.

!!! THESE DATA ARE SIMULATED — they are NOT real participants. !!!
They exist only to build and test the analysis pipeline before any real
data collection, as one would do when pre-registering an analysis plan.

Assumptions built into the simulation (deliberately modest):
- Accuracy on the 10 two-alternative items is the same in both conditions
  (power is not expected to change knowledge).
- Mean confidence is ~5 points higher in the high-power condition.
- The manipulation check (felt power, 1-7) is clearly higher in high power.
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42          # fixed seed so results are reproducible
N_PER_CONDITION = 60
N_ITEMS = 10

rng = np.random.default_rng(SEED)
rows = []
for condition in ["high_power", "low_power"]:
    for _ in range(N_PER_CONDITION):
        # Knowledge: each person has an underlying probability of being right
        p_correct = rng.beta(6.5, 3.5)                      # mean ~0.65
        n_correct = rng.binomial(N_ITEMS, p_correct)

        # Confidence (50-100 half-range scale)
        mean_conf = 72 + (5 if condition == "high_power" else 0) + rng.normal(0, 8)
        mean_conf = float(np.clip(mean_conf, 50, 100))

        # Estimated number correct (people tend to overestimate a bit)
        est = round(mean_conf / 100 * N_ITEMS + rng.normal(0, 1))
        est = int(np.clip(est, 0, N_ITEMS))

        # Manipulation check: "How powerful did you feel?" (1-7)
        felt = rng.normal(5.0 if condition == "high_power" else 3.3, 1.3)
        felt = int(np.clip(round(felt), 1, 7))

        rows.append({
            "condition": condition,
            "n_correct": n_correct,
            "accuracy_pct": n_correct / N_ITEMS * 100,
            "mean_confidence": round(mean_conf, 1),
            "estimated_correct": est,
            "felt_power": felt,
            "age": int(rng.integers(18, 40)),
        })

df = pd.DataFrame(rows).sample(frac=1, random_state=SEED).reset_index(drop=True)
df.insert(0, "participant_id", [f"SIM{i:03d}" for i in range(1, len(df) + 1)])

out = Path(__file__).resolve().parent.parent / "data" / "simulated_data.csv"
df.to_csv(out, index=False)
print(f"Saved {len(df)} SIMULATED participants to {out}")
