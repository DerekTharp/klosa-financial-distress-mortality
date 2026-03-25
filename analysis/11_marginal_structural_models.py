"""
11_marginal_structural_models.py
Marginal structural models with stabilised IPTW for time-varying exposures.

Implementation:
  - Denominator model uses lagged confounders (L_{t-1})
  - Combined model uses joint sequential treatment probability
  - Bootstrap CIs (1000 iterations, person-level resampling)
  - Full weight diagnostics: percentiles, ESS, covariate balance
"""

import os
import json
import warnings
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
from sklearn.linear_model import LogisticRegression
from config import BASE, OUT
from model_specs import *

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", message=".*delta_grad.*")  # scipy L-BFGS noise
np.random.seed(42)

# ── Load data ──────────────────────────────────────────────────────────
pp = pd.read_parquet(os.path.join(OUT, "person_period_data.parquet")).copy()
print(f"Person-period data: {len(pp)} intervals, {pp['pid'].nunique()} individuals")

# ── Prepare variables ──────────────────────────────────────────────────
pp["hh_income_clean"] = pp["hh_income"].copy()
pp.loc[pp["hh_income_clean"] <= 0, "hh_income_clean"] = np.nan

# Wave-specific income quintiles
pp["low_income_tv"] = np.nan
for wave in pp["wave"].unique():
    mask = pp["wave"] == wave
    q20 = pp.loc[mask, "hh_income_clean"].quantile(0.20)
    valid = mask & pp["hh_income_clean"].notna()
    pp.loc[valid, "low_income_tv"] = (pp.loc[valid, "hh_income_clean"] <= q20).astype(float)

# Sort by person and wave
pp = pp.sort_values(["pid", "wave"]).reset_index(drop=True)

# Baseline (time-invariant) covariates
baseline_covs = ["female", "edu_middle", "edu_high", "edu_college"]

# Time-varying confounders
tv_confounders = ["self_rated_health", "chronic_count", "depression", "iadl",
                  "age_10", "married", "current_smoker", "bmi"]

# Create LAGGED versions of exposures and confounders
for var in ["low_econ_sat", "low_income_tv"] + tv_confounders:
    pp[f"{var}_lag"] = pp.groupby("pid")[var].shift(1)

print("Lagged variables created.")


# ── Helper functions ───────────────────────────────────────────────────

def compute_stabilised_weights(data, exposure, baseline_covs, tv_confounders,
                                truncate_pct=(1, 99)):
    """
    Compute stabilised IPTW using LAGGED confounders in the denominator.

    Numerator:   P(A_t=a_t | A_{t-1}, V)
    Denominator: P(A_t=a_t | A_{t-1}, V, L_{t-1})

    where V = baseline covariates, L_{t-1} = lagged time-varying confounders.
    Wave 1 (no lag): weight = 1.
    """
    df = data.copy()
    exposure_lag = f"{exposure}_lag"
    lagged_tv = [f"{v}_lag" for v in tv_confounders]

    # Numerator predictors: lagged exposure + baseline
    num_preds = [exposure_lag] + baseline_covs

    # Denominator predictors: lagged exposure + baseline + LAGGED TV confounders
    den_preds = [exposure_lag] + baseline_covs + lagged_tv

    # Fit on rows where lag is available (wave >= 2) and all predictors present
    wave1_mask = df[exposure_lag].isna()
    fit_mask = ~wave1_mask & df[exposure].notna()
    for v in den_preds:
        if v in df.columns:
            fit_mask &= df[v].notna()

    fit_df = df[fit_mask].copy()
    y = fit_df[exposure].values

    if len(fit_df) < 100:
        print(f"  WARNING: Only {len(fit_df)} rows for weight model")
        df["sw"] = 1.0
        return df["sw"].values

    # Numerator model
    X_num = fit_df[[v for v in num_preds if v in fit_df.columns]].values
    lr_num = LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs")
    lr_num.fit(X_num, y)
    p_num = lr_num.predict_proba(X_num)[:, 1]

    # Denominator model (with LAGGED confounders)
    X_den = fit_df[[v for v in den_preds if v in fit_df.columns]].values
    lr_den = LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs")
    lr_den.fit(X_den, y)
    p_den = lr_den.predict_proba(X_den)[:, 1]

    # Per-interval weight contribution
    a = fit_df[exposure].values
    contrib_num = np.where(a == 1, p_num, 1 - p_num)
    contrib_den = np.where(a == 1, p_den, 1 - p_den)
    contrib_num = np.clip(contrib_num, 0.005, 0.995)
    contrib_den = np.clip(contrib_den, 0.005, 0.995)

    per_interval = contrib_num / contrib_den

    # Assign and cumulate
    df["_sw_interval"] = 1.0
    df.loc[fit_mask, "_sw_interval"] = per_interval
    df["sw"] = df.groupby("pid")["_sw_interval"].cumprod()

    # Truncate
    lo, hi = np.percentile(df["sw"].dropna(), truncate_pct)
    df["sw"] = df["sw"].clip(lo, hi)

    return df["sw"].values


