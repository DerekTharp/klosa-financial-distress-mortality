"""
07_extended_sensitivity.py
Extended Sensitivity and Supplementary Analyses

Construct validity of economic satisfaction measure, extended Cox models
with additional covariates (income, alcohol, exercise, continuous CES-D),
proportional hazards diagnostics, regularisation sensitivity, measurement
reliability (ICC), differential attrition analysis, post-hoc power analysis,
refreshment sample sensitivity, healthy-at-baseline restriction, robust
standard errors, and dose-response analysis.
"""

import pandas as pd
import numpy as np
import os
import logging
import warnings
import json
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', message='.*delta_grad.*')  # scipy L-BFGS noise
logging.basicConfig(level=logging.INFO)
_log = logging.getLogger(__name__)
# Log convergence warnings instead of suppressing them
_orig_showwarning = warnings.showwarning
def _log_convergence_warnings(message, category, filename, lineno, file=None, line=None):
    if 'convergence' in str(message).lower():
        _log.warning("ConvergenceWarning in %s:%d: %s", filename, lineno, message)
    else:
        _orig_showwarning(message, category, filename, lineno, file, line)
warnings.showwarning = _log_convergence_warnings

from lifelines import CoxPHFitter
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from config import BASE, OUT
from model_specs import *

FIG = os.path.join(OUT, "figures")
TAB = os.path.join(OUT, "tables")
SUPP = os.path.join(OUT, "supplementary")
os.makedirs(SUPP, exist_ok=True)

# ============================================================================
# LOAD DATA
# ============================================================================
print("Loading data...")
baseline = pd.read_parquet(os.path.join(OUT, 'baseline_analytic.parquet'))
panel = pd.read_parquet(os.path.join(OUT, 'panel_data.parquet'))
pp = pd.read_parquet(os.path.join(OUT, 'person_period_data.parquet'))
deaths = pd.read_parquet(os.path.join(OUT, 'death_records.parquet'))

print(f"Baseline: N={len(baseline):,}")
print(f"Panel: {len(panel):,} person-waves")
print(f"Person-period: {len(pp):,} intervals")

# ============================================================================
# PREPARE VARIABLES
# ============================================================================

# --- Continuous CES-D-10 score ---
print("\n--- Computing Continuous CES-D-10 Score ---")
cesd_neg = ['cesd_142', 'cesd_143', 'cesd_144', 'cesd_145',
            'cesd_147', 'cesd_148', 'cesd_150', 'cesd_151']
cesd_pos = ['cesd_146', 'cesd_149']  # hopeful, happy -> reverse code

def compute_cesd_score(df):
    """Compute CES-D-10 continuous score (0-30). Higher = more depressed."""
    score = pd.Series(np.nan, index=df.index)
    for col in cesd_neg:
        if col in df.columns:
            score = score.add(df[col] - 1, fill_value=0)  # recode 1-4 to 0-3
    for col in cesd_pos:
        if col in df.columns:
            score = score.add(4 - df[col], fill_value=0)  # reverse: 1->3, 2->2, 3->1, 4->0
    # Set to NaN if any item missing
    all_cesd = cesd_neg + cesd_pos
    available = [c for c in all_cesd if c in df.columns]
    any_missing = df[available].isna().any(axis=1)
    score[any_missing] = np.nan
    return score

baseline['cesd_score'] = compute_cesd_score(baseline)
panel['cesd_score'] = compute_cesd_score(panel)

print(f"  Baseline CES-D score: mean={baseline['cesd_score'].mean():.2f}, "
      f"SD={baseline['cesd_score'].std():.2f}, range={baseline['cesd_score'].min():.0f}-{baseline['cesd_score'].max():.0f}")
print(f"  Coverage: {baseline['cesd_score'].notna().mean()*100:.1f}%")
print(f"  Correlation with binary depression: r={baseline['cesd_score'].corr(baseline['depression']):.3f}")

# --- Drinking and exercise variables ---
print("\n--- Preparing Drinking and Exercise Variables ---")
# Drinking: 1=currently drinking, 2=former drinker, 3=never drank
# NOT available at wave 1 -> use wave 2 data for baseline models
# Exercise: 1=yes, 5=no

baseline['regular_exercise'] = (baseline['exercise'] == 1).astype(float)
baseline.loc[baseline['exercise'].isna(), 'regular_exercise'] = np.nan

# Get wave 2 drinking data for baseline models
wave2_drinking = panel.loc[panel['wave'] == 2, ['pid', 'drinking']].copy()
wave2_drinking['current_drinker'] = (wave2_drinking['drinking'] == 1).astype(float)
wave2_drinking = wave2_drinking[['pid', 'current_drinker']].dropna()
baseline = baseline.merge(wave2_drinking, on='pid', how='left')

