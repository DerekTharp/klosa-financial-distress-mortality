"""
02_build_analytic_sample.py
Financial Distress and All-Cause Mortality Among Older Adults in South Korea

Constructs the analytic dataset by:
1. Building person-wave panel from structural data
2. Computing financial distress measures (wealth shock, economic satisfaction, livelihood security)
3. Merging mortality data from exit interviews and longitudinal trackers
4. Computing survival time and event indicators
5. Saving the analytic sample
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', message='.*convergence.*')

from config import BASE, DATA, OUT
from model_specs import ECON_SAT_THRESHOLD

# Wave years
WAVE_YEARS = {1: 2006, 2: 2008, 3: 2010, 4: 2012, 5: 2014, 6: 2016, 7: 2018, 8: 2020, 9: 2022}

# ============================================================================
# 1. BUILD PERSON-WAVE PANEL FROM STRUCTURAL DATA
# ============================================================================
print("Building person-wave panel...")

panels = []
for w in range(1, 10):
    fpath = os.path.join(DATA, "structural", f"str{w:02d}_e.dta")
    df = pd.read_stata(fpath, convert_categoricals=False)
    prefix = f"w{w:02d}"

    # Standardize variable names
    record = pd.DataFrame()
    record['pid'] = df['pid']
    record['wave'] = w
    record['year'] = WAVE_YEARS[w]

    # Demographics
    record['age'] = df.get(f'{prefix}A002_age', np.nan)
    record['female'] = (df.get(f'{prefix}gender1', np.nan) == 5).astype(float)
    record['female'] = record['female'].where(df.get(f'{prefix}gender1', pd.Series(dtype=float)).notna())
    record['education'] = df.get(f'{prefix}edu', np.nan)
    record['marital'] = df.get(f'{prefix}marital', np.nan)
    record['region'] = df.get(f'{prefix}region1', np.nan)
    record['urban'] = df.get(f'{prefix}region3', np.nan)  # Metropolitan/City/Town
    record['hhsize'] = df.get(f'hhsize{w:02d}' if w <= 7 else f'w{w:02d}hhsize', np.nan)

    # Interview date
    record['iw_year'] = df.get(f'{prefix}mniw_y', np.nan)
    record['iw_month'] = df.get(f'{prefix}mniw_m', np.nan)

    # Financial variables
    record['hh_income'] = df.get(f'{prefix}hhinc', np.nan)
    record['hh_assets'] = df.get(f'{prefix}hhassets', np.nan)
    record['hh_debt'] = df.get(f'{prefix}hhliabilities', np.nan)
    record['hh_net_worth'] = df.get(f'{prefix}hhnetassets', np.nan)
    record['p_net_assets'] = df.get(f'{prefix}pnetassets', np.nan)
    record['p_income'] = df.get(f'{prefix}pinc', np.nan)
    record['earned_income'] = df.get(f'{prefix}earned', np.nan)
    record['real_estate'] = df.get(f'{prefix}realestate', np.nan)
    record['financial_assets'] = df.get(f'{prefix}financial', np.nan)

    # Pension/social safety net
    record['national_pension'] = df.get(f'{prefix}national', np.nan)
    record['basic_livelihood'] = df.get(f'{prefix}guarantee', np.nan)
    record['senior_pension'] = df.get(f'{prefix}senior_pension', np.nan) if w >= 5 else np.nan
    record['social_security'] = df.get(f'{prefix}socialsecurity', np.nan)

    # Family transfers
    record['transfer_from_family'] = df.get(f'{prefix}transferfrom', np.nan)
    record['transfer_to_family'] = df.get(f'{prefix}transferto', np.nan)

    # Health
    record['self_rated_health'] = df.get(f'{prefix}C001', np.nan)
    record['chronic_count'] = df.get(f'{prefix}chronic_sum', np.nan)
    record['hypertension'] = df.get(f'{prefix}chronic_a', np.nan)
    record['diabetes'] = df.get(f'{prefix}chronic_b', np.nan)
    record['cancer'] = df.get(f'{prefix}chronic_c', np.nan)
    record['lung_disease'] = df.get(f'{prefix}chronic_d', np.nan)
    record['liver_disease'] = df.get(f'{prefix}chronic_e', np.nan)
    record['heart_disease'] = df.get(f'{prefix}chronic_f', np.nan)
    record['stroke'] = df.get(f'{prefix}chronic_g', np.nan)
    record['psychiatric'] = df.get(f'{prefix}chronic_h', np.nan)
    record['arthritis'] = df.get(f'{prefix}chronic_i', np.nan)
    record['bmi'] = df.get(f'{prefix}bmi', np.nan)
    record['smoking'] = df.get(f'{prefix}smoke', np.nan)
    record['drinking'] = df.get(f'{prefix}alc', np.nan)
    record['exercise'] = df.get(f'{prefix}C108', np.nan)
    record['activity_limit'] = df.get(f'{prefix}C005', np.nan)
    record['iadl'] = df.get(f'{prefix}iadl', np.nan)

    # Depression
    record['depression'] = df.get(f'{prefix}dep1', np.nan)

    # CES-D items (for computing score if dep1 not available)
    for item in range(142, 152):
        record[f'cesd_{item}'] = df.get(f'{prefix}C{item}', np.nan)

    # Economic satisfaction (0-100)
    record['econ_satisfaction'] = df.get(f'{prefix}G027', np.nan)

    # Subjective living standard expectations
    record['living_std_lower'] = df.get(f'{prefix}G015', np.nan)

    # Social participation
    record['religion'] = df.get(f'{prefix}A030', np.nan)
    record['social_contact'] = df.get(f'{prefix}A032', np.nan)

    # Children
    record['n_children'] = df.get(f'{prefix}Ba003', np.nan)
    record['live_with_children'] = df.get(f'{prefix}livewith', np.nan)

    # Weights
    record['weight_cross'] = df.get(f'{prefix}wgt_c', np.nan)
    record['weight_long'] = df.get(f'{prefix}wgt_p', np.nan) if w > 1 else np.nan

    panels.append(record)

panel = pd.concat(panels, ignore_index=True)
print(f"Panel constructed: {len(panel):,} person-wave observations")
print(f"Unique persons: {panel['pid'].nunique():,}")

# ============================================================================
# 1b. CLEAN KLoSA MISSING-VALUE CODES (-9 = "Don't know", -8 = "Refuse")
# ============================================================================
print("\nCleaning KLoSA missing-value sentinel codes (-9, -8)...")
_klosa_missing = {-9, -8}
_vars_to_clean = [
    'econ_satisfaction', 'smoking', 'drinking', 'exercise',
    'self_rated_health', 'activity_limit', 'depression', 'religion',
    'social_contact', 'education', 'marital', 'basic_livelihood',
    'hh_income', 'hh_assets', 'hh_debt', 'hh_net_worth', 'p_net_assets',
]
_total_replaced = 0
for _var in _vars_to_clean:
    if _var in panel.columns:
        _mask = panel[_var].isin(_klosa_missing)
        _n = _mask.sum()
        if _n > 0:
            panel.loc[_mask, _var] = np.nan
            _total_replaced += _n
            print(f"  {_var}: replaced {_n} sentinel codes with NaN")
print(f"  Total sentinel values cleaned: {_total_replaced}")

# ============================================================================
# 2. CONSTRUCT FINANCIAL DISTRESS MEASURES
# ============================================================================
print("\nConstructing financial distress measures...")

# Sort for lag computation
panel = panel.sort_values(['pid', 'wave']).reset_index(drop=True)

# --- Approach A: Negative Wealth Shock (Pool et al., 2018) ---
# >=75% loss in household net worth between consecutive waves
# Using hh_net_worth (available waves 2+)
panel['lag_hh_net_worth'] = panel.groupby('pid')['hh_net_worth'].shift(1)
panel['lag_wave'] = panel.groupby('pid')['wave'].shift(1)

# Only compute shock for consecutive waves
panel['consecutive'] = (panel['wave'] - panel['lag_wave']) == 1

# Wealth shock: >=75% decline
# Handle edge cases: if previous NW was positive, need >=75% decline
# If previous NW was <=0, define shock if current NW is also negative or declined further
def compute_wealth_shock(row):
    if not row['consecutive'] or pd.isna(row['lag_hh_net_worth']) or pd.isna(row['hh_net_worth']):
        return np.nan
    prev = row['lag_hh_net_worth']
    curr = row['hh_net_worth']
    if prev > 0:
        pct_change = (curr - prev) / prev
        return 1.0 if pct_change <= -0.75 else 0.0
    elif prev == 0:
        # Require meaningful negative (not rounding/measurement noise);
        # threshold consistent with 06_wealth_shock_time_varying.py
        return 1.0 if curr < -1000 else 0.0
    else:  # prev < 0
        # Already negative; shock if debt got >=75% worse (consistent with script 06)
        return 1.0 if curr < prev * 1.75 else 0.0

panel['wealth_shock'] = panel.apply(compute_wealth_shock, axis=1)

# Also compute wealth shock using personal net assets (available wave 1+)
panel['lag_p_net_assets'] = panel.groupby('pid')['p_net_assets'].shift(1)

def compute_personal_wealth_shock(row):
    if not row['consecutive'] or pd.isna(row['lag_p_net_assets']) or pd.isna(row['p_net_assets']):
        return np.nan
    prev = row['lag_p_net_assets']
    curr = row['p_net_assets']
    if prev > 0:
        pct_change = (curr - prev) / prev
        return 1.0 if pct_change <= -0.75 else 0.0
    elif prev == 0:
        # Require meaningful negative (not rounding/measurement noise);
        # threshold consistent with 06_wealth_shock_time_varying.py
        return 1.0 if curr < -1000 else 0.0
    else:  # prev < 0
        # Already negative; shock if debt got >=75% worse (consistent with script 06)
        return 1.0 if curr < prev * 1.75 else 0.0

panel['personal_wealth_shock'] = panel.apply(compute_personal_wealth_shock, axis=1)

# --- Approach C: Low Economic Satisfaction ---
# Fixed threshold: scores <= 30 (bottom quintile of baseline distribution, four lowest
# categories on the 11-point 0-100 NRS). Applied consistently across all waves.
panel['low_econ_sat'] = np.where(
    panel['econ_satisfaction'].notna(),
    (panel['econ_satisfaction'] <= ECON_SAT_THRESHOLD).astype(float),
    np.nan
)

# Also create continuous z-scored economic satisfaction (reversed: higher = more distress)
panel['econ_distress_zscore'] = np.nan
for w in range(1, 10):
    mask = panel['wave'] == w
    econ = panel.loc[mask, 'econ_satisfaction']
    if econ.notna().sum() > 0:
        # Reverse: higher value = more distress
        reversed_econ = 100 - econ
        mean = reversed_econ.mean()
        std = reversed_econ.std()
        if std > 0:
            panel.loc[mask, 'econ_distress_zscore'] = (reversed_econ - mean) / std

# --- Approach D: Objective Poverty Indicators ---
# Receipt of National Basic Livelihood Security Benefit (means-tested welfare)
panel['on_welfare'] = (panel['basic_livelihood'].fillna(0) > 0).astype(float)

# Debt-to-asset ratio
panel['debt_to_asset'] = np.where(
    panel['hh_assets'] > 0,
    panel['hh_debt'] / panel['hh_assets'],
    np.where(panel['hh_debt'] > 0, 999, 0)  # debt but no assets = extreme
)
panel.loc[panel['hh_assets'].isna() | panel['hh_debt'].isna(), 'debt_to_asset'] = np.nan

# High debt burden (top quintile of debt-to-asset ratio)
for w in range(1, 10):
    mask = (panel['wave'] == w) & panel['debt_to_asset'].notna() & (panel['debt_to_asset'] < 999)
    if mask.sum() > 0:
        q80 = panel.loc[mask, 'debt_to_asset'].quantile(0.80)
        panel.loc[mask, 'high_debt_burden'] = (panel.loc[mask, 'debt_to_asset'] >= q80).astype(float)

# --- Combined Financial Distress Index ---
# For waves where wealth shock is available, combine indicators
panel['financial_distress_any'] = np.nan
for idx in panel.index:
    indicators = []
    for var in ['wealth_shock', 'low_econ_sat', 'on_welfare', 'high_debt_burden']:
        val = panel.at[idx, var] if var in panel.columns else np.nan
        if not pd.isna(val):
            indicators.append(val)
    if indicators:
        panel.at[idx, 'financial_distress_any'] = 1.0 if any(v == 1 for v in indicators) else 0.0

print("Financial distress measures constructed.")

# Report prevalence
for var in ['wealth_shock', 'personal_wealth_shock', 'low_econ_sat', 'on_welfare',
            'high_debt_burden', 'financial_distress_any']:
    if var in panel.columns:
        valid = panel[var].dropna()
        if len(valid) > 0:
            pct = valid.mean() * 100
            print(f"  {var}: {pct:.1f}% (N={len(valid):,})")

# ============================================================================
# 3. MERGE MORTALITY DATA
# ============================================================================
print("\nProcessing mortality data...")

# Load longitudinal tracker files to get mortality status
# These track whether respondents are alive, dead, or lost to follow-up
tracker_data = {}
for w in range(1, 10):
    fpath = os.path.join(DATA, "longitudinal_tracker", f"Lt{w:02d}_e.dta")
    if os.path.exists(fpath):
        tracker_data[w] = pd.read_stata(fpath, convert_categoricals=False)
        print(f"Tracker wave {w}: {tracker_data[w].shape[0]:,} obs, {tracker_data[w].shape[1]} vars")
        # Check for PID and type variables
        type_cols = [c for c in tracker_data[w].columns if 'type' in c.lower()]
        pid_cols = [c for c in tracker_data[w].columns if 'pid' in c.lower()]
        print(f"  PID cols: {pid_cols[:3]}, Type cols: {type_cols[:5]}")

# Load exit interviews to get date of death
print("\nProcessing exit interview death dates...")
death_records = []

exit_mappings = {
    'w03_exit_e.dta': {'year': 'w03Xa010y', 'month': 'w03Xa010m', 'day': 'w03Xa010d',
                       'cause': 'w03Xa007', 'type': 'w03Xa008'},
    'w04_exit_e.dta': {'year': 'w04Xa010y', 'month': 'w04Xa010m', 'day': 'w04Xa010d',
                       'cause': 'w04Xa007', 'type': 'w04Xa008'},
    'w05_exit_e.dta': {'year': 'w05xA010Y', 'month': 'w05xA010M', 'day': 'w05xA010D',
                       'cause': 'w05xA007', 'type': 'w05XA008'},
    'w06_Exit_e.dta': {'year': 'w06x_A010Y', 'month': 'w06x_A010M', 'day': 'w06x_A010D',
                       'cause': 'w06x_A007', 'type': 'w06x_A008'},
    'w07_exit_e.dta': {'year': 'w07x_a010y', 'month': 'w07x_a010m', 'day': 'w07x_a010d',
                       'cause': 'w07x_a007', 'type': 'w07x_a008'},
    'w08_exit_e.dta': {'year': 'w08x_a010Y', 'month': 'w08x_a010M', 'day': 'w08x_a010D',
                       'cause': 'w08x_a007', 'type': 'w08x_a008'},
    'Exit09_e.dta':   {'year': 'w09X_A010Y', 'month': 'w09X_A010M', 'day': 'w09X_A010D',
                       'cause': 'w09X_A007', 'type': 'w09X_A008'},
}

exit_dir = os.path.join(DATA, "exit_interviews")
for fname, cols in exit_mappings.items():
    fpath = os.path.join(exit_dir, fname)
    if not os.path.exists(fpath):
        print(f"  {fname}: NOT FOUND")
        continue

    df = pd.read_stata(fpath, convert_categoricals=False)

    # Find PID column
    pid_col = None
    for c in df.columns:
        if c.lower() == 'pid':
            pid_col = c
            break
    if pid_col is None:
        pid_candidates = [c for c in df.columns if 'pid' in c.lower()]
        if pid_candidates:
            pid_col = pid_candidates[0]

    if pid_col is None:
        print(f"  {fname}: No PID column found! Columns: {df.columns[:5].tolist()}")
        continue

    for _, row in df.iterrows():
        rec = {'pid': row[pid_col]}

        # Date of death
        for field, col in cols.items():
            if col in df.columns:
                rec[f'death_{field}'] = row[col]
            else:
                rec[f'death_{field}'] = np.nan

        rec['exit_wave'] = fname
        death_records.append(rec)

deaths_df = pd.DataFrame(death_records)
print(f"\nTotal death records: {len(deaths_df):,}")

# Clean death dates
deaths_df['death_year'] = pd.to_numeric(deaths_df['death_year'], errors='coerce')
deaths_df['death_month'] = pd.to_numeric(deaths_df['death_month'], errors='coerce')
deaths_df['death_day'] = pd.to_numeric(deaths_df['death_day'], errors='coerce')

# Fix sentinel codes: -8 (don't know) and -9 (refused) are coded as valid numbers
# by KLoSA but are not real dates. Replace any negative values with NaN.
n_sentinel_year = (deaths_df['death_year'] < 0).sum()
n_sentinel_month = (deaths_df['death_month'] < 0).sum()
n_sentinel_day = (deaths_df['death_day'] < 0).sum()
deaths_df.loc[deaths_df['death_year'] < 0, 'death_year'] = np.nan
deaths_df.loc[deaths_df['death_month'] < 0, 'death_month'] = np.nan
deaths_df.loc[deaths_df['death_day'] < 0, 'death_day'] = np.nan
print(f"Sentinel codes cleaned: {n_sentinel_year} year, {n_sentinel_month} month, {n_sentinel_day} day")

# Impute missing death dates for deaths with sentinel-coded years.
# These are confirmed deaths (reported in exit interviews) but with unknown
# exact date. Approximate: death_year = exit_wave_interview_year - 1 (midpoint
# between last main interview and exit interview), death_month = 6.
exit_wave_year_map = {
    'w03_exit_e.dta': 2010, 'w04_exit_e.dta': 2012, 'w05_exit_e.dta': 2014,
    'w06_Exit_e.dta': 2016, 'w07_exit_e.dta': 2018, 'w08_exit_e.dta': 2020,
    'Exit09_e.dta': 2022,
}
missing_year = deaths_df['death_year'].isna()
n_imputed = missing_year.sum()
if n_imputed > 0:
    deaths_df.loc[missing_year, 'death_year'] = deaths_df.loc[missing_year, 'exit_wave'].map(
        {k: v - 1 for k, v in exit_wave_year_map.items()}
    )
    deaths_df.loc[missing_year & deaths_df['death_month'].isna(), 'death_month'] = 6
    print(f"Imputed death dates for {n_imputed} deaths with sentinel-coded years")

# Filter to valid death dates (2006-2023) after cleaning and imputation
valid_dates = deaths_df[(deaths_df['death_year'] >= 2006) & (deaths_df['death_year'] <= 2023)]
n_invalid = len(deaths_df) - len(valid_dates)
print(f"Deaths with valid dates: {len(valid_dates):,}")
if len(valid_dates) > 0:
    print(f"Death year range: {valid_dates['death_year'].min():.0f} - {valid_dates['death_year'].max():.0f}")
if n_invalid > 0:
    print(f"WARNING: Dropping {n_invalid} deaths with invalid dates after cleaning")
deaths_df = valid_dates

# Keep first death record per person (should be unique but check)
deaths_df = deaths_df.sort_values('death_year').groupby('pid').first().reset_index()
print(f"Unique deceased persons: {len(deaths_df):,}")

# ============================================================================
# 4. MERGE MORTALITY WITH PANEL AND COMPUTE SURVIVAL TIME
# ============================================================================
print("\nMerging mortality with panel data...")

# Create person-level mortality indicator
person_death = deaths_df[['pid', 'death_year', 'death_month', 'death_day']].copy()
person_death['died'] = 1

# Get baseline info for each person
baseline = panel[panel['wave'] == panel.groupby('pid')['wave'].transform('min')].copy()
baseline = baseline.drop_duplicates(subset='pid', keep='first')

# Merge death info
baseline = baseline.merge(person_death, on='pid', how='left')
baseline['died'] = baseline['died'].fillna(0).astype(int)

# Compute entry time (first interview date)
baseline['entry_year'] = baseline['iw_year']
baseline['entry_month'] = baseline['iw_month'].fillna(6)  # midpoint if missing

# Compute exit time
# For deceased: date of death
# For alive at last observation: last interview date
last_obs = panel.groupby('pid').agg(
    last_wave=('wave', 'max'),
    last_iw_year=('iw_year', 'last'),
    last_iw_month=('iw_month', 'last')
).reset_index()

baseline = baseline.merge(last_obs, on='pid', how='left')

# Exit date
baseline['exit_year'] = np.where(
    baseline['died'] == 1,
    baseline['death_year'],
    baseline['last_iw_year']
)
baseline['exit_month'] = np.where(
    baseline['died'] == 1,
    baseline['death_month'].fillna(6),
    baseline['last_iw_month'].fillna(6)
)

# Survival time in years from entry
baseline['surv_time'] = (baseline['exit_year'] - baseline['entry_year']) + \
                        (baseline['exit_month'] - baseline['entry_month']) / 12

# Clean
baseline = baseline[baseline['surv_time'] > 0]  # must have positive follow-up

print(f"Persons in analytic sample: {len(baseline):,}")
print(f"Deaths: {baseline['died'].sum():,} ({baseline['died'].mean()*100:.1f}%)")
print(f"Mean follow-up: {baseline['surv_time'].mean():.1f} years")
print(f"Max follow-up: {baseline['surv_time'].max():.1f} years")

# ============================================================================
# 5. CONSTRUCT BASELINE COVARIATES FOR SIMPLE ANALYSIS
# ============================================================================
print("\nPreparing baseline covariates...")

# Education categories
baseline['edu_cat'] = pd.cut(
    baseline['education'],
    bins=[-np.inf, 1, 2, 3, np.inf],
    labels=['No formal/Elementary', 'Middle school', 'High school', 'College+']
)

# Marital status binary
baseline['married'] = (baseline['marital'] == 1).astype(float)

# Self-rated health (recode: 1=excellent...5=poor)
# Higher = worse health

# Chronic disease categories
baseline['any_chronic'] = (baseline['chronic_count'] > 0).astype(float)
baseline['multi_chronic'] = (baseline['chronic_count'] >= 2).astype(float)

# Smoking categories (preserve NaN from missing smoking data)
baseline['ever_smoker'] = np.where(baseline['smoking'].isna(), np.nan,
                                    (baseline['smoking'] > 0).astype(float))
baseline['current_smoker'] = np.where(baseline['smoking'].isna(), np.nan,
                                       (baseline['smoking'] == 2).astype(float))

# Economic satisfaction quintile at baseline
baseline['econ_sat_quintile'] = pd.qcut(
    baseline['econ_satisfaction'],
    q=5, labels=['Q1 (lowest)', 'Q2', 'Q3', 'Q4', 'Q5 (highest)'],
    duplicates='drop'
)

# Welfare receipt at baseline
baseline['on_welfare_bl'] = (baseline['basic_livelihood'].fillna(0) > 0).astype(float)

# National pension receipt at baseline
baseline['has_pension_bl'] = (baseline['national_pension'].fillna(0) > 0).astype(float)

# Age groups
baseline['age_group'] = pd.cut(
    baseline['age'],
    bins=[0, 54, 64, 74, np.inf],
    labels=['45-54', '55-64', '65-74', '75+']
)

# ============================================================================
# 6. SAVE DATASETS
# ============================================================================
print("\nSaving datasets...")

# Save person-wave panel
panel.to_parquet(os.path.join(OUT, 'panel_data.parquet'), index=False)
print(f"Panel saved: {len(panel):,} obs")

# Save baseline analytic sample
baseline.to_parquet(os.path.join(OUT, 'baseline_analytic.parquet'), index=False)
print(f"Baseline analytic sample saved: {len(baseline):,} obs")

# Save death records
deaths_df.to_parquet(os.path.join(OUT, 'death_records.parquet'), index=False)

# ============================================================================
# 7. DESCRIPTIVE TABLES
# ============================================================================
print("\n" + "=" * 70)
print("TABLE 1: BASELINE CHARACTERISTICS")
print("=" * 70)

# Overall and by financial distress status
# Use baseline economic satisfaction quintile as primary grouping

print(f"\nOverall Sample (N = {len(baseline):,})")
print(f"  Age: {baseline['age'].mean():.1f} ({baseline['age'].std():.1f})")
print(f"  Female: {baseline['female'].mean()*100:.1f}%")
print(f"  Married: {baseline['married'].mean()*100:.1f}%")
print(f"  Education:")
for cat in baseline['edu_cat'].dropna().unique():
    pct = (baseline['edu_cat'] == cat).mean() * 100
    print(f"    {cat}: {pct:.1f}%")
print(f"  Mean chronic diseases: {baseline['chronic_count'].mean():.2f}")
print(f"  Current smoker: {baseline['current_smoker'].mean()*100:.1f}%")
print(f"  BMI: {baseline['bmi'].mean():.1f}")
print(f"  Depressed: {(baseline['depression'] == 1).mean()*100:.1f}%")
print(f"  Econ satisfaction: {baseline['econ_satisfaction'].mean():.1f}")
print(f"  On welfare: {baseline['on_welfare_bl'].mean()*100:.1f}%")
print(f"  Has national pension: {baseline['has_pension_bl'].mean()*100:.1f}%")
print(f"  Died during follow-up: {baseline['died'].mean()*100:.1f}%")
print(f"  Mean follow-up years: {baseline['surv_time'].mean():.1f}")

# By economic satisfaction quintile
print(f"\nMortality by baseline economic satisfaction quintile:")
for q in ['Q1 (lowest)', 'Q2', 'Q3', 'Q4', 'Q5 (highest)']:
    mask = baseline['econ_sat_quintile'] == q
    if mask.sum() > 0:
        mort = baseline.loc[mask, 'died'].mean() * 100
        n = mask.sum()
        print(f"  {q}: {mort:.1f}% died (N={n:,})")

# By welfare receipt
print(f"\nMortality by welfare receipt:")
for val, label in [(0, 'Not on welfare'), (1, 'On welfare')]:
    mask = baseline['on_welfare_bl'] == val
    if mask.sum() > 0:
        mort = baseline.loc[mask, 'died'].mean() * 100
        print(f"  {label}: {mort:.1f}% died (N={mask.sum():,})")

print("Done.")
