# Final Closure Audit

**Date:** 2026-03-25  
**Scope:** provenance, machine-readable outputs versus manuscript/supplement, and readiness for a final submit-vs-revise panel

## Verdict

**Not fully closed yet.**

The package is now much cleaner at the manuscript/supplement level, and most of the earlier high-salience text problems are fixed. But I would **not** call it fully closed for a final provenance-sensitive panel because:

1. `submission_ssm/MANUSCRIPT_PROVENANCE.md` is still not accurate enough.
2. The revised manuscript/supplement now outrun some of the machine-readable output artifacts in `output/`.

### Practical interpretation

- **Ready for:** a near-final manuscript-quality review if the reviewers are judging the paper itself.
- **Not yet ready for:** a truly final package-level review where provenance, traceability, and output synchronization are part of the standard.

## What Is Confirmed Clean

These items are clearly fixed on disk:

- `analysis/run_all.py` now validates against `10,384` and `3,074`.
- `submission_ssm/manuscript.md` has the improved highlights, softer Korea framing, corrected NBLSS sentence, cleaned personality paragraph, less stereotyped response-style line, and tighter conclusion.
- `submission_ssm/supplementary_materials.md` now has updated Table 3, updated PH table/note, updated cut-point table, updated MI table, updated Basic Pension table, and refreshed MSM table.
- `output/ec2_pipeline.log` is no longer present in `output/`.
- `output/supplementary/msm_results.json` is fresh and aligns with eTable 8.

## Remaining Blockers

### 1. Provenance file still does not accurately map the package

`submission_ssm/MANUSCRIPT_PROVENANCE.md` still says:

- Table 2 complete-case output is `output/supplementary/objective_vs_subjective_models.csv`
- Table 3 combined output is `output/supplementary/objective_vs_subjective_models.csv`
- Table 3 is assembled from console outputs and has no single canonical CSV

This is still the same underlying provenance problem as before. The file has not been brought up to the current package standard.

Relevant lines:

- `submission_ssm/MANUSCRIPT_PROVENANCE.md:27`
- `submission_ssm/MANUSCRIPT_PROVENANCE.md:39`
- `submission_ssm/MANUSCRIPT_PROVENANCE.md:40`

### 2. The text package now appears ahead of some machine-readable outputs

The strongest confirmed example:

- `output/supplementary/supplementary_results.json` still has `healthy_baseline = N 1081, Events 133`
- but both:
  - `submission_ssm/manuscript.md:107`
  - `submission_ssm/supplementary_materials.md:212`
  now report `n=1,091; 139 deaths`

That means one of two things is true:

1. the manuscript/supplement were updated from a newer rerun whose machine-readable outputs were not all saved back to `output/`, or
2. the manuscript/supplement were hand-updated beyond the frozen output set

Either way, the package is not yet traceable end-to-end.

### 3. Several output artifacts still predate the latest text revision

Current mtimes show:

- `submission_ssm/manuscript.md` is `13:53`
- `submission_ssm/supplementary_materials.md` is `13:52`
- but several key output files are still from roughly `10:39-10:56`

That does not automatically mean the text is wrong, but it does mean the machine-readable artifacts were not comprehensively regenerated or refreshed after the latest revision pass.

Most notable:

- `output/tables/subgroup_analyses.csv`
- `output/tables/table2_cox_models.csv`
- `output/supplementary/supplementary_results.json`
- `output/supplementary/measurement_sensitivity.json`
- `output/supplementary/basic_pension_analysis.json`
- `output/supplementary/objective_vs_subjective_models.csv`

## What This Means For The Next Panel

If you run a final “submit now or revise once more?” panel **right now**, I would expect:

- strong marks on the manuscript itself
- lower marks on provenance/replicability/package readiness

So the panel would still be partly scoring a packaging problem rather than the paper.

## Recommended Next Move

Do one **very narrow closure pass** before the final panel:

1. Refresh or regenerate the machine-readable outputs that the revised supplement now cites.
2. Update `submission_ssm/MANUSCRIPT_PROVENANCE.md` so it only points to real current artifacts.
3. Recheck one last time that every count in:
   - `submission_ssm/manuscript.md`
   - `submission_ssm/supplementary_materials.md`
   - `output/`
   agrees.

After that, I would consider the package ready for a true final panel.

## Bottom Line

**The paper is close. The package is not fully closed.**

The remaining issue is no longer journal fit or framing. It is traceability.
