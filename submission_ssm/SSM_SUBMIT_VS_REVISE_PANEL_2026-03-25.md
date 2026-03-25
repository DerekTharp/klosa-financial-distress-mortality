# SSM Submit-vs-Revise Panel Review

**Date:** 2026-03-25  
**Target journal:** Social Science & Medicine  
**Package reviewed:** `submission_ssm/manuscript.md`, `submission_ssm/supplementary_materials.md`, `submission_ssm/MANUSCRIPT_PROVENANCE.md`, `submission_ssm/RERUN_COMPARISON.md`, plus selected output and analysis files as needed

## Consensus

**Verdict:** `6 of 6` reviewers recommended **one last cleanup pass before submission**.  
**No reviewer** recommended a major redesign or additional substantive analysis before the next decision point.  
**Every reviewer** thought the paper itself is plausibly SSM-worthy, but the current package still gives reviewers a few avoidable openings.

The panel's shared view was:

- The core paper is now strong enough for SSM review in topic, framing, and headline result.
- The main remaining risk is not the scientific question; it is **package coherence**.
- The biggest pre-submission problem is that the manuscript, supplement, provenance file, and some saved outputs are not fully synchronized after the rerun.
- AI risk was judged **moderate but not alarming**: the manuscript reads as human overall, but a few discussion/conclusion passages feel over-smoothed or template-like.

## Consensus Must-Fix Items

1. **Freeze one canonical output set and synchronize the whole package to it.**
   Main manuscript, supplement, provenance manifest, and saved outputs still disagree on rerun-sensitive counts and tables.

2. **Regenerate or manually reconcile the supplement.**
   This was the most repeated panel concern. Table 3 in `submission_ssm/supplementary_materials.md` still contains older time-varying values, and other appendix items also appear stale.

3. **Fix the provenance trail so it points to real current artifacts.**
   `submission_ssm/MANUSCRIPT_PROVENANCE.md` still maps some tables to nonexistent or incomplete output files, which undermines trust even if the manuscript text is substantively fine.

4. **Close the remaining source-fidelity issues.**
   Multiple reviewers still flagged the Basic Pension sentence, the NBLSS/obligatory-supporter explanation, and the personality-bias paragraph as over-specific or mis-cited.

5. **Keep time-varying and MSM results explicitly secondary.**
   Reviewers were comfortable with these analyses as sensitivity work, not as causal or within-person evidence.

6. **Tighten a few stylized discussion/conclusion passages.**
   The prose is strong overall, but some sections feel a bit too polished and symmetrical, which raises mild AI-signal concerns even though nobody thought this read like generic AI slop.

## Confirmed Package-Level Problems

These were confirmed directly during the audit that accompanied the panel review:

- `submission_ssm/supplementary_materials.md` still shows older Table 3 values than `submission_ssm/manuscript.md`.
- `submission_ssm/manuscript.md` Table 2 Panel C reports `N=5,010; 1,195 events`, while `submission_ssm/supplementary_materials.md` still shows `1,183` events for the corresponding complete-case combined model.
- `submission_ssm/MANUSCRIPT_PROVENANCE.md` still points Table 2 and Table 3 to stale or nonexistent output paths.
- `analysis/run_all.py` still validates against the old sample size and death count (`10,335` and `3,025`), so a true clean rerun would currently fail validation.
- `output/supplementary/ph_test_results.csv` does not match the values shown in the PH appendix table.

## Moderator Note

One reviewer compared the manuscript to `output/ec2_pipeline.log`. That log appears older than the current manuscript package, so it should not be treated as definitive evidence that the manuscript is wrong. But it **does** reinforce the broader panel point that the project no longer has one clean, frozen, unambiguous source of truth across all package files.

## Ratings Snapshot

Approximate panel summary across overlapping dimensions:

| Factor | Panel read |
|---|---|
| Overall quality | `~6.7/10` average; generally seen as solid and publishable |
| SSM fit | `~8.7/10` average among reviewers rating fit; consistently strong |
| Theoretical framing | `~7.7/10`; good stress-process/institutional framing, could sharpen sociological payoff |
| Methods credibility | `~6.3/10`; adequate and mostly honest, but package inconsistencies drag this down |
| Replicability/transparency | `~6/10` at the manuscript level, but much lower for provenance/package coherence |
| Package coherence / auditability | weakest area; several reviewers effectively rated this in the `2-4/10` range |
| Submission readiness | roughly `5-6/10`; close, but not this exact version |
| AI-generated likelihood risk | roughly `5-6/10`; not judged obvious AI, but some prose feels over-produced |

## Full Reviews

### Reviewer 1: Senior SSM Editor / Social Epidemiologist

**Verdict:** One last revision pass.

**Must-fix**

- Sync the main manuscript with the supplement and provenance materials.
- Fix the personality-bias paragraph, especially the mis-cited literature-based meta-analysis claim.
- Soften or re-cite the Basic Pension and NBLSS policy-history claims.

**Nice-to-have**

- Separate the baseline Cox, discordance, and time-varying stories a bit more explicitly.
- Trim some of the quantitative-bias-analysis precision unless every bound is fully sourced.
- Keep MSM and post hoc power material clearly exploratory.

**Ratings**

- Overall quality: 7/10
- SSM fit: 9/10
- Novelty/contribution: 7/10
- Theoretical framing: 8/10
- Methods credibility: 6/10
- Interpretive restraint: 7/10
- Clarity/organization: 7/10
- Replicability/transparency: 8/10
- Reviewer survivability: 6/10
- AI-generated-likelihood risk: 5/10

