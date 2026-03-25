"""
08_objective_vs_subjective.py
Head-to-Head Comparison: Objective vs Subjective Financial Distress and Mortality

Key question: Does subjective financial distress predict mortality
independently of objective financial indicators?

Objective measures: household income, welfare receipt, personal net assets
Subjective measure: economic satisfaction (0-100 VAS)
"""

import pandas as pd
import numpy as np
import os
import warnings
import json
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', message='.*delta_grad.*')
warnings.filterwarnings('ignore', message='.*convergence.*')

from lifelines import CoxPHFitter
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from config import BASE, OUT
from model_specs import *

SUPP = os.path.join(OUT, "supplementary")
os.makedirs(SUPP, exist_ok=True)

# ============================================================================
# LOAD AND PREPARE DATA
# ============================================================================
print("Loading data...")
baseline = pd.read_parquet(os.path.join(OUT, 'baseline_analytic.parquet'))
panel = pd.read_parquet(os.path.join(OUT, 'panel_data.parquet'))
pp = pd.read_parquet(os.path.join(OUT, 'person_period_data.parquet'))

# --- Prepare variables ---
df = baseline.copy()
df['age_10'] = df['age'] / 10
df['edu_middle'] = (df['education'] == 2).astype(float)
df['edu_high'] = (df['education'] == 3).astype(float)
df['edu_college'] = (df['education'] >= 4).astype(float)

# Subjective: low economic satisfaction (bottom quintile)
df['low_econ_sat_bl'] = (df['econ_sat_quintile'] == 'Q1 (lowest)').astype(float)
df['econ_sat_decrease_10'] = (100 - df['econ_satisfaction']) / 10

# Objective 1: Low household income (bottom quintile)
df['hh_income_clean'] = df['hh_income'].copy()
df.loc[df['hh_income_clean'] <= 0, 'hh_income_clean'] = np.nan
df['log_hh_income'] = np.log1p(df['hh_income_clean'])
inc_q20 = df['hh_income_clean'].quantile(0.20)
df['low_income'] = (df['hh_income_clean'] <= inc_q20).astype(float)
df.loc[df['hh_income_clean'].isna(), 'low_income'] = np.nan

# Objective 2: Welfare receipt
df['on_welfare'] = df['on_welfare_bl']

# Objective 3: Low personal net assets (bottom quintile)
pna_q20 = df['p_net_assets'].quantile(0.20)
df['low_assets'] = (df['p_net_assets'] <= pna_q20).astype(float)
df.loc[df['p_net_assets'].isna(), 'low_assets'] = np.nan

# Objective 4: No pension
df['no_pension'] = (df['has_pension_bl'] == 0).astype(float)

# Exercise and drinking
df['regular_exercise'] = (df['exercise'] == 1).astype(float)
df.loc[df['exercise'].isna(), 'regular_exercise'] = np.nan
wave2_drinking = panel.loc[panel['wave'] == 2, ['pid', 'drinking']].copy()
wave2_drinking['current_drinker'] = (wave2_drinking['drinking'] == 1).astype(float)
wave2_drinking = wave2_drinking[['pid', 'current_drinker']].dropna()
df = df.merge(wave2_drinking, on='pid', how='left')

# CES-D continuous
cesd_neg = ['cesd_142', 'cesd_143', 'cesd_144', 'cesd_145',
            'cesd_147', 'cesd_148', 'cesd_150', 'cesd_151']
cesd_pos = ['cesd_146', 'cesd_149']
def compute_cesd(row):
    score = 0
    for c in cesd_neg:
        if pd.isna(row.get(c)):
            return np.nan
        score += row[c] - 1
    for c in cesd_pos:
        if pd.isna(row.get(c)):
            return np.nan
        score += 4 - row[c]
    return score
df['cesd_score'] = df.apply(compute_cesd, axis=1)

# Covariates
demo_covs = ['age_10', 'female', 'married', 'edu_middle', 'edu_high', 'edu_college']
health_covs = ['self_rated_health', 'chronic_count', 'bmi', 'current_smoker', 'ever_smoker',
               'current_drinker', 'regular_exercise']
mediator_covs = ['cesd_score', 'iadl']

print(f"Baseline: N={len(df):,}, Deaths={df['died'].sum():,}")

# ============================================================================
# 1. DESCRIBE DISCORDANCE BETWEEN OBJECTIVE AND SUBJECTIVE
# ============================================================================
print("\n" + "=" * 70)
print("1. DISCORDANCE: OBJECTIVE vs SUBJECTIVE FINANCIAL DISTRESS")
print("=" * 70)

