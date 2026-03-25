# Code Review Remediation Plan

Date: 2026-03-25

Based on:

- [CODE_REVIEW_PANEL_2026-03-25.md](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/CODE_REVIEW_PANEL_2026-03-25.md)

## Ground Rule

Per your instruction, **everything below is treated as needing a fix unless explicitly marked `Preference only`**.

Recommended default stance:

- if code and manuscript disagree, fix the code or manuscript so there is one truth
- if there are multiple plausible definitions, pick one and propagate it everywhere
- if an output is used in the manuscript, it must have one authoritative generated artifact

## Stop-The-Line Issues

These are the items I would fix **before trusting any reported result**.

### 1. Fix death-date sentinel handling and rebuild the analytic sample

Status: `Required`

Why:

- [02_build_analytic_sample.py#L348](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/02_build_analytic_sample.py#L348)
- [02_build_analytic_sample.py#L400](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/02_build_analytic_sample.py#L400)
- Current build likely misses 3 deaths.

Concrete actions:

1. Convert death date sentinels like `-8/-9` to missing before survival-time calculation.
2. Rebuild:
   - `baseline_analytic.parquet`
   - `panel_data.parquet`
   - `death_records.parquet`
3. Record old vs new:
   - analytic `N`
   - deaths
   - mean follow-up

Acceptance criteria:

- death dates no longer contain sentinel values in the person-level death table
- sample counts are recomputed and documented
- every downstream manuscript number that depends on deaths is regenerated

### 2. Freeze one definition of low economic satisfaction and use it everywhere

Status: `Required`

Why:

- Manuscript says fixed baseline bottom-quintile threshold `<=30` at [manuscript.md#L57](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/manuscript.md#L57)
- Code uses wave-specific quintiles at [02_build_analytic_sample.py#L206](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/02_build_analytic_sample.py#L206)

Recommended default fix:

- adopt the manuscript’s current definition: fixed `<=30`

Concrete actions:

1. Replace wave-specific `low_econ_sat` construction with one fixed rule, or explicitly rename the time-varying construct if you decide to keep wave-specific quintiles.
2. Propagate the chosen rule through:
   - [02_build_analytic_sample.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/02_build_analytic_sample.py)
   - [06_wealth_shock_time_varying.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/06_wealth_shock_time_varying.py)
   - [08_objective_vs_subjective.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/08_objective_vs_subjective.py)
   - [11_marginal_structural_models.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/11_marginal_structural_models.py)
   - [12_basic_pension_analysis.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/12_basic_pension_analysis.py)
   - manuscript Methods and Results

Acceptance criteria:

- one threshold definition only
- no script silently recomputes a different low-satisfaction rule
- Methods, tables, and outputs all use the same construct name and definition

### 3. Fix time-varying interval construction across missed waves

Status: `Required`

Why:

- [06_wealth_shock_time_varying.py#L151](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/06_wealth_shock_time_varying.py#L151)
- Current implementation carries covariates across skipped waves while the manuscript says exposures are updated biennially.

Recommended default fix:

- treat nonconsecutive follow-up as a break in clean biennial updating

Concrete actions:

1. Decide and document one rule for missed waves:
   - censor at first missed wave, or
   - split at scheduled wave boundaries with explicit carry-forward logic
2. Implement the rule in the person-period builder.
3. Explicitly document what happens to:
   - exposures
   - time-varying confounders
   - censoring time

Acceptance criteria:

- interval construction matches manuscript language exactly
- no hidden carry-forward beyond what the Methods disclose
- time-varying counts (`N intervals`, `events`) are regenerated and updated in manuscript/table text

### 4. Harmonize the wealth-shock definition across scripts

Status: `Required`

Why:

- [02_build_analytic_sample.py#L177](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/02_build_analytic_sample.py#L177)
- [06_wealth_shock_time_varying.py#L93](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/06_wealth_shock_time_varying.py#L93)

Concrete actions:

1. Pick one edge-case rule for `prev == 0` and `prev < 0`.
2. Apply the same rule in all scripts.
3. Add the edge-case definition to the Methods or supplement.

Acceptance criteria:

- one wealth-shock rule only
- separate and time-varying analyses are based on the same construct

## Core Manuscript-Code Alignment Fixes

These are required **before another serious manuscript review round**.

### 5. Rebuild Table 2 from one canonical artifact

Status: `Required`

Why:

- Current Table 2 is stitched from multiple scripts and the narrative points to a different analysis than the displayed panel.

Concrete actions:

1. Create one authoritative table-building step for all Table 2 panels.
2. Feed it only from named model-output files.
3. Save a single generated artifact, for example:
   - `output/tables/table2_manuscript.csv`
4. Make the manuscript table match that file exactly.

Acceptance criteria:

- one file is the sole source for Table 2
- Table 2 panel labels, `N`, HRs, and text references all match that file
- README and `run_all.py` both point to that exact file

### 6. Rebuild Table 3 from one canonical artifact

Status: `Required`

Why:

- Current Table 3 cannot be regenerated cleanly from the declared outputs.

Concrete actions:

1. Create one authoritative time-varying results export covering all manuscript Table 3 panels.
2. Remove dependence on stale or duplicate files like `table4_time_varying_results.csv` unless promoted as the new canonical artifact.
3. Make the manuscript table and narrative read from that canonical output.

Acceptance criteria:

- one file is the sole source for Table 3
- all displayed Table 3 values can be traced directly to generated outputs

### 7. Decide what the primary baseline model actually is

Status: `Required`

Why:

- [03_cox_models.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/03_cox_models.py) and the manuscript do not line up on the covariate set.

Recommended default fix:

- designate the expanded-health / clearer manuscript-aligned model as primary, then regenerate the publication table from that pipeline

Concrete actions:

1. Pick the primary baseline specification.
2. Refactor scripts so that primary-model covariates are not hard-coded in multiple places.
3. Rewrite Methods to match the implemented model exactly.

Acceptance criteria:

- one declared primary model
- one declared covariate set
- no baseline table/text line points to a different script than the actual source

### 8. Rewrite the MSM section as a limited sensitivity analysis unless the code is upgraded

Status: `Required`

Why:

- No censoring weights
- incomplete history handling
- balance diagnostics are partial

Concrete actions:

1. Either:
   - upgrade MSMs to include censoring weights and stronger diagnostics, or
   - rewrite the manuscript to describe them as treatment-weighted sensitivity analyses with important limitations
2. Remove or soften:
   - “total effect”
   - strong sequential exchangeability language
   - direct-effect language for standard adjusted models

Acceptance criteria:

- prose does not claim a stronger estimand than the code supports

### 9. Fix MI so it matches what the manuscript says it is doing

Status: `Required`

Why:

- structurally missing `current_drinker` is being imputed
- objective “bottom quintile” exposures are not staying bottom quintile after imputation

Recommended default fix:

- remove structurally missing wave-2 drinking from the MI primary model unless you can justify and implement a principled treatment
- derive low-income / low-assets thresholds within each completed dataset, or rewrite the estimand plainly if you keep fixed observed thresholds

Concrete actions:

1. Decide whether `current_drinker` belongs in the MI primary model.
2. Fix binary/structural missingness handling.
3. Redefine post-imputation exposure derivation so the “bottom quintile” claim remains true, or change the manuscript wording.
4. Regenerate MI results and the manuscript’s joint-model narrative.

Acceptance criteria:

- no impossible imputed covariate values are fed into the analysis model
- exposure labels in the manuscript match how exposures are actually derived after imputation

### 10. Fix the measurement-sensitivity narrative

Status: `Required`

Why:

- cutpoint and spline analyses run on a smaller, different sample than the manuscript currently foregrounds

Concrete actions:

1. Either harmonize these analyses to the main sample, or
2. explicitly report the smaller sample and explain why it differs

Acceptance criteria:

- the manuscript no longer implies that these are same-sample robustness checks if they are not

## Reproducibility and Compendium Hardening

These are required if you want the package to survive outside scrutiny, and I would still fix them before submission if possible.

### 11. Make `run_all.py` fail hard on missing outputs

Status: `Required`

Concrete actions:

1. Missing expected output should exit nonzero.
2. Add validation for every declared manuscript-facing artifact.
3. Validate a few key row counts / summary numbers for the canonical table files.

Acceptance criteria:

- a broken pipeline cannot report success

### 12. Complete the environment spec

Status: `Required`

Concrete actions:

1. Add parquet support dependency.
2. Remove unused dependencies if truly unused.
3. Add one stronger environment artifact:
   - lockfile, or
   - exact Python version file, or
   - container spec

Acceptance criteria:

- a clean machine can install and run the project from the documented environment alone

### 13. Add a strict raw-data manifest and fail-fast checks

Status: `Required`

Concrete actions:

1. List every required raw file.
2. Add existence checks before the build begins.
3. Stop on missing tracker/exit files rather than continuing silently.

Acceptance criteria:

- partial raw-data states cannot produce “successful” outputs

### 14. Create one provenance manifest per manuscript table and figure

Status: `Required`

Concrete actions:

1. Add a simple provenance file, for example:
   - `submission_ssm/MANUSCRIPT_PROVENANCE.md`
2. For each manuscript table/figure, record:
   - canonical output file
   - generating script
   - manuscript location

Acceptance criteria:

- any reviewer can trace every displayed number without guesswork

### 15. Clean the output tree and remove stale artifacts

Status: `Required`

Concrete actions:

1. Remove or quarantine stale duplicates and legacy files.
2. Remove workspace residue like `.DS_Store` and committed `__pycache__`.
3. Keep only canonical outputs in the final manifest.

Acceptance criteria:

- no ambiguity between “current”, “legacy”, and “scratch” outputs

### 16. Refactor duplicated derivations into shared helpers

Status: `Required`

Why:

- duplicated derivation logic is the main source of analytic drift

Concrete actions:

1. Create shared helper functions for:
   - low-satisfaction derivation
   - drinking/exercise preparation
   - CES-D construction
   - low-income derivation
   - wealth-shock derivation
2. Import them everywhere instead of redefining locally.

Acceptance criteria:

- changing a construct definition requires touching one source, not five

### 17. Stop blanket suppression of convergence warnings

Status: `Required`

Concrete actions:

1. Remove broad `filterwarnings` calls for convergence issues.
2. If a model truly needs regularization, log that explicitly.
3. Fail or flag when the intended model does not converge.

Acceptance criteria:

- numerical instability is visible, not silently hidden

## Preference-Only Items

These are the few items I would treat as true preference rather than required fixes.

### A. Improve the Kaplan-Meier figure presentation

Status: `Preference only`

Examples:

- use a full 0-1 y-axis
- add numbers-at-risk

This matters for polish, but it is not a core validity blocker.

## Recommended Order of Operations

1. Fix death-date cleaning.
2. Freeze low-satisfaction definition.
3. Harmonize wealth-shock definition.
4. Fix person-period interval construction and carry-forward logic.
5. Rebuild core datasets and rerun all downstream analyses.
6. Fix MI and rerun joint models.
7. Rebuild canonical Table 2 and Table 3 artifacts.
8. Rewrite manuscript Methods/Results/limitations to match the rerun outputs exactly.
9. Rewrite MSM section conservatively unless upgraded.
10. Harden `run_all.py`, environment, and raw-data checks.
11. Clean the output tree and create provenance manifest.
12. Refactor shared derivations and remove duplicated logic.

## Suggested Deliverables

When the remediation is done, the repository should have:

- one corrected analytic rebuild
- one canonical output per manuscript table/figure
- one provenance manifest
- one strict replication driver
- one cleaned output tree
- one manuscript whose displayed numbers all match generated artifacts

## Practical Definition of “Done”

I would call this remediated only when all of the following are true:

1. The code and manuscript agree on every exposure definition and model description.
2. Every displayed manuscript table comes from one generated file.
3. `run_all.py` fails on missing raw data or missing outputs.
4. A clean machine can install the environment and run the pipeline.
5. The output directory no longer contains stale competing artifacts.
6. The high-severity panel findings no longer apply.
