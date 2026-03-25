"""
03_cox_models.py
Financial Distress and All-Cause Mortality Among Older Adults in South Korea

Cox Proportional Hazards Models:
1. Kaplan-Meier survival curves by financial distress
2. Sequential Cox models (unadjusted → fully adjusted)
3. Multiple financial distress operationalizations
4. Subgroup analyses
5. Generate tables and figures
"""

import pandas as pd
import numpy as np
import os
import logging
import warnings
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

from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import logrank_test
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from config import BASE, OUT
from model_specs import *
FIG = os.path.join(OUT, "figures")
TAB = os.path.join(OUT, "tables")

# ============================================================================
# LOAD DATA
# ============================================================================
print("Loading data...")
baseline = pd.read_parquet(os.path.join(OUT, 'baseline_analytic.parquet'))
panel = pd.read_parquet(os.path.join(OUT, 'panel_data.parquet'))

print(f"Baseline sample: N={len(baseline):,}, Deaths={baseline['died'].sum():,}")

# ============================================================================
# FIGURE 1: KAPLAN-MEIER CURVES BY ECONOMIC SATISFACTION QUINTILE
# ============================================================================
print("\nGenerating Kaplan-Meier curves...")

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Panel A: By economic satisfaction quintile
ax = axes[0]
colors = ['#d62728', '#ff7f0e', '#bcbd22', '#2ca02c', '#1f77b4']
kmf = KaplanMeierFitter()
quintiles = ['Q1 (lowest)', 'Q2', 'Q3', 'Q4', 'Q5 (highest)']

for i, q in enumerate(quintiles):
    mask = baseline['econ_sat_quintile'] == q
    if mask.sum() > 0:
        kmf.fit(baseline.loc[mask, 'surv_time'],
                baseline.loc[mask, 'died'],
                label=q)
        kmf.plot_survival_function(ax=ax, color=colors[i], linewidth=1.5)

ax.set_xlabel('Follow-up time (years)', fontsize=11)
ax.set_ylabel('Survival probability', fontsize=11)
ax.set_title('A. By economic satisfaction quintile', fontsize=12, fontweight='bold')
ax.legend(fontsize=9, loc='lower left')
ax.set_ylim(0.4, 1.02)
ax.set_xlim(0, 17)