print(f"  Regular exercise at baseline: {baseline['regular_exercise'].mean()*100:.1f}%")
print(f"  Current drinker (from wave 2): {baseline['current_drinker'].mean()*100:.1f}% "
      f"(coverage: {baseline['current_drinker'].notna().mean()*100:.1f}%)")

# --- Household income (log-transformed) ---
print("\n--- Preparing Household Income ---")
# Clean: -9 is missing code
baseline.loc[baseline['hh_income'] <= 0, 'hh_income_clean'] = np.nan
baseline.loc[baseline['hh_income'] > 0, 'hh_income_clean'] = baseline.loc[baseline['hh_income'] > 0, 'hh_income']
baseline['log_hh_income'] = np.log1p(baseline['hh_income_clean'])

print(f"  HH income: mean={baseline['hh_income_clean'].mean():.0f} (10K won), "
      f"median={baseline['hh_income_clean'].median():.0f}")
print(f"  Log income coverage: {baseline['log_hh_income'].notna().mean()*100:.1f}%")

# --- Prepare regression variables (same as 03_cox_models.py) ---
baseline['age_10'] = baseline['age'] / 10
baseline['edu_middle'] = (baseline['education'] == 2).astype(float)
baseline['edu_high'] = (baseline['education'] == 3).astype(float)
baseline['edu_college'] = (baseline['education'] >= 4).astype(float)
baseline['low_econ_sat_bl'] = (baseline['econ_sat_quintile'] == 'Q1 (lowest)').astype(float)
baseline['econ_sat_decrease_10'] = (100 - baseline['econ_satisfaction']) / 10

demo_covs = ['age_10', 'female', 'married', 'edu_middle', 'edu_high', 'edu_college']
health_covs_orig = ['self_rated_health', 'chronic_count', 'bmi', 'current_smoker', 'ever_smoker']
health_covs_new = ['self_rated_health', 'chronic_count', 'bmi', 'current_smoker', 'ever_smoker',
                   'current_drinker', 'regular_exercise']
full_covs_orig = demo_covs + health_covs_orig + ['depression', 'iadl']

all_results = {}

# ============================================================================
# CONSTRUCT VALIDITY ANALYSIS
# ============================================================================
print("\n" + "=" * 70)
print("CONSTRUCT VALIDITY OF ECONOMIC SATISFACTION")
print("=" * 70)

validity = {}

# Pearson r with continuous variables
for var, label in [('hh_income_clean', 'Household income'),
                   ('hh_net_worth', 'Household net worth'),
                   ('p_net_assets', 'Personal net assets'),
                   ('cesd_score', 'CES-D-10 score')]:
    valid = baseline[['econ_satisfaction', var]].dropna()
    if len(valid) > 30:
        r, p = stats.pearsonr(valid['econ_satisfaction'], valid[var])
        print(f"  r(econ satisfaction, {label}) = {r:.3f}, p={p:.4f}, N={len(valid):,}")
        validity[label] = {'r': round(r, 3), 'p': round(p, 4), 'N': len(valid)}

# Point-biserial r with binary variables
for var, label in [('on_welfare_bl', 'Welfare receipt (NBLSS)'),
                   ('depression', 'Depression (binary CES-D)')]:
    valid = baseline[['econ_satisfaction', var]].dropna()
    if len(valid) > 30:
        r, p = stats.pointbiserialr(valid[var], valid['econ_satisfaction'])
        print(f"  r_pb(econ satisfaction, {label}) = {r:.3f}, p={p:.4f}, N={len(valid):,}")
        validity[label] = {'r': round(r, 3), 'p': round(p, 4), 'N': len(valid)}

# Self-rated health (ordinal, use Spearman)
valid = baseline[['econ_satisfaction', 'self_rated_health']].dropna()
rho, p = stats.spearmanr(valid['econ_satisfaction'], valid['self_rated_health'])
print(f"  rho(econ satisfaction, SRH) = {rho:.3f}, p={p:.4f}, N={len(valid):,}")
validity['Self-rated health (Spearman)'] = {'rho': round(rho, 3), 'p': round(p, 4), 'N': len(valid)}

all_results['construct_validity'] = validity

# ============================================================================
# EXTENDED COX MODELS WITH ADDITIONAL COVARIATES
# ============================================================================
print("\n" + "=" * 70)
print("EXTENDED COX MODELS WITH ADDITIONAL COVARIATES")
print("=" * 70)

df = baseline.copy()
revised_results = []

exposure = 'low_econ_sat_bl'

