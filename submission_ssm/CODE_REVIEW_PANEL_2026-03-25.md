# Code Review Panel: Financial Distress and Mortality Pipeline

Date: 2026-03-25

## Scope

This memo consolidates a 10-reviewer expert code audit of the analysis pipeline and current manuscript:

- Manuscript: [submission_ssm/manuscript.md](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/manuscript.md)
- Analysis code: [analysis/](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis)
- Outputs: [output/](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/output)

Review criteria:

- whether the code matches the manuscript’s described methods
- whether the reported outputs can be traced cleanly to the code
- whether the package is strong on reproducibility and archive-readiness
- whether the code shows tell-tale signs of low-rigor AI-assisted development

## Executive Verdict

This is **not** generic “AI slop.” The code is highly project-specific, with real KLoSA-specific extraction logic and nontrivial analytic work. But it is also **not yet submission-grade as a research compendium** and **not archive-ready by AEA-style standards**.

The biggest problems are not cosmetic. Several affect reported numbers, exposure definitions, manuscript-code alignment, or the credibility of the reproducibility package:

1. a real death-date cleaning bug in sample construction
2. a mismatch between the manuscript’s stated low-satisfaction definition and the time-varying exposure actually built in code
3. time-varying intervals that can carry covariates across skipped waves while being described as biennially updated
4. ambiguous provenance for manuscript Tables 2 and 3
5. overclaimed MSM interpretation

## Master Findings

### High severity