valid = df[['low_econ_sat_bl', 'low_income', 'died', 'surv_time']].dropna()
print(f"\nSample with both measures: N={len(valid):,}")

# 2x2 table
groups = {
    'Both low': (valid['low_econ_sat_bl'] == 1) & (valid['low_income'] == 1),
    'Subjective only': (valid['low_econ_sat_bl'] == 1) & (valid['low_income'] == 0),
    'Objective only': (valid['low_econ_sat_bl'] == 0) & (valid['low_income'] == 1),
    'Neither': (valid['low_econ_sat_bl'] == 0) & (valid['low_income'] == 0),
}

print(f"\n{'Group':<25} {'N':>8} {'Deaths':>8} {'Mortality%':>12} {'Rate/1000py':>12}")
print("-" * 70)
for label, mask in groups.items():
    n = mask.sum()
    deaths = valid.loc[mask, 'died'].sum()
    mort_pct = deaths / n * 100
    py = valid.loc[mask, 'surv_time'].sum()
    rate = deaths / py * 1000
    print(f"{label:<25} {n:>8,} {int(deaths):>8,} {mort_pct:>11.1f}% {rate:>11.1f}")

# ============================================================================
# 2. INDIVIDUAL MEASURE COMPARISONS
# ============================================================================
print("\n" + "=" * 70)
print("2. EACH FINANCIAL DISTRESS MEASURE → MORTALITY (SEPARATE MODELS)")
print("=" * 70)

all_results = []
exposures = [
    ('low_econ_sat_bl', 'Low economic satisfaction (subjective)'),
    ('low_income', 'Low household income (objective)'),
    ('on_welfare', 'Welfare receipt (objective)'),
    ('low_assets', 'Low personal net assets (objective)'),
]

for exposure, label in exposures:
    print(f"\n--- {label} ---")
    for model_name, covs in [
        ('Unadjusted', []),
        ('Demographic', demo_covs),
        ('+ Health', demo_covs + health_covs),
        ('+ Mediators', demo_covs + health_covs + mediator_covs),
    ]:
        all_vars = [exposure] + covs
        model_df = df[['surv_time', 'died'] + all_vars].dropna()
        if model_df[exposure].sum() < 10:
            continue
        try:
            cph = CoxPHFitter()
            cph.fit(model_df, duration_col='surv_time', event_col='died')
            hr = np.exp(cph.params_[exposure])
            ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
            ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
            p = cph.summary['p'][exposure]
            print(f"  {model_name}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}, N={len(model_df):,}")
            all_results.append({
                'Exposure': label, 'Type': 'Subjective' if 'subjective' in label.lower() else 'Objective',
                'Model': model_name, 'HR': round(hr, 3), 'CI_low': round(ci_low, 3),
                'CI_high': round(ci_high, 3), 'p': round(p, 4),
                'N': len(model_df), 'Events': int(model_df['died'].sum()),
                'Exposed': int(model_df[exposure].sum())
            })
        except Exception as e:
            print(f"  {model_name}: Failed - {e}")

# ============================================================================
# 3. THE KEY TEST: SUBJECTIVE AFTER ADJUSTING FOR ALL OBJECTIVE MEASURES
# ============================================================================
print("\n" + "=" * 70)
print("3. KEY TEST: SUBJECTIVE AFTER ADJUSTING FOR ALL OBJECTIVE MEASURES")
print("=" * 70)

obj_measures = ['low_income', 'on_welfare', 'low_assets']

# Model A: All objective measures together
print("\n--- A. All objective measures combined (no subjective) ---")
model_df = df[['surv_time', 'died'] + obj_measures + demo_covs + health_covs].dropna()
cph = CoxPHFitter()
cph.fit(model_df, duration_col='surv_time', event_col='died')
for exp in obj_measures:
    hr = np.exp(cph.params_[exp])
    ci_l = np.exp(cph.confidence_intervals_.loc[exp].iloc[0])
    ci_h = np.exp(cph.confidence_intervals_.loc[exp].iloc[1])
    p = cph.summary['p'][exp]
    print(f"  {exp}: HR={hr:.2f} ({ci_l:.2f}-{ci_h:.2f}), p={p:.4f}")
print(f"  N={len(model_df):,}, Events={int(model_df['died'].sum()):,}")