# Model specifications (sequential)
model_specs = [
    ('Model 1: Unadjusted', []),
    ('Model 2: Demographics', demo_covs),
    ('Model 2a: Demographics + Income', demo_covs + ['log_hh_income']),
    ('Model 3: + Health behaviors (original)', demo_covs + health_covs_orig),
    ('Model 3a: + Health behaviors (expanded)', demo_covs + health_covs_new),
    ('Model 3b: + Health + Income', demo_covs + health_covs_new + ['log_hh_income']),
    ('Model 4: Fully adjusted (original)', full_covs_orig),
    ('Model 4a: + Income + Drinking + Exercise', demo_covs + health_covs_new + ['depression', 'iadl', 'log_hh_income']),
    ('Model 4b: + Continuous CES-D (replaces binary)', demo_covs + health_covs_new + ['cesd_score', 'iadl', 'log_hh_income']),
]

print(f"\nExposure: Low economic satisfaction (Q1)")
for model_name, covs in model_specs:
    all_vars = [exposure] + covs
    model_df = df[['surv_time', 'died'] + all_vars].dropna()
    try:
        cph = CoxPHFitter()
        cph.fit(model_df, duration_col='surv_time', event_col='died')
        hr = np.exp(cph.params_[exposure])
        ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
        ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
        p = cph.summary['p'][exposure]
        print(f"  {model_name}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}, N={len(model_df):,}")
        revised_results.append({
            'Exposure': 'Low economic satisfaction (Q1)',
            'Model': model_name,
            'HR': round(hr, 3), 'CI_low': round(ci_low, 3), 'CI_high': round(ci_high, 3),
            'p': round(p, 4), 'N': len(model_df), 'Events': int(model_df['died'].sum())
        })

        # Print key covariate HRs for the most complete model
        if model_name == 'Model 4b: + Continuous CES-D (replaces binary)':
            print(f"\n  Full Model 4b coefficients:")
            for var in cph.summary.index:
                hr_v = np.exp(cph.summary.loc[var, 'coef'])
                ci_l = np.exp(cph.summary.loc[var, 'coef lower 95%'])
                ci_h = np.exp(cph.summary.loc[var, 'coef upper 95%'])
                p_v = cph.summary.loc[var, 'p']
                sig = '***' if p_v < 0.001 else '**' if p_v < 0.01 else '*' if p_v < 0.05 else ''
                print(f"    {var:25s}: HR={hr_v:.3f} ({ci_l:.3f}-{ci_h:.3f}) p={p_v:.4f} {sig}")
    except Exception as e:
        print(f"  {model_name}: Failed - {e}")

# Also run continuous exposure with income
print(f"\nExposure: Economic dissatisfaction (per 10-pt decrease)")
exposure2 = 'econ_sat_decrease_10'
for model_name, covs in [
    ('Model 2a: Demographics + Income', demo_covs + ['log_hh_income']),
    ('Model 3b: + Health + Income', demo_covs + health_covs_new + ['log_hh_income']),
    ('Model 4b: + Continuous CES-D', demo_covs + health_covs_new + ['cesd_score', 'iadl', 'log_hh_income']),
]:
    all_vars = [exposure2] + covs
    model_df = df[['surv_time', 'died'] + all_vars].dropna()
    try:
        cph = CoxPHFitter()
        cph.fit(model_df, duration_col='surv_time', event_col='died')
        hr = np.exp(cph.params_[exposure2])
        ci_low = np.exp(cph.confidence_intervals_.loc[exposure2].iloc[0])
        ci_high = np.exp(cph.confidence_intervals_.loc[exposure2].iloc[1])
        p = cph.summary['p'][exposure2]
        print(f"  {model_name}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}, N={len(model_df):,}")
        revised_results.append({
            'Exposure': 'Economic dissatisfaction (per 10-pt decrease)',
            'Model': model_name,
            'HR': round(hr, 3), 'CI_low': round(ci_low, 3), 'CI_high': round(ci_high, 3),
            'p': round(p, 4), 'N': len(model_df), 'Events': int(model_df['died'].sum())
        })
    except Exception as e:
        print(f"  {model_name}: Failed - {e}")

