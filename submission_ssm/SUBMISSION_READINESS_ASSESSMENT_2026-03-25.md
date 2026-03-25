# Submission Readiness Assessment

**Date:** 2026-03-25  
**Question:** Is this ready to submit to *Social Science & Medicine*, assessed primarily from the current manuscript and the code repository/package?

## Bottom Line

**Manuscript:** yes, essentially submission-ready.  
**Manuscript + public code repo together:** almost, but not quite ideal.

If submission were due today, I would be comfortable submitting the manuscript. But if the goal is to send the cleanest possible package, I would spend a short final pass syncing the public-facing repository first.

## Why The Manuscript Looks Ready

- The manuscript now has a clear primary result hierarchy: baseline joint model first, discordance as supporting evidence, and time-varying / MSM analyses framed as secondary sensitivity analyses.
- The main limitations are visible and appropriately candid: measurement asymmetry, attrition / missed deaths, personality confounding, and weaker interpretability of time-varying models.
- The Korea framing is now institutional and mostly disciplined rather than culturally overclaimed.
- The abstract, Results, tables, and conclusion are internally coherent enough to look like a real SSM submission rather than a moving target.

## Why I Would Still Pause Briefly Before Submission

### 1. The public GitHub repo is visibly behind the manuscript

The manuscript’s data-sharing statement points readers to the GitHub code repository:

- `submission_ssm/manuscript.md`, Data sharing section

But the public repo currently still presents the older paper identity and older output structure:

- GitHub README title: `Analysis Code: Financial Distress and Mortality in South Korea`
- GitHub README manuscript title: `Objective and subjective financial hardship as predictors ...`
- GitHub README output structure still centers `table1_publication.csv`, `table2_cox_models.csv`, and `objective_vs_subjective_models.csv`

That does not make the science wrong, but it makes the repo look one version behind the manuscript.

### 2. `run_all.py` validates an older output set, not the full canonical manuscript-facing set

`analysis/run_all.py` successfully validates the current rerun, but its expected outputs are still the older artifact set:

- [run_all.py](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/run_all.py#L28)

It checks:

- `output/tables/table1_publication.csv`
- `output/tables/table2_cox_models.csv`
- `output/supplementary/objective_vs_subjective_models.csv`

But it does **not** validate some of the manuscript-facing canonical artifacts now used in the provenance manifest, including:

- `output/tables/table1_baseline_characteristics.csv`
- `output/tables/table2_combined_models.csv`
- `output/tables/table3_time_varying_models.csv`

So the pipeline is fail-hard, which is good, but still not fully aligned with the current manuscript package.

### 3. The repo/output tree still looks more archival than curated

The active package is clearly identified in:

- [CURRENT_FILES.md](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/CURRENT_FILES.md#L5)

But the actual output tree still contains multiple parallel artifact sets:

- `output/_stale/`
- `output/ec2_rerun_supplementary/`
- both `table1_publication.csv` and `table1_baseline_characteristics.csv`
- both `figure2_discordance.*` and `figure2_forest_plot.*`

That is manageable locally, but in a public repo it makes the package feel less canonical than it should.

### 4. The analysis README is stale enough to create avoidable doubt

The local README still uses the old paper title and old output map:

- [README.md](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/README.md#L1)
- [README.md](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/analysis/README.md#L67)

This matters because the public GitHub repo is what outside readers will actually see first.

## My Recommendation

If your question is strictly, "Is the manuscript ready for SSM?" then **yes**.

If your question is, "Is the full outward-facing package polished enough that I would feel good sending reviewers to the GitHub repo today?" then **almost, but I would do one last repo-sync pass first**.

## Highest-Value Final Repo Fixes

1. Update the public README to match the current manuscript title, framing, and canonical outputs.
2. Update `analysis/run_all.py` so it validates the canonical manuscript-facing artifacts, not just the older intermediate ones.
3. Decide which output files are canonical and quarantine or stop advertising the rest.
4. If possible, push the current provenance logic into the repo-facing docs so the GitHub package mirrors the submission package more closely.

## Final Verdict

**Recommendation:** `Submit after a short same-day repo cleanup pass.`

If you choose not to do that cleanup, I still think the manuscript itself is strong enough to submit, but I would view the repo as the weak link rather than the paper.
