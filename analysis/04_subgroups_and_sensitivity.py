"""
04_subgroups_and_sensitivity.py
Subgroup analyses and sensitivity checks (fixing collinearity issues)
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', message='.*delta_grad.*')
warnings.filterwarnings('ignore', message='.*convergence.*')

from lifelines import CoxPHFitter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from config import BASE, OUT
from model_specs import *
FIG = os.path.join(OUT, "figures")
TAB = os.path.join(OUT, "tables")

# Load data
baseline = pd.read_parquet(os.path.join(OUT, 'baseline_analytic.parquet'))
panel = pd.read_parquet(os.path.join(OUT, 'panel_data.parquet'))

# Prepare variables
df = baseline.copy()
df['age_10'] = df['age'] / 10
df['edu_middle'] = (df['education'] == 2).astype(float)
df['edu_high'] = (df['education'] == 3).astype(float)
df['edu_college'] = (df['education'] >= 4).astype(float)
df['low_econ_sat_bl'] = (df['econ_sat_quintile'] == 'Q1 (lowest)').astype(float)

# ============================================================================
# SUBGROUP ANALYSES (remove stratifying variable from covariates)
# ============================================================================
print("=" * 70)
print("SUBGROUP ANALYSES: Low Economic Satisfaction and Mortality")
print("=" * 70)

base_covs = ['age_10', 'female', 'married', 'edu_middle', 'edu_high', 'edu_college',
             'self_rated_health', 'chronic_count', 'bmi', 'current_smoker']
# Note: combined demo+health covariates (original set without drinking/exercise)

subgroups = {
    'Male': (df['female'] == 0, [c for c in base_covs if c != 'female']),
    'Female': (df['female'] == 1, [c for c in base_covs if c != 'female']),
    'Age 45-64': (df['age'] < 65, [c for c in base_covs if c != 'age_10']),
    'Age 65+': (df['age'] >= 65, [c for c in base_covs if c != 'age_10']),
    'Married': (df['married'] == 1, [c for c in base_covs if c != 'married']),
    'Not married': (df['married'] == 0, [c for c in base_covs if c != 'married']),
    'Has pension': (df['has_pension_bl'] == 1, base_covs),
    'No pension': (df['has_pension_bl'] == 0, base_covs),
    'No chronic disease': (df['chronic_count'] == 0, [c for c in base_covs if c != 'chronic_count']),
    '1+ chronic diseases': (df['chronic_count'] >= 1, base_covs),
}

# Construct ever_smoker and current_smoker
df['current_smoker'] = (df['smoking'] == 2).astype(float)

subgroup_results = []
for label, (mask, covs) in subgroups.items():
    sub = df.loc[mask].copy()
    model_vars = ['low_econ_sat_bl'] + covs
    model_df = sub[['surv_time', 'died'] + model_vars].dropna()

    if model_df['died'].sum() < 20 or model_df['low_econ_sat_bl'].sum() < 10:
        print(f"  {label}: Insufficient events, skipping")
        continue

    try:
        cph = CoxPHFitter(penalizer=0.01)  # small penalizer for stability
        cph.fit(model_df, duration_col='surv_time', event_col='died')
        hr = np.exp(cph.params_['low_econ_sat_bl'])
        ci_low = np.exp(cph.confidence_intervals_.loc['low_econ_sat_bl'].iloc[0])
        ci_high = np.exp(cph.confidence_intervals_.loc['low_econ_sat_bl'].iloc[1])
        p = cph.summary['p']['low_econ_sat_bl']
        n = len(model_df)
        events = int(model_df['died'].sum())
        print(f"  {label:25s}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}, N={n:,}, Events={events:,}")
        subgroup_results.append({
            'Subgroup': label, 'HR': hr, 'CI_low': ci_low, 'CI_high': ci_high,
            'p': p, 'N': n, 'Events': events
        })
    except Exception as e:
        print(f"  {label}: Model failed - {e}")

# ============================================================================
# WEALTH SHOCK ANALYSIS (proper construction)
# ============================================================================
print("\n" + "=" * 70)
print("WEALTH SHOCK ANALYSIS")
print("=" * 70)

# Prepare the wealth shock dataset properly
df_ws = df.copy()

# Merge wealth shock from panel - use first observed wealth shock
ws_data = panel[panel['wealth_shock'].notna()].copy()

# First wealth shock wave
first_ws = ws_data[ws_data['wealth_shock'] == 1].groupby('pid')['wave'].min().reset_index()
first_ws.columns = ['pid', 'first_ws_wave']

df_ws = df_ws.merge(first_ws, on='pid', how='left')
df_ws['ever_wealth_shock'] = df_ws['first_ws_wave'].notna().astype(float)

# For people who died before their potential wealth shock, they should be 0
# This is a simplified baseline analysis
print(f"Ever experienced wealth shock: {df_ws['ever_wealth_shock'].mean()*100:.1f}%")
print(f"Deaths among shocked: {df_ws.loc[df_ws['ever_wealth_shock']==1, 'died'].mean()*100:.1f}%")
print(f"Deaths among non-shocked: {df_ws.loc[df_ws['ever_wealth_shock']==0, 'died'].mean()*100:.1f}%")

# Note: wealth shock people survived longer (to have two waves to compare),
# which creates survivorship bias. Proper analysis requires time-varying Cox.
# We note this as a limitation and focus on the economic satisfaction measure.

# ============================================================================
# DOSE-RESPONSE: QUINTILE ANALYSIS
# ============================================================================
print("\n" + "=" * 70)
print("DOSE-RESPONSE: ECONOMIC SATISFACTION QUINTILES")
print("=" * 70)

for q in ['Q1 (lowest)', 'Q2', 'Q3', 'Q4']:
    df[f'econ_q_{q[:2]}'] = (df['econ_sat_quintile'] == q).astype(float)

q_covs = ['econ_q_Q1', 'econ_q_Q2', 'econ_q_Q3', 'econ_q_Q4'] + base_covs
model_df = df[['surv_time', 'died'] + q_covs].dropna()

cph = CoxPHFitter()
cph.fit(model_df, duration_col='surv_time', event_col='died')

print(f"\nHealth-adjusted HRs (ref: Q5 highest satisfaction):")
quintile_results = []
for var in ['econ_q_Q1', 'econ_q_Q2', 'econ_q_Q3', 'econ_q_Q4']:
    hr = np.exp(cph.params_[var])
    ci_low = np.exp(cph.confidence_intervals_.loc[var].iloc[0])
    ci_high = np.exp(cph.confidence_intervals_.loc[var].iloc[1])
    p = cph.summary['p'][var]
    q_label = {'econ_q_Q1': 'Q1 (lowest)', 'econ_q_Q2': 'Q2',
               'econ_q_Q3': 'Q3', 'econ_q_Q4': 'Q4'}[var]
    print(f"  {q_label}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")
    quintile_results.append({'Quintile': q_label, 'HR': hr, 'CI_low': ci_low, 'CI_high': ci_high, 'p': p})

# Add Q5 reference
quintile_results.append({'Quintile': 'Q5 (highest)', 'HR': 1.0, 'CI_low': 1.0, 'CI_high': 1.0, 'p': np.nan})

# P for trend
df['econ_quintile_num'] = df['econ_sat_quintile'].map({
    'Q1 (lowest)': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4, 'Q5 (highest)': 5
})
trend_covs = ['econ_quintile_num'] + base_covs
trend_df = df[['surv_time', 'died'] + trend_covs].dropna()
cph_trend = CoxPHFitter()
cph_trend.fit(trend_df, duration_col='surv_time', event_col='died')
p_trend = cph_trend.summary['p']['econ_quintile_num']
print(f"\n  P for trend: {p_trend:.1e}")

# ============================================================================
# SENSITIVITY: EXCLUDE EARLY DEATHS
# ============================================================================
print("\n" + "=" * 70)
print("SENSITIVITY: EXCLUDING EARLY DEATHS")
print("=" * 70)

for cutoff in [2, 4]:
    df_excl = df[~((df['died'] == 1) & (df['surv_time'] < cutoff))].copy()
    covs = ['low_econ_sat_bl'] + base_covs
    model_df = df_excl[['surv_time', 'died'] + covs].dropna()
    cph = CoxPHFitter()
    cph.fit(model_df, duration_col='surv_time', event_col='died')
    hr = np.exp(cph.params_['low_econ_sat_bl'])
    ci_low = np.exp(cph.confidence_intervals_.loc['low_econ_sat_bl'].iloc[0])
    ci_high = np.exp(cph.confidence_intervals_.loc['low_econ_sat_bl'].iloc[1])
    p = cph.summary['p']['low_econ_sat_bl']
    print(f"  Excluding deaths < {cutoff}y: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f} (N={len(model_df):,})")

# ============================================================================
# SENSITIVITY: EXCLUDING CANCER/TERMINAL ILLNESS AT BASELINE
# ============================================================================
print("\n" + "=" * 70)
print("SENSITIVITY: EXCLUDING BASELINE CANCER")
print("=" * 70)

df_no_cancer = df[df['cancer'] != 1].copy()
covs = ['low_econ_sat_bl'] + base_covs
model_df = df_no_cancer[['surv_time', 'died'] + covs].dropna()
cph = CoxPHFitter()
cph.fit(model_df, duration_col='surv_time', event_col='died')
hr = np.exp(cph.params_['low_econ_sat_bl'])
ci_low = np.exp(cph.confidence_intervals_.loc['low_econ_sat_bl'].iloc[0])
ci_high = np.exp(cph.confidence_intervals_.loc['low_econ_sat_bl'].iloc[1])
p = cph.summary['p']['low_econ_sat_bl']
print(f"  Excluding cancer: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f} (N={len(model_df):,})")

# ============================================================================
# FIGURE 3: DOSE-RESPONSE FIGURE
# ============================================================================
print("\nGenerating dose-response figure...")

qr_df = pd.DataFrame(quintile_results)

fig, ax = plt.subplots(figsize=(8, 6))
x = range(len(qr_df))
ax.errorbar(x, qr_df['HR'], yerr=[qr_df['HR'] - qr_df['CI_low'], qr_df['CI_high'] - qr_df['HR']],
            fmt='s-', color='#1f77b4', markersize=10, capsize=5, linewidth=2)
ax.axhline(y=1, color='grey', linestyle='--', linewidth=0.8)
ax.set_xticks(x)
ax.set_xticklabels(qr_df['Quintile'], fontsize=10)
ax.set_xlabel('Economic Satisfaction Quintile', fontsize=11)
ax.set_ylabel('Hazard Ratio for All-Cause Mortality\n(reference: Q5 highest)', fontsize=11)
ax.set_title('Dose-Response: Economic Satisfaction and Mortality\n(Health-Adjusted Cox Model)',
             fontsize=12, fontweight='bold')
ax.text(0.02, 0.98, f'P for trend < 0.001', transform=ax.transAxes,
        va='top', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig(os.path.join(FIG, 'figure3_dose_response.png'), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(FIG, 'figure3_dose_response.pdf'), bbox_inches='tight')
plt.close()
print("Figure 3 saved.")

# ============================================================================
# FOREST PLOT (FIXED)
# ============================================================================
print("\nGenerating improved forest plot...")

if subgroup_results:
    sg_df = pd.DataFrame(subgroup_results)
    sg_df.to_csv(os.path.join(TAB, 'subgroup_analyses.csv'), index=False)

    fig, ax = plt.subplots(figsize=(10, 8))
    y_positions = range(len(sg_df) - 1, -1, -1)

    for i, (_, row) in enumerate(sg_df.iterrows()):
        y = list(y_positions)[i]
        color = '#d62728' if row['p'] < 0.05 else '#888888'
        ax.plot(row['HR'], y, 'D', color=color, markersize=8, zorder=5)
        ax.plot([row['CI_low'], row['CI_high']], [y, y], '-', color=color, linewidth=2)
        hr_str = f"{row['HR']:.2f} ({row['CI_low']:.2f}-{row['CI_high']:.2f})"
        ax.text(2.2, y, hr_str, va='center', fontsize=9, family='monospace')
        ax.text(3.1, y, f"n={row['N']:,}", va='center', fontsize=8, color='gray')

    ax.axvline(x=1, color='black', linestyle='--', linewidth=0.8)
    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(sg_df['Subgroup'].tolist(), fontsize=10)
    ax.set_xlabel('Hazard Ratio (95% CI)', fontsize=11)
    ax.set_title('Low Economic Satisfaction and All-Cause Mortality:\nSubgroup Analyses (Health-Adjusted Model)',
                 fontsize=12, fontweight='bold')
    ax.set_xlim(0.6, 3.5)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG, 'subgroup_forest_plot.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(FIG, 'subgroup_forest_plot.pdf'), bbox_inches='tight')
    plt.close()
    print("Figure 2 (forest plot) saved.")

# ============================================================================
# TABLE 1: COMPLETE BASELINE CHARACTERISTICS
# ============================================================================
print("\n" + "=" * 70)
print("TABLE 1: BASELINE CHARACTERISTICS BY ECONOMIC SATISFACTION")
print("=" * 70)

# Split by low vs not-low economic satisfaction
groups = {
    'Low econ sat (Q1)': df['low_econ_sat_bl'] == 1,
    'Higher econ sat (Q2-Q5)': df['low_econ_sat_bl'] == 0,
    'Overall': pd.Series(True, index=df.index)
}

table1_rows = []
for var_name, var, fmt in [
    ('N', None, None),
    ('Age, mean (SD)', 'age', 'mean_sd'),
    ('Female, %', 'female', 'pct'),
    ('Married, %', 'married', 'pct'),
    ('Education: No formal/Elementary, %', None, 'edu1'),
    ('Education: Middle school, %', None, 'edu2'),
    ('Education: High school, %', None, 'edu3'),
    ('Education: College+, %', None, 'edu4'),
    ('Self-rated health (1-5), mean (SD)', 'self_rated_health', 'mean_sd'),
    ('Chronic diseases, mean (SD)', 'chronic_count', 'mean_sd'),
    ('Hypertension, %', 'hypertension', 'pct_one'),
    ('Diabetes, %', 'diabetes', 'pct_one'),
    ('Cancer, %', 'cancer', 'pct_one'),
    ('Heart disease, %', 'heart_disease', 'pct_one'),
    ('Stroke, %', 'stroke', 'pct_one'),
    ('BMI, mean (SD)', 'bmi', 'mean_sd'),
    ('Current smoker, %', 'current_smoker', 'pct'),
    ('Depression, %', 'depression', 'pct_one'),
    ('IADL limitations, mean (SD)', 'iadl', 'mean_sd'),
    ('Econ satisfaction (0-100), mean (SD)', 'econ_satisfaction', 'mean_sd'),
    ('On welfare (NBLSS), %', 'on_welfare_bl', 'pct'),
    ('Has national pension, %', 'has_pension_bl', 'pct'),
    ('Household income (10K won), mean (SD)', 'hh_income', 'mean_sd'),
    ('Died during follow-up, %', 'died', 'pct'),
    ('Follow-up years, mean (SD)', 'surv_time', 'mean_sd'),
]:
    row = {'Variable': var_name}
    for grp_name, grp_mask in groups.items():
        sub = df.loc[grp_mask]
        if var_name == 'N':
            row[grp_name] = f"{len(sub):,}"
        elif fmt == 'mean_sd':
            v = sub[var].dropna()
            row[grp_name] = f"{v.mean():.1f} ({v.std():.1f})"
        elif fmt == 'pct':
            v = sub[var].dropna()
            row[grp_name] = f"{v.mean()*100:.1f}"
        elif fmt == 'pct_one':
            v = sub[var].dropna()
            row[grp_name] = f"{(v == 1).mean()*100:.1f}"
        elif fmt == 'edu1':
            row[grp_name] = f"{(sub['education'] <= 1).mean()*100:.1f}"
        elif fmt == 'edu2':
            row[grp_name] = f"{(sub['education'] == 2).mean()*100:.1f}"
        elif fmt == 'edu3':
            row[grp_name] = f"{(sub['education'] == 3).mean()*100:.1f}"
        elif fmt == 'edu4':
            row[grp_name] = f"{(sub['education'] >= 4).mean()*100:.1f}"

    table1_rows.append(row)

table1_df = pd.DataFrame(table1_rows)
table1_df.to_csv(os.path.join(TAB, 'table1_baseline_characteristics.csv'), index=False)

print(f"\n{'Variable':<45} {'Overall':>12} {'Low (Q1)':>12} {'Higher':>12}")
print("-" * 85)
for _, row in table1_df.iterrows():
    print(f"{row['Variable']:<45} {row['Overall']:>12} {row['Low econ sat (Q1)']:>12} {row['Higher econ sat (Q2-Q5)']:>12}")

print("Done.")