# Model B: Subjective only (same sample for comparability)
print("\n--- B. Subjective measure only (same sample) ---")
model_df_b = df[['surv_time', 'died', 'low_econ_sat_bl'] + obj_measures + demo_covs + health_covs].dropna()
cph_b = CoxPHFitter()
cph_b.fit(model_df_b[['surv_time', 'died', 'low_econ_sat_bl'] + demo_covs + health_covs],
          duration_col='surv_time', event_col='died')
hr = np.exp(cph_b.params_['low_econ_sat_bl'])
ci_l = np.exp(cph_b.confidence_intervals_.loc['low_econ_sat_bl'].iloc[0])
ci_h = np.exp(cph_b.confidence_intervals_.loc['low_econ_sat_bl'].iloc[1])
p = cph_b.summary['p']['low_econ_sat_bl']
print(f"  low_econ_sat_bl: HR={hr:.2f} ({ci_l:.2f}-{ci_h:.2f}), p={p:.4f}")
print(f"  N={len(model_df_b):,}")

# Model C: THE KEY MODEL — Subjective AFTER adjusting for all objective
print("\n--- C. Subjective AFTER adjusting for all objective measures ---")
combined_vars = ['low_econ_sat_bl'] + obj_measures + demo_covs + health_covs
model_df_c = df[['surv_time', 'died'] + combined_vars].dropna()
cph_c = CoxPHFitter()
cph_c.fit(model_df_c, duration_col='surv_time', event_col='died')
print(f"\n  Combined model (objective + subjective):")
for var in ['low_econ_sat_bl'] + obj_measures:
    hr = np.exp(cph_c.params_[var])
    ci_l = np.exp(cph_c.confidence_intervals_.loc[var].iloc[0])
    ci_h = np.exp(cph_c.confidence_intervals_.loc[var].iloc[1])
    p = cph_c.summary['p'][var]
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    print(f"  {var:25s}: HR={hr:.2f} ({ci_l:.2f}-{ci_h:.2f}), p={p:.4f} {sig}")
print(f"  N={len(model_df_c):,}, Events={int(model_df_c['died'].sum()):,}")

# Model D: Add mediators too
print("\n--- D. Full model with objective + subjective + mediators ---")
full_vars = ['low_econ_sat_bl'] + obj_measures + demo_covs + health_covs + mediator_covs
model_df_d = df[['surv_time', 'died'] + full_vars].dropna()
cph_d = CoxPHFitter()
cph_d.fit(model_df_d, duration_col='surv_time', event_col='died')
for var in ['low_econ_sat_bl'] + obj_measures:
    hr = np.exp(cph_d.params_[var])
    ci_l = np.exp(cph_d.confidence_intervals_.loc[var].iloc[0])
    ci_h = np.exp(cph_d.confidence_intervals_.loc[var].iloc[1])
    p = cph_d.summary['p'][var]
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    print(f"  {var:25s}: HR={hr:.2f} ({ci_l:.2f}-{ci_h:.2f}), p={p:.4f} {sig}")
print(f"  N={len(model_df_d):,}")

# ============================================================================
# 4. CONTINUOUS MEASURES HEAD-TO-HEAD
# ============================================================================
print("\n" + "=" * 70)
print("4. CONTINUOUS MEASURES: INCOME vs SATISFACTION")
print("=" * 70)

# Per 10-point decrease in satisfaction vs per log-unit decrease in income
print("\n--- Separate models ---")
for exposure, label in [('econ_sat_decrease_10', 'Econ dissatisfaction (per 10-pt)'),
                         ('log_hh_income', 'Log HH income (per unit)')]:
    covs = demo_covs + health_covs
    # Need to reverse income direction for comparable interpretation
    model_df = df[['surv_time', 'died', exposure] + covs].dropna()
    cph = CoxPHFitter()
    cph.fit(model_df, duration_col='surv_time', event_col='died')
    hr = np.exp(cph.params_[exposure])
    ci_l = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
    ci_h = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
    p = cph.summary['p'][exposure]
    print(f"  {label}: HR={hr:.3f} ({ci_l:.3f}-{ci_h:.3f}), p={p:.4f}")

print("\n--- Combined model (both continuous) ---")
both_exp = ['econ_sat_decrease_10', 'log_hh_income']
covs = demo_covs + health_covs
model_df = df[['surv_time', 'died'] + both_exp + covs].dropna()
cph = CoxPHFitter()
cph.fit(model_df, duration_col='surv_time', event_col='died')
for exp in both_exp:
    hr = np.exp(cph.params_[exp])
    ci_l = np.exp(cph.confidence_intervals_.loc[exp].iloc[0])
    ci_h = np.exp(cph.confidence_intervals_.loc[exp].iloc[1])
    p = cph.summary['p'][exp]
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    print(f"  {exp}: HR={hr:.3f} ({ci_l:.3f}-{ci_h:.3f}), p={p:.4f} {sig}")

