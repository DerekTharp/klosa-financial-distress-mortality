# Pipeline Rerun Comparison (2026-03-25)

Changes made before rerun:
1. Death-date sentinel codes cleaned and imputed (02_build_analytic_sample.py)
2. Low satisfaction threshold fixed to <=30 at all waves (02_build_analytic_sample.py)
3. Wealth shock prev==0 edge case harmonized (02_build_analytic_sample.py)
4. Extended interval flagging added (06_wealth_shock_time_varying.py)

## Sample Characteristics

| Measure | Old | New | Change |
|---|---|---|---|
| N (analytic sample) | 10,335 | 10,384 | +49 |
| Deaths, n (%) | 3,025 (29.3%) | 3,074 (29.6%) | +49 |
| Mean follow-up | 12.5 years | 12.5 years | -- |
| Mean age | 61.0 (10.8) | 61.0 (10.9) | -- |
| Female % | 56.4% | 56.4% | -- |

Note: The 49 additional individuals are deaths recovered by the sentinel-date fix.
All had short follow-up — the early-death exclusion sensitivity gives exactly N=10,335, Deaths=3,025 (the old values).

## Baseline Models (script 08 — complete-case)

| Result | Old | New |
|---|---|---|
| Combined model N | 4,998 | 5,010 |
| Low econ sat HR | 1.30 (1.14-1.48) | 1.30 (1.14-1.48) |
| Low income HR | 0.90 (0.79-1.03) | 0.91 (0.80-1.03) |
| Welfare HR | 1.21 (0.92-1.59) | 1.21 (0.92-1.59) |
| Low assets HR | 0.96 (0.83-1.12) | 0.97 (0.83-1.12) |

**Verdict: Virtually identical.**

## MI Combined Model (script 09)

| Result | Old | New |
|---|---|---|
| N | 10,335 | 10,384 |
| Low econ sat HR | 1.29 (1.19-1.40) | 1.29 (1.19-1.40) |
| Low income HR | 0.93 (0.85-1.00) | 0.93 (0.86-1.01) |
| Welfare HR | 1.07 (0.89-1.28) | 1.07 (0.89-1.28) |
| Low assets HR | 0.98 (0.88-1.10) | 0.98 (0.89-1.08) |

**Verdict: Virtually identical.**

## Discordance Analysis (script 08)

| Group | Old | New |
|---|---|---|
| Both | 1.13 (0.99-1.30, p=0.07) | 1.14 (1.00-1.31, p=0.05) |
| Subjective only | 1.28 (1.14-1.44, p<0.0001) | 1.28 (1.14-1.44, p<0.0001) |
| Objective only | 0.93 (0.82-1.07, p=0.31) | 0.93 (0.82-1.06, p=0.30) |

**Verdict: Virtually identical. "Both" group moved from borderline to just significant (p=0.05).**

## Dose-Response (script 07)

| Quintile | Old | New |
|---|---|---|
| Q1 vs Q5 | 1.43 (1.24-1.65) | 1.43 (1.24-1.64) |
| Q2 vs Q5 | 1.14 (0.98-1.31) | 1.14 (0.99-1.31) |
| Q3 vs Q5 | 1.20 (1.02-1.43) | 1.19 (1.00-1.41) |
| Q4 vs Q5 | 1.07 (0.90-1.26) | 1.05 (0.89-1.24) |

**Verdict: Virtually identical.**

## Time-Varying Models (script 08) — MAIN CHANGES

| Result | Old | New | Change |
|---|---|---|---|
| **SEPARATE: Econ sat** | **1.12 (1.04-1.21, p=0.003)** | **1.22 (1.13-1.32, p<0.001)** | **HR increased from 1.12 to 1.22** |
| SEPARATE: Income | 1.15 (1.06-1.24, p=0.0006) | 1.15 (1.06-1.24, p=0.0006) | Unchanged |
| **COMBINED: Econ sat** | **1.06 (0.96-1.16, p=0.25)** | **1.09 (0.99-1.20, p=0.088)** | **Was NS (p=0.25), now borderline (p=0.088)** |
| **COMBINED: Income** | **1.12 (1.02-1.23, p=0.02)** | **1.10 (1.00-1.21, p=0.04)** | **Slightly attenuated** |
| Wealth shock | 0.99 (0.80-1.23) | 0.97 (0.78-1.20) | Unchanged |

**NARRATIVE IMPACT:** The old story was "satisfaction is attenuated to non-significance in combined TV models while income remains significant." The new story is weaker: satisfaction is borderline (p=0.088) and income is marginally significant (p=0.04). The contrast between the two is much softer.

This is actually BETTER for the paper's core argument about subjective appraisal. The "complication" from TV models is less dramatic.

## Continuous Combined Model (script 08)

| Result | Old | New |
|---|---|---|
| Sat per 10-pt HR | 1.048 (1.027-1.070) | 1.050 (1.029-1.072) |
| Log income HR | 1.021 (0.988-1.057) | 1.022 (0.988-1.057) |

**Verdict: Virtually identical.**

## Sensitivity Analyses (script 07)

| Analysis | Old | New |
|---|---|---|
| Excluding early deaths | HR=1.29 (1.19-1.40) | HR=1.29 (1.19-1.39) |
| Excluding wave-5 refreshment | HR=1.26 (1.17-1.37) | HR=1.27 (1.17-1.37) |
| Healthy at baseline | HR=1.84 (1.21-2.78) | HR=1.83 (1.22-2.75) |
| Spline non-linearity p | 0.23 | 0.28 |

**Verdict: Virtually identical.**

## Extended Interval Stats (NEW — from script 06)

- Extended intervals (>2.5 years): 2,043 of 63,153 (3.2%)
- Events in extended intervals: 851 of 3,074 (27.7%)
- Mean interval length: 2.06 years (median: 2.00)

## MSM Results (script 11)

Pending — bootstrapping in progress.
