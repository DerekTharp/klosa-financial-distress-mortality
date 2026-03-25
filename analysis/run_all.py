"""
run_all.py
Pipeline driver script. Runs all analysis scripts in order and validates outputs.

Usage: python run_all.py
"""

import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

SCRIPTS = [
    "02_build_analytic_sample.py",
    "03_cox_models.py",
    "04_subgroups_and_sensitivity.py",
    "05_generate_publication_tables.py",
    "06_wealth_shock_time_varying.py",
    "07_extended_sensitivity.py",
    "08_objective_vs_subjective.py",
    "09_multiple_imputation.py",
    "10_measurement_sensitivity.py",
    "11_marginal_structural_models.py",
    "12_basic_pension_analysis.py",
]

EXPECTED_OUTPUTS = {
    # Data files
    "output/baseline_analytic.parquet": "02",
    "output/panel_data.parquet": "02",
    "output/death_records.parquet": "02",
    "output/person_period_data.parquet": "06",
    # Figures
    "output/figures/figure1_km_curves.png": "03",
    "output/figures/figure2_discordance.png": "08",
    "output/figures/figure3_dose_response.png": "04",
    "output/figures/figure4_km_wealth_shock.png": "06",
    "output/figures/efigure4_spline_dose_response.png": "10",
    # Tables
    "output/tables/table1_publication.csv": "05",
    "output/tables/table1_baseline_characteristics.csv": "05",
    "output/tables/table2_cox_models.csv": "03",
    "output/tables/subgroup_analyses.csv": "03",
    # Supplementary
    "output/supplementary/supplementary_results.json": "07",
    "output/supplementary/objective_vs_subjective_models.csv": "08",
    "output/supplementary/multiple_imputation_results.json": "09",
    "output/supplementary/measurement_sensitivity.json": "10",
    "output/supplementary/msm_results.json": "11",
    "output/supplementary/basic_pension_analysis.json": "12",
}


def run_script(script_name):
    """Run a single analysis script."""
    script_path = os.path.join(BASE, script_name)
    print(f"\n{'=' * 60}")
    print(f"Running: {script_name}")
    print("=" * 60)
    result = subprocess.run(
        [sys.executable, script_path],
        cwd=BASE,
        capture_output=False,
    )
    if result.returncode != 0:
        print(f"FAILED: {script_name} (exit code {result.returncode})")
        return False
    return True


def validate_outputs():
    """Check that all expected output files exist."""
    project_root = os.path.dirname(BASE)
    missing = []
    for rel_path, source_script in EXPECTED_OUTPUTS.items():
        full_path = os.path.join(project_root, rel_path)
        if not os.path.exists(full_path):
            missing.append((rel_path, source_script))
    return missing


def validate_data():
    """Check key data properties."""
    import pandas as pd

    project_root = os.path.dirname(BASE)
    out = os.path.join(project_root, "output")

    baseline = pd.read_parquet(os.path.join(out, "baseline_analytic.parquet"))
    assert len(baseline) == 10384, f"Expected 10384, got {len(baseline)}"
    assert baseline["died"].sum() == 3074, f"Expected 3074 deaths, got {baseline['died'].sum()}"

    pp = pd.read_parquet(os.path.join(out, "person_period_data.parquet"))
    assert len(pp) > 60000, f"Expected >60000 person-intervals, got {len(pp)}"

    print("\nData validation passed:")
    print(f"  Baseline N = {len(baseline)}")
    print(f"  Deaths = {int(baseline['died'].sum())}")
    print(f"  Person-intervals = {len(pp)}")


if __name__ == "__main__":
    print("KLoSA Financial Distress & Mortality Analysis Pipeline")
    print("=" * 60)

    failed = []
    for script in SCRIPTS:
        success = run_script(script)
        if not success:
            failed.append(script)
            print(f"\nStopping: {script} failed.")
            sys.exit(1)

    print(f"\n{'=' * 60}")
    print("OUTPUT VALIDATION")
    print("=" * 60)

    missing = validate_outputs()
    if missing:
        print("Missing output files:")
        for path, script in missing:
            print(f"  {path} (from script {script})")
        print(f"\nVALIDATION FAILED: {len(missing)} expected output(s) missing.")
        sys.exit(1)
    else:
        print("All expected output files present.")

    validate_data()

    print(f"\nVALIDATION PASSED: all {len(EXPECTED_OUTPUTS)} outputs verified.")
    print(f"All {len(SCRIPTS)} scripts completed successfully.")