# ============================================================================
# 5. DISCORDANCE ANALYSIS: WHO IS AT RISK?
# ============================================================================
print("\n" + "=" * 70)
print("5. DISCORDANCE ANALYSIS: MORTALITY BY AGREEMENT/DISAGREEMENT")
print("=" * 70)

# Create 4-group variable
valid = df[['low_econ_sat_bl', 'low_income', 'surv_time', 'died'] + demo_covs + health_covs].dropna()
valid['group'] = 'Neither'
valid.loc[(valid['low_econ_sat_bl'] == 1) & (valid['low_income'] == 1), 'group'] = 'Both'
valid.loc[(valid['low_econ_sat_bl'] == 1) & (valid['low_income'] == 0), 'group'] = 'Subjective only'
valid.loc[(valid['low_econ_sat_bl'] == 0) & (valid['low_income'] == 1), 'group'] = 'Objective only'

# Create dummies (reference: Neither)
for g in ['Both', 'Subjective only', 'Objective only']:
    valid[f'grp_{g.replace(" ", "_")}'] = (valid['group'] == g).astype(float)

grp_vars = ['grp_Both', 'grp_Subjective_only', 'grp_Objective_only']

print("\n--- Health-adjusted model (ref: Neither low income nor low satisfaction) ---")
model_df = valid[['surv_time', 'died'] + grp_vars + demo_covs + health_covs]
cph = CoxPHFitter()
cph.fit(model_df, duration_col='surv_time', event_col='died')

for var in grp_vars:
    hr = np.exp(cph.params_[var])
    ci_l = np.exp(cph.confidence_intervals_.loc[var].iloc[0])
    ci_h = np.exp(cph.confidence_intervals_.loc[var].iloc[1])
    p = cph.summary['p'][var]
    n = int((valid[var] == 1).sum())
    events = int(valid.loc[valid[var] == 1, 'died'].sum())
    sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
    label = var.replace('grp_', '').replace('_', ' ')
    print(f"  {label:20s}: HR={hr:.2f} ({ci_l:.2f}-{ci_h:.2f}), p={p:.4f} {sig}  [N={n:,}, events={events:,}]")
print(f"  Reference (Neither): N={int((valid['group']=='Neither').sum()):,}")

# ============================================================================
# 6. TIME-VARYING: OBJECTIVE vs SUBJECTIVE
# ============================================================================
print("\n" + "=" * 70)
print("6. TIME-VARYING MODELS: OBJECTIVE vs SUBJECTIVE")
print("=" * 70)

# Prepare person-period data
pp2 = pp.copy()
pp2['age_10'] = pp2['age'] / 10
pp2['edu_middle'] = (pp2['education'] == 2).astype(float)
pp2['edu_high'] = (pp2['education'] == 3).astype(float)
pp2['edu_college'] = (pp2['education'] >= 4).astype(float)
pp2['current_smoker'] = (pp2['smoking'] == 2).astype(float)

# Create low income indicator (time-varying)
# Log income
pp2['hh_income_clean'] = pp2['hh_income'].copy()
pp2.loc[pp2['hh_income_clean'] <= 0, 'hh_income_clean'] = np.nan
pp2['log_hh_income'] = np.log1p(pp2['hh_income_clean'])

# Wave-specific income quintiles
pp2['low_income_tv'] = np.nan
for w in pp2['wave'].unique():
    mask = pp2['wave'] == w
    inc = pp2.loc[mask, 'hh_income_clean']
    if inc.notna().sum() > 100:
        q20 = inc.quantile(0.20)
        pp2.loc[mask & inc.notna(), 'low_income_tv'] = (inc <= q20).astype(float)

# On welfare (time-varying) - already in pp as 'on_welfare' if present
# Check what's available
if 'on_welfare' not in pp2.columns:
    # Derive from panel
    panel_welfare = panel[['pid', 'wave', 'on_welfare']].copy()
    pp2 = pp2.merge(panel_welfare, on=['pid', 'wave'], how='left', suffixes=('', '_panel'))
    if 'on_welfare_panel' in pp2.columns:
        pp2['on_welfare'] = pp2['on_welfare_panel']

tv_demo = ['age_10', 'female', 'married', 'edu_middle', 'edu_high', 'edu_college']
tv_health = ['self_rated_health', 'chronic_count', 'bmi', 'current_smoker']
tv_full = tv_demo + tv_health + ['depression', 'iadl']

