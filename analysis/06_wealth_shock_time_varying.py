"""
06_wealth_shock_time_varying.py
Time-Varying Cox Models for Negative Wealth Shocks and All-Cause Mortality

Proper implementation following Pool et al. (2018, JAMA):
- Person-period (counting process) format: each row = one wave-to-wave interval
- Wealth shock defined as >=75% decline in household net worth between waves
- Time-varying exposure updated at each interval
- Also: personal net assets version (available from wave 1)
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', message='.*delta_grad.*')
warnings.filterwarnings('ignore', message='.*convergence.*')

from lifelines import CoxPHFitter, KaplanMeierFitter
from lifelines.statistics import logrank_test
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from config import BASE, DATA, OUT
from model_specs import *
FIG = os.path.join(OUT, "figures")
TAB = os.path.join(OUT, "tables")

WAVE_YEARS = {1: 2006, 2: 2008, 3: 2010, 4: 2012, 5: 2014, 6: 2016, 7: 2018, 8: 2020, 9: 2022}
MAX_STUDY_YEAR = max(WAVE_YEARS.values())  # end of study period

# ============================================================================
# 1. LOAD PANEL DATA AND DEATH RECORDS
# ============================================================================
print("Loading data...")
panel = pd.read_parquet(os.path.join(OUT, 'panel_data.parquet'))
deaths = pd.read_parquet(os.path.join(OUT, 'death_records.parquet'))

# Clean deaths
deaths['death_year'] = pd.to_numeric(deaths['death_year'], errors='coerce')
deaths['death_month'] = pd.to_numeric(deaths['death_month'], errors='coerce')
deaths = deaths[(deaths['death_year'] >= 2006) & (deaths['death_year'] <= 2023)]
deaths = deaths.sort_values('death_year').groupby('pid').first().reset_index()

print(f"Panel: {len(panel):,} person-waves, {panel['pid'].nunique():,} persons")
print(f"Deaths: {len(deaths):,}")

# ============================================================================
# 2. BUILD PERSON-PERIOD DATASET (COUNTING PROCESS FORMAT)
# ============================================================================
print("\nBuilding person-period dataset...")

# For each person, we need intervals between consecutive waves they participated in.
# Time is measured in years from their first interview.

panel = panel.sort_values(['pid', 'wave']).reset_index(drop=True)

# Compute interview date as fractional year
panel['iw_date'] = panel['iw_year'] + (panel['iw_month'].fillna(6) - 1) / 12

# Get first interview date per person
first_iw = panel.groupby('pid')['iw_date'].min().reset_index()
first_iw.columns = ['pid', 'first_iw_date']
panel = panel.merge(first_iw, on='pid')

# Time since first interview (in years)
panel['t'] = panel['iw_date'] - panel['first_iw_date']

# Merge death info
panel = panel.merge(deaths[['pid', 'death_year', 'death_month']], on='pid', how='left')
panel['died_ever'] = panel['death_year'].notna().astype(int)
panel['death_date'] = panel['death_year'] + (panel['death_month'].fillna(6) - 1) / 12
panel['death_t'] = panel['death_date'] - panel['first_iw_date']

# Compute wealth shock between consecutive waves
panel['prev_hh_nw'] = panel.groupby('pid')['hh_net_worth'].shift(1)
panel['prev_p_na'] = panel.groupby('pid')['p_net_assets'].shift(1)
panel['prev_wave'] = panel.groupby('pid')['wave'].shift(1)
panel['is_consecutive'] = (panel['wave'] - panel['prev_wave']) == 1

# Household wealth shock (>=75% decline)
def hh_wealth_shock(row):
    if not row['is_consecutive']:
        return np.nan
    prev = row['prev_hh_nw']
    curr = row['hh_net_worth']
    if pd.isna(prev) or pd.isna(curr):
        return np.nan
    if prev > 0:
        return 1.0 if (curr - prev) / prev <= -0.75 else 0.0
    elif prev == 0:
        return 1.0 if curr < -1000 else 0.0  # meaningful negative = shock
    else:  # prev < 0
        return 1.0 if curr < prev * 1.75 else 0.0  # got 75% worse

panel['hh_wealth_shock'] = panel.apply(hh_wealth_shock, axis=1)

# Personal net asset shock (>=75% decline)
def p_wealth_shock(row):
    if not row['is_consecutive']:
        return np.nan
    prev = row['prev_p_na']
    curr = row['p_net_assets']
    if pd.isna(prev) or pd.isna(curr):
        return np.nan
    if prev > 0:
        return 1.0 if (curr - prev) / prev <= -0.75 else 0.0
    elif prev == 0:
        return 1.0 if curr < -1000 else 0.0
    else:
        return 1.0 if curr < prev * 1.75 else 0.0

panel['p_wealth_shock'] = panel.apply(p_wealth_shock, axis=1)

# "Absorbed" shock: once shocked, stays shocked (ever-shocked up to time t)
panel['hh_shock_cumulative'] = panel.groupby('pid')['hh_wealth_shock'].cummax()
panel['p_shock_cumulative'] = panel.groupby('pid')['p_wealth_shock'].cummax()

# Derive married from marital (1=married/cohabiting, else=0)
panel['married'] = (panel['marital'] == 1).astype(float)

# LOCF imputation within person for chronic_count and depression (72-78% coverage)
panel = panel.sort_values(['pid', 'wave'])
for col in ['chronic_count', 'depression']:
    panel[col] = panel.groupby('pid')[col].ffill()

# ============================================================================
# 3. BUILD COUNTING PROCESS INTERVALS
# ============================================================================
print("Building counting process intervals...")

# For each person, create intervals: [t_i, t_{i+1}) with covariates from wave i
# Event indicator: did death occur in this interval?

intervals = []
grouped = panel.groupby('pid')

for pid, grp in grouped:
    grp = grp.sort_values('wave')
    rows = grp.to_dict('records')

    for i in range(len(rows)):
        row = rows[i]

        # Start time
        t_start = row['t']

        # Stop time: next interview or death or censoring
        if i < len(rows) - 1:
            t_stop = rows[i + 1]['t']
        else:
            # Last observed wave
            if row['died_ever'] == 1 and not pd.isna(row['death_t']):
                t_stop = row['death_t']
            else:
                # Censor at the midpoint between last interview and next
                # scheduled wave (biennial), or end of study if last wave
                cur_wave = row['wave']
                if cur_wave < max(WAVE_YEARS):
                    next_wave_yr = WAVE_YEARS.get(cur_wave + 1, WAVE_YEARS[cur_wave] + 2)
                    midpoint_yr = (WAVE_YEARS[cur_wave] + next_wave_yr) / 2
                    t_stop = (midpoint_yr - row['first_iw_date'])
                else:
                    # Last study wave: censor at end of study (last wave year)
                    t_stop = MAX_STUDY_YEAR - row['first_iw_date']

        # Event: death in this interval?
        if row['died_ever'] == 1 and not pd.isna(row['death_t']):
            event = 1 if (row['death_t'] > t_start and row['death_t'] <= t_stop) else 0
            # Adjust stop time to death time if death occurs in interval
            if event == 1:
                t_stop = row['death_t']
        else:
            event = 0

        # Must have positive interval
        if t_stop <= t_start:
            continue

        interval = {
            'pid': pid,
            'wave': row['wave'],
            't_start': t_start,
            't_stop': t_stop,
            'event': event,
            # Exposures (time-varying)
            'hh_wealth_shock': row.get('hh_wealth_shock', np.nan),
            'hh_shock_cumulative': row.get('hh_shock_cumulative', np.nan),
            'p_wealth_shock': row.get('p_wealth_shock', np.nan),
            'p_shock_cumulative': row.get('p_shock_cumulative', np.nan),
            'econ_satisfaction': row.get('econ_satisfaction', np.nan),
            'low_econ_sat': row.get('low_econ_sat', np.nan),
            'on_welfare': row.get('on_welfare', np.nan),
            # Time-varying covariates
            'age': row.get('age', np.nan),
            'female': row.get('female', np.nan),
            'married': row.get('married', np.nan),
            'education': row.get('education', np.nan),
            'self_rated_health': row.get('self_rated_health', np.nan),
            'chronic_count': row.get('chronic_count', np.nan),
            'bmi': row.get('bmi', np.nan),
            'smoking': row.get('smoking', np.nan),
            'depression': row.get('depression', np.nan),
            'iadl': row.get('iadl', np.nan),
            'hh_net_worth': row.get('hh_net_worth', np.nan),
            'hh_income': row.get('hh_income', np.nan),
        }
        intervals.append(interval)

pp = pd.DataFrame(intervals)
print(f"Person-period dataset: {len(pp):,} intervals, {pp['pid'].nunique():,} persons")
print(f"Events: {pp['event'].sum():,}")
print(f"Total person-time: {(pp['t_stop'] - pp['t_start']).sum():,.0f} person-years")

# Flag intervals that span more than one wave gap (>2.5 years)
# These occur when participants miss waves; covariates are carried forward
pp['interval_years'] = pp['t_stop'] - pp['t_start']
extended = pp['interval_years'] > 2.5
n_extended = extended.sum()
n_events_extended = pp.loc[extended, 'event'].sum()
print(f"\nExtended intervals (>2.5 years): {n_extended:,} of {len(pp):,} "
      f"({n_extended/len(pp)*100:.1f}%)")
print(f"Events in extended intervals: {int(n_events_extended):,} of "
      f"{int(pp['event'].sum()):,} ({n_events_extended/pp['event'].sum()*100:.1f}%)")
print(f"Mean interval length: {pp['interval_years'].mean():.2f} years "
      f"(median: {pp['interval_years'].median():.2f})")

# Verify key covariates
print("\nCovariate coverage in person-period data:")
for col in ['married', 'low_econ_sat', 'chronic_count', 'depression', 'hh_wealth_shock']:
    if col in pp.columns:
        print(f"  {col}: {pp[col].notna().mean()*100:.1f}%")

# ============================================================================
# 4. DESCRIPTIVE: WEALTH SHOCK PREVALENCE
# ============================================================================
print("\n" + "=" * 70)
print("WEALTH SHOCK DESCRIPTIVES")
print("=" * 70)

# Household wealth shock by wave
print("\nHousehold wealth shock (>=75% NW decline) by wave:")
for w in range(2, 10):
    mask = (panel['wave'] == w) & panel['hh_wealth_shock'].notna()
    if mask.sum() > 0:
        pct = panel.loc[mask, 'hh_wealth_shock'].mean() * 100
        n = mask.sum()
        print(f"  Wave {w} ({WAVE_YEARS[w]}): {pct:.1f}% (N={n:,})")

# Personal wealth shock by wave
print("\nPersonal net asset shock (>=75% decline) by wave:")
for w in range(2, 10):
    mask = (panel['wave'] == w) & panel['p_wealth_shock'].notna()
    if mask.sum() > 0:
        pct = panel.loc[mask, 'p_wealth_shock'].mean() * 100
        n = mask.sum()
        print(f"  Wave {w} ({WAVE_YEARS[w]}): {pct:.1f}% (N={n:,})")

# Overall
hh_valid = panel['hh_wealth_shock'].dropna()
p_valid = panel['p_wealth_shock'].dropna()
print(f"\nOverall HH wealth shock prevalence: {hh_valid.mean()*100:.1f}% across {len(hh_valid):,} person-waves")
print(f"Overall personal wealth shock prevalence: {p_valid.mean()*100:.1f}% across {len(p_valid):,} person-waves")

# How many unique persons ever experienced a shock?
hh_ever = panel[panel['hh_wealth_shock'] == 1]['pid'].nunique()
p_ever = panel[panel['p_wealth_shock'] == 1]['pid'].nunique()
total_persons = panel['pid'].nunique()
print(f"\nPersons ever experiencing HH wealth shock: {hh_ever:,}/{total_persons:,} ({hh_ever/total_persons*100:.1f}%)")
print(f"Persons ever experiencing personal wealth shock: {p_ever:,}/{total_persons:,} ({p_ever/total_persons*100:.1f}%)")

# ============================================================================
# 5. TIME-VARYING COX MODELS: HOUSEHOLD WEALTH SHOCK
# ============================================================================
print("\n" + "=" * 70)
print("TIME-VARYING COX MODELS: HOUSEHOLD WEALTH SHOCK")
print("=" * 70)

# Prepare covariates
pp['age_10'] = pp['age'] / 10
pp['edu_middle'] = (pp['education'] == 2).astype(float)
pp['edu_high'] = (pp['education'] == 3).astype(float)
pp['edu_college'] = (pp['education'] >= 4).astype(float)
pp['current_smoker'] = (pp['smoking'] == 2).astype(float)
pp['ever_smoker'] = np.where(pp['smoking'].isna(), np.nan,
                              (pp['smoking'] > 0).astype(float))

demo_covs = ['age_10', 'female', 'married', 'edu_middle', 'edu_high', 'edu_college']
health_covs = ['self_rated_health', 'chronic_count', 'bmi', 'current_smoker', 'ever_smoker']
full_covs = demo_covs + health_covs + ['depression', 'iadl']

# --- A. Current-wave household wealth shock ---
print("\n--- A. Current-wave HH wealth shock (time-varying) ---")

for model_name, covs in [
    ('Model 1: Unadjusted', []),
    ('Model 2: Demographics', demo_covs),
    ('Model 3: + Health', demo_covs + health_covs),
    ('Model 4: Fully adjusted', full_covs),
]:
    exposure = 'hh_wealth_shock'
    all_vars = [exposure] + covs
    model_df = pp[['t_start', 't_stop', 'event'] + all_vars].dropna()

    if model_df[exposure].sum() < 10 or model_df['event'].sum() < 20:
        print(f"  {model_name}: Insufficient data")
        continue

    try:
        cph = CoxPHFitter(penalizer=0.01)
        cph.fit(model_df, duration_col='t_stop', event_col='event',
                entry_col='t_start')
        hr = np.exp(cph.params_[exposure])
        ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
        ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
        p = cph.summary['p'][exposure]
        n_events = int(model_df['event'].sum())
        n_exposed = int(model_df[exposure].sum())
        print(f"  {model_name}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f} "
              f"[N intervals={len(model_df):,}, events={n_events:,}, exposed={n_exposed:,}]")
    except Exception as e:
        print(f"  {model_name}: Failed - {e}")

# --- B. Cumulative (ever-shocked) household wealth shock ---
print("\n--- B. Cumulative HH wealth shock (ever shocked up to time t) ---")

for model_name, covs in [
    ('Model 1: Unadjusted', []),
    ('Model 2: Demographics', demo_covs),
    ('Model 3: + Health', demo_covs + health_covs),
    ('Model 4: Fully adjusted', full_covs),
]:
    exposure = 'hh_shock_cumulative'
    all_vars = [exposure] + covs
    model_df = pp[['t_start', 't_stop', 'event'] + all_vars].dropna()

    if model_df[exposure].sum() < 10 or model_df['event'].sum() < 20:
        print(f"  {model_name}: Insufficient data")
        continue

    try:
        cph = CoxPHFitter(penalizer=0.01)
        cph.fit(model_df, duration_col='t_stop', event_col='event',
                entry_col='t_start')
        hr = np.exp(cph.params_[exposure])
        ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
        ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
        p = cph.summary['p'][exposure]
        n_events = int(model_df['event'].sum())
        print(f"  {model_name}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f} "
              f"[N={len(model_df):,}, events={n_events:,}]")
    except Exception as e:
        print(f"  {model_name}: Failed - {e}")

# ============================================================================
# 6. TIME-VARYING COX: PERSONAL NET ASSET SHOCK (available from wave 2)
# ============================================================================
print("\n" + "=" * 70)
print("TIME-VARYING COX MODELS: PERSONAL NET ASSET SHOCK")
print("=" * 70)

print("\n--- A. Current-wave personal wealth shock ---")

for model_name, covs in [
    ('Model 1: Unadjusted', []),
    ('Model 2: Demographics', demo_covs),
    ('Model 3: + Health', demo_covs + health_covs),
    ('Model 4: Fully adjusted', full_covs),
]:
    exposure = 'p_wealth_shock'
    all_vars = [exposure] + covs
    model_df = pp[['t_start', 't_stop', 'event'] + all_vars].dropna()

    if model_df[exposure].sum() < 10 or model_df['event'].sum() < 20:
        print(f"  {model_name}: Insufficient data")
        continue

    try:
        cph = CoxPHFitter(penalizer=0.01)
        cph.fit(model_df, duration_col='t_stop', event_col='event',
                entry_col='t_start')
        hr = np.exp(cph.params_[exposure])
        ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
        ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
        p = cph.summary['p'][exposure]
        n_events = int(model_df['event'].sum())
        n_exposed = int(model_df[exposure].sum())
        print(f"  {model_name}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f} "
              f"[N={len(model_df):,}, events={n_events:,}, exposed intervals={n_exposed:,}]")
    except Exception as e:
        print(f"  {model_name}: Failed - {e}")

print("\n--- B. Cumulative personal wealth shock ---")

for model_name, covs in [
    ('Model 1: Unadjusted', []),
    ('Model 2: Demographics', demo_covs),
    ('Model 3: + Health', demo_covs + health_covs),
    ('Model 4: Fully adjusted', full_covs),
]:
    exposure = 'p_shock_cumulative'
    all_vars = [exposure] + covs
    model_df = pp[['t_start', 't_stop', 'event'] + all_vars].dropna()

    if model_df[exposure].sum() < 10 or model_df['event'].sum() < 20:
        print(f"  {model_name}: Insufficient data")
        continue

    try:
        cph = CoxPHFitter(penalizer=0.01)
        cph.fit(model_df, duration_col='t_stop', event_col='event',
                entry_col='t_start')
        hr = np.exp(cph.params_[exposure])
        ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
        ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
        p = cph.summary['p'][exposure]
        n_events = int(model_df['event'].sum())
        print(f"  {model_name}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f} "
              f"[N={len(model_df):,}, events={n_events:,}]")
    except Exception as e:
        print(f"  {model_name}: Failed - {e}")

# ============================================================================
# 7. TIME-VARYING COX: ECONOMIC SATISFACTION (time-varying)
# ============================================================================
print("\n" + "=" * 70)
print("TIME-VARYING COX: ECONOMIC SATISFACTION (UPDATED EACH WAVE)")
print("=" * 70)

pp['econ_sat_decrease_10'] = (100 - pp['econ_satisfaction']) / 10

# Low econ sat (time-varying)
for model_name, covs in [
    ('Model 1: Unadjusted', []),
    ('Model 2: Demographics', demo_covs),
    ('Model 3: + Health', demo_covs + health_covs),
    ('Model 4: Fully adjusted', full_covs),
]:
    exposure = 'low_econ_sat'
    all_vars = [exposure] + covs
    model_df = pp[['t_start', 't_stop', 'event'] + all_vars].dropna()

    try:
        cph = CoxPHFitter(penalizer=0.01)
        cph.fit(model_df, duration_col='t_stop', event_col='event',
                entry_col='t_start')
        hr = np.exp(cph.params_[exposure])
        ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
        ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
        p = cph.summary['p'][exposure]
        n_events = int(model_df['event'].sum())
        print(f"  {model_name}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f} "
              f"[N={len(model_df):,}, events={n_events:,}]")
    except Exception as e:
        print(f"  {model_name}: Failed - {e}")

# Continuous (time-varying)
print("\n  Continuous economic dissatisfaction (per 10-pt decrease, time-varying):")
for model_name, covs in [
    ('Model 4: Fully adjusted', full_covs),
]:
    exposure = 'econ_sat_decrease_10'
    all_vars = [exposure] + covs
    model_df = pp[['t_start', 't_stop', 'event'] + all_vars].dropna()

    try:
        cph = CoxPHFitter(penalizer=0.01)
        cph.fit(model_df, duration_col='t_stop', event_col='event',
                entry_col='t_start')
        hr = np.exp(cph.params_[exposure])
        ci_low = np.exp(cph.confidence_intervals_.loc[exposure].iloc[0])
        ci_high = np.exp(cph.confidence_intervals_.loc[exposure].iloc[1])
        p = cph.summary['p'][exposure]
        print(f"  {model_name}: HR={hr:.2f} ({ci_low:.2f}-{ci_high:.2f}), p={p:.4f}")
    except Exception as e:
        print(f"  {model_name}: Failed - {e}")

# ============================================================================
# 8. COMBINED MODEL: WEALTH SHOCK + ECONOMIC SATISFACTION
# ============================================================================
print("\n" + "=" * 70)
print("COMBINED MODEL: WEALTH SHOCK + ECONOMIC SATISFACTION (time-varying)")
print("=" * 70)

covs = full_covs
exposures = ['hh_wealth_shock', 'low_econ_sat']
all_vars = exposures + covs
model_df = pp[['t_start', 't_stop', 'event'] + all_vars].dropna()

print(f"\nCombined model data: N={len(model_df):,}, events={int(model_df['event'].sum()):,}")
try:
    cph = CoxPHFitter(penalizer=0.01)
    cph.fit(model_df, duration_col='t_stop', event_col='event',
            entry_col='t_start')
    print(f"Fully adjusted model with both exposures:")
    for var in cph.summary.index:
        hr = np.exp(cph.summary.loc[var, 'coef'])
        ci_l = np.exp(cph.summary.loc[var, 'coef lower 95%'])
        ci_h = np.exp(cph.summary.loc[var, 'coef upper 95%'])
        p = cph.summary.loc[var, 'p']
        sig = '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
        print(f"  {var:25s}: HR={hr:.3f} ({ci_l:.3f}-{ci_h:.3f}) p={p:.4f} {sig}")
except Exception as e:
    print(f"Combined model failed: {e}")

# ============================================================================
# 9. FIGURE: KM CURVES FOR WEALTH SHOCK
# ============================================================================
print("\nGenerating Kaplan-Meier curves for wealth shock...")

# For KM, use person-level "ever shocked" with landmark approach
# Landmark at wave 3 (first wave where HH shock can be computed from wave 2→3)
wave3_panel = panel[panel['wave'] == 3].copy()
wave3_panel = wave3_panel[['pid', 'hh_wealth_shock', 't', 'death_t', 'died_ever']].dropna(subset=['hh_wealth_shock'])

# Survival time from wave 3 interview
# Compute max study duration from data rather than hardcoding
_max_study_duration = MAX_STUDY_YEAR - panel['first_iw_date'].min()
wave3_panel['surv_from_w3'] = np.where(
    wave3_panel['died_ever'] == 1,
    wave3_panel['death_t'] - wave3_panel['t'],
    _max_study_duration - wave3_panel['t']  # censor at end of study
)
wave3_panel['surv_from_w3'] = wave3_panel['surv_from_w3'].clip(lower=0.01)

# Event after wave 3
wave3_panel['event_after_w3'] = np.where(
    (wave3_panel['died_ever'] == 1) & (wave3_panel['death_t'] > wave3_panel['t']),
    1, 0
)

fig, ax = plt.subplots(figsize=(8, 6))
kmf = KaplanMeierFitter()

for val, label, color in [(0, 'No wealth shock', '#1f77b4'),
                           (1, 'Wealth shock (>=75% NW decline)', '#d62728')]:
    mask = wave3_panel['hh_wealth_shock'] == val
    if mask.sum() > 10:
        kmf.fit(wave3_panel.loc[mask, 'surv_from_w3'],
                wave3_panel.loc[mask, 'event_after_w3'],
                label=label)
        kmf.plot_survival_function(ax=ax, color=color, linewidth=2)

# Log-rank test
mask_any = wave3_panel['hh_wealth_shock'].notna()
if mask_any.sum() > 0:
    shocked = wave3_panel[wave3_panel['hh_wealth_shock'] == 1]
    not_shocked = wave3_panel[wave3_panel['hh_wealth_shock'] == 0]
    if len(shocked) > 5 and len(not_shocked) > 5:
        lr = logrank_test(
            shocked['surv_from_w3'], not_shocked['surv_from_w3'],
            shocked['event_after_w3'], not_shocked['event_after_w3']
        )
        p_str = f"p={lr.p_value:.4f}" if lr.p_value >= 0.001 else "p<0.001"
        ax.text(0.98, 0.98, f'Log-rank {p_str}\nN shocked = {len(shocked):,}\nN not shocked = {len(not_shocked):,}',
                transform=ax.transAxes, ha='right', va='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

ax.set_xlabel('Years from wave 3 (2010) interview', fontsize=11)
ax.set_ylabel('Survival probability', fontsize=11)
ax.set_title('Survival by Negative Wealth Shock Status at Wave 3\n(>=75% decline in household net worth, waves 2-3)',
             fontsize=12, fontweight='bold')
ax.legend(fontsize=10, loc='lower left')
ax.set_ylim(0.4, 1.02)

plt.tight_layout()
plt.savefig(os.path.join(FIG, 'figure4_km_wealth_shock.png'), dpi=300, bbox_inches='tight')
plt.savefig(os.path.join(FIG, 'figure4_km_wealth_shock.pdf'), bbox_inches='tight')
plt.close()
print("Figure 4 saved.")

# ============================================================================
# 10. SUMMARY TABLE
# ============================================================================
print("\n" + "=" * 70)
print("SUMMARY: ALL TIME-VARYING COX MODEL RESULTS")
print("=" * 70)

# Save person-period dataset
pp.to_parquet(os.path.join(OUT, 'person_period_data.parquet'), index=False)
print(f"\nPerson-period dataset saved: {len(pp):,} intervals")

print("Done.")