# Log-rank test
econ_groups = baseline.dropna(subset=['econ_sat_quintile', 'surv_time', 'died'])
from lifelines.statistics import multivariate_logrank_test
result = multivariate_logrank_test(
    econ_groups['surv_time'],
    econ_groups['econ_sat_quintile'],
    econ_groups['died']
)
_p_econ = result.p_value
_p_econ_str = f"p={_p_econ:.4f}" if _p_econ >= 0.001 else "p<0.001"
ax.text(0.98, 0.98, f'Log-rank {_p_econ_str}',
        transform=ax.transAxes, ha='right', va='top', fontsize=9,
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Panel B: By welfare receipt
ax = axes[1]
for val, label, color in [(0, 'Not on welfare', '#1f77b4'), (1, 'On welfare', '#d62728')]:
    mask = baseline['on_welfare_bl'] == val
    if mask.sum() > 0:
        kmf.fit(baseline.loc[mask, 'surv_time'],
                baseline.loc[mask, 'died'],
                label=label)
        kmf.plot_survival_function(ax=ax, color=color, linewidth=1.5)

ax.set_xlabel('Follow-up time (years)', fontsize=11)
ax.set_ylabel('Survival probability', fontsize=11)
ax.set_title('B. By welfare receipt', fontsize=12, fontweight='bold')
ax.legend(fontsize=10, loc='lower left')
ax.set_ylim(0.2, 1.02)
ax.set_xlim(0, 17)

# Log-rank test
welfare_groups = baseline.dropna(subset=['on_welfare_bl', 'surv_time', 'died'])
lr = logrank_test(
    welfare_groups.loc[welfare_groups['on_welfare_bl'] == 0, 'surv_time'],
    welfare_groups.loc[welfare_groups['on_welfare_bl'] == 1, 'surv_time'],
    welfare_groups.loc[welfare_groups['on_welfare_bl'] == 0, 'died'],
    welfare_groups.loc[welfare_groups['on_welfare_bl'] == 1, 'died'],
)
_p_welfare = lr.p_value
_p_welfare_str = f"p={_p_welfare:.4f}" if _p_welfare >= 0.001 else "p<0.001"
ax.text(0.98, 0.98, f'Log-rank {_p_welfare_str}',
        transform=ax.transAxes, ha='right', va='top', fontsize=9,
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig(os.path.join(FIG, 'figure1_km_curves.png'), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(FIG, 'figure1_km_curves.pdf'), bbox_inches='tight')
plt.close()
print("Figure 1 saved.")

# ============================================================================
# TABLE 2: COX PROPORTIONAL HAZARDS MODELS
# ============================================================================
print("\nFitting Cox models...")

# Prepare analysis dataset
df = baseline.copy()

# Recode variables for regression
df['age_10'] = df['age'] / 10  # per 10-year increment
df['edu_middle'] = (df['education'] == 2).astype(float)
df['edu_high'] = (df['education'] == 3).astype(float)
df['edu_college'] = (df['education'] >= 4).astype(float)

# Low economic satisfaction (bottom quintile = financial distress)
df['low_econ_sat_bl'] = (df['econ_sat_quintile'] == 'Q1 (lowest)').astype(float)

# Economic satisfaction continuous (per 10-point decrease = more distress)
df['econ_sat_decrease_10'] = (100 - df['econ_satisfaction']) / 10

# Clean: drop rows with missing key variables
complete_vars_basic = ['surv_time', 'died', 'age', 'female']
df_basic = df.dropna(subset=complete_vars_basic)

# --- Model 1: Unadjusted ---
print("\n--- Model 1: Unadjusted ---")
results_table = []

# 1a. Low economic satisfaction (binary)
cph = CoxPHFitter()
model_df = df_basic[['surv_time', 'died', 'low_econ_sat_bl']].dropna()
cph.fit(model_df, duration_col='surv_time', event_col='died')
hr = np.exp(cph.params_['low_econ_sat_bl'])
ci_low = np.exp(cph.confidence_intervals_.iloc[0, 0])
ci_high = np.exp(cph.confidence_intervals_.iloc[0, 1])
p = cph.summary['p']['low_econ_sat_bl']
print(f"  Low econ satisfaction (unadjusted): HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")
results_table.append({
    'Exposure': 'Low economic satisfaction (Q1)',
    'Model': 'Unadjusted',
    'HR': hr, 'CI_low': ci_low, 'CI_high': ci_high, 'p': p,
    'N': len(model_df), 'Events': model_df['died'].sum()
})

# 1b. Economic satisfaction continuous
cph = CoxPHFitter()
model_df = df_basic[['surv_time', 'died', 'econ_sat_decrease_10']].dropna()
cph.fit(model_df, duration_col='surv_time', event_col='died')
hr = np.exp(cph.params_['econ_sat_decrease_10'])
ci_low = np.exp(cph.confidence_intervals_.iloc[0, 0])
ci_high = np.exp(cph.confidence_intervals_.iloc[0, 1])
p = cph.summary['p']['econ_sat_decrease_10']
print(f"  Econ sat decrease per 10pts (unadj): HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")
results_table.append({
    'Exposure': 'Economic dissatisfaction (per 10-pt decrease)',
    'Model': 'Unadjusted',
    'HR': hr, 'CI_low': ci_low, 'CI_high': ci_high, 'p': p,
    'N': len(model_df), 'Events': model_df['died'].sum()
})

# 1c. Welfare receipt
cph = CoxPHFitter()
model_df = df_basic[['surv_time', 'died', 'on_welfare_bl']].dropna()
cph.fit(model_df, duration_col='surv_time', event_col='died')
hr = np.exp(cph.params_['on_welfare_bl'])
ci_low = np.exp(cph.confidence_intervals_.iloc[0, 0])
ci_high = np.exp(cph.confidence_intervals_.iloc[0, 1])
p = cph.summary['p']['on_welfare_bl']
print(f"  Welfare receipt (unadjusted): HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")
results_table.append({
    'Exposure': 'Welfare receipt (NBLSS)',
    'Model': 'Unadjusted',
    'HR': hr, 'CI_low': ci_low, 'CI_high': ci_high, 'p': p,
    'N': len(model_df), 'Events': model_df['died'].sum()
})

# --- Model 2: Demographic-adjusted ---
print("\n--- Model 2: Demographic-adjusted ---")
demo_covs = ['age_10', 'female', 'married', 'edu_middle', 'edu_high', 'edu_college']

for exposure, label in [('low_econ_sat_bl', 'Low econ sat'),
                        ('econ_sat_decrease_10', 'Econ sat decrease/10'),
                        ('on_welfare_bl', 'Welfare')]:
    cph = CoxPHFitter()
    covs = [exposure] + demo_covs
    model_df = df_basic[['surv_time', 'died'] + covs].dropna()
    cph.fit(model_df, duration_col='surv_time', event_col='died')
    hr = np.exp(cph.params_[exposure])
    ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
    ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
    p = cph.summary['p'][exposure]
    print(f"  {label}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")
    results_table.append({
        'Exposure': label if label != 'Econ sat decrease/10' else 'Economic dissatisfaction (per 10-pt decrease)',
        'Model': 'Demographic-adjusted',
        'HR': hr, 'CI_low': ci_low, 'CI_high': ci_high, 'p': p,
        'N': len(model_df), 'Events': model_df['died'].sum()
    })
    if exposure == 'low_econ_sat_bl':
        results_table[-1]['Exposure'] = 'Low economic satisfaction (Q1)'
    elif exposure == 'on_welfare_bl':
        results_table[-1]['Exposure'] = 'Welfare receipt (NBLSS)'

# --- Model 3: + Health ---
print("\n--- Model 3: Health-adjusted ---")
health_covs = ['self_rated_health', 'chronic_count', 'bmi', 'current_smoker', 'ever_smoker']

for exposure, label in [('low_econ_sat_bl', 'Low economic satisfaction (Q1)'),
                        ('econ_sat_decrease_10', 'Economic dissatisfaction (per 10-pt decrease)'),
                        ('on_welfare_bl', 'Welfare receipt (NBLSS)')]:
    cph = CoxPHFitter()
    covs = [exposure] + demo_covs + health_covs
    model_df = df_basic[['surv_time', 'died'] + covs].dropna()
    cph.fit(model_df, duration_col='surv_time', event_col='died')
    hr = np.exp(cph.params_[exposure])
    ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
    ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
    p = cph.summary['p'][exposure]
    print(f"  {label}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")
    results_table.append({
        'Exposure': label,
        'Model': 'Health-adjusted',
        'HR': hr, 'CI_low': ci_low, 'CI_high': ci_high, 'p': p,
        'N': len(model_df), 'Events': model_df['died'].sum()
    })

# --- Model 4: Fully adjusted (+ depression, IADL, social) ---
print("\n--- Model 4: Fully adjusted ---")
full_covs = demo_covs + health_covs + ['depression', 'iadl']
# Note: uses original health covariates (without drinking/exercise)

for exposure, label in [('low_econ_sat_bl', 'Low economic satisfaction (Q1)'),
                        ('econ_sat_decrease_10', 'Economic dissatisfaction (per 10-pt decrease)'),
                        ('on_welfare_bl', 'Welfare receipt (NBLSS)')]:
    cph = CoxPHFitter()
    covs = [exposure] + full_covs
    model_df = df_basic[['surv_time', 'died'] + covs].dropna()
    cph.fit(model_df, duration_col='surv_time', event_col='died')
    hr = np.exp(cph.params_[exposure])
    ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
    ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
    p = cph.summary['p'][exposure]
    print(f"  {label}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")
    results_table.append({
        'Exposure': label,
        'Model': 'Fully adjusted',
        'HR': hr, 'CI_low': ci_low, 'CI_high': ci_high, 'p': p,
        'N': len(model_df), 'Events': model_df['died'].sum()
    })

    # Print all coefficients for the fully adjusted model with low econ sat
    if exposure == 'low_econ_sat_bl':
        print("\n  Full model coefficients:")
        summary = cph.summary
        for var in summary.index:
            hr_v = np.exp(summary.loc[var, 'coef'])
            ci_l = np.exp(summary.loc[var, 'coef lower 95%'])
            ci_h = np.exp(summary.loc[var, 'coef upper 95%'])
            p_v = summary.loc[var, 'p']
            sig = '***' if p_v < 0.001 else '**' if p_v < 0.01 else '*' if p_v < 0.05 else ''
            print(f"    {var:25s}: HR={hr_v:.3f} ({ci_l:.3f}-{ci_h:.3f}) p={p_v:.4f} {sig}")

# ============================================================================
# SAVE RESULTS TABLE
# ============================================================================
results_df = pd.DataFrame(results_table)
results_df['HR_CI'] = results_df.apply(
    lambda r: f"{r['HR']:.2f} ({r['CI_low']:.2f}-{r['CI_high']:.2f})", axis=1
)
results_df.to_csv(os.path.join(TAB, 'table2_cox_models.csv'), index=False)
print(f"\nResults table saved to {os.path.join(TAB, 'table2_cox_models.csv')}")

# Print formatted table
print("\n" + "=" * 90)
print("TABLE 2: Association Between Financial Distress and All-Cause Mortality")
print("=" * 90)
print(f"{'Exposure':<45} {'Model':<20} {'HR (95% CI)':<25} {'p':<10}")
print("-" * 90)
for _, row in results_df.iterrows():
    p_str = f"<0.001" if row['p'] < 0.001 else f"{row['p']:.3f}"
    print(f"{row['Exposure']:<45} {row['Model']:<20} {row['HR_CI']:<25} {p_str:<10}")

# ============================================================================
# SUBGROUP ANALYSES
# ============================================================================
print("\n" + "=" * 70)
print("SUBGROUP ANALYSES: Low Economic Satisfaction and Mortality")
print("=" * 70)

subgroups = {
    'Male': df_basic['female'] == 0,
    'Female': df_basic['female'] == 1,
    'Age 45-64': df_basic['age'] < 65,
    'Age 65+': df_basic['age'] >= 65,
    'Married': df_basic['married'] == 1,
    'Not married': df_basic['married'] == 0,
    'Has pension': df_basic['has_pension_bl'] == 1,
    'No pension': df_basic['has_pension_bl'] == 0,
    'No chronic disease': df_basic['chronic_count'] == 0,
    '1+ chronic diseases': df_basic['chronic_count'] >= 1,
}

subgroup_results = []
# Variables to drop when they are the stratification variable
_drop_map = {
    'Male': ['female'], 'Female': ['female'],
    'Married': ['married'], 'Not married': ['married'],
    'No chronic disease': ['chronic_count'], '1+ chronic diseases': ['chronic_count'],
}
for label, mask in subgroups.items():
    sub = df_basic.loc[mask].copy()
    covs_sub = [c for c in demo_covs + health_covs if c not in _drop_map.get(label, [])]
    covs = ['low_econ_sat_bl'] + covs_sub
    model_df = sub[['surv_time', 'died'] + covs].dropna()
    if model_df['died'].sum() < 20 or model_df['low_econ_sat_bl'].sum() < 10:
        print(f"  {label}: Insufficient events, skipping")
        continue
    try:
        cph = CoxPHFitter()
        cph.fit(model_df, duration_col='surv_time', event_col='died')
        hr = np.exp(cph.params_['low_econ_sat_bl'])
        ci_low = np.exp(cph.confidence_intervals_.loc['low_econ_sat_bl'].iloc[0])
        ci_high = np.exp(cph.confidence_intervals_.loc['low_econ_sat_bl'].iloc[1])
        p = cph.summary['p']['low_econ_sat_bl']
        n = len(model_df)
        events = model_df['died'].sum()
        print(f"  {label}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}, N={n:,}, Events={events:,}")
        subgroup_results.append({
            'Subgroup': label, 'HR': hr, 'CI_low': ci_low, 'CI_high': ci_high,
            'p': p, 'N': n, 'Events': events
        })
    except Exception as e:
        print(f"  {label}: Model failed - {e}")

# Save subgroup results
if subgroup_results:
    sg_df = pd.DataFrame(subgroup_results)
    sg_df.to_csv(os.path.join(TAB, 'subgroup_analyses.csv'), index=False)

# ============================================================================
# FIGURE 2: FOREST PLOT OF SUBGROUP ANALYSES
# ============================================================================
print("\nGenerating forest plot...")

if subgroup_results:
    sg_df = pd.DataFrame(subgroup_results)

    fig, ax = plt.subplots(figsize=(10, 8))

    y_positions = range(len(sg_df) - 1, -1, -1)

    for i, (_, row) in enumerate(sg_df.iterrows()):
        y = list(y_positions)[i]
        color = '#d62728' if row['p'] < 0.05 else '#1f77b4'
        ax.plot(row['HR'], y, 'o', color=color, markersize=8)
        ax.plot([row['CI_low'], row['CI_high']], [y, y], '-', color=color, linewidth=2)

        # Label
        hr_str = f"{row['HR']:.2f} ({row['CI_low']:.2f}-{row['CI_high']:.2f})"
        ax.text(3.5, y, hr_str, va='center', fontsize=9)

    ax.axvline(x=1, color='black', linestyle='--', linewidth=0.8)
    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(sg_df['Subgroup'].tolist(), fontsize=10)
    ax.set_xlabel('Hazard Ratio (95% CI)', fontsize=11)
    ax.set_title('Low Economic Satisfaction and All-Cause Mortality:\nSubgroup Analyses (Health-Adjusted)',
                 fontsize=12, fontweight='bold')
    ax.set_xlim(0.5, 4.5)

    plt.tight_layout()
    plt.savefig(os.path.join(FIG, 'subgroup_forest_plot.png'), dpi=300, bbox_inches='tight')
    plt.savefig(os.path.join(FIG, 'subgroup_forest_plot.pdf'), bbox_inches='tight')
    plt.close()
    print("Figure 2 saved.")

# ============================================================================
# SENSITIVITY: WEALTH SHOCK ANALYSIS (waves 3+ only)
# ============================================================================
print("\n" + "=" * 70)
print("SENSITIVITY: WEALTH SHOCK ANALYSIS")
print("=" * 70)

# For wealth shock, we use the panel data with time-varying covariates
# Simplified: use wealth shock at any point as a baseline exposure
ws_ever = panel.groupby('pid')['wealth_shock'].max().reset_index()
ws_ever.columns = ['pid', 'ever_wealth_shock']

df_ws = df.merge(ws_ever, on='pid', how='left')
df_ws['ever_wealth_shock'] = df_ws['ever_wealth_shock'].fillna(0)

print(f"\nWealth shock ever experienced: {df_ws['ever_wealth_shock'].mean()*100:.1f}%")
print(f"Deaths among wealth-shocked: {df_ws.loc[df_ws['ever_wealth_shock']==1, 'died'].mean()*100:.1f}%")
print(f"Deaths among non-shocked: {df_ws.loc[df_ws['ever_wealth_shock']==0, 'died'].mean()*100:.1f}%")

# Cox model for wealth shock
for model_name, covs in [
    ('Unadjusted', []),
    ('Demographic-adjusted', demo_covs),
    ('Health-adjusted', demo_covs + health_covs),
    ('Fully adjusted', full_covs)
]:
    cph = CoxPHFitter()
    vars_list = ['ever_wealth_shock'] + covs
    model_df = df_ws[['surv_time', 'died'] + vars_list].dropna()
    try:
        cph.fit(model_df, duration_col='surv_time', event_col='died')
        hr = np.exp(cph.params_['ever_wealth_shock'])
        ci_low = np.exp(cph.confidence_intervals_.loc['ever_wealth_shock'].iloc[0])
        ci_high = np.exp(cph.confidence_intervals_.loc['ever_wealth_shock'].iloc[1])
        p = cph.summary['p']['ever_wealth_shock']
        print(f"  {model_name}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")
    except Exception as e:
        print(f"  {model_name}: Failed - {e}")

# ============================================================================
# DOSE-RESPONSE: ECONOMIC SATISFACTION QUINTILES
# ============================================================================
print("\n" + "=" * 70)
print("DOSE-RESPONSE: MORTALITY BY ECONOMIC SATISFACTION QUINTILE")
print("=" * 70)

# Create dummies for quintiles (reference: Q5 highest)
for q in ['Q1 (lowest)', 'Q2', 'Q3', 'Q4']:
    df_basic[f'econ_q_{q[:2]}'] = (df_basic['econ_sat_quintile'] == q).astype(float)

q_covs = ['econ_q_Q1', 'econ_q_Q2', 'econ_q_Q3', 'econ_q_Q4'] + demo_covs + health_covs
model_df = df_basic[['surv_time', 'died'] + q_covs].dropna()

cph = CoxPHFitter()
cph.fit(model_df, duration_col='surv_time', event_col='died')

print("\nHealth-adjusted HRs by economic satisfaction quintile (ref: Q5 highest):")
for var in ['econ_q_Q1', 'econ_q_Q2', 'econ_q_Q3', 'econ_q_Q4']:
    hr = np.exp(cph.params_[var])
    ci_low = np.exp(cph.confidence_intervals_.loc[var].iloc[0])
    ci_high = np.exp(cph.confidence_intervals_.loc[var].iloc[1])
    p = cph.summary['p'][var]
    q_label = var.replace('econ_q_', '')
    print(f"  {q_label} vs Q5: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")

# P for trend
cph_trend = CoxPHFitter()
df_basic['econ_quintile_num'] = df_basic['econ_sat_quintile'].map({
    'Q1 (lowest)': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4, 'Q5 (highest)': 5
})
trend_covs = ['econ_quintile_num'] + demo_covs + health_covs
trend_df = df_basic[['surv_time', 'died'] + trend_covs].dropna()
cph_trend.fit(trend_df, duration_col='surv_time', event_col='died')
p_trend = cph_trend.summary['p']['econ_quintile_num']
print(f"\n  P for trend: {p_trend:.6f}")

# ============================================================================
# SENSITIVITY: EXCLUDE DEATHS WITHIN FIRST 2 YEARS
# ============================================================================
print("\n" + "=" * 70)
print("SENSITIVITY: EXCLUDING EARLY DEATHS (< 2 years)")
print("=" * 70)

df_no_early = df_basic[~((df_basic['died'] == 1) & (df_basic['surv_time'] < 2))].copy()
print(f"Sample after excluding early deaths: N={len(df_no_early):,}, Deaths={df_no_early['died'].sum():,}")

covs = ['low_econ_sat_bl'] + demo_covs + health_covs
model_df = df_no_early[['surv_time', 'died'] + covs].dropna()
cph = CoxPHFitter()
cph.fit(model_df, duration_col='surv_time', event_col='died')
hr = np.exp(cph.params_['low_econ_sat_bl'])
ci_low = np.exp(cph.confidence_intervals_.loc['low_econ_sat_bl'].iloc[0])
ci_high = np.exp(cph.confidence_intervals_.loc['low_econ_sat_bl'].iloc[1])
p = cph.summary['p']['low_econ_sat_bl']
print(f"Low econ sat (excl. early deaths): HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")

print("Done.")