# Welfare receipt with income
print(f"\nExposure: Welfare receipt (NBLSS)")
exposure3 = 'on_welfare_bl'
for model_name, covs in [
    ('Model 2a: Demographics + Income', demo_covs + ['log_hh_income']),
    ('Model 4b: + Continuous CES-D', demo_covs + health_covs_new + ['cesd_score', 'iadl', 'log_hh_income']),
]:
    all_vars = [exposure3] + covs
    model_df = df[['surv_time', 'died'] + all_vars].dropna()
    try:
        cph = CoxPHFitter()
        cph.fit(model_df, duration_col='surv_time', event_col='died')
        hr = np.exp(cph.params_[exposure3])
        ci_low = np.exp(cph.confidence_intervals_.loc[exposure3].iloc[0])
        ci_high = np.exp(cph.confidence_intervals_.loc[exposure3].iloc[1])
        p = cph.summary['p'][exposure3]
        print(f"  {model_name}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}, N={len(model_df):,}")
        revised_results.append({
            'Exposure': 'Welfare receipt (NBLSS)',
            'Model': model_name,
            'HR': round(hr, 3), 'CI_low': round(ci_low, 3), 'CI_high': round(ci_high, 3),
            'p': round(p, 4), 'N': len(model_df), 'Events': int(model_df['died'].sum())
        })
    except Exception as e:
        print(f"  {model_name}: Failed - {e}")

all_results['extended_models'] = revised_results

# ============================================================================
# PROPORTIONAL HAZARDS DIAGNOSTICS
# ============================================================================
print("\n" + "=" * 70)
print("PROPORTIONAL HAZARDS DIAGNOSTICS")
print("=" * 70)

# Test PH for primary model (Model 3: demographics + health)
exposure = 'low_econ_sat_bl'
covs = demo_covs + health_covs_orig
model_df = df[['surv_time', 'died', exposure] + covs].dropna()

cph = CoxPHFitter()
cph.fit(model_df, duration_col='surv_time', event_col='died')

print("\nSchoenfeld residual test for Model 3 (health-adjusted):")
try:
    ph_results = cph.check_assumptions(model_df, p_value_threshold=0.05, show_plots=False)
    print("  PH assumption test completed.")
except Exception as e:
    print(f"  PH test output: {e}")

# Manual Schoenfeld test using lifelines
print("\n  Individual variable p-values (Schoenfeld):")
ph_summary = {}
try:
    from lifelines.statistics import proportional_hazard_test
    ph_test = proportional_hazard_test(cph, model_df, time_transform='rank')
    print(ph_test.summary)
    ph_summary = ph_test.summary.to_dict()
    # Save results
    ph_test.summary.to_csv(os.path.join(SUPP, 'ph_test_results.csv'))
except Exception as e:
    print(f"  Schoenfeld test failed: {e}")
    # Fallback: try with log time transform
    try:
        ph_test = proportional_hazard_test(cph, model_df, time_transform='log')
        print(ph_test.summary)
        ph_test.summary.to_csv(os.path.join(SUPP, 'ph_test_results.csv'))
    except Exception as e2:
        print(f"  Log transform also failed: {e2}")

# Time-partitioned models if PH violated
print("\n  Time-partitioned models (0-8 vs 8-16 years):")
for period_name, time_filter in [('0-8 years', (0, 8)), ('8-16 years', (8, 16))]:
    sub = model_df.copy()
    # Left-truncate and right-censor
    sub = sub[sub['surv_time'] > time_filter[0]]
    sub.loc[sub['surv_time'] > time_filter[1], 'died'] = 0
    sub.loc[sub['surv_time'] > time_filter[1], 'surv_time'] = time_filter[1]
    # Adjust time origin
    sub['surv_time'] = sub['surv_time'] - time_filter[0]
    sub = sub[sub['surv_time'] > 0]

    try:
        cph_period = CoxPHFitter()
        cph_period.fit(sub, duration_col='surv_time', event_col='died')
        hr = np.exp(cph_period.params_[exposure])
        ci_low = np.exp(cph_period.confidence_intervals_.loc[exposure].iloc[0])
        ci_high = np.exp(cph_period.confidence_intervals_.loc[exposure].iloc[1])
        p = cph_period.summary['p'][exposure]
        events = int(sub['died'].sum())
        print(f"  {period_name}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}, events={events}")
    except Exception as e:
        print(f"  {period_name}: Failed - {e}")

# ============================================================================
# REGULARISATION SENSITIVITY ANALYSIS
# ============================================================================
print("\n" + "=" * 70)
print("REGULARISATION SENSITIVITY ANALYSIS")
print("=" * 70)

# Prepare person-period covariates
pp['age_10'] = pp['age'] / 10
pp['edu_middle'] = (pp['education'] == 2).astype(float)
pp['edu_high'] = (pp['education'] == 3).astype(float)
pp['edu_college'] = (pp['education'] >= 4).astype(float)
pp['current_smoker'] = (pp['smoking'] == 2).astype(float)
pp['ever_smoker'] = np.where(pp['smoking'].isna(), np.nan,
                              (pp['smoking'] > 0).astype(float))

