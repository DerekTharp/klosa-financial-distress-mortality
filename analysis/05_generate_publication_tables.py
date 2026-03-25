"""
05_generate_publication_tables.py
Generate publication-ready tables in CSV and formatted text.
"""

import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', message='.*delta_grad.*')
warnings.filterwarnings('ignore', message='.*convergence.*')
from scipy import stats

from config import BASE, OUT
from model_specs import *
TAB = os.path.join(OUT, "tables")

baseline = pd.read_parquet(os.path.join(OUT, 'baseline_analytic.parquet'))

# Prepare
df = baseline.copy()
df['low_econ_sat_bl'] = (df['econ_sat_quintile'] == 'Q1 (lowest)').astype(float)
df['current_smoker'] = (df['smoking'] == 2).astype(float)

# ============================================================================
# TABLE 1: BASELINE CHARACTERISTICS WITH P-VALUES
# ============================================================================
print("GENERATING TABLE 1")
print("=" * 100)

low = df[df['low_econ_sat_bl'] == 1]
high = df[df['low_econ_sat_bl'] == 0]

def fmt_mean_sd(series):
    v = series.dropna()
    return f"{v.mean():.1f} ({v.std():.1f})"

def fmt_pct(series, val=None):
    v = series.dropna()
    if val is not None:
        return f"{(v == val).mean()*100:.1f}"
    return f"{v.mean()*100:.1f}"

def p_continuous(s1, s2):
    v1 = s1.dropna()
    v2 = s2.dropna()
    try:
        _, p = stats.mannwhitneyu(v1, v2, alternative='two-sided')
        return p
    except (ValueError, TypeError, ZeroDivisionError):
        return np.nan

def p_categorical(s1, s2):
    combined = pd.concat([s1, s2])
    cats = combined.dropna().unique()
    try:
        ct = pd.crosstab(
            pd.concat([pd.Series(['low']*len(s1), index=s1.index),
                       pd.Series(['high']*len(s2), index=s2.index)]),
            pd.concat([s1, s2])
        )
        _, p, _, _ = stats.chi2_contingency(ct)
        return p
    except (ValueError, TypeError, ZeroDivisionError):
        return np.nan

def fmt_p(p):
    if pd.isna(p): return ''
    if p < 0.001: return '<0.001'
    return f"{p:.3f}"

rows = []

# N
rows.append(['N', f"{len(df):,}", f"{len(low):,}", f"{len(high):,}", ''])

# Age
p = p_continuous(low['age'], high['age'])
rows.append(['Age, years, mean (SD)', fmt_mean_sd(df['age']), fmt_mean_sd(low['age']),
             fmt_mean_sd(high['age']), fmt_p(p)])

# Female
p = p_categorical(low['female'], high['female'])
rows.append(['Female, %', fmt_pct(df['female']), fmt_pct(low['female']),
             fmt_pct(high['female']), fmt_p(p)])

# Married
p = p_categorical(low['married'], high['married'])
rows.append(['Married, %', fmt_pct(df['married']), fmt_pct(low['married']),
             fmt_pct(high['married']), fmt_p(p)])

# Education
edu_map = {
    'No formal/elementary': lambda s: (s <= 1).mean()*100,
    'Middle school': lambda s: (s == 2).mean()*100,
    'High school': lambda s: (s == 3).mean()*100,
    'College or higher': lambda s: (s >= 4).mean()*100,
}
p = p_categorical(low['education'], high['education'])
rows.append(['Education, %', '', '', '', fmt_p(p)])
for label, fn in edu_map.items():
    rows.append([f'  {label}', f"{fn(df['education']):.1f}",
                 f"{fn(low['education']):.1f}",
                 f"{fn(high['education']):.1f}", ''])

# Health
p = p_continuous(low['self_rated_health'], high['self_rated_health'])
rows.append(['Self-rated health (1-5), mean (SD)', fmt_mean_sd(df['self_rated_health']),
             fmt_mean_sd(low['self_rated_health']), fmt_mean_sd(high['self_rated_health']), fmt_p(p)])

p = p_continuous(low['chronic_count'], high['chronic_count'])
rows.append(['No. of chronic diseases, mean (SD)', fmt_mean_sd(df['chronic_count']),
             fmt_mean_sd(low['chronic_count']), fmt_mean_sd(high['chronic_count']), fmt_p(p)])

# Individual chronic conditions
for var, label in [('hypertension', 'Hypertension'), ('diabetes', 'Diabetes'),
                   ('cancer', 'Cancer'), ('heart_disease', 'Heart disease'),
                   ('stroke', 'Cerebrovascular disease')]:
    p = p_categorical(low[var], high[var])
    rows.append([f'{label}, %', fmt_pct(df[var], 1), fmt_pct(low[var], 1),
                 fmt_pct(high[var], 1), fmt_p(p)])