**Bottom line**

The paper itself is good enough for SSM review, but the package is not yet clean enough to submit as-is.

### Reviewer 2: Social Epidemiologist / Frequent SSM Reviewer

**Verdict:** One last cleanup pass.

**Main issues**

- The package is internally out of sync on rerun-sensitive results, especially time-varying models and MI/composite counts.
- Several literature/context claims still need source cleanup.
- The Basic Pension interpretation is too strong relative to the appendix evidence.
- The subjective-vs-objective framing still leans a bit too hard given measurement asymmetry.
- Discordance and time-varying analyses should remain explicitly descriptive/sensitivity-based.
- Mortality ascertainment and attrition should stay front-and-center.

**Ratings**

- Overall quality: 8/10
- SSM fit: 9/10
- Originality: 7/10
- Theoretical grounding: 8/10
- Methods rigor: 6/10
- Limitations honesty: 7/10
- Replicability/transparency: 6/10
- Writing quality: 8/10
- Probability of revise-and-resubmit if sent now: 6/10
- AI-generated-likelihood risk: 6/10

**Bottom line**

Strong paper, but not quite submission-clean yet. A focused reconciliation pass on numbers, citations, and a few claims should materially improve the odds.

### Reviewer 3: Medical Sociologist / Aging Scholar

**Verdict:** Close to a strong SSM paper, but not quite send-ready.

**Must-fix**

- Reconcile the main combined-model story so MI and complete-case estimates are separated cleanly.
- Resolve the MSM/rerun mismatch.
- Harmonize the healthy-baseline sensitivity counts across manuscript and supplement.
- Tighten the Korea framing so it remains institutional rather than culturally essentializing.

**Optional**

- Sharpen the sociological payoff.
- Reduce some self-undermining caveat density in Results/Discussion.

**Ratings**

- Overall quality: 7/10
- SSM fit: 8/10
- Sociological/theoretical contribution: 7/10
- Institutional-context framing: 6/10
- Readability: 7/10
- Likely reviewer enthusiasm: 6/10
- Replicability/transparency: 6/10
- AI-generated-likelihood risk: 4/10

**Bottom line**

The empirical finding is interesting enough to carry a paper, but the submission will land better if internal consistency is fixed and Korea framing is made more institutional and less generalized.

### Reviewer 4: Quantitative Methods Reviewer

**Verdict:** Analytic framework broadly defensible, but not submission-ready because displayed numbers are still mixed across reruns.

**Findings**

1. Time-varying reporting still appears to mix versions across package artifacts.
2. Multiple-imputation event counts are stale in the supplement.
3. Diagnostic and sensitivity appendices are not fully synchronized with current output files.
4. Time-varying and MSM analyses are defensible as sensitivity analyses, not causal evidence.

**Ratings**

- Methods credibility: 7/10
- Manuscript-code alignment: 4/10
- Reproducibility: 6/10
- Transparency: 8/10
- Interpretive restraint: 7/10
- Overall quality: 6/10
- Submit-readiness: 4/10
- AI-generated-likelihood risk: 7/10

**Bottom line**

Regenerate the manuscript and supplement from one frozen output set, then recheck every event count, interval count, and appendix table against that exact run.

### Reviewer 5: Replication / Transparency Specialist

**Verdict:** Close, but not submission-ready.

**Blockers**

- `analysis/run_all.py` still validates against old counts.
- Manuscript and supplement are not synchronized on time-varying results.
- The provenance trail is not yet trustworthy enough for an audit; some table mappings point to files that do not exist or do not actually serialize the cited results.

**Archive-later**

- Add a real environment lock or container spec.
- Emit every published table panel and figure summary to machine-readable files.
- Add checksums or input-file fingerprints to the provenance manifest.
- Quarantine or remove `output/_stale` before final deposit.

**Ratings**

- Replicability: 4/10
- Provenance quality: 3/10
- Documentation quality: 6/10
- Auditability: 3/10
- Manuscript-package coherence: 2/10
- Overall quality: 4/10
- AI-generated-likelihood risk: 6/10

**Bottom line**

The remaining work is mostly a traceability and package-hardening problem, not a rethink of the science.

### Reviewer 6: Writing / AI-Signal Reviewer

**Verdict:** Close to journal-ready on substance, but a bit too smooth and symmetrical in places.

**Main flags**

- Reconcile the combined-model event count and the time-varying sample count across package files.
- Trim over-explained discussion language in the appraisal/personality sections.
- End more tightly; the conclusion currently widens into somewhat generic cross-country generalization.

**Ratings**

- Overall quality: 8/10
- Prose quality: 6/10
- Narrative coherence: 8/10
- Distinctiveness of voice: 5/10
- AI-generated-likelihood risk: 6/10
- Submission readiness: 7/10

**Bottom line**

This does not read like generic AI slop. The risk is subtler: slightly over-produced prose plus visible count mismatches that could make readers suspicious.

## Practical Recommendation

If I were sequencing the next move based on this panel, I would do exactly one final targeted cleanup pass:

1. Freeze one canonical rerun.
2. Rebuild or manually reconcile `submission_ssm/supplementary_materials.md`.
3. Fix `submission_ssm/MANUSCRIPT_PROVENANCE.md`.
4. Update `analysis/run_all.py` validation counts.
5. Apply the last source-fidelity edits in the manuscript.
6. Tighten a handful of stylized discussion/conclusion sentences.

After that, the panel's likely answer would shift from **\"revise once more\"** to **\"submit\"**.
