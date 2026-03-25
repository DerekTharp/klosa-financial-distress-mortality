# Manuscript Provenance Manifest

**Date:** 2026-03-25
**Manuscript:** `submission_ssm/manuscript.md`
**Status:** Authoritative provenance record for the SSM submission

This file maps every table, figure, and supplementary display item in the manuscript to its generating script and canonical output file. If a number in the manuscript cannot be traced back through this manifest, it should be treated as unverified.

---

## Main Tables

### Table 1 -- Baseline Characteristics

| Field | Value |
|---|---|
| Script | `analysis/05_generate_publication_tables.py` |
| Output | `output/tables/table1_baseline_characteristics.csv` |
| Manuscript location | `submission_ssm/manuscript.md`, Table 1 section |

### Table 2 -- Cox Proportional Hazards Models (Separate and Combined)

| Field | Value |
|---|---|
| Script (Panels A--B, separate models) | `analysis/08_objective_vs_subjective.py` |
| Script (Panels C--D, combined models) | `analysis/08_objective_vs_subjective.py` |
| Script (MI version, Supplementary Table 7) | `analysis/09_multiple_imputation.py` |
| Output (Panels A--B) | `output/supplementary/objective_vs_subjective_models.csv` |
| Output (Panels C--D) | `output/tables/table2_combined_models.csv` |
| Output (MI) | `output/supplementary/multiple_imputation_results.json` |
| Manuscript location | `submission_ssm/manuscript.md`, Table 2 section |
| Note | Panel C complete-case results come from script 08. MI results (N=10,384) referenced in the running text come from script 09. |

### Table 3 -- Time-Varying Models

| Field | Value |
|---|---|
| Script (wealth shock panels) | `analysis/06_wealth_shock_time_varying.py` |
| Script (satisfaction + income TV models, combined model) | `analysis/08_objective_vs_subjective.py` |
| Output | `output/tables/table3_time_varying_models.csv` |
| Note | This file is the canonical source for all Table 3 values. |
| Manuscript location | `submission_ssm/manuscript.md`, Table 3 section |

---

## Main Figures

### Figure 1 -- Kaplan-Meier Survival Curves

| Field | Value |
|---|---|
| Script | `analysis/03_cox_models.py` |
| Output | `output/figures/figure1_km_curves.png` |
| Manuscript copy | `submission_ssm/figures/Figure1_KM_curves.png` |

### Figure 2 -- Discordance Forest Plot

| Field | Value |
|---|---|
| Script | `analysis/08_objective_vs_subjective.py` |
| Output | `output/figures/figure2_discordance.png` |
| Manuscript copy | `submission_ssm/figures/Figure2_discordance.png` |

---

## Supplementary Tables

### Supplementary Table 1 -- Construct Validity

| Field | Value |
|---|---|
| Script | `analysis/03_cox_models.py` |
| Output | `output/supplementary/supplementary_results.json` (`construct_validity`) |

### Supplementary Table 2 -- Subgroup Analyses

| Field | Value |
|---|---|
| Script | `analysis/03_cox_models.py` |
| Output | `output/tables/subgroup_analyses.csv` |

### Supplementary Table 3 -- Proportional Hazards Tests

| Field | Value |
|---|---|
| Script | `analysis/03_cox_models.py` |
| Output | `output/supplementary/ph_test_results.csv` |

### Supplementary Table 4 -- Sensitivity Analyses

| Field | Value |
|---|---|
| Script | `analysis/07_extended_sensitivity.py` |
| Output | `output/supplementary/supplementary_results.json` (`sensitivity_no_refreshment`, `healthy_baseline`, `dose_response`, `power_analysis`) |
| Output (income equivalization) | `output/supplementary/income_equivalisation.json` |

### Supplementary Table 5 -- Retention Analysis

| Field | Value |
|---|---|
| Script | `analysis/04_subgroups_and_sensitivity.py` |
| Output | `output/supplementary/supplementary_results.json` (`attrition`) |

### Supplementary Table 6 -- Alternative Thresholds

| Field | Value |
|---|---|
| Script | `analysis/10_measurement_sensitivity.py` |
| Output | `output/supplementary/measurement_sensitivity.json` |

### Supplementary Table 7 -- Multiple Imputation Results

| Field | Value |
|---|---|
| Script | `analysis/09_multiple_imputation.py` |
| Output | `output/supplementary/multiple_imputation_results.json` |

### Supplementary Table 8 -- Marginal Structural Model Results

| Field | Value |
|---|---|
| Script | `analysis/11_marginal_structural_models.py` |
| Output | `output/supplementary/msm_results.json` |

### Supplementary Table 9 -- Basic Pension Analysis

| Field | Value |
|---|---|
| Script | `analysis/12_basic_pension_analysis.py` |
| Output | `output/supplementary/basic_pension_analysis.json` |

---

## Supplementary Figures

### Supplementary Figure 1 -- Directed Acyclic Graph (DAG)

| Field | Value |
|---|---|
| Output | `output/figures/efigure3_dag.png` |

### Supplementary Figure 2 -- Kaplan-Meier Curves for Wealth Shock

| Field | Value |
|---|---|
| Script | `analysis/06_wealth_shock_time_varying.py` |
| Output | `output/figures/figure4_km_wealth_shock.png` |

### Supplementary Figure 3 -- Dose-Response by Quintiles

| Field | Value |
|---|---|
| Script | `analysis/03_cox_models.py` |
| Output | `output/figures/figure3_dose_response.png` |

### Supplementary Figure 4 -- Restricted Cubic Spline

| Field | Value |
|---|---|
| Script | `analysis/10_measurement_sensitivity.py` |
| Output | `output/figures/efigure4_spline_dose_response.png` |
