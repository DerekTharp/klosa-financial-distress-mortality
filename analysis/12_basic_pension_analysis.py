"""
12_basic_pension_analysis.py
Exploratory analysis of the Basic Pension expansion (introduced 2008, expanded 2014)
examining whether associations changed after 2014.

Tests whether:
1. The satisfaction-mortality association differs before vs after 2014
2. The income-mortality association changed after pension expansion
3. Period interaction effects in the time-varying model
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from config import BASE, OUT
from model_specs import *

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*delta_grad.*")

# ── Load data ──────────────────────────────────────────────────────────
pp = pd.read_parquet(os.path.join(OUT, "person_period_data.parquet")).copy()
panel = pd.read_parquet(os.path.join(OUT, "panel_data.parquet"))

print(f"Person-period data: {len(pp)} intervals")

# ── Prepare variables ──────────────────────────────────────────────────
# Time-varying low income
pp["hh_income_clean"] = pp["hh_income"].copy()
pp.loc[pp["hh_income_clean"] <= 0, "hh_income_clean"] = np.nan
pp["low_income_tv"] = np.nan
for wave in pp["wave"].unique():
    mask = pp["wave"] == wave
    q20 = pp.loc[mask, "hh_income_clean"].quantile(0.20)
    valid = mask & pp["hh_income_clean"].notna()
    pp.loc[valid, "low_income_tv"] = (pp.loc[valid, "hh_income_clean"] <= q20).astype(float)

# Period indicator: post-2014 Basic Pension expansion
# Waves 1-4 (2006-2012) = pre-expansion; Waves 5-8 (2014-2022) = post-expansion
pp["post_2014"] = (pp["wave"] >= 5).astype(float)

# Age eligibility: Basic Pension targets adults aged 65+
pp["age_65plus"] = (pp["age"] >= 65).astype(float)

# Interaction terms
pp["lowsat_x_post"] = pp["low_econ_sat"] * pp["post_2014"]
pp["lowinc_x_post"] = pp["low_income_tv"] * pp["post_2014"]

# Covariates
demo_covs = ["age_10", "female", "married", "edu_middle", "edu_high", "edu_college"]
health_covs = ["self_rated_health", "chronic_count", "current_smoker"]
full_covs = demo_covs + health_covs + ["depression", "iadl"]

# Wave-year mapping for display
wave_years = {1: 2006, 2: 2008, 3: 2010, 4: 2012, 5: 2014, 6: 2016, 7: 2018, 8: 2020}

# ════════════════════════════════════════════════════════════════════════
# 1. PERIOD-STRATIFIED MODELS
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("1. PERIOD-STRATIFIED MODELS (pre vs post 2014)")
print("=" * 70)

period_results = {}
for period_name, wave_range in [("Pre-2014 (waves 1-4)", [1, 2, 3, 4]),
                                 ("Post-2014 (waves 5-8)", [5, 6, 7, 8])]:
    period_df = pp[pp["wave"].isin(wave_range)].copy()

    for exposure, label in [("low_econ_sat", "Low satisfaction"),
                            ("low_income_tv", "Low income")]:
        model_vars = ["t_start", "t_stop", "event", exposure] + full_covs
        model_df = period_df[model_vars].dropna()

        cph = CoxPHFitter()
        cph.fit(model_df, duration_col="t_stop", event_col="event",
                entry_col="t_start")

        hr = np.exp(cph.params_[exposure])
        ci = np.exp(cph.confidence_intervals_.loc[exposure].values)
        p = cph.summary.loc[exposure, "p"]

        key = f"{exposure}_{period_name[:8]}"
        period_results[key] = {
            "period": period_name,
            "exposure": label,
            "N_intervals": len(model_df),
            "events": int(model_df["event"].sum()),
            "HR": round(float(hr), 3),
            "CI_lower": round(float(ci[0]), 3),
            "CI_upper": round(float(ci[1]), 3),
            "p": round(float(p), 4),
        }

        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"  {period_name}: {label:20s} HR {hr:.3f} ({ci[0]:.3f}-{ci[1]:.3f}), "
              f"p={p:.4f}{sig}  [{len(model_df)} intervals, {int(model_df['event'].sum())} events]")

# ════════════════════════════════════════════════════════════════════════
# 2. INTERACTION MODELS (formal test)
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("2. PERIOD INTERACTION MODELS")
print("=" * 70)

interaction_results = {}
for exposure, interaction, label in [
    ("low_econ_sat", "lowsat_x_post", "Satisfaction × post-2014"),
    ("low_income_tv", "lowinc_x_post", "Income × post-2014"),
]:
    model_vars = (
        ["t_start", "t_stop", "event", exposure, "post_2014", interaction]
        + full_covs
    )
    model_df = pp[model_vars].dropna()

    cph = CoxPHFitter()
    cph.fit(model_df, duration_col="t_stop", event_col="event",
            entry_col="t_start")

    # Main effect
    hr_main = np.exp(cph.params_[exposure])
    p_main = cph.summary.loc[exposure, "p"]

    # Interaction
    hr_int = np.exp(cph.params_[interaction])
    ci_int = np.exp(cph.confidence_intervals_.loc[interaction].values)
    p_int = cph.summary.loc[interaction, "p"]

    # Period
    hr_period = np.exp(cph.params_["post_2014"])
    p_period = cph.summary.loc["post_2014", "p"]

    print(f"\n  {label}:")
    print(f"    Main effect ({exposure}):  HR {hr_main:.3f}, p={p_main:.4f}")
    print(f"    Period (post_2014):         HR {hr_period:.3f}, p={p_period:.4f}")
    print(f"    Interaction:                HR {hr_int:.3f} ({ci_int[0]:.3f}-{ci_int[1]:.3f}), p={p_int:.4f}")

    # Compute period-specific effects
    # Pre-2014 effect = main effect
    # Post-2014 effect = main effect * interaction (on HR scale, or sum on log scale)
    beta_main = cph.params_[exposure]
    beta_int = cph.params_[interaction]
    se_main = cph.standard_errors_[exposure]
    se_int = cph.standard_errors_[interaction]
    cov_main_int = cph.variance_matrix_.loc[exposure, interaction]

    beta_post = beta_main + beta_int
    se_post = np.sqrt(se_main**2 + se_int**2 + 2 * cov_main_int)
    hr_post = np.exp(beta_post)
    ci_post_lo = np.exp(beta_post - 1.96 * se_post)
    ci_post_hi = np.exp(beta_post + 1.96 * se_post)
    p_post = 2 * (1 - __import__("scipy").stats.norm.cdf(abs(beta_post / se_post)))

    print(f"    Pre-2014 effect:  HR {hr_main:.3f}")
    print(f"    Post-2014 effect: HR {hr_post:.3f} ({ci_post_lo:.3f}-{ci_post_hi:.3f}), p={p_post:.4f}")

    interaction_results[exposure] = {
        "label": label,
        "main_effect_HR": round(float(hr_main), 3),
        "main_effect_p": round(float(p_main), 4),
        "interaction_HR": round(float(hr_int), 3),
        "interaction_CI_lower": round(float(ci_int[0]), 3),
        "interaction_CI_upper": round(float(ci_int[1]), 3),
        "interaction_p": round(float(p_int), 4),
        "pre_2014_HR": round(float(hr_main), 3),
        "post_2014_HR": round(float(hr_post), 3),
        "post_2014_CI_lower": round(float(ci_post_lo), 3),
        "post_2014_CI_upper": round(float(ci_post_hi), 3),
        "post_2014_p": round(float(p_post), 4),
    }

# ════════════════════════════════════════════════════════════════════════
# 3. AGE-RESTRICTED ANALYSIS (65+ only, pension-eligible)
# ════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("3. AGE 65+ ONLY (pension-eligible population)")
print("=" * 70)

elderly = pp[pp["age"] >= 65].copy()
print(f"  Elderly subsample: {len(elderly)} intervals, "
      f"{elderly['pid'].nunique()} individuals, "
      f"{int(elderly['event'].sum())} events")

age65_results = {}
for period_name, wave_range in [("Pre-2014", [1, 2, 3, 4]),
                                 ("Post-2014", [5, 6, 7, 8])]:
    period_df = elderly[elderly["wave"].isin(wave_range)]

    for exposure, label in [("low_econ_sat", "Low satisfaction"),
                            ("low_income_tv", "Low income")]:
        model_vars = ["t_start", "t_stop", "event", exposure] + full_covs
        model_df = period_df[model_vars].dropna()

        if len(model_df) < 100 or model_df["event"].sum() < 20:
            print(f"  {period_name}: {label:20s} — insufficient data")
            continue

        cph = CoxPHFitter()
        cph.fit(model_df, duration_col="t_stop", event_col="event",
                entry_col="t_start")

        hr = np.exp(cph.params_[exposure])
        ci = np.exp(cph.confidence_intervals_.loc[exposure].values)
        p = cph.summary.loc[exposure, "p"]

        key = f"{exposure}_{period_name[:8]}_65plus"
        age65_results[key] = {
            "period": period_name,
            "exposure": label,
            "N_intervals": len(model_df),
            "events": int(model_df["event"].sum()),
            "HR": round(float(hr), 3),
            "CI_lower": round(float(ci[0]), 3),
            "CI_upper": round(float(ci[1]), 3),
            "p": round(float(p), 4),
        }

        sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        print(f"  {period_name}: {label:20s} HR {hr:.3f} ({ci[0]:.3f}-{ci[1]:.3f}), "
              f"p={p:.4f}{sig}  [{len(model_df)} intervals, {int(model_df['event'].sum())} events]")

# ── Save ──────────────────────────────────────────────────────────────
output = {
    "description": "Basic Pension expansion analysis (pre vs post 2014)",
    "period_stratified": period_results,
    "interaction_models": interaction_results,
    "age_65plus_stratified": age65_results,
}

out_path = os.path.join(OUT, "supplementary", "basic_pension_analysis.json")
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nResults saved to {out_path}")