1. **Death-date cleaning bug changes the analytic sample and death count.**  
   [02_build_analytic_sample.py#L348](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/02_build_analytic_sample.py#L348) coerces death month/day to numeric but does not clean sentinel codes like `-8/-9`, and [02_build_analytic_sample.py#L400](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/02_build_analytic_sample.py#L400) then uses those values as if valid. Reviewer 1 found this understates deaths by 3 in the current build.

2. **The time-varying low-satisfaction exposure does not match the manuscript definition.**  
   The manuscript defines low satisfaction as baseline bottom quintile / `<=30` at [manuscript.md#L57](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/manuscript.md#L57), and [model_specs.py#L38](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/model_specs.py#L38) encodes the same threshold. But [02_build_analytic_sample.py#L206](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/02_build_analytic_sample.py#L206) recomputes wave-specific quintiles. In the realized output, the threshold drifts from `30` in waves 1-4 to `40` in waves 5-8 and `50` in wave 9.

3. **The “biennially updated” time-varying description is materially cleaner than the implementation.**  
   In [06_wealth_shock_time_varying.py#L151](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/06_wealth_shock_time_varying.py#L151), intervals run from one observed interview to the next observed interview, even after missed waves. That means current-row covariates can be carried across gaps longer than two years. Reviewer 3 found 1,882 of 59,918 low-satisfaction intervals exceeded 2.5 years and contained 765 of 2,809 events.

4. **The manuscript understates the effective carry-forward rule in time-varying models.**  
   The manuscript discloses LOCF only for depression and chronic disease at [manuscript.md#L71](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/manuscript.md#L71), matching [06_wealth_shock_time_varying.py#L124](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/06_wealth_shock_time_varying.py#L124). But because intervals stretch across skipped waves, many other covariates are also effectively carried forward across those gaps.

5. **Table 2 does not have a single authoritative generating artifact.**  
   [03_cox_models.py#L289](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/03_cox_models.py#L289) writes [table2_cox_models.csv](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/output/tables/table2_cox_models.csv), but that file contains only subjective-satisfaction and welfare rows. The manuscript’s inline Table 2 at [manuscript.md#L213](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/manuscript.md#L213) also depends on [08_objective_vs_subjective.py#L147](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/08_objective_vs_subjective.py#L147), [08_objective_vs_subjective.py#L212](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/08_objective_vs_subjective.py#L212), and [09_multiple_imputation.py#L202](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/09_multiple_imputation.py#L202).

6. **The manuscript narrative and displayed Table 2 point to different analyses.**  
   The Results text says the primary joint model is MI with `N=10,335` at [manuscript.md#L91](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/manuscript.md#L91), but the displayed inline Table 2 Panel C at [manuscript.md#L230](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/manuscript.md#L230) is the complete-case joint model with `N=4,998`.

7. **Table 3 is not reproducible from the declared outputs.**  
   The inline table at [manuscript.md#L264](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/manuscript.md#L264) is assembled manually from multiple files. [06_wealth_shock_time_varying.py#L568](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/06_wealth_shock_time_varying.py#L568) saves only person-period data; [08_objective_vs_subjective.py#L448](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/08_objective_vs_subjective.py#L448) saves only `objective_vs_subjective_models.csv`; [run_all.py#L28](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/run_all.py#L28) validates no Table 3 artifact.

8. **The baseline script does not implement the manuscript’s stated primary covariate set.**  
   [03_cox_models.py#L225](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/03_cox_models.py#L225) and [03_cox_models.py#L248](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/03_cox_models.py#L248) omit alcohol and exercise and use binary `depression`, while the manuscript and [model_specs.py#L19](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/model_specs.py#L19) / [model_specs.py#L26](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/model_specs.py#L26) point to expanded health covariates and continuous CES-D in the more complete models.

9. **The MSMs are overinterpreted.**  
   [11_marginal_structural_models.py#L61](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/11_marginal_structural_models.py#L61) and [11_marginal_structural_models.py#L130](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/11_marginal_structural_models.py#L130) implement treatment weighting only, with no censoring weights, despite censoring concerns acknowledged in [manuscript.md#L61](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/manuscript.md#L61) and [manuscript.md#L143](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/manuscript.md#L143). The “total effect” framing at [manuscript.md#L135](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/manuscript.md#L135) is too strong.

10. **The MI implementation is rougher than the manuscript suggests.**  
    [09_multiple_imputation.py#L127](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/09_multiple_imputation.py#L127) uses a Gaussian iterative imputer and ends up imputing structurally missing `current_drinker` values from wave 2, then feeds those into the Cox model at [09_multiple_imputation.py#L151](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/09_multiple_imputation.py#L151). Reviewer 4 also found the fixed observed-case thresholds shift the effective prevalence of “low income” and “low assets” away from 20%.

11. **The one-command replication driver is fail-soft and incomplete.**  
    [run_all.py#L117](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/run_all.py#L117) only prints missing outputs and still ends successfully at [run_all.py#L130](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/run_all.py#L130). That is incompatible with a strong replication-package standard.

12. **The environment spec is incomplete for a clean rerun.**  
    [requirements.txt#L1](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/requirements.txt#L1) omits a parquet engine even though the package reads and writes parquet repeatedly, including [02_build_analytic_sample.py#L472](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/02_build_analytic_sample.py#L472) and [run_all.py#L88](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/run_all.py#L88).

### Medium severity

1. **PH diagnostics are incomplete for the way the manuscript is written.**  
   The manuscript highlights that the primary exposure passes PH at [manuscript.md#L73](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/manuscript.md#L73), but [ph_test_results.csv](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/output/supplementary/ph_test_results.csv) shows age, sex, self-rated health, and college education violating PH.

2. **Across-model attenuation is partly a sample-change story.**  
   Many analyses rebuild `model_df` with model-specific `dropna()`, such as [03_cox_models.py#L205](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/03_cox_models.py#L205), [03_cox_models.py#L232](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/03_cox_models.py#L232), and [03_cox_models.py#L256](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/03_cox_models.py#L256). Some manuscript language treats attenuation as if it were purely covariate adjustment.

3. **Basic Pension sensitivity omits wave 9 despite prose implying full-period coverage.**  
   [12_basic_pension_analysis.py#L68](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/12_basic_pension_analysis.py#L68) and [12_basic_pension_analysis.py#L188](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/12_basic_pension_analysis.py#L188) use waves 5-8, not 5-9.

4. **The wealth-shock power statement is more definitive than the code justifies.**  
   [07_extended_sensitivity.py#L553](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/07_extended_sensitivity.py#L553) uses a rough detectable-HR calculation on person-interval data, not a strong design-stage power analysis for repeated-interval Cox modeling.

5. **Regularization sensitivity is partial, not comprehensive.**  
   The manuscript says unpenalized time-varying results are reported for comparison at [manuscript.md#L71](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/manuscript.md#L71), but [07_extended_sensitivity.py#L366](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/07_extended_sensitivity.py#L366) covers low satisfaction and wealth shock, not low income or the combined income+satisfaction model the Results emphasize.

6. **Measurement-sensitivity analyses run on a smaller sample than the manuscript foregrounds.**  
   [10_measurement_sensitivity.py#L86](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/10_measurement_sensitivity.py#L86) and [10_measurement_sensitivity.py#L176](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/10_measurement_sensitivity.py#L176) operate on a drinking/exercise-augmented sample around `N=8,441`, not the larger main baseline sample.

7. **There is no real single source of truth for derived variables or covariate sets.**  
   The duplication documented across [07_extended_sensitivity.py#L89](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/07_extended_sensitivity.py#L89), [08_objective_vs_subjective.py#L72](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/08_objective_vs_subjective.py#L72), [09_multiple_imputation.py#L46](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/09_multiple_imputation.py#L46), [10_measurement_sensitivity.py#L35](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/10_measurement_sensitivity.py#L35), [11_marginal_structural_models.py#L34](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/11_marginal_structural_models.py#L34), and [12_basic_pension_analysis.py#L31](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/12_basic_pension_analysis.py#L31) makes analytic drift likely.

8. **The raw-data contract is permissive rather than archival.**  
   The README at [README.md#L5](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/README.md#L5) provides folder sketches but no exact file inventory or checksums, and [02_build_analytic_sample.py#L277](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/02_build_analytic_sample.py#L277) / [02_build_analytic_sample.py#L311](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/02_build_analytic_sample.py#L311) allow partial raw-data states to continue.

9. **The repository contains stale and overlapping artifacts.**  
   Examples include [table4_time_varying_results.csv](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/output/tables/table4_time_varying_results.csv), [extended_models.csv](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/output/supplementary/extended_models.csv), [B1_B2_B3_revised_models.csv](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/output/supplementary/B1_B2_B3_revised_models.csv), and [all_revision_results.json](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/output/supplementary/all_revision_results.json).

10. **Warning suppression is too aggressive.**  
    Representative examples: [03_cox_models.py#L17](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/03_cox_models.py#L17), [07_extended_sensitivity.py#L18](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/07_extended_sensitivity.py#L18), [09_multiple_imputation.py#L27](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/09_multiple_imputation.py#L27), and [11_marginal_structural_models.py#L22](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/11_marginal_structural_models.py#L22).

### AI-slop assessment

The panel consensus is that this **does not** read like generic hallucinated AI code. The project-specific extraction logic, wave mappings, and KLoSA-specific data handling are too concrete for that.

What it **does** look like is an accretive analyst codebase with some AI-era symptoms:

- duplicated derivation blocks
- overconfident comments/docstrings
- manual table stitching
- weak cleanup of stale outputs
- insufficient single-source-of-truth discipline

That is a rigor and curation problem, not a “bot wrote fake code” problem.

### Reproducibility assessment

For internal review or a peer reviewer willing to inspect things manually, this package is usable.

For an external replicator who expects one-command regeneration with clear provenance, it is **not ready**.

For a public archive in the style of AEA replication standards, it is **not ready**.

## Panel Roster

1. **Longitudinal data engineering / sample construction**  
   Focus: [02_build_analytic_sample.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/02_build_analytic_sample.py)  
   Main findings: death-date sentinel bug; time-varying low-satisfaction definition drift; tracker logic not actually used for censoring/death construction; wealth-shock edge-case definition broader than described.

2. **Baseline survival modeling / manuscript alignment**  
   Focus: [03_cox_models.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/03_cox_models.py), [model_specs.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/model_specs.py), manuscript baseline sections  
   Main findings: baseline script does not implement the manuscript’s stated primary covariate set; PH handling is underdescribed; Table 2 ownership is broken; dose-response result cites the wrong figure; attenuation language overlooks shifting complete-case samples.

3. **Time-varying survival analysis**  
   Focus: [06_wealth_shock_time_varying.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/06_wealth_shock_time_varying.py), [07_extended_sensitivity.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/07_extended_sensitivity.py)  
   Main findings: intervals do not enforce true biennial updates; implicit carry-forward exceeds manuscript disclosure; ridge penalty use is broader than prose suggests; within-person interpretation is too strong.

4. **Missing data / measurement sensitivity**  
   Focus: [09_multiple_imputation.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/09_multiple_imputation.py), [10_measurement_sensitivity.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/10_measurement_sensitivity.py)  
   Main findings: structurally missing `current_drinker` is imputed with Gaussian values; MI changes effective “bottom quintile” prevalence; spline/cutpoint analyses use a smaller wave-1-only style sample; Rubin-style pooling is approximate.

5. **Causal inference / MSMs**  
   Focus: [11_marginal_structural_models.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/11_marginal_structural_models.py)  
   Main findings: no censoring weights; baseline/history-missing intervals default to unit weight; combined-MSM “total effect” language is overstated; balance diagnostics do not fully assess the modeled history; bootstrap omits first-stage weight-estimation uncertainty.

6. **Reproducibility / archive standards**  
   Focus: [README.md](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/README.md), [run_all.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/run_all.py), [requirements.txt](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/requirements.txt)  
   Main findings: missing parquet dependency; non-binding output validation; loose raw-data contract; output directories assumed to pre-exist; no lockfile/container-grade environment.

7. **Publication-table provenance / manuscript-code alignment**  
   Focus: [03_cox_models.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/03_cox_models.py), [05_generate_publication_tables.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/05_generate_publication_tables.py), [08_objective_vs_subjective.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/08_objective_vs_subjective.py), [09_multiple_imputation.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/09_multiple_imputation.py)  
   Main findings: no canonical source for Table 2; narrative and displayed joint model mismatch; Table 3 assembled from multiple files/stale artifacts; output sprawl increases provenance risk.

8. **Sensitivity analyses / diagnostics**  
   Focus: [04_subgroups_and_sensitivity.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/04_subgroups_and_sensitivity.py), [07_extended_sensitivity.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/07_extended_sensitivity.py), [10_measurement_sensitivity.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/10_measurement_sensitivity.py), [12_basic_pension_analysis.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/12_basic_pension_analysis.py)  
   Main findings: Basic Pension analysis omits wave 9; wealth-shock power estimate is rough; regularization sensitivity is incomplete; split-period follow-up result is exploratory; measurement robustness uses a smaller sample.

9. **Software engineering / maintainability / anti-slop**  
   Focus: whole package  
   Main findings: no real single source of truth despite `model_specs.py`; duplicated derivation blocks across scripts; fail-soft behavior; aggressive warning suppression; stale workspace residue; not generic AI slop, but not curated compendium code either.

10. **Replication-package / archive-readiness**  
    Focus: whole package plus manuscript embedding  
    Main findings: manuscript tables are hand-copied rather than generated from authoritative outputs; no validated Table 3 artifact; manifest mismatches in both directions; curation residue in output tree; package is inspectable but not archive-ready.

## What the Panel Liked

- The codebase is clearly project-specific and not fabricated boilerplate.
- The pipeline has real structure: numbered scripts, a driver, pinned top-level package versions, and fixed seeds in stochastic scripts.
- The manuscript has enough linkage to the outputs that a careful internal auditor can usually figure out what happened.

## Bottom Line

If the question is “does this look like fake AI-generated junk?”, the answer is **no**.

If the question is “is this methodologically and reproducibly tight enough that I would want an editor, reviewer, or archivist auditing it in its current form?”, the answer is **also no**.

The top fixes before any public-facing confidence should be:

1. fix the death-date cleaning bug and rerun downstream analyses
2. choose and document one low-satisfaction definition for time-varying work
3. rebuild the time-varying methods/prose so they match the actual interval construction
4. create one authoritative output per manuscript table and rewire the manuscript to those outputs
5. rewrite the MSM description as a limited treatment-weighted sensitivity analysis unless censoring weights and fuller diagnostics are added
6. harden the replication package: parquet dependency, fail-fast checks, raw-data manifest, cleanup of stale outputs

## Supporting Reviewer Memos

- [CODE_REVIEW_PRELIM_2026-03-25.md](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/CODE_REVIEW_PRELIM_2026-03-25.md)
- [CODE_REVIEW_TOP_FINDINGS_2026-03-25.md](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/CODE_REVIEW_TOP_FINDINGS_2026-03-25.md)