def compute_joint_weights(data, exp1, exp2, baseline_covs, tv_confounders,
                           truncate_pct=(1, 99)):
    """
    Joint IPTW for two exposures using sequential factorisation:
    P(A1, A2 | history) = P(A1 | history) * P(A2 | A1, history)

    Both use LAGGED confounders.
    """
    df = data.copy()
    exp1_lag = f"{exp1}_lag"
    exp2_lag = f"{exp2}_lag"
    lagged_tv = [f"{v}_lag" for v in tv_confounders]

    wave1_mask = df[exp1_lag].isna() | df[exp2_lag].isna()
    fit_mask = ~wave1_mask & df[exp1].notna() & df[exp2].notna()
    for v in lagged_tv + baseline_covs:
        if v in df.columns:
            fit_mask &= df[v].notna()

    fit_df = df[fit_mask].copy()

    # ── Factor 1: P(A1 | lag(A1), lag(A2), V, lag(L)) ──
    num1_preds = [exp1_lag, exp2_lag] + baseline_covs
    den1_preds = [exp1_lag, exp2_lag] + baseline_covs + lagged_tv

    X_num1 = fit_df[[v for v in num1_preds if v in fit_df.columns]].values
    X_den1 = fit_df[[v for v in den1_preds if v in fit_df.columns]].values
    y1 = fit_df[exp1].values

    lr_num1 = LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs")
    lr_num1.fit(X_num1, y1)
    p_num1 = lr_num1.predict_proba(X_num1)[:, 1]

    lr_den1 = LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs")
    lr_den1.fit(X_den1, y1)
    p_den1 = lr_den1.predict_proba(X_den1)[:, 1]

    # ── Factor 2: P(A2 | A1, lag(A1), lag(A2), V, lag(L)) ──
    num2_preds = [exp1, exp1_lag, exp2_lag] + baseline_covs
    den2_preds = [exp1, exp1_lag, exp2_lag] + baseline_covs + lagged_tv

    X_num2 = fit_df[[v for v in num2_preds if v in fit_df.columns]].values
    X_den2 = fit_df[[v for v in den2_preds if v in fit_df.columns]].values
    y2 = fit_df[exp2].values

    lr_num2 = LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs")
    lr_num2.fit(X_num2, y2)
    p_num2 = lr_num2.predict_proba(X_num2)[:, 1]

    lr_den2 = LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs")
    lr_den2.fit(X_den2, y2)
    p_den2 = lr_den2.predict_proba(X_den2)[:, 1]

    # Joint per-interval weight
    a1 = fit_df[exp1].values
    a2 = fit_df[exp2].values

    cn1 = np.clip(np.where(a1 == 1, p_num1, 1 - p_num1), 0.005, 0.995)
    cd1 = np.clip(np.where(a1 == 1, p_den1, 1 - p_den1), 0.005, 0.995)
    cn2 = np.clip(np.where(a2 == 1, p_num2, 1 - p_num2), 0.005, 0.995)
    cd2 = np.clip(np.where(a2 == 1, p_den2, 1 - p_den2), 0.005, 0.995)

    per_interval = (cn1 / cd1) * (cn2 / cd2)

    df["_jw_interval"] = 1.0
    df.loc[fit_mask, "_jw_interval"] = per_interval
    df["jw"] = df.groupby("pid")["_jw_interval"].cumprod()

    lo, hi = np.percentile(df["jw"].dropna(), truncate_pct)
    df["jw"] = df["jw"].clip(lo, hi)

    return df["jw"].values