tv_demo = ['age_10', 'female', 'married', 'edu_middle', 'edu_high', 'edu_college']
tv_health = ['self_rated_health', 'chronic_count', 'bmi', 'current_smoker', 'ever_smoker']
tv_full = tv_demo + tv_health + ['depression', 'iadl']

tv_results = []

for exposure, exp_label in [('low_econ_sat', 'Low econ sat (time-varying)'),
                             ('hh_wealth_shock', 'HH wealth shock (time-varying)')]:
    print(f"\n  Exposure: {exp_label}")
    all_vars = [exposure] + tv_full
    model_df = pp[['t_start', 't_stop', 'event'] + all_vars].dropna()

    if model_df[exposure].sum() < 10:
        print(f"    Insufficient exposed observations")
        continue

    for pen_val, pen_label in [(0.0, 'Unpenalised'), (0.01, 'Penalised (0.01)')]:
        try:
            cph = CoxPHFitter(penalizer=pen_val)
            cph.fit(model_df, duration_col='t_stop', event_col='event', entry_col='t_start')
            hr = np.exp(cph.params_[exposure])
            ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
            ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
            p = cph.summary['p'][exposure]
            print(f"    {pen_label}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")
            tv_results.append({
                'Exposure': exp_label, 'Penalizer': pen_label,
                'HR': round(hr, 3), 'CI_low': round(ci_low, 3), 'CI_high': round(ci_high, 3),
                'p': round(p, 4), 'N': len(model_df), 'Events': int(model_df['event'].sum())
            })
        except Exception as e:
            print(f"    {pen_label}: Failed - {e}")
            # Try with small penalizer
            if pen_val == 0.0:
                try:
                    cph = CoxPHFitter(penalizer=0.001)
                    cph.fit(model_df, duration_col='t_stop', event_col='event', entry_col='t_start')
                    hr = np.exp(cph.params_[exposure])
                    ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
                    ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
                    p = cph.summary['p'][exposure]
                    print(f"    Penalised (0.001): HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")
                    tv_results.append({
                        'Exposure': exp_label, 'Penalizer': 'Smallest (0.001)',
                        'HR': round(hr, 3), 'CI_low': round(ci_low, 3), 'CI_high': round(ci_high, 3),
                        'p': round(p, 4), 'N': len(model_df), 'Events': int(model_df['event'].sum())
                    })
                except Exception as e2:
                    print(f"    Penalised (0.001) also failed: {e2}")

all_results['regularisation_sensitivity'] = tv_results

# ROBUST STANDARD ERRORS
print("\n--- Robust Standard Errors (time-varying) ---")
for exposure, exp_label in [('low_econ_sat', 'Low econ sat (time-varying)'),
                             ('hh_wealth_shock', 'HH wealth shock (time-varying)')]:
    all_vars = [exposure] + tv_full
    model_df = pp[['t_start', 't_stop', 'event', 'pid'] + all_vars].dropna()
    if model_df[exposure].sum() < 10:
        continue
    try:
        cph = CoxPHFitter(penalizer=0.01)
        cph.fit(model_df, duration_col='t_stop', event_col='event',
                entry_col='t_start', cluster_col='pid', robust=True)
        hr = np.exp(cph.params_[exposure])
        ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
        ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
        p = cph.summary['p'][exposure]
        print(f"  {exp_label} (robust SE, clustered by pid): HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")
    except Exception as e:
        print(f"  {exp_label} robust: Failed - {e}")
        # Try without cluster
        try:
            cph = CoxPHFitter(penalizer=0.01)
            cph.fit(model_df.drop(columns=['pid']), duration_col='t_stop',
                    event_col='event', entry_col='t_start', robust=True)
            hr = np.exp(cph.params_[exposure])
            ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
            ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
            p = cph.summary['p'][exposure]
            print(f"  {exp_label} (robust SE, no cluster): HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")
        except Exception as e2:
            print(f"  {exp_label} robust (no cluster): Failed - {e2}")

# ============================================================================
# MEASUREMENT RELIABILITY (ICC)
# ============================================================================
print("\n" + "=" * 70)
print("MEASUREMENT RELIABILITY (ICC) FOR ECONOMIC SATISFACTION")
print("=" * 70)

# Pearson correlation between adjacent waves
icc_results = {}
for w in range(1, 9):
    w1_data = panel.loc[panel['wave'] == w, ['pid', 'econ_satisfaction']].dropna()
    w2_data = panel.loc[panel['wave'] == w + 1, ['pid', 'econ_satisfaction']].dropna()
    merged = w1_data.merge(w2_data, on='pid', suffixes=(f'_w{w}', f'_w{w+1}'))
    if len(merged) > 30:
        r, p = stats.pearsonr(merged.iloc[:, 1], merged.iloc[:, 2])
        print(f"  Wave {w}-{w+1}: r={r:.3f}, p={p:.4f}, N={len(merged):,}")
        icc_results[f'w{w}_w{w+1}'] = {'r': round(r, 3), 'N': len(merged)}

