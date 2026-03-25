# Final 10-Person Mock SSM Panel

**Date:** 2026-03-25  
**Package reviewed:** `submission_ssm/manuscript.md` + `submission_ssm/supplementary_materials.md` + `submission_ssm/MANUSCRIPT_PROVENANCE.md` + canonical output tables/JSONs  
**Important note:** One initial Korea-context reviewer accidentally reviewed stale Lancet-era files and was excluded. A replacement Korea welfare-state reviewer assessed the current SSM package. The synthesis below reflects **10 valid current-package reviews**.

## Executive Verdict

**Consensus:** `10 of 10` reviewers recommended **one last pass before submission**, not a major redesign and not another broad code review.

**Bottom line:** the paper is now broadly seen as **strong enough for SSM after a short final cleanup pass**. The panel did **not** think the project is maxed out or that the science has collapsed. The remaining concerns are concentrated in:

1. a few **package-alignment/provenance** issues,
2. a few places where the manuscript still **overgeneralizes the discordance result**,
3. a few places where **time-varying/MSM results still do too much narrative work**,
4. a few prose passages that still feel **slightly over-produced**.

## Score Summary

- Mean overall quality: `7.83/10`
- Median overall quality: `8.0/10`
- Mean SSM fit: `8.44/10`
- Mean AI-generated-likelihood risk: `5.33/10`
- Median AI-generated-likelihood risk: `5.0/10`
- Mean send-out probability: `73.9%`
- Median send-out probability: `75%`

Interpretation:
- The panel sees this as a **good SSM paper with a package-cleanup problem**, not a weak paper.
- The AI-risk score is best read as **“some prose still sounds over-smoothed”**, not “this looks machine-generated.”

## Reviewer-by-Reviewer

| Reviewer | Lens | Verdict | Send-out | Key take |
|---|---|---|---:|---|
| 1 | Editor-in-chief | One last pass | 72% | Strong fit and transparency, but abstract/discussion still slightly stronger than design supports. |
| 2 | SSM social epidemiology editor | One last pass | 65% | Strong scope fit, but wanted final package coherence and a little more inferential restraint. |
| 3 | Medical sociology / inequality | One last pass | 75% | Good paper, but still more social epidemiology than sociology; wants cleaner analytic separation. |
| 4 | Senior social epidemiologist | One last pass | 65-70% as-is | Good science, but package freezing and estimand integration still need tightening. |
| 5 | Aging / gerontology inequality | One last pass | not numerically specified | Strong later-life inequality paper; main risks are measurement asymmetry and overintegrated narrative. |
| 6 | Korea welfare-state / East Asian social policy | One last pass | 78% | Korea framing is good and useful, but a few lines still drift into speculation. |
| 7 | Measurement expert | One last pass | 82% | Subjective measure is framed fairly overall, but discordance evidence only covers income vs satisfaction. |
| 8 | Quantitative methods reviewer | One last pass | 80% | Methods package is strong; remaining issue is wording that still overstates discordance and sensitivity analyses. |
| 9 | Transparency / provenance reviewer | One last pass | 65% as-is, 78% after cleanup | Still found a few real alignment issues between supplement/manuscript/canonical outputs. |
| 10 | Writing / positioning / AI-signal | One last pass | 68% | Strong enough scientifically; main remaining work is voice, positioning, and trimming over-explained prose. |

## What The Panel Agreed On

### Strongest parts of the package

- The **baseline joint model** is the manuscript's clearest and most defensible anchor.
- The **income-satisfaction discordance** analysis is the most distinctive and publishable hook.
- The **limitations sections** are much stronger than before and now show real restraint.
- The **SSM fit is good**: aging, inequality, subjective appraisal, and institutional context all land.
- The package now looks **substantially more transparent and auditable** than it did before.

### Most common remaining vulnerabilities

- The discordance evidence is specifically **income-satisfaction discordance**, but the prose sometimes expands that to **objective indicators** more broadly.
- The **time-varying** and **MSM** analyses still need to stay visibly **secondary / sensitivity** rather than co-equal pillars.
- A few Korea-context sentences still read more like **hypotheses or interpretations** than directly supported claims.
- A few passages in the highlights, discussion, and conclusion still feel **slightly too polished / symmetrical**.

## Confirmed Remaining Blockers

These were not just reviewer impressions. I spot-checked them against the live files.

