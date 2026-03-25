# Current Working Files

Last updated: 2026-03-25 14:56 EDT

This file exists so that any tool (Claude Code, Codex, or otherwise) reviewing this project knows which files are current and authoritative. If a file is not listed here, it is either stale, archived, or not part of the active submission.

## Authoritative Manuscript

The ONLY current manuscript is:

    submission_ssm/manuscript.md

Do NOT use or review any of these older versions:
- `manuscript/manuscript_combined_v6.md` (old Lancet version)
- `manuscript/manuscript_ssm_v1.md` (Codex's earlier SSM draft, superseded)
- `submission_lancet_regional_health_wp/manuscript_source.md` (archived Lancet submission)
- `submission_lancet_regional_health_wp/appendix_source.md` (archived)

## Authoritative Supplementary Materials

    submission_ssm/supplementary_materials.md

## Submission Folder Structure

    submission_ssm/
    ├── manuscript.md                          ← THE manuscript
    ├── supplementary_materials.md             ← supplementary tables/figures
    ├── figures/                               ← submission-ready figures
    ├── strobe_checklist.docx                  ← STROBE checklist
    ├── MANUSCRIPT_PROVENANCE.md               ← maps every table/figure to its generating script
    ├── CURRENT_FILES.md                       ← this file
    ├── RERUN_COMPARISON.md                    ← old vs new numbers from 2026-03-25 pipeline rerun
    ├── REFERENCE_AUDIT.md                     ← Claude's reference audit (all issues fixed)
    ├── REFERENCE_AUDIT_2026-03-25.md          ← Codex's reference audit (all issues fixed)
    ├── SSM_PANEL_REVIEWS_2026-03-25.md        ← 10-editor SSM panel reviews
    ├── SSM_RESEARCHER_PANEL_REVIEWS_2026-03-25.md ← 6-researcher SSM panel reviews
    ├── CODE_REVIEW_PANEL_2026-03-25.md        ← 10-agent code review
    ├── CODE_REVIEW_REMEDIATION_PLAN_2026-03-25.md ← remediation plan (all items addressed)
    └── CODE_REVIEW_PRELIM_2026-03-25.md       ← supporting code review memo

## Analysis Code (modified 2026-03-25)

    analysis/02_build_analytic_sample.py   ← death-date fix, threshold fix, wealth shock fix
    analysis/06_wealth_shock_time_varying.py ← extended interval flagging
    analysis/03_cox_models.py              ← warning suppression fix
    analysis/07_extended_sensitivity.py    ← warning suppression fix
    analysis/09_multiple_imputation.py     ← warning suppression fix
    analysis/11_marginal_structural_models.py ← comment added
    analysis/run_all.py                    ← fail-hard validation
    analysis/requirements.txt              ← pyarrow added
    analysis/model_specs.py                ← unchanged but authoritative for ECON_SAT_THRESHOLD=30

## Pipeline Outputs (regenerated 2026-03-25)

All files in `output/tables/` and `output/supplementary/` are from the 2026-03-25 rerun.
- `output/_stale/` contains quarantined legacy artifacts and should not be used.

## Key Sample Numbers (post-rerun)

- N = 10,384
- Deaths = 3,074 (29.6%)
- Mean follow-up = 12.5 years