# Overall ICC(1) using all waves
# ICC(1) = (MSB - MSW) / (MSB + (k-1)*MSW)
# where MSB = between-person mean square, MSW = within-person mean square
print("\n  Computing ICC(1) across all waves...")
econ_data = panel[['pid', 'wave', 'econ_satisfaction']].dropna()
# Only use persons with 2+ observations
obs_per_person = econ_data.groupby('pid').size()
pids_multi = obs_per_person[obs_per_person >= 2].index
econ_multi = econ_data[econ_data['pid'].isin(pids_multi)]

# One-way random effects ANOVA
grand_mean = econ_multi['econ_satisfaction'].mean()
person_means = econ_multi.groupby('pid')['econ_satisfaction'].mean()
n_persons = len(person_means)
k_bar = len(econ_multi) / n_persons  # average observations per person

# Between-person variance
ssb = sum(econ_multi.groupby('pid').size() * (person_means - grand_mean)**2)
msb = ssb / (n_persons - 1)

# Within-person variance
ssw = sum((econ_multi['econ_satisfaction'] - econ_multi['pid'].map(person_means))**2)
msw = ssw / (len(econ_multi) - n_persons)

icc1 = (msb - msw) / (msb + (k_bar - 1) * msw)
print(f"  ICC(1) = {icc1:.3f}")
print(f"  Mean square between (MSB) = {msb:.2f}")
print(f"  Mean square within (MSW) = {msw:.2f}")
print(f"  N persons = {n_persons:,}, Mean obs/person = {k_bar:.1f}")

icc_results['ICC1'] = round(icc1, 3)
icc_results['MSB'] = round(msb, 2)
icc_results['MSW'] = round(msw, 2)
all_results['ICC'] = icc_results

# ============================================================================
# DIFFERENTIAL ATTRITION ANALYSIS
# ============================================================================
print("\n" + "=" * 70)
print("DIFFERENTIAL ATTRITION BY BASELINE FINANCIAL DISTRESS STATUS")
print("=" * 70)

# Get baseline economic satisfaction status
# Restrict to original wave-1 cohort to avoid inflating denominators
# with refreshment sample members who were not present at earlier waves
wave1_pids_set = set(panel.loc[panel['wave'] == 1, 'pid'])
baseline_w1 = baseline[baseline['pid'].isin(wave1_pids_set)]
bl_exposure = baseline_w1[['pid', 'low_econ_sat']].rename(columns={'low_econ_sat': 'bl_low_econ_sat'})
panel_with_bl = panel.merge(bl_exposure, on='pid', how='left')

attrition = {}
print(f"\n  Wave-by-wave retention by baseline economic satisfaction (wave-1 cohort only):")
print(f"  {'Wave':<8} {'Low ES retained':<20} {'High ES retained':<20} {'Diff':<10}")
print(f"  {'-'*58}")

wave1_low = set(baseline_w1.loc[baseline_w1['low_econ_sat'] == 1, 'pid'])
wave1_high = set(baseline_w1.loc[baseline_w1['low_econ_sat'] == 0, 'pid'])

for w in range(1, 10):
    wave_pids = set(panel.loc[panel['wave'] == w, 'pid'])
    # Only count original cohort (not refreshment)
    low_retained = len(wave_pids & wave1_low)
    high_retained = len(wave_pids & wave1_high)
    low_pct = low_retained / len(wave1_low) * 100 if len(wave1_low) > 0 else 0
    high_pct = high_retained / len(wave1_high) * 100 if len(wave1_high) > 0 else 0
    diff = low_pct - high_pct
    print(f"  {w:<8} {low_pct:>6.1f}% ({low_retained:,}){'':<5} {high_pct:>6.1f}% ({high_retained:,}){'':<5} {diff:>+.1f}%")
    attrition[f'wave_{w}'] = {
        'low_es_pct': round(low_pct, 1), 'high_es_pct': round(high_pct, 1),
        'low_es_n': low_retained, 'high_es_n': high_retained
    }

# Death-adjusted attrition
print(f"\n  N baseline low ES: {len(wave1_low):,}")
print(f"  N baseline high ES: {len(wave1_high):,}")

# Check if attrition is due to death or dropout
dead_low = len(set(deaths['pid']) & wave1_low)
dead_high = len(set(deaths['pid']) & wave1_high)
print(f"  Deaths among low ES: {dead_low:,} ({dead_low/len(wave1_low)*100:.1f}%)")
print(f"  Deaths among high ES: {dead_high:,} ({dead_high/len(wave1_high)*100:.1f}%)")

