"""
01_data_exploration.py
Financial Distress and All-Cause Mortality Among Older Adults in South Korea
KLoSA Data Exploration and Feasibility Assessment

This script:
1. Loads the structural data files (which contain pre-built generated variables)
2. Loads exit interview data (mortality ascertainment)
3. Tabulates deaths across waves
4. Explores financial distress measures
5. Checks distributions and feasibility
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', message='.*convergence.*')

from config import BASE, DATA, OUT

# ============================================================================
# 1. LOAD STRUCTURAL DATA (contains generated/harmonized variables)
# ============================================================================
print("=" * 70)
print("LOADING STRUCTURAL DATA FILES")
print("=" * 70)

str_files = {}
for w in range(1, 10):
    fname = f"str{w:02d}_e.dta"
    fpath = os.path.join(DATA, "structural", fname)
    if os.path.exists(fpath):
        str_files[w] = pd.read_stata(fpath, convert_categoricals=False)
        print(f"Wave {w}: {str_files[w].shape[0]:,} obs, {str_files[w].shape[1]:,} vars")

# ============================================================================
# 2. LOAD EXIT INTERVIEW DATA (mortality ascertainment)
# ============================================================================
print("\n" + "=" * 70)
print("LOADING EXIT INTERVIEW DATA")
print("=" * 70)

exit_files = {}
exit_dir = os.path.join(DATA, "exit_interviews")
for f in sorted(os.listdir(exit_dir)):
    if f.endswith('.dta'):
        wave_label = f.replace('_e.dta', '').replace('_exit', '').replace('_Exit', '')
        df = pd.read_stata(os.path.join(exit_dir, f), convert_categoricals=False)
        exit_files[wave_label] = df
        print(f"{f}: {df.shape[0]:,} deaths recorded, {df.shape[1]} vars")
        # Try to find death-related columns
        death_cols = [c for c in df.columns if any(x in c.upper() for x in ['A010', 'A007', 'A008', 'DEATH', 'DIE'])]
        if death_cols:
            print(f"  Death-related columns: {death_cols[:10]}")

# ============================================================================
# 3. TABULATE DEATHS ACROSS WAVES
# ============================================================================
print("\n" + "=" * 70)
print("MORTALITY SUMMARY")
print("=" * 70)

total_deaths = 0
for label, df in exit_files.items():
    n = len(df)
    total_deaths += n
    # Look for date of death variables
    date_cols = [c for c in df.columns if 'A010' in c.upper() or 'death' in c.lower()]
    print(f"{label}: {n:,} deaths")
    if date_cols:
        print(f"  Date columns: {date_cols[:5]}")

print(f"\nTotal deaths across all exit interviews: {total_deaths:,}")

# ============================================================================
# 4. EXPLORE FINANCIAL VARIABLES IN STRUCTURAL DATA
# ============================================================================
print("\n" + "=" * 70)
print("FINANCIAL VARIABLES - WAVE 1 (BASELINE)")
print("=" * 70)

w1 = str_files[1]

# Key financial variables
fin_vars = {
    'w01hhinc': 'Household income',
    'w01hhassets': 'Household assets',
    'w01hhliabilities': 'Household debt',
    'w01hhnetassets': 'Household net assets',
    'w01pnetassets': 'Personal net assets',
    'w01pinc': 'Personal income',
    'w01earned': 'Earned income',
    'w01realestate': 'Real estate assets',
    'w01financial': 'Financial assets',
    'w01national': 'National Pension income',
    'w01guarantee': 'Basic Livelihood Security',
}

for var, label in fin_vars.items():
    if var in w1.columns:
        valid = w1[var].dropna()
        valid = valid[valid >= 0]  # exclude missing codes
        print(f"\n{label} ({var}):")
        print(f"  N valid: {len(valid):,}")
        print(f"  Mean: {valid.mean():,.0f}")
        print(f"  Median: {valid.median():,.0f}")
        print(f"  SD: {valid.std():,.0f}")
        print(f"  Min: {valid.min():,.0f}, Max: {valid.max():,.0f}")
        print(f"  % zero: {(valid == 0).mean()*100:.1f}%")
    else:
        print(f"\n{label} ({var}): NOT FOUND in data")

# ============================================================================
# 5. CHECK NET WORTH DISTRIBUTION ACROSS WAVES
# ============================================================================
print("\n" + "=" * 70)
print("NET WORTH ACROSS WAVES (for wealth shock construction)")
print("=" * 70)

for w in range(1, 10):
    if w in str_files:
        df = str_files[w]
        prefix = f"w{w:02d}"
        nw_var = f"{prefix}hhnetassets"
        n_var = f"{prefix}hhinc"

        if nw_var in df.columns:
            valid = df[nw_var].dropna()
            print(f"Wave {w}: N={len(valid):,}, "
                  f"Mean NW={valid.mean():,.0f}, "
                  f"Median NW={valid.median():,.0f}, "
                  f"% negative={((valid < 0).mean()*100):.1f}%")
        else:
            # Try without leading zero
            nw_var2 = f"w{w}hhnetassets"
            if nw_var2 in df.columns:
                valid = df[nw_var2].dropna()
                print(f"Wave {w}: N={len(valid):,}, "
                      f"Mean NW={valid.mean():,.0f}, "
                      f"Median NW={valid.median():,.0f}, "
                      f"% negative={((valid < 0).mean()*100):.1f}%")
            else:
                print(f"Wave {w}: net worth variable not found. Cols with 'netassets': "
                      f"{[c for c in df.columns if 'netassets' in c.lower()]}")

# ============================================================================
# 6. DEMOGRAPHIC OVERVIEW AT BASELINE
# ============================================================================
print("\n" + "=" * 70)
print("BASELINE DEMOGRAPHICS (Wave 1)")
print("=" * 70)

demo_vars = {
    'w01gender1': 'Gender',
    'w01A002_age': 'Age',
    'w01edu': 'Education',
    'w01marital': 'Marital status',
    'w01region1': 'Region',
    'w01C001': 'Self-rated health',
}

for var, label in demo_vars.items():
    if var in w1.columns:
        print(f"\n{label} ({var}):")
        if var in ['w01A002_age']:
            valid = w1[var].dropna()
            print(f"  Mean: {valid.mean():.1f}, SD: {valid.std():.1f}")
            print(f"  Range: {valid.min():.0f} - {valid.max():.0f}")
        else:
            print(w1[var].value_counts().head(10).to_string())
    else:
        print(f"\n{label} ({var}): NOT FOUND")

# ============================================================================
# 7. HEALTH VARIABLES AT BASELINE
# ============================================================================
print("\n" + "=" * 70)
print("BASELINE HEALTH (Wave 1)")
print("=" * 70)

health_vars = {
    'w01chronic_sum': 'Number of chronic diseases',
    'w01bmi': 'BMI',
    'w01smoke': 'Smoking status',
    'w01alc': 'Drinking status',
    'w01adl': 'ADL index',
    'w01iadl': 'IADL index',
}

for var, label in health_vars.items():
    if var in w1.columns:
        valid = w1[var].dropna()
        print(f"\n{label} ({var}):")
        if var in ['w01bmi']:
            print(f"  Mean: {valid.mean():.1f}, SD: {valid.std():.1f}")
        elif var in ['w01chronic_sum', 'w01adl', 'w01iadl']:
            print(f"  Mean: {valid.mean():.2f}, SD: {valid.std():.2f}")
            print(f"  Distribution:")
            print(valid.value_counts().sort_index().head(10).to_string())
        else:
            print(valid.value_counts().head(10).to_string())
    else:
        print(f"\n{label} ({var}): NOT FOUND")

# ============================================================================
# 8. CES-D DEPRESSION SCORE
# ============================================================================
print("\n" + "=" * 70)
print("DEPRESSION (CES-D) - Check availability")
print("=" * 70)

for w in range(1, 10):
    if w in str_files:
        df = str_files[w]
        cesd_vars = [c for c in df.columns if 'cesd' in c.lower() or 'dep' in c.lower()]
        print(f"Wave {w}: CES-D/depression vars: {cesd_vars}")

# ============================================================================
# 9. ECONOMIC SATISFACTION (Approach C)
# ============================================================================
print("\n" + "=" * 70)
print("ECONOMIC SATISFACTION (G027) ACROSS WAVES")
print("=" * 70)

for w in range(1, 10):
    if w in str_files:
        df = str_files[w]
        g027_vars = [c for c in df.columns if 'G027' in c or 'g027' in c.lower()]
        if g027_vars:
            var = g027_vars[0]
            valid = df[var].dropna()
            valid = valid[(valid >= 0) & (valid <= 100)]
            print(f"Wave {w} ({var}): N={len(valid):,}, "
                  f"Mean={valid.mean():.1f}, Median={valid.median():.0f}, SD={valid.std():.1f}")
        else:
            print(f"Wave {w}: G027 not found in structural data")

# ============================================================================
# 10. SAMPLE TRACKING ACROSS WAVES
# ============================================================================
print("\n" + "=" * 70)
print("SAMPLE SIZE AND ATTRITION ACROSS WAVES")
print("=" * 70)

# Check PIDs across waves
all_pids = {}
for w in range(1, 10):
    if w in str_files:
        pids = set(str_files[w]['PID'].dropna().unique())
        all_pids[w] = pids
        print(f"Wave {w}: N = {len(pids):,}")

# Retention from wave 1
w1_pids = all_pids.get(1, set())
print(f"\nRetention from Wave 1 baseline (N={len(w1_pids):,}):")
for w in range(2, 10):
    if w in all_pids:
        retained = len(w1_pids & all_pids[w])
        pct = retained / len(w1_pids) * 100
        print(f"  Wave {w}: {retained:,} ({pct:.1f}%)")

# ============================================================================
# 11. PENSION RECEIPT (Moderator)
# ============================================================================
print("\n" + "=" * 70)
print("NATIONAL PENSION & BASIC OLD-AGE PENSION RECEIPT")
print("=" * 70)

for w in range(1, 10):
    if w in str_files:
        df = str_files[w]
        prefix = f"w{w:02d}"
        nat_var = f"{prefix}national"
        pension_vars = [c for c in df.columns if 'national' in c.lower() or 'senior_pension' in c.lower() or 'annuity' in c.lower()]

        if nat_var in df.columns:
            has_pension = (df[nat_var] > 0).sum()
            total = df[nat_var].notna().sum()
            print(f"Wave {w}: National Pension recipients: {has_pension:,}/{total:,} ({has_pension/total*100:.1f}%)")

# ============================================================================
# 12. FINANCIAL HARDSHIP INDICATORS (Wave 7+ only)
# ============================================================================
print("\n" + "=" * 70)
print("FINANCIAL HARDSHIP INDICATORS (Wave 7)")
print("=" * 70)

if 7 in str_files:
    w7 = str_files[7]
    hardship_vars = [c for c in w7.columns if 'Eadd' in c or 'eadd' in c.lower()]
    print(f"Hardship variables found: {hardship_vars}")
    for var in hardship_vars:
        valid = w7[var].dropna()
        print(f"\n{var}: N={len(valid):,}")
        print(valid.value_counts().sort_index().to_string())

# Check in main survey data instead
print("\n\nChecking main survey wave 7 for hardship indicators...")
w7_main_path = os.path.join(DATA, "main_survey", "w07_e.dta")
if os.path.exists(w7_main_path):
    w7_main = pd.read_stata(w7_main_path, convert_categoricals=False)
    hardship_main = [c for c in w7_main.columns if 'Eadd' in c or 'eadd' in c.lower()]
    print(f"Hardship vars in main survey: {hardship_main}")
    for var in hardship_main:
        valid = w7_main[var].dropna()
        print(f"\n{var}: N={len(valid):,}")
        print(valid.value_counts().sort_index().head(10).to_string())

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("FEASIBILITY SUMMARY")
print("=" * 70)

print(f"Baseline sample: {len(w1_pids):,} respondents")
print(f"Total deaths across exit interviews: {total_deaths:,}")
print("Done.")
