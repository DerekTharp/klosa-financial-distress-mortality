"""
09_multiple_imputation.py
Multiple imputation for the combined model (Panel C of Table 2).
Addresses the 52% sample loss from listwise deletion when all four
financial measures are required simultaneously.

Uses MICE (via sklearn IterativeImputer) to impute missing values for:
  - hh_income (7.1% missing)
  - p_net_assets (33% missing)
  - bmi (2.3% missing)
Then re-runs the combined Cox model across M=20 imputed datasets
and pools results using Rubin's rules.
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer
from lifelines import CoxPHFitter, NelsonAalenFitter
from scipy import stats as sp_stats
from config import BASE, OUT
from model_specs import *

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*delta_grad.*")  # scipy L-BFGS noise
# IterativeImputer emits UserWarnings about feature names after transform;
# filter only that specific pattern rather than all UserWarnings.
warnings.filterwarnings("ignore", category=UserWarning, message=".*IterativeImputer.*")
warnings.filterwarnings("ignore", category=UserWarning, message=".*feature names.*")
np.random.seed(42)

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

# Drinking from wave 2
w2 = panel[panel["wave"] == 2][["pid", "drinking"]].drop_duplicates("pid")
w2["current_drinker"] = (w2["drinking"] == 1).astype(float)
df = df.merge(w2[["pid", "current_drinker"]], on="pid", how="left")

# Exercise
df["regular_exercise"] = (df["exercise"] == 1).astype(float)

# Subjective exposure
df["low_econ_sat_bl"] = (df["econ_sat_quintile"] == "Q1 (lowest)").astype(float)

# Objective thresholds from observed data (fixed across imputations)
hh_income_clean = df["hh_income"].copy()
hh_income_clean[hh_income_clean <= 0] = np.nan
income_q20 = hh_income_clean.quantile(0.20)
assets_q20 = df["p_net_assets"].quantile(0.20)

print(f"Income Q20 threshold: {income_q20:.0f}")
print(f"Assets Q20 threshold: {assets_q20:.0f}")

# Nelson-Aalen cumulative hazard (recommended for imputation model)
naf = NelsonAalenFitter()
naf.fit(df["surv_time"], event_observed=df["died"])
df["na_hazard"] = df["surv_time"].map(
    lambda t: naf.cumulative_hazard_at_times([t]).values[0]
)

# ── Define variable lists ──────────────────────────────────────────────
demo_covs = ["age_10", "female", "married", "edu_middle", "edu_high", "edu_college"]
analysis_health_covs = [
    "self_rated_health", "chronic_count", "bmi",
    "current_smoker", "current_drinker", "regular_exercise",
]
exposures = ["low_econ_sat_bl", "low_income", "on_welfare", "low_assets"]

# Variables for imputation model: everything that will be in the analysis
# plus auxiliary predictors and outcome information
imp_predictors = (
    ["hh_income", "p_net_assets", "bmi"]  # vars to impute
    + demo_covs
    + ["self_rated_health", "chronic_count", "current_smoker",
       "current_drinker", "regular_exercise"]
    + ["died", "na_hazard"]  # outcome info
    + ["econ_satisfaction", "on_welfare_bl"]  # auxiliary
)

# Build imputation dataframe — drop rows missing on non-imputable vars
imp_df = df[["pid", "surv_time", "died"] + imp_predictors].copy()
# Remove duplicates in column list
imp_df = imp_df.loc[:, ~imp_df.columns.duplicated()]

# Drop rows where required complete vars are missing
required_complete = demo_covs + ["died", "surv_time", "econ_satisfaction",
                                  "on_welfare_bl", "self_rated_health",
                                  "chronic_count"]
n_before = len(imp_df)
imp_df = imp_df.dropna(subset=required_complete)
print(f"Imputation sample: {len(imp_df)} (dropped {n_before - len(imp_df)} "
      f"with missing required vars)")

# Report pre-imputation missingness
print("\nPre-imputation missingness:")
for v in ["hh_income", "p_net_assets", "bmi", "current_drinker", "regular_exercise"]:
    if v in imp_df.columns:
        n_miss = imp_df[v].isna().sum()
        print(f"  {v}: {n_miss} ({n_miss / len(imp_df) * 100:.1f}%)")

# ── Multiple imputation (M=20) ────────────────────────────────────────
M = 20
print(f"\nRunning {M} imputations...")

# Columns to feed to the imputer (numeric only, no pid/surv_time)
imp_cols = [c for c in imp_predictors if c in imp_df.columns]
# Deduplicate
imp_cols = list(dict.fromkeys(imp_cols))

betas_list = []
vars_list = []
ns_list = []
events_list = []

for m in range(M):
    imputer = IterativeImputer(
        max_iter=20,
        random_state=42 + m,
        sample_posterior=True,
    )

    imp_data = imp_df[imp_cols].values.copy()
    imp_array = imputer.fit_transform(imp_data)
    imp_complete = pd.DataFrame(imp_array, columns=imp_cols, index=imp_df.index)

    # Derive binary exposures from imputed continuous values
    hh_inc = imp_complete["hh_income"].copy()
    hh_inc[hh_inc <= 0] = 0.01
    imp_complete["low_income"] = (hh_inc <= income_q20).astype(float)
    imp_complete["low_assets"] = (imp_complete["p_net_assets"] <= assets_q20).astype(float)
    imp_complete["on_welfare"] = imp_df["on_welfare_bl"].values
    imp_complete["low_econ_sat_bl"] = (imp_df["econ_satisfaction"] <= 30).astype(float).values

    # Add outcome
    imp_complete["surv_time"] = imp_df["surv_time"].values
    imp_complete["died"] = imp_df["died"].values

    # Build model dataframe
    model_vars = ["surv_time", "died"] + exposures + demo_covs + analysis_health_covs
    model_df = imp_complete[model_vars].dropna()

    # Fit Cox model
    try:
        cph = CoxPHFitter()
        cph.fit(model_df, duration_col="surv_time", event_col="died")
        betas = cph.params_[exposures].values
        var_matrix = cph.variance_matrix_.loc[exposures, exposures].values
        variances = np.diag(var_matrix)
        betas_list.append(betas)
        vars_list.append(variances)
        ns_list.append(len(model_df))
        events_list.append(int(model_df["died"].sum()))
        if m == 0:
            print(f"  Imputation 1: N={len(model_df)}, events={int(model_df['died'].sum())}")
    except Exception as e:
        print(f"  Imputation {m + 1} failed: {e}")
        continue

    if (m + 1) % 5 == 0:
        print(f"  Completed {m + 1}/{M}")

# ── Pool results using Rubin's rules ──────────────────────────────────
M_actual = len(betas_list)
print(f"\nPooling {M_actual} imputations...")

betas_arr = np.array(betas_list)
vars_arr = np.array(vars_list)

beta_pooled = betas_arr.mean(axis=0)
W = vars_arr.mean(axis=0)                   # within-imputation variance
B = betas_arr.var(axis=0, ddof=1)            # between-imputation variance
T = W + (1 + 1 / M_actual) * B              # total variance
se_pooled = np.sqrt(T)

# Relative increase in variance due to missingness
r_var = (1 + 1 / M_actual) * B / W

# HR and CI
hr_pooled = np.exp(beta_pooled)
ci_lo = np.exp(beta_pooled - 1.96 * se_pooled)
ci_hi = np.exp(beta_pooled + 1.96 * se_pooled)
z_stat = beta_pooled / se_pooled
p_pooled = 2 * (1 - sp_stats.norm.cdf(np.abs(z_stat)))

# ── Report results ────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("COMBINED MODEL — MULTIPLE IMPUTATION (Rubin's Rules)")
print(f"M={M_actual}, mean N={np.mean(ns_list):.0f}, mean events={np.mean(events_list):.0f}")
print("=" * 70)

results = {}
for i, var in enumerate(exposures):
    fmi = float(r_var[i] / (1 + r_var[i]))
    print(f"  {var:25s}: HR {hr_pooled[i]:.3f} "
          f"({ci_lo[i]:.3f}-{ci_hi[i]:.3f}), p={p_pooled[i]:.4f}, FMI={fmi:.3f}")
    results[var] = {
        "HR": round(float(hr_pooled[i]), 3),
        "CI_lower": round(float(ci_lo[i]), 3),
        "CI_upper": round(float(ci_hi[i]), 3),
        "p": round(float(p_pooled[i]), 4),
        "beta": round(float(beta_pooled[i]), 4),
        "SE": round(float(se_pooled[i]), 4),
        "FMI": round(fmi, 3),
    }

# ── Complete-case comparison ──────────────────────────────────────────
print("\n" + "=" * 70)
print("COMPLETE-CASE COMPARISON")
print("=" * 70)

df["low_income"] = np.nan
valid_inc = hh_income_clean.notna()
df.loc[valid_inc, "low_income"] = (hh_income_clean[valid_inc] <= income_q20).astype(float)

df["low_assets"] = np.nan
valid_assets = df["p_net_assets"].notna()
df.loc[valid_assets, "low_assets"] = (
    df.loc[valid_assets, "p_net_assets"] <= assets_q20
).astype(float)

cc_model_vars = ["surv_time", "died"] + exposures + demo_covs + analysis_health_covs
cc_df = df[cc_model_vars].dropna()
print(f"  Complete-case N: {len(cc_df)}, events: {int(cc_df['died'].sum())}")

cph_cc = CoxPHFitter()
cph_cc.fit(cc_df, duration_col="surv_time", event_col="died")

cc_results = {}
for var in exposures:
    hr = np.exp(cph_cc.params_[var])
    ci = np.exp(cph_cc.confidence_intervals_.loc[var].values)
    p = cph_cc.summary.loc[var, "p"]
    print(f"  {var:25s}: HR {hr:.3f} ({ci[0]:.3f}-{ci[1]:.3f}), p={p:.4f}")
    cc_results[var] = {
        "HR": round(float(hr), 3),
        "CI_lower": round(float(ci[0]), 3),
        "CI_upper": round(float(ci[1]), 3),
        "p": round(float(p), 4),
    }

# ── Save ──────────────────────────────────────────────────────────────
output = {
    "description": "Multiple imputation for combined model (Panel C)",
    "M": M_actual,
    "mean_N": round(float(np.mean(ns_list))),
    "mean_events": round(float(np.mean(events_list))),
    "MI_results": results,
    "complete_case_N": len(cc_df),
    "complete_case_events": int(cc_df["died"].sum()),
    "complete_case_results": cc_results,
}

out_path = os.path.join(OUT, "supplementary", "multiple_imputation_results.json")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nResults saved to {out_path}")