1. **Supplementary Table 8 does not match the current MSM JSON.**  
   The table in `submission_ssm/supplementary_materials.md` still shows, for example, separate-model low-satisfaction estimates of `1.11` and `1.62`, while `output/supplementary/msm_results.json` now contains different values (`1.23` direct effect and `1.909` treatment-weighted total effect for low economic satisfaction).

2. **Main Table 2 Panel C p-values do not exactly match the canonical combined-model CSV.**  
   In `submission_ssm/manuscript.md`, Panel C currently reports `0.12`, `0.18`, and `0.62`, while `output/tables/table2_combined_models.csv` gives `0.1374`, `0.1771`, and `0.6535`. This looks like a rounding/provenance issue, not a substantive result change, but it should be harmonized.

3. **Supplementary Table 4 still contains partially reported equivalized-income rows.**  
   In `submission_ssm/supplementary_materials.md`, the equivalized-income lines still have missing CIs/p-values in the combined-model rows.

4. **The provenance manifest is improved but still incomplete for some supplement items.**  
   `submission_ssm/MANUSCRIPT_PROVENANCE.md` now maps the main tables well, but it still does not explicitly map Supplementary Table 8 to `output/supplementary/msm_results.json`, and several supplementary tables are still listed mainly by script rather than by canonical output artifact.

5. **`CURRENT_FILES.md` is stale.**  
   This is not part of the submitted manuscript package, but it still says `output/supplementary/msm_results.json` is stale and pending rerun. That can mislead future audits or collaborators.

## High-Priority Text Changes

These are the manuscript-facing edits the panel most consistently wanted.

1. **Narrow the discordance claim.**  
   Rename or describe it as **income-satisfaction discordance**, not as a discordance test spanning all objective indicators.

2. **Make the baseline joint association the unmistakable headline.**  
   Keep the time-varying and MSM results in the paper, but frame them as **secondary sensitivity analyses with mixed/attenuated support**.

3. **Soften phrases implying too much causal independence.**  
   Examples the panel repeatedly flagged:
   - `beyond objective financial indicators`
   - `independent information`
   - `distinct risk group`
   - generalized claims that subjective indicators “beat” objective indicators

4. **Trim the most speculative Korea-context sentences.**  
   The biggest targets were:
   - the `weakening filial support norms` interpretation when it becomes too specific,
   - the `1997 Asian Financial Crisis` cohort-imprint sentence,
   - any line that feels closer to cultural explanation than institutional context.

5. **De-AI the highest-risk prose.**  
   The panel's most common advice was to make the highlights, title, and closing discussion/conclusion a bit more direct and less polished-symmetrical.

## Recommended Next Step

The panel's collective answer is:

**Do one short final cleanup pass, then submit to SSM.**

Not recommended:
- another broad code review,
- another full reframing exercise,
- new substantive analyses before submission.

Recommended:
- one fast **package reconciliation pass**,
- one fast **line-edit pass for framing and tone**,
- then a final pre-submission check.

## Minimal Pre-Submission Checklist

Before submission, the panel would fix these exact items:

1. Rebuild or directly replace **Supplementary Table 8** from `output/supplementary/msm_results.json`.
2. Harmonize **Table 2 Panel C** p-values with `output/tables/table2_combined_models.csv` and use one rounding convention throughout.
3. Fill in or remove the incomplete **equivalized-income** rows in Supplementary Table 4.
4. Update **MANUSCRIPT_PROVENANCE.md** so Supplementary Table 8 and the other supplementary displays point to explicit canonical output files, not only scripts.
5. Update or quarantine **CURRENT_FILES.md** so it no longer advertises stale MSM status.
6. Revise manuscript wording so the discordance claim is explicitly **income-satisfaction discordance**.
7. Add one plain sentence in the main discussion that the **time-varying and MSM analyses are exploratory sensitivity analyses** rather than definitive within-person or total-effect evidence.
8. Trim or qualify the most speculative Korea-context lines, especially around filial-support interpretation and the Asian Financial Crisis cohort sentence.
9. Tighten the title, highlights, and conclusion so they sound more direct and less formulaic.

## Final Decision If I Were You

I would **not** open another giant review loop right now.

I would:

1. fix the confirmed package issues above,
2. apply a very small wording pass focused on discordance, TV/MSM demotion, and prose naturalness,
3. then submit.