def weight_diagnostics(weights, label):
    """Report weight distribution diagnostics."""
    w = weights[~np.isnan(weights)]
    ess = (w.sum() ** 2) / (w ** 2).sum()
    pcts = np.percentile(w, [1, 5, 25, 50, 75, 95, 99])
    diag = {
        "mean": round(float(w.mean()), 4),
        "sd": round(float(w.std()), 4),
        "min": round(float(w.min()), 4),
        "max": round(float(w.max()), 4),
        "P1": round(float(pcts[0]), 4),
        "P5": round(float(pcts[1]), 4),
        "P25": round(float(pcts[2]), 4),
        "P50": round(float(pcts[3]), 4),
        "P75": round(float(pcts[4]), 4),
        "P95": round(float(pcts[5]), 4),
        "P99": round(float(pcts[6]), 4),
        "ESS": round(float(ess)),
        "N": len(w),
    }
    print(f"\n  Weight diagnostics ({label}):")
    print(f"    Mean={diag['mean']:.3f}, SD={diag['sd']:.3f}, "
          f"Range=[{diag['min']:.3f}, {diag['max']:.3f}]")
    print(f"    P1={diag['P1']:.3f}, P5={diag['P5']:.3f}, P50={diag['P50']:.3f}, "
          f"P95={diag['P95']:.3f}, P99={diag['P99']:.3f}")
    print(f"    ESS={diag['ESS']} / N={diag['N']} "
          f"({diag['ESS']/diag['N']*100:.1f}%)")
    return diag


def bootstrap_cox_msm(data, exposures, weight_col, n_boot=200,
                       duration="t_stop", event="event", entry="t_start"):
    """
    Bootstrap CIs for weighted Cox model.
    Resamples PERSONS (not intervals) to preserve within-person correlation.
    """
    pids = data["pid"].unique()
    n_pids = len(pids)

    boot_betas = []
    for b in range(n_boot):
        # Resample persons with replacement
        boot_pids = np.random.choice(pids, size=n_pids, replace=True)
        # Reconstruct dataset (handling duplicate pids)
        boot_frames = []
        for i, pid in enumerate(boot_pids):
            chunk = data[data["pid"] == pid].copy()
            chunk["_boot_pid"] = i  # unique ID for duplicated persons
            boot_frames.append(chunk)
        boot_df = pd.concat(boot_frames, ignore_index=True)

        model_vars = [duration, event, entry, weight_col] + exposures
        model_df = boot_df[model_vars].dropna()

        if len(model_df) < 100 or model_df[event].sum() < 20:
            continue

        try:
            cph = CoxPHFitter(penalizer=0.001)
            cph.fit(model_df, duration_col=duration, event_col=event,
                    entry_col=entry, weights_col=weight_col)
            betas = [float(cph.params_[e]) for e in exposures]
            boot_betas.append(betas)
        except Exception:
            continue

    if len(boot_betas) < 50:
        print(f"  WARNING: Only {len(boot_betas)} successful bootstraps")

    boot_arr = np.array(boot_betas)
    return boot_arr


