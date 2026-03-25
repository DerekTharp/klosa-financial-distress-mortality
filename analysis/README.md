# Analysis Code: Economic Insecurity and Mortality in South Korea

Replication package for: "Economic insecurity and mortality in later life: a 16-year national cohort study from South Korea"

## Data

KLoSA (Korean Longitudinal Study of Aging) data are publicly available from the Korea Employment Information Service: https://survey.keis.or.kr

Place the KLoSA data files in:
```
KLoSA Dataset (Korean Longitudinal Study of Aging)/data/
    main_survey/       # w01_e.dta through w09_e.dta
    structural/        # str01_e.dta through str09_e.dta
    exit_interviews/   # Exit interview files
    longitudinal_tracker/  # Tracker files
```

## Setup

```bash
pip install -r requirements.txt
```

Requires Python >= 3.12.

## Running

Run all scripts in sequence:
```bash
python run_all.py
```

Or run individual scripts (must respect dependency order):
```bash
python 02_build_analytic_sample.py   # Must run first
python 03_cox_models.py
python 04_subgroups_and_sensitivity.py
python 05_generate_publication_tables.py
python 06_wealth_shock_time_varying.py  # Must run before 08, 11, 12
python 07_extended_sensitivity.py
python 08_objective_vs_subjective.py
python 09_multiple_imputation.py
python 10_measurement_sensitivity.py
python 11_marginal_structural_models.py  # ~2 hours (1000 bootstrap iterations)
python 12_basic_pension_analysis.py
```

## Script descriptions

| Script | Purpose | Key outputs |
|--------|---------|-------------|
| `config.py` | Shared paths | — |
| `model_specs.py` | Centralized covariate definitions | — |
| `01_data_exploration.py` | Exploratory data analysis | Console output only |
| `02_build_analytic_sample.py` | Build analytic datasets | `baseline_analytic.parquet`, `panel_data.parquet`, `death_records.parquet` |
| `03_cox_models.py` | KM curves, sequential Cox models | Figure 1, Table 2 |
| `04_subgroups_and_sensitivity.py` | Dose-response, subgroups | Figure 3 (dose-response), eTable 2, eTable 4 |
| `05_generate_publication_tables.py` | Table 1 descriptive statistics | Table 1 |
| `06_wealth_shock_time_varying.py` | Person-period dataset, time-varying Cox | Figure 4 (wealth shock KM), `person_period_data.parquet` |
| `07_extended_sensitivity.py` | Construct validity, ICC, attrition, PH tests | eTables 1, 3, 5; supplementary results |
| `08_objective_vs_subjective.py` | Combined models (Table 2 Panels C-D), discordance | Figure 2 (discordance), Table 2 combined models |
| `09_multiple_imputation.py` | MI for combined model (M=20) | eTable 7 |
| `10_measurement_sensitivity.py` | Alternative cut-points, RCS splines | eTable 6, eFigure 4 |
| `11_marginal_structural_models.py` | MSMs with stabilised IPTW, bootstrap CIs | eTable 8 |
| `12_basic_pension_analysis.py` | Basic Pension expansion analysis | eTable 9 |

## Output structure

```
output/
    baseline_analytic.parquet
    panel_data.parquet
    person_period_data.parquet
    death_records.parquet
    figures/
        figure1_km_curves.png
        figure2_discordance.png
        figure3_dose_response.png
        figure4_km_wealth_shock.png
        efigure3_dag.png
        efigure4_spline_dose_response.png
    tables/
        table1_publication.csv
        table1_baseline_characteristics.csv
        table2_cox_models.csv
        table2_combined_models.csv
        table3_time_varying_models.csv
        subgroup_analyses.csv
    supplementary/
        supplementary_results.json
        objective_vs_subjective_models.csv
        multiple_imputation_results.json
        measurement_sensitivity.json
        msm_results.json
        basic_pension_analysis.json
        income_equivalisation.json
```