all_results['attrition'] = attrition

# ============================================================================
# POST-HOC POWER ANALYSIS
# ============================================================================
print("\n" + "=" * 70)
print("POST-HOC POWER ANALYSIS FOR WEALTH SHOCK")
print("=" * 70)

# From the time-varying model: wealth shock prevalence ~5.2%, CI 0.91-1.28
# Formula: detectable HR at 80% power
# z_alpha = 1.96, z_beta = 0.84
# log(HR) = (z_alpha + z_beta) / sqrt(d * p * (1-p))
# where d = events, p = exposure prevalence

# Get actual numbers from person-period data
ws_data = pp[['hh_wealth_shock', 'event']].dropna()
n_intervals = len(ws_data)
n_events = int(ws_data['event'].sum())
p_exposed = ws_data['hh_wealth_shock'].mean()
n_exposed_events = int(ws_data.loc[ws_data['hh_wealth_shock'] == 1, 'event'].sum())

print(f"  N intervals: {n_intervals:,}")
print(f"  Total events: {n_events:,}")
print(f"  Exposure prevalence: {p_exposed:.3f}")
print(f"  Events among exposed: {n_exposed_events:,}")

# Detectable HR at 80% power, alpha=0.05 (two-sided)
z_alpha = 1.96
z_beta = 0.84
log_hr_detectable = (z_alpha + z_beta) / np.sqrt(n_events * p_exposed * (1 - p_exposed))
hr_detectable = np.exp(log_hr_detectable)

print(f"\n  Detectable HR at 80% power (alpha=0.05): {hr_detectable:.2f}")
print(f"  (i.e., the study can detect HR >= {hr_detectable:.2f} or HR <= {1/hr_detectable:.2f})")

# Power at various HRs
print(f"\n  Power at various HRs:")
for test_hr in [1.10, 1.15, 1.20, 1.25, 1.30, 1.40, 1.50]:
    z_stat = abs(np.log(test_hr)) * np.sqrt(n_events * p_exposed * (1 - p_exposed)) - z_alpha
    power = stats.norm.cdf(z_stat)
    print(f"    HR={test_hr:.2f}: power={power*100:.1f}%")

all_results['power_analysis'] = {
    'n_events': n_events, 'p_exposed': round(p_exposed, 3),
    'hr_detectable_80pct': round(hr_detectable, 2),
    'n_exposed_events': n_exposed_events
}

# ============================================================================
# REFRESHMENT SAMPLE SENSITIVITY
# ============================================================================
print("\n" + "=" * 70)
print("SENSITIVITY EXCLUDING WAVE-5 REFRESHMENT SAMPLE")
print("=" * 70)

# Wave 5 refreshment = people first appearing at wave 5
wave1_pids = set(panel.loc[panel['wave'] == 1, 'pid'])
df_orig = baseline[baseline['pid'].isin(wave1_pids)].copy()
n_excluded = len(baseline) - len(df_orig)
print(f"  Excluded {n_excluded} refreshment sample members")
print(f"  Original cohort: N={len(df_orig):,}, Deaths={df_orig['died'].sum():,}")

exposure = 'low_econ_sat_bl'
covs = demo_covs + health_covs_orig
model_df = df_orig[['surv_time', 'died', exposure] + covs].dropna()

cph = CoxPHFitter()
cph.fit(model_df, duration_col='surv_time', event_col='died')
hr = np.exp(cph.params_[exposure])
ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
p = cph.summary['p'][exposure]
print(f"  Health-adjusted HR: {hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")

# Fully adjusted
covs_full = full_covs_orig
model_df2 = df_orig[['surv_time', 'died', exposure] + covs_full].dropna()
cph2 = CoxPHFitter()
cph2.fit(model_df2, duration_col='surv_time', event_col='died')
hr2 = np.exp(cph2.params_[exposure])
ci_low2 = np.exp(cph2.confidence_intervals_.loc[exposure].iloc[0])
ci_high2 = np.exp(cph2.confidence_intervals_.loc[exposure].iloc[1])
p2 = cph2.summary['p'][exposure]
print(f"  Fully adjusted HR: {hr2:.2f} ({ci_low2:.2f}-{ci_high2:.2f}), p={p2:.4f}")

all_results['sensitivity_no_refreshment'] = {
    'N': len(df_orig), 'N_excluded': n_excluded,
    'health_adj_HR': round(hr, 3), 'health_adj_CI': f"{ci_low:.3f}-{ci_high:.3f}",
    'full_adj_HR': round(hr2, 3), 'full_adj_CI': f"{ci_low2:.3f}-{ci_high2:.3f}"
}