def covariate_balance(data, exposure, weight_col, covariates):
    """
    Compute standardised mean differences (SMDs) before and after weighting.
    SMD = (mean_exposed - mean_unexposed) / pooled_SD
    """
    df = data.dropna(subset=[exposure, weight_col] + covariates).copy()
    exposed = df[exposure] == 1
    balance = []
    for cov in covariates:
        if cov not in df.columns:
            continue
        vals = df[cov].values.astype(float)
        w = df[weight_col].values

        # Unweighted SMD
        m1 = vals[exposed].mean()
        m0 = vals[~exposed].mean()
        s1 = vals[exposed].std()
        s0 = vals[~exposed].std()
        pooled_sd = np.sqrt((s1**2 + s0**2) / 2) if (s1 + s0) > 0 else 1.0
        smd_raw = (m1 - m0) / pooled_sd if pooled_sd > 0 else 0.0

        # Weighted SMD
        w_exp = w[exposed]
        w_unexp = w[~exposed]
        m1_w = np.average(vals[exposed], weights=w_exp)
        m0_w = np.average(vals[~exposed], weights=w_unexp)
        smd_weighted = (m1_w - m0_w) / pooled_sd if pooled_sd > 0 else 0.0

        balance.append({
            "covariate": cov,
            "SMD_unweighted": round(float(smd_raw), 4),
            "SMD_weighted": round(float(smd_weighted), 4),
            "reduction_pct": round((1 - abs(smd_weighted) / abs(smd_raw)) * 100, 1)
                            if abs(smd_raw) > 0.001 else 0.0,
        })

    balance_df = pd.DataFrame(balance)
    print(f"\n  Covariate balance ({exposure}):")
    print(f"    {'Covariate':25s} {'SMD raw':>10s} {'SMD weighted':>13s} {'Reduction':>10s}")
    for _, row in balance_df.iterrows():
        print(f"    {row['covariate']:25s} {row['SMD_unweighted']:>10.3f} "
              f"{row['SMD_weighted']:>13.3f} {row['reduction_pct']:>9.1f}%")
    print(f"    Mean |SMD| unweighted: {balance_df['SMD_unweighted'].abs().mean():.4f}")
    print(f"    Mean |SMD| weighted:   {balance_df['SMD_weighted'].abs().mean():.4f}")
    return balance


# ════════════════════════════════════════════════════════════════════════
# SEPARATE MSMs
# ════════════════════════════════════════════════════════════════════════
N_BOOT = 1000
results = {}

