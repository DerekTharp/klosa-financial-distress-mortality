# Exact Pre-Submission Fixes

**Date:** 2026-03-25  
**Goal:** Raise the paper's perceived `overall quality`, `methods credibility`, `replicability/transparency`, and `AI-risk` scores by removing avoidable package problems before SSM submission.

This memo is deliberately operational. It is not a review summary. It is a file-by-file execution document.

---

## 1. What Is Actually Depressing The Scores

The paper itself is not the main problem. The scores are being dragged down by:

1. `submission_ssm/manuscript.md`, `submission_ssm/supplementary_materials.md`, and the saved outputs not matching each other.
2. `submission_ssm/MANUSCRIPT_PROVENANCE.md` still pointing to artifacts that do not actually contain the cited results.
3. `analysis/run_all.py` still validating against old counts.
4. A few source-fidelity lines in the manuscript that are still too specific or mis-cited.
5. A few discussion/conclusion paragraphs that feel over-smoothed rather than clearly human.

If these are fixed, the likely result is:

- `overall quality`: moves up because the package feels frozen and trustworthy
- `methods credibility`: moves up because the paper no longer looks like it is mixing reruns
- `replicability/transparency`: moves up because the provenance trail becomes believable
- `AI-risk`: moves down because the paper reads less over-produced and less internally inconsistent

---

## 2. Execution Order

Do these in this order:

1. Update `analysis/run_all.py` validation counts.
2. Freeze one canonical output state.
3. Sync `submission_ssm/manuscript.md`.
4. Sync `submission_ssm/supplementary_materials.md`.
5. Fix `submission_ssm/MANUSCRIPT_PROVENANCE.md`.
6. Clean out or quarantine stale files that are creating confusion.
7. Run one final validation pass.

Do **not** start by polishing prose. The package-sync fixes matter more.

---

## 3. Must-Do Before Submission

### 3.1 Update `analysis/run_all.py`

At [`analysis/run_all.py`](../analysis/run_all.py), replace the old validation counts with the current rerun counts:

```diff
-    assert len(baseline) == 10335, f"Expected 10335, got {len(baseline)}"
-    assert baseline["died"].sum() == 3025, f"Expected 3025 deaths, got {baseline['died'].sum()}"
+    assert len(baseline) == 10384, f"Expected 10384, got {len(baseline)}"
+    assert baseline["died"].sum() == 3074, f"Expected 3074 deaths, got {baseline['died'].sum()}"
```

Why this matters:

- Right now a truly clean rerun would fail its own validation.
- This directly hurts `replicability`, `provenance`, and `package coherence`.

### 3.2 Freeze one canonical output state

Before editing any more prose:

1. Decide that the current authoritative results are the ones reflected in:
   - `submission_ssm/manuscript.md`
   - `output/tables/table1_baseline_characteristics.csv`
   - `output/tables/subgroup_analyses.csv`
   - `output/tables/table2_cox_models.csv`
   - `output/supplementary/multiple_imputation_results.json`
   - `output/supplementary/supplementary_results.json`
   - `output/supplementary/measurement_sensitivity.json`
   - `output/supplementary/ph_test_results.csv`
   - `output/supplementary/basic_pension_analysis.json`
2. Treat these as frozen unless you rerun again.
3. If you rerun again, you must refresh both manuscript and supplement from that rerun before submission.

### 3.3 Decide what to do about MSM **before submission**

Current situation:

- `output/supplementary/msm_results.json` is older than the main rerun.
- The manuscript already treats MSM more cautiously, which is good.
- Reviewers still notice that the file date and rerun notes do not line up cleanly.

Two acceptable options:

**Option A: Better option**

- rerun `analysis/11_marginal_structural_models.py`
- refresh eTable 8 from the new file
- keep current cautious manuscript language

**Option B: Fast option**

- leave eTable 8 in the supplement
- remove any sentence in the main text that sounds like MSM is part of the main evidentiary spine
- make MSM clearly auxiliary

If you choose Option B, use the manuscript text replacements in section 4.5 below.

---

## 4. Exact Edits For `submission_ssm/manuscript.md`

### 4.1 Highlights

Replace the current highlights at [`submission_ssm/manuscript.md:15-19`](../submission_ssm/manuscript.md) with:

```diff
- Perceived economic insecurity predicted mortality after adjusting for objective indicators
- Adults dissatisfied despite adequate income had 28% higher mortality risk
- Low income without dissatisfaction was not associated with excess mortality
- Income changes predicted mortality in time-varying models after joint adjustment
- Subjective and objective indicators carry distinct mortality information
+ Perceived economic insecurity predicted mortality after adjustment for objective indicators
+ Adults with low satisfaction despite adequate income had elevated mortality
+ Low income without dissatisfaction was not associated with excess mortality
+ In time-updated models, low income remained associated after joint adjustment and satisfaction was attenuated
+ Subjective appraisal and objective resources were related but not interchangeable
```

Why:

- Lowers overclaim.
- Reads less slogan-like.
- Reduces the “too polished / too symmetrical” feel.

### 4.2 Introduction: Korea framing

Replace the paragraph beginning at [`submission_ssm/manuscript.md:45`](../submission_ssm/manuscript.md#L45) with:

```diff
- South Korea offers a particularly informative institutional setting for these questions. Approximately 40% of Korean adults aged 65 and older fall below the relative poverty line---the highest rate in the OECD^12^---yet welfare receipt remains low (approximately 2%) because the National Basic Livelihood Security System's obligatory supporter criterion excludes applicants with qualifying adult children, regardless of whether those children actually provide support.^20^ Korea achieved universal health insurance in 1989,^15^ but out-of-pocket healthcare costs remain among the highest in the OECD,^13^ meaning that financial insecurity can impair healthcare access despite formal coverage. The traditional safety net of filial support has weakened as younger generations increasingly prioritize nuclear family obligations, leaving many older adults with diminished informal support even as public transfers remain limited in scope.^14^ This combination of high objective poverty, incomplete public protection, and shifting family obligations creates conditions in which the subjective experience of economic insecurity may diverge substantially from objective circumstances.
+ South Korea offers an informative institutional setting for these questions. Approximately 40% of Korean adults aged 65 and older fall below the relative poverty line---the highest rate in the OECD.^12^ Yet welfare receipt remains low because eligibility for the National Basic Livelihood Security System considers support potentially available from adult children.^20^ Korea achieved universal health insurance in 1989,^15^ but out-of-pocket healthcare costs remain among the highest in the OECD,^13^ so economic strain can still affect access to care despite formal coverage. At the same time, family support in later life has become less reliable while public transfers remain limited in scope.^14^ Together, these features create conditions in which subjective economic insecurity may diverge from measured income or assets.
```

Why:

- Keeps the institutional point.
- Removes the most culturally sweeping phrasing.
- Better matches the actual citation support.

### 4.3 Introduction: time-varying framing

At [`submission_ssm/manuscript.md:47`](../submission_ssm/manuscript.md#L47), replace:

```diff
- ...and to explore whether this association is robust to time-varying models that capture within-person changes over time.
+ ...and to assess whether the baseline pattern persists in time-varying models using updated exposures over follow-up.
```

Why:

- Avoids overselling standard time-varying Cox models as within-person designs.

### 4.4 Methods: wave-5 / Basic Pension sentence

At [`submission_ssm/manuscript.md:53`](../submission_ssm/manuscript.md#L53), replace:

```diff
- The wave-5 entrants joined after the introduction (2008) and expansion (2014) of the Basic Pension; sensitivity analyses excluding them yielded identical results.
+ The wave-5 entrants joined later in the study period; sensitivity analyses excluding them yielded materially unchanged results.
```

Why:

- Removes a source-fidelity problem.
- Keeps the methodological point without leaning on uncited policy chronology.

### 4.5 Methods: NBLSS sentence

At [`submission_ssm/manuscript.md:59`](../submission_ssm/manuscript.md#L59), replace the NBLSS clause with:

```diff
- (2) Receipt of National Basic Livelihood Security System (NBLSS) welfare benefits---a stringently means-tested program with very low take-up (approximately 2% prevalence despite approximately 40% relative poverty) due to the obligatory supporter criterion. NBLSS recipients also receive Medical Aid with lower copayments, confounding its interpretation as a pure poverty indicator.
+ (2) Receipt of National Basic Livelihood Security System (NBLSS) welfare benefits---a stringently means-tested program with very low take-up among older adults, partly because eligibility rules consider support potentially available from adult children.^20^ NBLSS recipients also receive Medical Aid with lower copayments, which complicates its interpretation as a pure poverty indicator.
```

Why:

- More faithful to the citation.
- Less vulnerable than the current “approximately 2% despite approximately 40% relative poverty due to...” phrasing.

### 4.6 Results: remove unnecessary time-varying aggregate counts from prose

At [`submission_ssm/manuscript.md:103`](../submission_ssm/manuscript.md#L103), change the opening sentence to:

```diff
- In time-varying models with exposures updated at each observed interview (Table 3; 63,153 person-intervals; 3,074 events), economic dissatisfaction...
+ In time-varying models with exposures updated at each observed interview (Table 3), economic dissatisfaction...
```

Why:

- This removes one of the easiest places for reviewers to spot interval-count mismatches.
- The detailed counts already belong in Table 3.

### 4.7 If MSM is **not** rerun, de-emphasize it further

If `output/supplementary/msm_results.json` is not refreshed before submission:

At the end of [`submission_ssm/manuscript.md:103`](../submission_ssm/manuscript.md#L103), replace the final sentence with:

```diff
- In treatment-weighted marginal structural models (Supplementary Table 8), both measures retained significance in the combined model, though residual covariate imbalance and the absence of censoring weights limit interpretation of these estimates.
+ Exploratory marginal structural models are reported in Supplementary Table 8, but because these models use treatment weights without censoring weights and achieved only partial covariate balance, we treat them as ancillary sensitivity analyses rather than as part of the main evidentiary spine.
```

At [`submission_ssm/manuscript.md:135`](../submission_ssm/manuscript.md#L135), replace:

```diff
- Exploratory treatment-weighted marginal structural models found both satisfaction and income significant in the combined model (Supplementary Table 8), but these estimates should be interpreted with caution: the models achieved only partial covariate balance, used treatment weights without censoring weights, and the resulting estimates are best understood as approximate sensitivity analyses rather than definitive total-effect estimates.
+ Exploratory marginal structural models are reported in Supplementary Table 8, but these estimates should be interpreted cautiously: the models achieved only partial covariate balance, used treatment weights without censoring weights, and are best understood as rough sensitivity analyses rather than definitive total-effect estimates.
```

### 4.8 Personality-confounding paragraph

Replace the paragraph at [`submission_ssm/manuscript.md:133`](../submission_ssm/manuscript.md#L133) with:

```diff
- The most important alternative explanation is confounding by personality. Trait neuroticism or negative affectivity could simultaneously lower economic satisfaction ratings and increase mortality risk. KLoSA does not include personality measures, precluding direct adjustment. We conducted a quantitative bias analysis using published estimates as a rough sensitivity exercise rather than a sample-specific estimate of residual confounding. In a large UK cohort (N=321,456), neuroticism was associated with modestly increased all-cause mortality (age- and sex-adjusted HR 1.06 per SD, 95% CI 1.03--1.09),^18^ though an individual-participant meta-analysis of 76,150 adults found neuroticism was not independently associated with mortality after adjusting for other personality traits;^17^ a literature-based meta-analysis reported a pooled association of HR 1.15 per SD (1.04--1.26).^17^ Meta-analyses of personality and subjective well-being report neuroticism-life satisfaction correlations of r=-0.38 to -0.42.^19^ Using r=-0.38 and the 29/71 exposure split, the low-satisfaction group would have approximately 0.60 SD higher neuroticism; with the cohort-study HR of 1.06, confounding bias would be modest (bias HR approximately 1.04, explaining less than 15% of the observed association). Even using the upper meta-analytic range (HR 1.15 per SD), confounding would reduce the observed HR from 1.30 to approximately 1.19---still meaningfully elevated, with personality explaining roughly one third of the association. The baseline association between dissatisfaction and mortality should accordingly be interpreted as robust but not fully explained. Adjustment for depressive symptoms (CES-D-10) only partially addresses this concern, as it captures state symptoms rather than trait negative affectivity.
+ The most important alternative explanation is confounding by personality. Trait neuroticism or negative affectivity could lower economic satisfaction ratings and increase mortality risk. KLoSA does not include personality measures, so direct adjustment is not possible. We therefore treat the bias analysis as a rough sensitivity exercise based on published estimates rather than as a sample-specific estimate of residual confounding. In a large UK cohort (N=321,456), neuroticism was associated with modestly higher all-cause mortality (age- and sex-adjusted HR 1.06 per SD, 95% CI 1.03--1.09).^18^ An individual-participant meta-analysis of 76,150 adults, however, found no independent association after adjustment for the other major personality traits.^17^ Meta-analyses of personality and subjective well-being report neuroticism-life satisfaction correlations of about r=-0.38 to -0.42.^19^ Using r=-0.38 and the 29/71 exposure split, the low-satisfaction group would have about 0.60 SD higher neuroticism; with the cohort-study HR of 1.06, the implied bias would be modest (bias HR about 1.04), explaining less than 15% of the observed association. The baseline association between dissatisfaction and mortality should accordingly be interpreted as robust but not fully explained. Adjustment for depressive symptoms (CES-D-10) only partially addresses this concern, as it captures state symptoms rather than trait negative affectivity.
```

Why:

- Removes the unresolved `HR 1.15` meta-analysis citation problem.
- Still keeps the sensitivity analysis point.
- Reads less over-engineered.

### 4.9 Limitations: remove essentializing response-style sentence

At [`submission_ssm/manuscript.md:141`](../submission_ssm/manuscript.md#L141), replace:

```diff
- East Asian response styles that avoid extreme positive endorsements may compress the satisfaction distribution, which would limit generalizability to other cultural contexts.
+ Response distributions may also be culturally patterned, which could limit direct comparability of the satisfaction scale across settings.
```

Why:

- Keeps the comparability caveat.
- Removes the most stereotyped phrasing.

### 4.10 Limitations: Basic Pension interpretation

At [`submission_ssm/manuscript.md:143`](../submission_ssm/manuscript.md#L143), replace the last sentence with:

```diff
- Korea's Basic Pension expansion during the study period may have shifted the income-satisfaction relationship over time, though both associations strengthened rather than weakened after 2014 (Supplementary Table 9).
+ Korea's Basic Pension expansion during the study period may have altered the income-satisfaction relationship over time; exploratory period-stratified and interaction analyses suggest possible heterogeneity after 2014, but these results should not be overinterpreted (Supplementary Table 9).
```

Why:

- Better matches the evidence in the appendix.
- Avoids a claim reviewers can easily challenge.

### 4.11 Conclusions: tighten and de-symmetrize

Replace [`submission_ssm/manuscript.md:147-149`](../submission_ssm/manuscript.md#L147) with:

```diff
- Both subjective and objective dimensions of economic insecurity carry mortality-relevant information, but they are not interchangeable. In this Korean cohort, perceived economic insecurity was associated with mortality beyond income, assets, and welfare receipt in baseline models, and the discordance between objective and subjective indicators provided additional descriptive support for this pattern. These findings are consistent with the stress process model, in which economic hardship is socially appraised---shaped by expectations, reference group comparisons, and institutional context---and that appraisal may carry health consequences, though this study cannot establish causality. This study identifies subjective economic dissatisfaction as a potentially important risk marker, but it does not estimate the effects of specific interventions; stronger within-person, quasi-experimental, or policy-evaluation designs are needed before drawing intervention conclusions. For measurement, cohort studies that rely solely on objective financial indicators risk missing a consequential dimension of economic insecurity in later life.
- 
- These findings may be relevant beyond South Korea, though replication in other aging populations is needed. Population aging, pension inadequacy, and the erosion of informal family support are trends shared across high-income and middle-income countries. If the pattern observed here generalizes, it would suggest that how economic insecurity is experienced---shaped by institutional context, family expectations, and social comparisons---matters for health across diverse welfare-state configurations.
+ Subjective and objective dimensions of economic insecurity were both informative, but they were not interchangeable. In this Korean cohort, perceived economic insecurity was associated with mortality beyond income, assets, and welfare receipt in baseline models, and the discordance analysis provided descriptive support for that pattern. We interpret subjective economic dissatisfaction as a potentially useful risk marker rather than as definitive causal evidence. Replication in other aging cohorts will be important for determining how strongly this pattern depends on Korea's institutional setting.
```

Why:

- Much less generic.
- Ends on the empirical contribution.
- Reduces the “too polished / too broad” feel.

---

## 5. Exact Edits For `submission_ssm/supplementary_materials.md`

### 5.1 Table 1

The supplement's Table 1 is stale relative to both the manuscript and `output/tables/table1_baseline_characteristics.csv`.

**Action:** replace [`submission_ssm/supplementary_materials.md:11-38`](../submission_ssm/supplementary_materials.md#L11) with the current inline Table 1 from [`submission_ssm/manuscript.md:180-207`](../submission_ssm/manuscript.md#L180).

Do **not** hand-edit only one or two cells. Copy the full block.

### 5.2 Figure 2 caption

At [`submission_ssm/supplementary_materials.md:91`](../submission_ssm/supplementary_materials.md#L91), replace:

```diff
- *Health-adjusted model. Reference group: neither low income nor low satisfaction (N=4,188). Both: HR=1.13 (0.99--1.30); Subjective only: HR=1.28 (1.14--1.44); Objective only: HR=0.93 (0.82--1.07).*
+ *Health-adjusted model. Reference group: neither low income nor low satisfaction (N=4,188). Both: HR=1.14 (1.00--1.31); Subjective only: HR=1.28 (1.14--1.44); Objective only: HR=0.93 (0.82--1.06).*
```

Also:

- regenerate `output/figures/figure2_discordance.png` and `output/figures/figure2_discordance.pdf`, **or**
- verify manually that the embedded figure labels are still correct

because those files are older than the rerun.

### 5.3 Table 3

The supplement's Table 3 is still pre-rerun.  
The simplest clean fix is:

**Action:** replace [`submission_ssm/supplementary_materials.md:95-145`](../submission_ssm/supplementary_materials.md#L95) with the current inline Table 3 from [`submission_ssm/manuscript.md:264-307`](../submission_ssm/manuscript.md#L264).

Do not try to patch this piecemeal. Replace the whole table block.

### 5.4 eTable 1: construct validity

Update the rows in [`submission_ssm/supplementary_materials.md:157-165`](../submission_ssm/supplementary_materials.md#L157) to match `output/supplementary/supplementary_results.json`.

Use:

- Household income (Pearson r): `0.30`, `N=9,055`
- Household net worth (Pearson r): `0.31`, `N=891`
- Personal net assets (Pearson r): `0.26`, `N=6,945`
- CES-D-10 score (Pearson r): `-0.38`, `N=10,320`
- Welfare receipt (point-biserial r): `-0.18`, `N=10,384`
- Depression, binary (point-biserial r): `-0.22`, `N=9,484`
- Self-rated health (Spearman rho): `-0.39`, `N=10,384`

### 5.5 eTable 2: subgroup analyses

Replace [`submission_ssm/supplementary_materials.md:175-184`](../submission_ssm/supplementary_materials.md#L175) with the current values from `output/tables/subgroup_analyses.csv`:

```diff
- | Male | 1.33 (1.19--1.49) | <0.001 | 4,454 | 1,412 |
- | Female | 1.23 (1.11--1.37) | <0.001 | 5,644 | 1,464 |
- | Age 45--64 | 1.28 (1.10--1.48) | 0.001 | 6,431 | 839 |
- | Age 65+ | 1.19 (1.08--1.30) | <0.001 | 3,667 | 2,037 |
- | Married | 1.35 (1.22--1.48) | <0.001 | 8,048 | 1,860 |
- | Not married | 1.15 (1.01--1.31) | 0.030 | 2,050 | 1,016 |
- | Has pension | 1.26 (1.00--1.59) | 0.054 | 882 | 324 |
- | No pension | 1.28 (1.18--1.39) | <0.001 | 9,216 | 2,552 |
- | No chronic disease | 1.23 (1.08--1.40) | 0.002 | 5,507 | 1,085 |
- | 1+ chronic diseases | 1.30 (1.18--1.44) | <0.001 | 4,591 | 1,791 |
+ | Male | 1.33 (1.19--1.49) | <0.001 | 4,469 | 1,427 |
+ | Female | 1.23 (1.11--1.37) | <0.001 | 5,676 | 1,496 |
+ | Age 45--64 | 1.28 (1.10--1.48) | 0.001 | 6,446 | 854 |
+ | Age 65+ | 1.19 (1.08--1.30) | <0.001 | 3,699 | 2,069 |
+ | Married | 1.35 (1.23--1.49) | <0.001 | 8,072 | 1,884 |
+ | Not married | 1.15 (1.01--1.31) | 0.031 | 2,073 | 1,039 |
+ | Has pension | 1.26 (1.00--1.59) | 0.053 | 884 | 326 |
+ | No pension | 1.28 (1.18--1.39) | <0.001 | 9,261 | 2,597 |
+ | No chronic disease | 1.25 (1.10--1.42) | 0.001 | 5,529 | 1,107 |
+ | 1+ chronic diseases | 1.30 (1.18--1.43) | <0.001 | 4,616 | 1,816 |
```

### 5.6 eTable 3: proportional hazards tests

Replace [`submission_ssm/supplementary_materials.md:192-203`](../submission_ssm/supplementary_materials.md#L192) with the current values from `output/supplementary/ph_test_results.csv`:

```diff
- | low_econ_sat_bl | 1.36 | 0.243 |
- | age_10 | 6.86 | 0.009 |
- | female | 17.27 | <0.001 |
- | married | 0.04 | 0.846 |
- | edu_middle | 2.25 | 0.133 |
- | edu_high | 1.09 | 0.297 |
- | edu_college | 4.74 | 0.029 |
- | self_rated_health | 17.81 | <0.001 |
- | chronic_count | 0.11 | 0.738 |
- | bmi | 2.29 | 0.130 |
- | current_smoker | 2.48 | 0.115 |
- | ever_smoker | 1.38 | 0.240 |
+ | low_econ_sat_bl | 1.59 | 0.207 |
+ | age_10 | 6.98 | 0.008 |
+ | female | 18.00 | <0.001 |
+ | married | 0.03 | 0.858 |
+ | edu_middle | 3.90 | 0.048 |
+ | edu_high | 1.28 | 0.257 |
+ | edu_college | 6.17 | 0.013 |
+ | self_rated_health | 17.88 | <0.001 |
+ | chronic_count | 0.07 | 0.795 |
+ | bmi | 2.38 | 0.123 |
+ | current_smoker | 2.06 | 0.151 |
+ | ever_smoker | 1.55 | 0.213 |
```

Also change the footnote at [`submission_ssm/supplementary_materials.md:205`](../submission_ssm/supplementary_materials.md#L205) to:

```diff
- *The primary exposure (low_econ_sat_bl) satisfies the proportional hazards assumption (p=0.24). Variables female, age_10, and self_rated_health show violations; results are robust to stratification on these variables.*
+ *The primary exposure (low_econ_sat_bl) satisfies the proportional hazards assumption (p=0.21). Variables female, age_10, edu_middle, and self_rated_health show evidence of non-proportionality; the main conclusions are unchanged in time-partitioned sensitivity analyses.*
```

### 5.7 eTable 4: sensitivity analyses

At [`submission_ssm/supplementary_materials.md:214-232`](../submission_ssm/supplementary_materials.md#L214), make these changes:

```diff
- | Excluding deaths <2 years | 1.29 (1.19--1.40) | <0.001 | --- | --- |
+ | Excluding deaths <2 years | 1.29 (1.19--1.39) | <0.001 | --- | --- |

- | Health-adjusted (wave-1 only) | 1.29 (1.19--1.40) | <0.001 | 9,436 | 2,983 |
- | Fully adjusted (wave-1 only) | 1.26 (1.17--1.37) | <0.001 | 9,436 | 2,983 |
+ | Health-adjusted (wave-1 only) | 1.30 (1.20--1.40) | <0.001 | 9,484 | 2,983 |
+ | Fully adjusted (wave-1 only) | 1.27 (1.17--1.37) | <0.001 | 9,484 | 2,983 |

- | Good/excellent SRH, no chronic diseases | 1.84 (1.21--2.78) | 0.004 | 1,076 | 128 |
+ | Good/excellent SRH, no chronic diseases | 1.83 (1.22--2.75) | 0.004 | 1,081 | 133 |

- | Q4 (highest satisfaction after Q5) | 1.07 (0.90--1.26) | 0.45 | --- | --- |
- | Q3 | 1.20 (1.02--1.43) | 0.03 | --- | --- |
- | Q2 | 1.14 (0.98--1.31) | 0.08 | --- | --- |
- | Q1 (lowest satisfaction) | 1.43 (1.24--1.65) | <0.001 | --- | --- |
+ | Q4 (highest satisfaction after Q5) | 1.05 (0.89--1.24) | 0.57 | --- | --- |
+ | Q3 | 1.19 (1.00--1.41) | 0.04 | --- | --- |
+ | Q2 | 1.14 (0.99--1.31) | 0.08 | --- | --- |
+ | Q1 (lowest satisfaction) | 1.43 (1.24--1.65) | <0.001 | --- | --- |

- | Low equivalised income (combined model) | 0.93 | --- | --- | --- |
- | Economic dissatisfaction (combined, equiv income) | 1.30 | --- | --- | --- |
+ | Low equivalised income (combined model) | 0.93 | --- | --- | --- |
+ | Economic dissatisfaction (combined, equiv income) | 1.30 | --- | --- | --- |
```

Note:

- The last two rows are unchanged numerically, but keep them aligned with `output/supplementary/income_equivalisation.json`.

### 5.8 eTable 5: attrition

Replace [`submission_ssm/supplementary_materials.md:240-248`](../submission_ssm/supplementary_materials.md#L240) with the current counts from `output/supplementary/supplementary_results.json`:

```diff
- | 1 (2006) | 100.0% (2,949) | 100.0% (6,487) | 0.0% |
- | 2 (2008) | 90.5% (2,670) | 92.3% (5,988) | --1.8% |
- | 3 (2010) | 80.3% (2,368) | 85.2% (5,526) | --4.9% |
- | 4 (2012) | 74.4% (2,195) | 81.2% (5,270) | --6.8% |
- | 5 (2014) | 68.6% (2,024) | 76.9% (4,989) | --8.3% |
- | 6 (2016) | 62.8% (1,853) | 73.3% (4,755) | --10.5% |
- | 7 (2018) | 56.2% (1,656) | 68.9% (4,472) | --12.8% |
- | 8 (2020) | 50.6% (1,492) | 65.1% (4,221) | --14.5% |
- | 9 (2022) | 45.9% (1,354) | 61.0% (3,956) | --15.1% |
+ | 1 (2006) | 100.0% (2,969) | 100.0% (6,515) | 0.0% |
+ | 2 (2008) | 90.3% (2,681) | 92.2% (6,007) | --1.9% |
+ | 3 (2010) | 80.1% (2,379) | 85.0% (5,541) | --4.9% |
+ | 4 (2012) | 74.3% (2,205) | 81.1% (5,281) | --6.8% |
+ | 5 (2014) | 68.4% (2,030) | 76.7% (4,999) | --8.3% |
+ | 6 (2016) | 62.6% (1,859) | 73.0% (4,759) | --10.4% |
+ | 7 (2018) | 55.9% (1,661) | 68.7% (4,475) | --12.8% |
+ | 8 (2020) | 50.4% (1,495) | 64.8% (4,222) | --14.4% |
+ | 9 (2022) | 45.6% (1,354) | 60.7% (3,956) | --15.1% |
```

And replace the footnote at [`submission_ssm/supplementary_materials.md:250`](../submission_ssm/supplementary_materials.md#L250) with:

```diff
- *Low ES: low economic satisfaction at baseline (bottom quintile, scores <=30). High ES: higher economic satisfaction (Q2--Q5). Wave-1 cohort only (N=9,436). Deaths among low ES: 1,264 (42.9%); deaths among high ES: 1,719 (26.5%).*
+ *Low ES: low economic satisfaction at baseline (bottom quintile, scores <=30). High ES: higher economic satisfaction (Q2--Q5). Wave-1 cohort only (N=9,484). Deaths among low ES: 1,284 (43.2%); deaths among high ES: 1,747 (26.8%).*
```

### 5.9 eTable 6: cut-point sensitivity

Replace [`submission_ssm/supplementary_materials.md:282-287`](../submission_ssm/supplementary_materials.md#L282) with:

```diff
- | <=0 (lowest only) | 563 | 7% | 1.21 (1.06--1.38) | 0.005 |
- | <=10 (bottom 2 cats) | 912 | 11% | 1.23 (1.10--1.38) | <0.001 |
- | <=20 (bottom 3 cats) | 1,506 | 18% | 1.26 (1.15--1.39) | <0.001 |
- | <=30 (bottom 4 cats) | 2,555 | 30% | 1.28 (1.17--1.39) | <0.001 |
- | <=40 (bottom 5 cats) | 3,376 | 40% | 1.20 (1.10--1.30) | <0.001 |
- | <=50 (bottom half) | 5,143 | 61% | 1.12 (1.02--1.24) | 0.015 |
+ | <=0 (lowest only) | 565 | 7% | 1.21 (1.06--1.38) | 0.005 |
+ | <=10 (bottom 2 cats) | 916 | 11% | 1.23 (1.10--1.38) | <0.001 |
+ | <=20 (bottom 3 cats) | 1,512 | 18% | 1.26 (1.15--1.39) | <0.001 |
+ | <=30 (bottom 4 cats) | 2,565 | 30% | 1.28 (1.17--1.39) | <0.001 |
+ | <=40 (bottom 5 cats) | 3,392 | 40% | 1.20 (1.10--1.31) | <0.001 |
+ | <=50 (bottom half) | 5,165 | 61% | 1.14 (1.03--1.25) | 0.008 |
```

### 5.10 eTable 7: multiple imputation

Update [`submission_ssm/supplementary_materials.md:297-302`](../submission_ssm/supplementary_materials.md#L297) to match `output/supplementary/multiple_imputation_results.json`:

```diff
- | Low HH income | 0.90 (0.79--1.03), p=0.13 | 0.93 (0.85--1.00), p=0.06 |
- | Welfare receipt (NBLSS) | 1.21 (0.92--1.59), p=0.18 | 1.07 (0.89--1.28), p=0.48 |
- | Low personal net assets | 0.96 (0.83--1.12), p=0.62 | 0.98 (0.88--1.10), p=0.75 |
- *Multiple imputation using chained equations (MICE) with 20 imputations. Fraction of missing information (FMI) for low economic satisfaction: 0.008. The primary bottleneck for missingness was personal net assets (33% missing). Results are virtually identical between complete-case and MI analyses.*
+ | Low HH income | 0.90 (0.79--1.03), p=0.13 | 0.93 (0.86--1.01), p=0.08 |
+ | Welfare receipt (NBLSS) | 1.21 (0.92--1.59), p=0.18 | 1.07 (0.89--1.28), p=0.47 |
+ | Low personal net assets | 0.96 (0.83--1.12), p=0.62 | 0.98 (0.89--1.08), p=0.70 |
+ *Multiple imputation using chained equations (MICE) with 20 imputations. Fraction of missing information (FMI) for low economic satisfaction: 0.005. The primary bottleneck for missingness was personal net assets (33% missing). Results are virtually identical between complete-case and MI analyses.*
```

### 5.11 eTable 9: Basic Pension analysis

Replace [`submission_ssm/supplementary_materials.md:338-348`](../submission_ssm/supplementary_materials.md#L338) with the current values from `output/supplementary/basic_pension_analysis.json`:

```diff
- | Pre-2014 (waves 1--4) | 1.11 (1.00--1.24) | 0.055 | 1.12 (1.00--1.26) | 0.053 |
- | Post-2014 (waves 5--8) | 1.10 (0.98--1.24) | 0.098 | 1.16 (1.04--1.30) | 0.010 |
+ | Pre-2014 (waves 1--4) | 1.14 (1.03--1.27) | 0.015 | 1.13 (1.01--1.26) | 0.039 |
+ | Post-2014 (waves 5--8) | 1.15 (1.02--1.30) | 0.025 | 1.16 (1.04--1.30) | 0.010 |

- | Satisfaction x post-2014 | 1.18 (1.02--1.37) | 0.027 |
- | Income x post-2014 | 1.22 (1.05--1.42) | 0.011 |
+ | Satisfaction x post-2014 | 1.20 (1.04--1.40) | 0.015 |
+ | Income x post-2014 | 1.20 (1.03--1.39) | 0.021 |
```

And replace the footnote at [`submission_ssm/supplementary_materials.md:350`](../submission_ssm/supplementary_materials.md#L350) with:

```diff
- *Time-varying Cox models fully adjusted for demographics, health, depression, and IADL. Post-2014 corresponds to waves 5--8, after the major Basic Pension expansion. Interaction terms test whether the exposure-mortality association changed after the pension expansion. Exploratory analysis; results may reflect compositional changes rather than pension effects.*
+ *Time-varying Cox models fully adjusted for demographics, health, depression, and IADL. Post-2014 corresponds to waves 5--8. Interaction terms test whether the exposure-mortality association differed after 2014. This is an exploratory effect-modification analysis and should not be interpreted as a policy-effect estimate.*
```

---

## 6. Exact Edits For `submission_ssm/MANUSCRIPT_PROVENANCE.md`

### 6.1 Immediate honesty fix

The current file is still too optimistic about what exists.

At minimum:

- keep the note that no single canonical CSV exists for all of Table 3
- stop claiming that `output/supplementary/objective_vs_subjective_models.csv` contains the time-varying combined model if it does not

### 6.2 Better fix that will materially improve scores

Create two machine-readable files and then update the manifest to point to them:

1. `output/tables/table2_combined_models.csv`
2. `output/tables/table3_time_varying_models.csv`

**What should go in `table2_combined_models.csv`:**

- Table 2 Panel C rows
- Table 2 Panel D rows
- complete-case `N` and `Events`

**What should go in `table3_time_varying_models.csv`:**

- Table 3 Panels A-F
- one row per model/exposure
- columns: `panel`, `exposure`, `model`, `N_intervals`, `events`, `HR`, `CI_low`, `CI_high`, `p`

Then rewrite the manifest section to something like:

```diff
- | Output (complete-case) | `output/supplementary/objective_vs_subjective_models.csv` |
+ | Output (Panels A-B) | `output/tables/table2_cox_models.csv` |
+ | Output (Panels C-D) | `output/tables/table2_combined_models.csv` |

- | Output (satisfaction + income TV, combined) | `output/supplementary/objective_vs_subjective_models.csv` (time-varying section) |
- | Note | Table 3 is assembled from console outputs of scripts 06 and 08. No single canonical CSV exists for all Table 3 panels. |
+ | Output | `output/tables/table3_time_varying_models.csv` |
+ | Note | This file is the canonical source for all Table 3 values. |
```

If you do **not** create these files, the provenance score will stay artificially low even if the manuscript itself is fine.

---

## 7. Clean Up Files That Are Actively Hurting Scores

### 7.1 `output/ec2_pipeline.log`

This file is older than the current manuscript state and has already confused one reviewer.

**Action:**

- move it to `output/_stale/ec2_pipeline_2026-03-21.log`, or
- keep it but exclude it from any package you share for review

Do **not** leave it sitting in `output/` as though it were current.

### 7.2 `output/_stale/`

This directory is fine internally, but it should not be part of anything submission-facing.

**Action:**

- exclude it from any replication bundle or review zip
- do not cite it in provenance docs

### 7.3 `output/figures/figure2_discordance.png` and `.pdf`

These are older than the rerun.

**Action:**

- regenerate them from the current code if possible
- if not, manually verify that embedded labels still match the caption and current manuscript text

### 7.4 `output/supplementary/msm_results.json`

If this is not rerun, it should not silently sit in the package as if it were part of the final frozen state.

**Action:**

- either rerun script 11 and overwrite it
- or move the current file to `output/_stale/msm_results_pre-final-rerun.json` and remove MSM from the main evidentiary narrative

---

## 8. Optional But High-Value Code/Export Improvements

These are not strictly required to submit, but they would raise the replicability/provenance scores more than anything else:

1. Extend `analysis/08_objective_vs_subjective.py` so it exports:
   - combined baseline model rows
   - continuous combined model rows
   - discordance rows
   - time-varying combined model rows

2. Extend `analysis/06_wealth_shock_time_varying.py` so it exports:
   - Panels C and D of Table 3 to CSV

3. Export appendix tables directly from the scripts instead of maintaining them by hand in `submission_ssm/supplementary_materials.md`.

If you do only one of these, do **#1**.

---

## 9. Final Validation Checklist

Do not submit until all of these are true:

- `analysis/run_all.py` validates against `10,384` and `3,074`
- `submission_ssm/manuscript.md` and `submission_ssm/supplementary_materials.md` match each other
- Table 1 matches `output/tables/table1_baseline_characteristics.csv`
- eTable 2 matches `output/tables/subgroup_analyses.csv`
- eTable 3 matches `output/supplementary/ph_test_results.csv`
- eTable 6 matches `output/supplementary/measurement_sensitivity.json`
- eTable 7 matches `output/supplementary/multiple_imputation_results.json`
- eTable 9 matches `output/supplementary/basic_pension_analysis.json`
- `submission_ssm/MANUSCRIPT_PROVENANCE.md` points only to real current artifacts
- stale logs / stale output folders are out of the submission-facing package
- the final discussion/conclusion prose has been tightened using the replacements above

---

## 10. Fastest Path If Time Is Tight

If you only have one more serious pass left, do exactly this:

1. Fix `analysis/run_all.py`
2. Apply the manuscript text replacements in section 4
3. Replace Supplement Table 1 and Table 3 from the manuscript
4. Update eTables 1, 2, 3, 5, 6, 7, and 9 with the values above
5. Clean `MANUSCRIPT_PROVENANCE.md`
6. Quarantine `output/ec2_pipeline.log` and keep `output/_stale/` out of the submission package

That will address most of what the panel was actually punishing.