# BMI
p = p_continuous(low['bmi'], high['bmi'])
rows.append(['BMI, kg/m\u00b2, mean (SD)', fmt_mean_sd(df['bmi']),
             fmt_mean_sd(low['bmi']), fmt_mean_sd(high['bmi']), fmt_p(p)])

# Smoking
p = p_categorical(low['current_smoker'], high['current_smoker'])
rows.append(['Current smoker, %', fmt_pct(df['current_smoker']),
             fmt_pct(low['current_smoker']), fmt_pct(high['current_smoker']), fmt_p(p)])

# Depression
p = p_categorical(low['depression'], high['depression'])
rows.append(['Depression (CES-D), %', fmt_pct(df['depression'], 1),
             fmt_pct(low['depression'], 1), fmt_pct(high['depression'], 1), fmt_p(p)])

# IADL
p = p_continuous(low['iadl'], high['iadl'])
rows.append(['IADL limitations, mean (SD)', fmt_mean_sd(df['iadl']),
             fmt_mean_sd(low['iadl']), fmt_mean_sd(high['iadl']), fmt_p(p)])

# Financial
p = p_continuous(low['econ_satisfaction'], high['econ_satisfaction'])
rows.append(['Economic satisfaction (0-100), mean (SD)', fmt_mean_sd(df['econ_satisfaction']),
             fmt_mean_sd(low['econ_satisfaction']), fmt_mean_sd(high['econ_satisfaction']), fmt_p(p)])

p = p_continuous(low['hh_income'], high['hh_income'])
rows.append(['Household income (10,000 won), mean (SD)', fmt_mean_sd(df['hh_income']),
             fmt_mean_sd(low['hh_income']), fmt_mean_sd(high['hh_income']), fmt_p(p)])

on_welf_all = (df['basic_livelihood'].fillna(0) > 0).astype(float)
on_welf_low = (low['basic_livelihood'].fillna(0) > 0).astype(float)
on_welf_high = (high['basic_livelihood'].fillna(0) > 0).astype(float)
rows.append(['Welfare recipient (NBLSS), %', fmt_pct(on_welf_all),
             fmt_pct(on_welf_low), fmt_pct(on_welf_high),
             fmt_p(p_categorical(on_welf_low, on_welf_high))])

pension_all = (df['national_pension'].fillna(0) > 0).astype(float)
pension_low = (low['national_pension'].fillna(0) > 0).astype(float)
pension_high = (high['national_pension'].fillna(0) > 0).astype(float)
rows.append(['National Pension recipient, %', fmt_pct(pension_all),
             fmt_pct(pension_low), fmt_pct(pension_high),
             fmt_p(p_categorical(pension_low, pension_high))])

# Outcomes
rows.append(['', '', '', '', ''])
rows.append(['Follow-up years, mean (SD)', fmt_mean_sd(df['surv_time']),
             fmt_mean_sd(low['surv_time']), fmt_mean_sd(high['surv_time']), ''])
rows.append(['Deaths during follow-up, n (%)',
             f"{df['died'].sum():,} ({df['died'].mean()*100:.1f})",
             f"{low['died'].sum():,} ({low['died'].mean()*100:.1f})",
             f"{high['died'].sum():,} ({high['died'].mean()*100:.1f})",
             fmt_p(p_categorical(low['died'], high['died']))])

# Save
t1 = pd.DataFrame(rows, columns=['Characteristic',
                                   f'Overall\n(N={len(df):,})',
                                   f'Low economic\nsatisfaction (Q1)\n(N={len(low):,})',
                                   f'Higher economic\nsatisfaction (Q2-Q5)\n(N={len(high):,})',
                                   'P value'])
t1.to_csv(os.path.join(TAB, 'table1_publication.csv'), index=False)

# Print
for _, row in t1.iterrows():
    print(f"{row['Characteristic']:<45} {row.iloc[1]:>18} {row.iloc[2]:>20} {row.iloc[3]:>20} {row.iloc[4]:>10}")

# ============================================================================
# Verify person-years
# ============================================================================
print(f"\n\nTotal person-years of follow-up: {df['surv_time'].sum():,.0f}")
print(f"Mortality rate: {df['died'].sum() / df['surv_time'].sum() * 1000:.1f} per 1000 person-years")

mort_low = low['died'].sum() / low['surv_time'].sum() * 1000
mort_high = high['died'].sum() / high['surv_time'].sum() * 1000
print(f"Mortality rate, low econ sat: {mort_low:.1f} per 1000 person-years")
print(f"Mortality rate, higher econ sat: {mort_high:.1f} per 1000 person-years")

print("Done.")
