"""
10_measurement_sensitivity.py
Measurement sensitivity analyses:
  1. Full response distribution of the 11-point economic satisfaction NRS
  2. Alternative dichotomisation cut-points
  3. Restricted cubic spline dose-response
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from scipy.interpolate import BSpline
from config import BASE, OUT
from model_specs import *

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*delta_grad.*")

# ── Load data ──────────────────────────────────────────────────────────
df = pd.read_parquet(os.path.join(OUT, "baseline_analytic.parquet")).copy()
panel = pd.read_parquet(os.path.join(OUT, "panel_data.parquet"))

print(f"Baseline sample: N={len(df)}")

# ── Prepare variables (same as script 08) ─────────────────────────────
df["age_10"] = df["age"] / 10
df["edu_middle"] = (df["education"] == 2).astype(float)
df["edu_high"] = (df["education"] == 3).astype(float)
df["edu_college"] = (df["education"] >= 4).astype(float)
df["current_smoker"] = (df["smoking"] == 2).astype(float)

w2 = panel[panel["wave"] == 2][["pid", "drinking"]].drop_duplicates("pid")
w2["current_drinker"] = (w2["drinking"] == 1).astype(float)
df = df.merge(w2[["pid", "current_drinker"]], on="pid", how="left")
df["regular_exercise"] = (df["exercise"] == 1).astype(float)

demo_covs = ["age_10", "female", "married", "edu_middle", "edu_high", "edu_college"]
health_covs = [
    "self_rated_health", "chronic_count", "bmi",
    "current_smoker", "current_drinker", "regular_exercise",
]
all_covs = demo_covs + health_covs

# ════════════════════════════════════════════════════════════════════════
# 1. RESPONSE DISTRIBUTION
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("1. ECONOMIC SATISFACTION RESPONSE DISTRIBUTION")
print("=" * 70)

dist = df.groupby("econ_satisfaction").agg(
    n=("econ_satisfaction", "count"),
    deaths=("died", "sum"),
).reset_index()
dist["pct"] = (dist["n"] / len(df) * 100).round(1)
dist["mortality_rate"] = (dist["deaths"] / dist["n"] * 100).round(1)
dist["cumulative_pct"] = dist["pct"].cumsum().round(1)

print(f"\n{'Value':>6} {'N':>6} {'%':>6} {'Cum%':>6} {'Deaths':>7} {'Mort%':>7}")
print("-" * 45)
for _, row in dist.iterrows():
    print(f"{int(row['econ_satisfaction']):>6} {int(row['n']):>6} "
          f"{row['pct']:>6.1f} {row['cumulative_pct']:>6.1f} "
          f"{int(row['deaths']):>7} {row['mortality_rate']:>7.1f}")

# ════════════════════════════════════════════════════════════════════════
# 2. ALTERNATIVE CUT-POINTS
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("2. ALTERNATIVE DICHOTOMISATION CUT-POINTS")
print("=" * 70)

cutpoints = [
    ("<=0 (lowest only)", 0, "bottom_0"),
    ("<=10 (bottom 2 cats)", 10, "bottom_10"),
    ("<=20 (bottom 3 cats)", 20, "bottom_20"),
    ("<=30 (bottom 4 cats)", 30, "bottom_30"),
    ("<=40 (bottom 5 cats)", 40, "bottom_40"),
    ("<=50 (bottom half)", 50, "bottom_50"),
]

cutpoint_results = []
base_vars = ["surv_time", "died"] + all_covs

for label, threshold, name in cutpoints:
    df[name] = (df["econ_satisfaction"] <= threshold).astype(float)
    model_df = df[base_vars + [name]].dropna()
    n_exposed = int(model_df[name].sum())
    pct_exposed = n_exposed / len(model_df) * 100

    cph = CoxPHFitter()
    cph.fit(model_df, duration_col="surv_time", event_col="died")

    hr = np.exp(cph.params_[name])
    ci = np.exp(cph.confidence_intervals_.loc[name].values)
    p = cph.summary.loc[name, "p"]

    result = {
        "label": label,
        "threshold": threshold,
        "N": len(model_df),
        "n_exposed": n_exposed,
        "pct_exposed": round(pct_exposed, 1),
        "HR": round(float(hr), 3),
        "CI_lower": round(float(ci[0]), 3),
        "CI_upper": round(float(ci[1]), 3),
        "p": round(float(p), 4),
    }
    cutpoint_results.append(result)

    sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
    print(f"  {label:30s}: HR {hr:.3f} ({ci[0]:.3f}-{ci[1]:.3f}), "
          f"p={p:.4f}{sig}  [n={n_exposed}, {pct_exposed:.0f}%]")

# ════════════════════════════════════════════════════════════════════════
# 3. RESTRICTED CUBIC SPLINES
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("3. RESTRICTED CUBIC SPLINE DOSE-RESPONSE")
print("=" * 70)


def natural_cubic_spline_basis(x, knots):
    """Create natural (restricted) cubic spline basis.
    Uses the truncated power basis with the constraint that the function
    is linear beyond the boundary knots.
    """
    knots = np.sort(knots)
    K = len(knots)
    n = len(x)
    x = np.asarray(x, dtype=float)

    # Truncated cubic function
    def h(x, k):
        return np.maximum(0, x - k) ** 3

    # Natural spline basis (K-2 basis functions for K knots)
    # Following Harrell's formulation
    basis = np.zeros((n, K - 2))
    dk = knots[-1] - knots[-2]

    for j in range(K - 2):
        # Harrell's truncated power basis formulation
        basis[:, j] = h(x, knots[j]) - (
            h(x, knots[-2]) * (knots[-1] - knots[j])
            - h(x, knots[-1]) * (knots[-2] - knots[j])
        ) / (knots[-1] - knots[-2])

    return basis


# Use 5 knots at fixed percentiles (Harrell's recommendation)
knot_pcts = [5, 27.5, 50, 72.5, 95]
knots = np.percentile(df["econ_satisfaction"].dropna(), knot_pcts)
print(f"  Knots at percentiles {knot_pcts}: {knots}")

# Create spline basis
x = df["econ_satisfaction"].values
spline_basis = natural_cubic_spline_basis(x, knots)

# Add spline columns to dataframe
spline_cols = []
for j in range(spline_basis.shape[1]):
    col_name = f"es_spline_{j}"
    df[col_name] = spline_basis[:, j]
    spline_cols.append(col_name)

# Also include linear term
df["econ_sat_linear"] = df["econ_satisfaction"]

# Fit model with spline terms
spline_model_vars = ["surv_time", "died", "econ_sat_linear"] + spline_cols + all_covs
spline_df = df[spline_model_vars].dropna()
print(f"  Spline model N: {len(spline_df)}, events: {int(spline_df['died'].sum())}")

cph_spline = CoxPHFitter()
cph_spline.fit(spline_df, duration_col="surv_time", event_col="died")

# Extract spline coefficients
spline_coefs = {}
for col in ["econ_sat_linear"] + spline_cols:
    spline_coefs[col] = {
        "beta": float(cph_spline.params_[col]),
        "se": float(cph_spline.standard_errors_[col]),
        "p": float(cph_spline.summary.loc[col, "p"]),
    }
print(f"\n  Spline coefficients:")
for col, vals in spline_coefs.items():
    print(f"    {col}: beta={vals['beta']:.5f}, p={vals['p']:.4f}")

# Test non-linearity (joint Wald test on spline terms)
from scipy.stats import chi2

spline_betas = np.array([cph_spline.params_[c] for c in spline_cols])
spline_vcov = cph_spline.variance_matrix_.loc[spline_cols, spline_cols].values
try:
    wald_stat = float(spline_betas @ np.linalg.inv(spline_vcov) @ spline_betas)
    wald_df = len(spline_cols)
    wald_p = 1 - chi2.cdf(wald_stat, wald_df)
    print(f"\n  Non-linearity test: chi2={wald_stat:.2f}, df={wald_df}, p={wald_p:.4f}")
except np.linalg.LinAlgError:
    wald_stat, wald_p = None, None
    print("\n  Non-linearity test: matrix singular, could not compute")

# Predict HR across the range, relative to reference (satisfaction=100)
ref_value = 100
grid = np.arange(0, 101, 1)
ref_basis = natural_cubic_spline_basis(np.array([ref_value]), knots)[0]

log_hrs = []
log_hr_ses = []
for val in grid:
    val_basis = natural_cubic_spline_basis(np.array([val]), knots)[0]

    # Difference in linear predictor relative to reference
    diff_linear = val - ref_value
    diff_spline = val_basis - ref_basis

    # Combine
    all_diffs = np.concatenate([[diff_linear], diff_spline])
    all_cols = ["econ_sat_linear"] + spline_cols
    beta_vec = np.array([cph_spline.params_[c] for c in all_cols])
    vcov = cph_spline.variance_matrix_.loc[all_cols, all_cols].values

    log_hr = float(all_diffs @ beta_vec)
    log_hr_se = float(np.sqrt(all_diffs @ vcov @ all_diffs))

    log_hrs.append(log_hr)
    log_hr_ses.append(log_hr_se)

log_hrs = np.array(log_hrs)
log_hr_ses = np.array(log_hr_ses)
hrs_grid = np.exp(log_hrs)
ci_lo_grid = np.exp(log_hrs - 1.96 * log_hr_ses)
ci_hi_grid = np.exp(log_hrs + 1.96 * log_hr_ses)

# Print key values
print(f"\n  Dose-response (ref=100, health-adjusted):")
for val in [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
    idx = val
    print(f"    Sat={val:3d}: HR {hrs_grid[idx]:.3f} "
          f"({ci_lo_grid[idx]:.3f}-{ci_hi_grid[idx]:.3f})")

# ── Save plot ──────────────────────────────────────────────────────────
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(grid, hrs_grid, "b-", linewidth=2)
ax.fill_between(grid, ci_lo_grid, ci_hi_grid, alpha=0.2, color="blue")
ax.axhline(1.0, color="grey", linestyle="--", linewidth=0.8)
ax.set_xlabel("Economic Satisfaction (0-100)", fontsize=12)
ax.set_ylabel("Hazard Ratio (ref: 100)", fontsize=12)
ax.set_title("Dose-Response: Economic Satisfaction and Mortality\n"
             "(Restricted Cubic Spline, Health-Adjusted)", fontsize=13)
ax.set_xlim(0, 100)

# Add rug plot of the actual data distribution
sat_vals = df["econ_satisfaction"].dropna().values
ax.plot(sat_vals, np.full_like(sat_vals, ax.get_ylim()[0]),
        "|", color="grey", alpha=0.05, markersize=4)

# Mark the 11 response categories
for val in range(0, 101, 10):
    n = (df["econ_satisfaction"] == val).sum()
    ax.annotate(f"n={n}", xy=(val, ci_hi_grid[val]),
                fontsize=6, ha="center", va="bottom", color="grey")

nonlin_text = (f"Non-linearity p={wald_p:.3f}" if wald_p is not None
               else "Non-linearity test: N/A")
ax.text(0.02, 0.98, nonlin_text, transform=ax.transAxes,
        fontsize=9, va="top", ha="left")

plt.tight_layout()
fig_path = os.path.join(OUT, "figures", "efigure4_spline_dose_response.png")
plt.savefig(fig_path, dpi=300)
plt.close()
print(f"\n  Figure saved to {fig_path}")

# ── Save all results ──────────────────────────────────────────────────
output = {
    "response_distribution": dist.to_dict(orient="records"),
    "alternative_cutpoints": cutpoint_results,
    "spline_analysis": {
        "knots": knots.tolist(),
        "knot_percentiles": knot_pcts,
        "nonlinearity_chi2": float(wald_stat) if wald_stat else None,
        "nonlinearity_df": len(spline_cols),
        "nonlinearity_p": float(wald_p) if wald_p else None,
        "coefficients": spline_coefs,
        "dose_response": {
            "satisfaction_values": grid.tolist(),
            "HR": hrs_grid.tolist(),
            "CI_lower": ci_lo_grid.tolist(),
            "CI_upper": ci_hi_grid.tolist(),
        },
    },
}

out_path = os.path.join(OUT, "supplementary", "measurement_sensitivity.json")
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"Results saved to {out_path}")
