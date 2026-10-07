"""
Analysis for the power & overconfidence demo (runs on SIMULATED data).

Pre-specified analysis:
1. Manipulation check: felt power, high vs. low (Welch t-test).
2. Overconfidence (mean confidence - accuracy, in percentage points):
   a) Are people overconfident overall? (one-sample t-test vs. 0)
   b) Main test: high vs. low power (Welch t-test, Cohen's d, 95% CI).
3. Accuracy by condition (should NOT differ - rules out a knowledge confound).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
df = pd.read_csv(ROOT / "data" / "simulated_data.csv")
df["overconfidence"] = df["mean_confidence"] - df["accuracy_pct"]

hi = df[df.condition == "high_power"]
lo = df[df.condition == "low_power"]


def welch(x, y):
    """Welch t-test with Cohen's d and 95% CI for the mean difference."""
    t, p = stats.ttest_ind(x, y, equal_var=False)
    vx, vy = x.var(ddof=1) / len(x), y.var(ddof=1) / len(y)
    df_w = (vx + vy) ** 2 / (vx**2 / (len(x) - 1) + vy**2 / (len(y) - 1))
    diff = x.mean() - y.mean()
    half = stats.t.ppf(0.975, df_w) * np.sqrt(vx + vy)
    pooled_sd = np.sqrt(((len(x) - 1) * x.var(ddof=1) + (len(y) - 1) * y.var(ddof=1))
                        / (len(x) + len(y) - 2))
    return {"t": t, "df": df_w, "p": p, "diff": diff,
            "ci_low": diff - half, "ci_high": diff + half, "d": diff / pooled_sd}


def describe(col):
    return {c: {"mean": g[col].mean(), "sd": g[col].std(ddof=1), "n": len(g)}
            for c, g in [("high_power", hi), ("low_power", lo)]}


t1, p1 = stats.ttest_1samp(df["overconfidence"], 0)
results = {
    "N": len(df),
    "manipulation_check": {**describe("felt_power"), "test": welch(hi.felt_power, lo.felt_power)},
    "overconfidence_overall": {"mean": df.overconfidence.mean(),
                               "sd": df.overconfidence.std(ddof=1), "t": t1,
                               "df": len(df) - 1, "p": p1},
    "overconfidence": {**describe("overconfidence"),
                       "test": welch(hi.overconfidence, lo.overconfidence)},
    "accuracy": {**describe("accuracy_pct"), "test": welch(hi.accuracy_pct, lo.accuracy_pct)},
    "confidence": describe("mean_confidence"),
}

# ---- Print a readable summary ----
def fmt_p(p):
    return "p < .001" if p < .001 else f"p = {p:.3f}".replace("0.", ".")

mc, oc, acc = results["manipulation_check"], results["overconfidence"], results["accuracy"]
print("SIMULATED DATA — demo only\n")
print(f"Manipulation check (felt power 1-7): high M = {mc['high_power']['mean']:.2f}, "
      f"low M = {mc['low_power']['mean']:.2f}, t({mc['test']['df']:.1f}) = "
      f"{mc['test']['t']:.2f}, {fmt_p(mc['test']['p'])}, d = {mc['test']['d']:.2f}")
ov = results["overconfidence_overall"]
print(f"Overall overconfidence: M = {ov['mean']:.1f} pts, t({ov['df']}) = {ov['t']:.2f}, {fmt_p(ov['p'])}")
print(f"Overconfidence by condition: high M = {oc['high_power']['mean']:.1f}, "
      f"low M = {oc['low_power']['mean']:.1f}, diff = {oc['test']['diff']:.1f} "
      f"[95% CI {oc['test']['ci_low']:.1f}, {oc['test']['ci_high']:.1f}], "
      f"t({oc['test']['df']:.1f}) = {oc['test']['t']:.2f}, {fmt_p(oc['test']['p'])}, "
      f"d = {oc['test']['d']:.2f}")
print(f"Accuracy by condition: high M = {acc['high_power']['mean']:.1f}%, "
      f"low M = {acc['low_power']['mean']:.1f}%, {fmt_p(acc['test']['p'])}")

(ROOT / "analysis" / "results.json").write_text(json.dumps(results, indent=2, default=float))

# ---- Figure: overconfidence by condition (means ± 95% CI + individual points) ----
fig, ax = plt.subplots(figsize=(5.2, 3.6), dpi=200)
colors = {"high_power": "#C0392B", "low_power": "#2E6DA4"}
labels = {"high_power": "High power", "low_power": "Low power"}
rng = np.random.default_rng(1)
for i, (cond, g) in enumerate([("high_power", hi), ("low_power", lo)]):
    y = g["overconfidence"]
    ax.scatter(i + rng.uniform(-0.15, 0.15, len(y)), y, s=10, alpha=0.35,
               color=colors[cond], edgecolor="none")
    ci = stats.t.ppf(0.975, len(y) - 1) * y.std(ddof=1) / np.sqrt(len(y))
    ax.errorbar(i + 0.32, y.mean(), yerr=ci, fmt="o", color=colors[cond],
                markersize=7, capsize=5, linewidth=2)
ax.axhline(0, color="#555", linestyle="--", linewidth=1)
ax.text(-0.45, 1, "well calibrated", fontsize=7, color="#555", va="bottom", ha="left")
ax.set_xticks([0.15, 1.15], [labels["high_power"], labels["low_power"]])
ax.set_xlim(-0.5, 1.6)
ax.set_ylabel("Overconfidence\n(confidence − accuracy, pts)")
ax.set_title("Overconfidence by power condition (simulated data)", fontsize=9)
for s in ["top", "right"]:
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(ROOT / "figures" / "overconfidence_by_condition.png")
print("\nFigure saved to figures/overconfidence_by_condition.png")