# A. Each time-varying measure separately
print("\n--- Each time-varying measure (fully adjusted) ---")
tv_exposures = [
    ('low_econ_sat', 'Low econ satisfaction (subjective, TV)'),
    ('hh_wealth_shock', 'HH wealth shock (objective, TV)'),
    ('low_income_tv', 'Low HH income (objective, TV)'),
]

for exposure, label in tv_exposures:
    if exposure not in pp2.columns:
        print(f"  {label}: column not found")
        continue
    all_vars = [exposure] + tv_full
    model_df = pp2[['t_start', 't_stop', 'event'] + all_vars].dropna()
    if model_df[exposure].sum() < 10:
        print(f"  {label}: insufficient exposed")
        continue
    try:
        cph = CoxPHFitter(penalizer=0.01)
        cph.fit(model_df, duration_col='t_stop', event_col='event', entry_col='t_start')
        hr = np.exp(cph.params_[exposure])
        ci_l = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
        ci_h = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
        p = cph.summary['p'][exposure]
        print(f"  {label}: HR={hr:.2f} ({ci_l:.2f}-{ci_h:.2f}), p={p:.4f}, N={len(model_df):,}")
    except Exception as e:
        print(f"  {label}: Failed - {e}")

# B. Combined time-varying model
print("\n--- Combined time-varying model (subjective + objective) ---")
tv_combined = ['low_econ_sat', 'low_income_tv', 'hh_wealth_shock']
available_tv = [v for v in tv_combined if v in pp2.columns]
all_vars = available_tv + tv_full
model_df = pp2[['t_start', 't_stop', 'event'] + all_vars].dropna()
print(f"  Combined model data: N={len(model_df):,}, events={int(model_df['event'].sum()):,}")

try:
    cph = CoxPHFitter(penalizer=0.01)
    cph.fit(model_df, duration_col='t_stop', event_col='event', entry_col='t_start')
    for exp in available_tv:
        hr = np.exp(cph.params_[exp])
        ci_l = np.exp(cph.confidence_intervals_.loc[exp].iloc[0])
        ci_h = np.exp(cph.confidence_intervals_.loc[exp].iloc[1])
        p = cph.summary['p'][exp]
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        print(f"  {exp:25s}: HR={hr:.2f} ({ci_l:.2f}-{ci_h:.2f}), p={p:.4f} {sig}")
except Exception as e:
    print(f"  Combined model failed: {e}")

# ============================================================================
# 7. MODEL COMPARISON: C-INDEX
# ============================================================================
print("\n" + "=" * 70)
print("7. PREDICTIVE DISCRIMINATION: C-INDEX COMPARISON")
print("=" * 70)

# Compare concordance of models with objective only, subjective only, and both
base_covs = demo_covs + health_covs
sample = df[['surv_time', 'died', 'low_econ_sat_bl', 'low_income', 'on_welfare', 'low_assets'] + base_covs].dropna()

# Base model (demographics + health only)
cph_base = CoxPHFitter()
cph_base.fit(sample[['surv_time', 'died'] + base_covs], duration_col='surv_time', event_col='died')
print(f"  Base model (demo + health): C-index = {cph_base.concordance_index_:.4f}")

# + Objective only
obj_vars = ['low_income', 'on_welfare', 'low_assets']
cph_obj = CoxPHFitter()
cph_obj.fit(sample[['surv_time', 'died'] + obj_vars + base_covs], duration_col='surv_time', event_col='died')
print(f"  + Objective financial:      C-index = {cph_obj.concordance_index_:.4f}")

# + Subjective only
cph_subj = CoxPHFitter()
cph_subj.fit(sample[['surv_time', 'died', 'low_econ_sat_bl'] + base_covs], duration_col='surv_time', event_col='died')
print(f"  + Subjective financial:     C-index = {cph_subj.concordance_index_:.4f}")

# + Both
cph_both = CoxPHFitter()
cph_both.fit(sample[['surv_time', 'died', 'low_econ_sat_bl'] + obj_vars + base_covs],
             duration_col='surv_time', event_col='died')
print(f"  + Both (obj + subj):        C-index = {cph_both.concordance_index_:.4f}")

# ============================================================================
# SAVE
# ============================================================================
print("\n" + "=" * 70)
print("SAVING RESULTS")
print("=" * 70)

pd.DataFrame(all_results).to_csv(os.path.join(SUPP, 'objective_vs_subjective_models.csv'), index=False)
print("Results saved.")

print("Done.")