for exposure, label in [
    ("low_econ_sat", "Low economic satisfaction"),
    ("low_income_tv", "Low household income"),
]:
    print(f"\n{'=' * 70}")
    print(f"SEPARATE MSM: {label}")
    print("=" * 70)

    # Compute weights
    weights = compute_stabilised_weights(pp, exposure, baseline_covs, tv_confounders)
    pp[f"w_{exposure}"] = weights
    w_diag = weight_diagnostics(weights, label)

    # Covariate balance
    balance_covs = ["age_10", "female", "married", "edu_middle", "edu_high",
                    "edu_college", "self_rated_health", "chronic_count",
                    "current_smoker", "depression", "iadl", "bmi"]
    bal = covariate_balance(pp, exposure, f"w_{exposure}", balance_covs)

    # Prepare dataset
    analysis_vars = ["pid", "t_start", "t_stop", "event", exposure, f"w_{exposure}"]
    analysis_df = pp[analysis_vars].dropna()
    analysis_df = analysis_df.rename(columns={f"w_{exposure}": "weight"})

    print(f"  N intervals: {len(analysis_df)}, events: {int(analysis_df['event'].sum())}")

    # Point estimate (weighted Cox, no covariates — total effect)
    cph = CoxPHFitter(penalizer=0.001)
    model_df = analysis_df[["t_start", "t_stop", "event", exposure, "weight"]]
    cph.fit(model_df, duration_col="t_stop", event_col="event",
            entry_col="t_start", weights_col="weight")
    hr_point = float(np.exp(cph.params_[exposure]))

    # Bootstrap CIs
    print(f"  Running {N_BOOT} bootstrap iterations...")
    boot_betas = bootstrap_cox_msm(analysis_df, [exposure], "weight", n_boot=N_BOOT)
    boot_hrs = np.exp(boot_betas[:, 0])
    ci_lo = float(np.percentile(boot_hrs, 2.5))
    ci_hi = float(np.percentile(boot_hrs, 97.5))
    boot_se = float(boot_betas[:, 0].std())
    # P-value from bootstrap (proportion of bootstrap samples with opposite sign)
    beta_point = float(cph.params_[exposure])
    p_boot = float(2 * min(np.mean(boot_betas[:, 0] > 0), np.mean(boot_betas[:, 0] < 0)))
    if p_boot == 0:
        p_boot = 1.0 / len(boot_betas)  # conservative floor

    print(f"\n  Results:")
    print(f"    Point estimate: HR {hr_point:.3f}")
    print(f"    Bootstrap 95% CI: ({ci_lo:.3f}–{ci_hi:.3f})")
    print(f"    Bootstrap SE: {boot_se:.4f}")
    print(f"    Bootstrap p: {p_boot:.4f}")
    print(f"    N bootstraps: {len(boot_betas)}")

    # Standard adjusted for comparison
    adj_covs = ["age_10", "female", "married", "edu_middle", "edu_high",
                "edu_college", "self_rated_health", "chronic_count",
                "current_smoker", "depression", "iadl"]
    adj_vars = ["t_start", "t_stop", "event", exposure] + adj_covs
    adj_df = pp[adj_vars].dropna()
    cph_adj = CoxPHFitter()
    cph_adj.fit(adj_df, duration_col="t_stop", event_col="event", entry_col="t_start")
    hr_adj = float(np.exp(cph_adj.params_[exposure]))
    ci_adj = np.exp(cph_adj.confidence_intervals_.loc[exposure].values)
    p_adj = float(cph_adj.summary.loc[exposure, "p"])

    print(f"    Standard adjusted (direct effect): HR {hr_adj:.3f} "
          f"({ci_adj[0]:.3f}–{ci_adj[1]:.3f}), p={p_adj:.4f}")

    results[exposure] = {
        "label": label,
        "MSM_total_effect": {
            "HR": round(hr_point, 3),
            "CI_lower": round(ci_lo, 3),
            "CI_upper": round(ci_hi, 3),
            "bootstrap_SE": round(boot_se, 4),
            "bootstrap_p": round(p_boot, 4),
            "n_bootstraps": len(boot_betas),
        },
        "standard_adjusted_direct_effect": {
            "HR": round(hr_adj, 3),
            "CI_lower": round(float(ci_adj[0]), 3),
            "CI_upper": round(float(ci_adj[1]), 3),
            "p": round(p_adj, 4),
        },
        "weight_diagnostics": w_diag,
        "covariate_balance": bal,
    }

# ════════════════════════════════════════════════════════════════════════
# COMBINED MSM (joint treatment weights)
# ════════════════════════════════════════════════════════════════════════
print(f"\n{'=' * 70}")
print("COMBINED MSM (joint sequential weights)")
print("=" * 70)

joint_weights = compute_joint_weights(
    pp, "low_econ_sat", "low_income_tv", baseline_covs, tv_confounders
)
pp["w_joint"] = joint_weights
jw_diag = weight_diagnostics(joint_weights, "Joint (satisfaction + income)")

# Balance for joint weights (check balance for both exposures)
balance_covs_j = ["age_10", "female", "married", "edu_middle", "edu_high",
                  "edu_college", "self_rated_health", "chronic_count",
                  "current_smoker", "depression", "iadl", "bmi"]
bal_sat_joint = covariate_balance(pp, "low_econ_sat", "w_joint", balance_covs_j)
bal_inc_joint = covariate_balance(pp, "low_income_tv", "w_joint", balance_covs_j)

# Prepare dataset
both_exp = ["low_econ_sat", "low_income_tv"]
comb_vars = ["pid", "t_start", "t_stop", "event"] + both_exp + ["w_joint"]
comb_df = pp[comb_vars].dropna().rename(columns={"w_joint": "weight"})
print(f"  N intervals: {len(comb_df)}, events: {int(comb_df['event'].sum())}")