# ============================================================================
# HEALTHY-AT-BASELINE SENSITIVITY
# ============================================================================
print("\n" + "=" * 70)
print("HEALTHY-AT-BASELINE SENSITIVITY ANALYSIS")
print("=" * 70)

# Restrict to good/excellent SRH (1-2) and zero chronic diseases
df_healthy = df[
    (df['self_rated_health'].isin([1, 2])) &
    (df['chronic_count'] == 0)
].copy()
print(f"  Healthy at baseline: N={len(df_healthy):,}, Deaths={df_healthy['died'].sum():,}")

exposure = 'low_econ_sat_bl'
covs = demo_covs + ['bmi', 'current_smoker', 'ever_smoker']  # drop SRH and chronic (restricted)
model_df = df_healthy[['surv_time', 'died', exposure] + covs].dropna()

if model_df['died'].sum() >= 20 and model_df[exposure].sum() >= 10:
    cph = CoxPHFitter()
    cph.fit(model_df, duration_col='surv_time', event_col='died')
    hr = np.exp(cph.params_[exposure])
    ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
    ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
    p = cph.summary['p'][exposure]
    print(f"  Demographic + behavior adjusted: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")
    all_results['healthy_baseline'] = {
        'N': len(model_df), 'Events': int(model_df['died'].sum()),
        'HR': round(hr, 3), 'CI': f"{ci_low:.3f}-{ci_high:.3f}", 'p': round(p, 4)
    }
else:
    print(f"  Insufficient events ({model_df['died'].sum()}) or exposed ({model_df[exposure].sum()})")

# ============================================================================
# DOSE-RESPONSE ANALYSIS
# ============================================================================
print("\n" + "=" * 70)
print("DOSE-RESPONSE: QUINTILE HRs")
print("=" * 70)

# Use the most complete model
for q in ['Q1 (lowest)', 'Q2', 'Q3', 'Q4']:
    df[f'econ_q_{q[:2]}'] = (df['econ_sat_quintile'] == q).astype(float)

q_covs = ['econ_q_Q1', 'econ_q_Q2', 'econ_q_Q3', 'econ_q_Q4'] + demo_covs + health_covs_orig
model_df = df[['surv_time', 'died'] + q_covs].dropna()

cph = CoxPHFitter()
cph.fit(model_df, duration_col='surv_time', event_col='died')

print("\nHealth-adjusted HRs by quintile (ref: Q5 highest satisfaction):")
dose_response = {}
for var in ['econ_q_Q4', 'econ_q_Q3', 'econ_q_Q2', 'econ_q_Q1']:
    hr = np.exp(cph.params_[var])
    ci_low = np.exp(cph.confidence_intervals_.loc[var].iloc[0])
    ci_high = np.exp(cph.confidence_intervals_.loc[var].iloc[1])
    p = cph.summary['p'][var]
    q_label = var.replace('econ_q_', '')
    print(f"  {q_label} vs Q5: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")
    dose_response[q_label] = {'HR': round(hr, 3), 'CI_low': round(ci_low, 3),
                               'CI_high': round(ci_high, 3), 'p': round(p, 4)}

# P for trend
df['econ_quintile_num'] = df['econ_sat_quintile'].map({
    'Q1 (lowest)': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4, 'Q5 (highest)': 5
})
trend_covs = ['econ_quintile_num'] + demo_covs + health_covs_orig
trend_df = df[['surv_time', 'died'] + trend_covs].dropna()
cph_trend = CoxPHFitter()
cph_trend.fit(trend_df, duration_col='surv_time', event_col='died')
p_trend = cph_trend.summary['p']['econ_quintile_num']
print(f"\n  P for trend: {p_trend:.6f}")
dose_response['p_trend'] = round(p_trend, 6)
all_results['dose_response'] = dose_response

# ============================================================================
# SAVE ALL RESULTS
# ============================================================================
print("\n" + "=" * 70)
print("SAVING SUPPLEMENTARY RESULTS")
print("=" * 70)

# Save extended model results
pd.DataFrame(revised_results).to_csv(os.path.join(SUPP, 'extended_models.csv'), index=False)
print(f"  Extended models saved")

# Save regularisation comparison
pd.DataFrame(tv_results).to_csv(os.path.join(SUPP, 'regularisation_sensitivity.csv'), index=False)
print(f"  Regularisation comparison saved")

# Save all results as JSON
with open(os.path.join(SUPP, 'supplementary_results.json'), 'w') as f:
    json.dump(all_results, f, indent=2, default=str)
print(f"  All results JSON saved")

print("Done.")