# Point estimate
cph_comb = CoxPHFitter(penalizer=0.001)
cph_comb.fit(
    comb_df[["t_start", "t_stop", "event"] + both_exp + ["weight"]],
    duration_col="t_stop", event_col="event",
    entry_col="t_start", weights_col="weight"
)

# Bootstrap CIs
print(f"  Running {N_BOOT} bootstrap iterations for combined model...")
boot_betas_comb = bootstrap_cox_msm(comb_df, both_exp, "weight", n_boot=N_BOOT)

combined_results = {}
for i, exp in enumerate(both_exp):
    hr_point = float(np.exp(cph_comb.params_[exp]))
    boot_hrs = np.exp(boot_betas_comb[:, i])
    ci_lo = float(np.percentile(boot_hrs, 2.5))
    ci_hi = float(np.percentile(boot_hrs, 97.5))
    boot_se = float(boot_betas_comb[:, i].std())
    beta_pt = float(cph_comb.params_[exp])
    p_boot = float(2 * min(np.mean(boot_betas_comb[:, i] > 0),
                           np.mean(boot_betas_comb[:, i] < 0)))
    if p_boot == 0:
        p_boot = 1.0 / len(boot_betas_comb)

    # Standard adjusted comparison
    adj_vars2 = ["t_start", "t_stop", "event"] + both_exp + adj_covs
    adj_df2 = pp[adj_vars2].dropna()
    cph_adj2 = CoxPHFitter()
    cph_adj2.fit(adj_df2, duration_col="t_stop", event_col="event", entry_col="t_start")
    hr_adj2 = float(np.exp(cph_adj2.params_[exp]))
    ci_adj2 = np.exp(cph_adj2.confidence_intervals_.loc[exp].values)
    p_adj2 = float(cph_adj2.summary.loc[exp, "p"])

    print(f"\n  {exp}:")
    print(f"    MSM (total effect):        HR {hr_point:.3f} ({ci_lo:.3f}–{ci_hi:.3f}), "
          f"bootstrap p={p_boot:.4f}")
    print(f"    Standard adj (direct eff): HR {hr_adj2:.3f} ({ci_adj2[0]:.3f}–{ci_adj2[1]:.3f}), "
          f"p={p_adj2:.4f}")

    combined_results[exp] = {
        "MSM_total_effect": {
            "HR": round(hr_point, 3),
            "CI_lower": round(ci_lo, 3),
            "CI_upper": round(ci_hi, 3),
            "bootstrap_SE": round(boot_se, 4),
            "bootstrap_p": round(p_boot, 4),
            "n_bootstraps": len(boot_betas_comb),
        },
        "standard_adjusted_direct_effect": {
            "HR": round(hr_adj2, 3),
            "CI_lower": round(float(ci_adj2[0]), 3),
            "CI_upper": round(float(ci_adj2[1]), 3),
            "p": round(p_adj2, 4),
        },
    }

# ── Save ──────────────────────────────────────────────────────────────
output = {
    "description": "Marginal structural models with stabilised IPTW",
    "implementation": [
        "Denominator uses lagged confounders (L_{t-1})",
        "Combined model uses sequential joint weights",
        "Bootstrap CIs (1000 iterations, person-level resampling)",
        "Full weight diagnostics reported",
    ],
    "notes": {
        "MSM_estimand": "Total effect (all pathways including through depression/IADL)",
        "standard_estimand": "Controlled direct effect (blocking depression/IADL pathways)",
        "interpretation": "MSM and standard estimates answer different causal questions and are complementary, not contradictory",
    },
    "separate_models": {k: v for k, v in results.items() if k in ["low_econ_sat", "low_income_tv"]},
    "combined_model": combined_results,
    "joint_weight_diagnostics": jw_diag,
    "joint_covariate_balance_satisfaction": bal_sat_joint,
    "joint_covariate_balance_income": bal_inc_joint,
    "n_bootstrap": N_BOOT,
}

out_path = os.path.join(OUT, "supplementary", "msm_results.json")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w") as f:
    json.dump(output, f, indent=2)
print(f"\nResults saved to {out_path}")
