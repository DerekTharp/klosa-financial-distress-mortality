# Final Panel Diff Edits

**Date:** 2026-03-25  
**Purpose:** exact diff-style edits responding to the final 10-person SSM panel in [SSM_FINAL_10PANEL_2026-03-25.md](/Users/derektharp/Documents/_Projects/26.21%20Korean%20Financial%20Distress%20--%20Mortality/submission_ssm/SSM_FINAL_10PANEL_2026-03-25.md)

These diffs are written against the current live files. They focus on the panel's remaining confirmed blockers:

1. `manuscript.md` wording and table-alignment fixes
2. `supplementary_materials.md` MSM alignment and equivalization cleanup
3. `MANUSCRIPT_PROVENANCE.md` supplement-output mapping
4. `CURRENT_FILES.md` stale MSM status

## 1. `submission_ssm/manuscript.md`

```diff
--- a/submission_ssm/manuscript.md
+++ b/submission_ssm/manuscript.md
@@
-# Economic insecurity and mortality in later life: a 16-year national cohort study from South Korea
+# Economic dissatisfaction, income-satisfaction discordance, and mortality in later life: a 16-year national cohort study from South Korea
@@
-## Highlights
-
-- Perceived economic insecurity predicted mortality after adjustment for objective indicators
-- Adults with low satisfaction despite adequate income had elevated mortality
-- Low income without dissatisfaction was not associated with excess mortality
-- In time-updated models, low income remained associated after joint adjustment and satisfaction was attenuated
-- Subjective appraisal and objective resources were related but not interchangeable
+## Highlights
+
+- Economic dissatisfaction remained associated with mortality in joint baseline models
+- Adults with low satisfaction despite adequate income had elevated mortality
+- Low income without dissatisfaction was not associated with excess mortality
+- Time-updated joint models attenuated both income and satisfaction estimates
+- Subjective appraisal and objective indicators captured overlapping but non-identical dimensions
@@
-**Background:** Economic insecurity in later life is linked to mortality, but studies rarely examine objective and subjective indicators simultaneously. Whether perceived economic dissatisfaction predicts mortality beyond income and assets is unclear.
+**Background:** Economic insecurity in later life is linked to mortality, but studies rarely examine objective and subjective indicators simultaneously. Whether perceived economic dissatisfaction predicts mortality after adjustment for income and assets is unclear.
@@
-**Methods:** We analyzed nine waves (2006--2022) of the Korean Longitudinal Study of Aging (N=10,384; 3,074 deaths; mean follow-up 12.5 years). We compared three objective indicators (household income, welfare receipt, personal net assets) with subjective economic satisfaction as predictors of all-cause mortality using Cox proportional hazards models, a discordance analysis cross-classifying participants by income and satisfaction, and time-varying models with biennially updated exposures.
+**Methods:** We analyzed nine waves (2006--2022) of the Korean Longitudinal Study of Aging (N=10,384; 3,074 deaths; mean follow-up 12.5 years). We compared three objective indicators (household income, welfare receipt, personal net assets) with subjective economic satisfaction as predictors of all-cause mortality using Cox proportional hazards models, an income-satisfaction discordance analysis cross-classifying participants by income and satisfaction, and time-varying models with biennially updated exposures.
@@
-**Results:** In jointly adjusted models with multiple imputation, economic dissatisfaction was the only significant predictor of mortality (HR 1.29, 95% CI 1.19--1.40; p<0.001); no objective indicator was significant. Among participants cross-classified by income and satisfaction, those with low satisfaction despite adequate income had elevated mortality (HR 1.28, 1.14--1.44), while those with low income but adequate satisfaction did not (HR 0.93, 0.82--1.07). In time-varying models with jointly modeled exposures, both income (HR 1.10, 1.00--1.21; p=0.04) and satisfaction (HR 1.09, 0.99--1.20; p=0.09) were attenuated, though satisfaction more so.
+**Results:** In multiply imputed joint models, economic dissatisfaction remained associated with mortality (HR 1.29, 95% CI 1.19--1.40; p<0.001), whereas none of the objective indicators in that joint model reached statistical significance. Among participants cross-classified by income and satisfaction, those with low satisfaction despite adequate income had elevated mortality (HR 1.28, 1.14--1.44), while those with low income but adequate satisfaction did not (HR 0.93, 0.82--1.07). In time-varying models with jointly modeled exposures, both income (HR 1.10, 1.00--1.21; p=0.04) and satisfaction (HR 1.09, 0.99--1.20; p=0.09) were attenuated; these secondary analyses therefore provided mixed support rather than a cleaner replication of the baseline joint model.
@@
-**Conclusions:** In this Korean aging cohort, perceived economic insecurity was associated with mortality after adjustment for objective financial indicators. The discordance between subjective and objective indicators is informative: economic dissatisfaction in the absence of low income was associated with elevated mortality, while low income without dissatisfaction was not. These findings are consistent with stress process theory and suggest that appraised economic insecurity warrants attention alongside objective measures in population health research.
+**Conclusions:** In this Korean aging cohort, perceived economic dissatisfaction was associated with mortality in baseline models after adjustment for objective financial indicators. Income-satisfaction discordance was descriptively suggestive: economic dissatisfaction in the absence of low income was associated with elevated mortality, while low income without dissatisfaction was not. These findings are consistent with stress process theory and suggest that appraised economic insecurity warrants attention alongside coarse objective measures in population health research.
@@
-**Keywords:** Economic insecurity; Mortality; Aging; Stress process; South Korea; Cohort study
+**Keywords:** Economic dissatisfaction; Mortality; Aging; Stress process; South Korea; Cohort study
@@
-Prior research has examined either objective or subjective financial indicators in relation to mortality, but rarely both simultaneously. Two Asian studies have directly compared both dimensions: Lee and Huang found that consistently low economic satisfaction trajectories predicted mortality in Taiwanese older adults,^10^ and Wang and colleagues reported that subjective financial status was more strongly associated with mortality than objective status in Chinese older adults.^11^ Neither study, however, cross-classified participants by objective and subjective indicators to examine what happens when the two dimensions disagree---that is, when someone reports economic dissatisfaction despite adequate income, or adequate satisfaction despite low income. Understanding these discordant groups is important because they reveal whether subjective appraisal carries independent mortality-relevant information or merely proxies for unmeasured objective deprivation.
+Prior research has examined either objective or subjective financial indicators in relation to mortality, but rarely both simultaneously. Two Asian studies have directly compared both dimensions: Lee and Huang found that consistently low economic satisfaction trajectories predicted mortality in Taiwanese older adults,^10^ and Wang and colleagues reported that subjective financial status was more strongly associated with mortality than objective status in Chinese older adults.^11^ Neither study, however, cross-classified participants by objective and subjective indicators to examine what happens when the two dimensions disagree---that is, when someone reports economic dissatisfaction despite adequate income, or adequate satisfaction despite low income. Understanding these discordant groups may clarify whether subjective appraisal captures mortality-relevant information not well represented by coarse objective measures, or instead proxies for unmeasured objective deprivation.
@@
-*Objective financial indicators.* We examined three indicators: (1) Low household income (bottom quintile; baseline-specific in cross-sectional models, wave-specific in time-varying models). Household income was not equivalized for household size in primary analyses; sensitivity analyses using OECD square-root equivalization confirmed unchanged results (Supplementary Table 4). (2) Receipt of National Basic Livelihood Security System (NBLSS) welfare benefits---a stringently means-tested program with very low take-up among older adults, partly because eligibility rules consider support potentially available from adult children.^20^ NBLSS recipients also receive Medical Aid with lower copayments, which complicates its interpretation as a pure poverty indicator. (3) Low personal net assets (bottom quintile). We also examined negative wealth shocks (>=75% decline in household net worth between waves), following Pool and colleagues.^1^
+*Objective financial indicators.* We examined three indicators: (1) Low household income (bottom quintile; baseline-specific in cross-sectional models, wave-specific in time-varying models). Household income was not equivalized for household size in primary analyses; a sensitivity analysis using OECD square-root equivalization did not materially change the separate-model estimate for low income (Supplementary Table 4). (2) Receipt of National Basic Livelihood Security System (NBLSS) welfare benefits---a stringently means-tested program with very low take-up among older adults, partly because eligibility rules consider support potentially available from adult children.^20^ NBLSS recipients also receive Medical Aid with lower copayments, which complicates its interpretation as a pure poverty indicator. (3) Low personal net assets (bottom quintile). We also examined negative wealth shocks (>=75% decline in household net worth between waves), following Pool and colleagues.^1^
@@
-In the jointly adjusted model including all three objective indicators and economic satisfaction simultaneously (Table 2, Model C; N=10,384 with multiple imputation, M=20; Supplementary Table 7), economic dissatisfaction was the only significant predictor (HR 1.29, 95% CI 1.19--1.40; p<0.001), though as noted in Methods, this may partly reflect mediation (income causing satisfaction) rather than true independence. Low income (HR 0.93, 0.86--1.01), welfare receipt (HR 1.07, 0.89--1.28), and low assets (HR 0.98, 0.89--1.08) were all non-significant. Complete-case results (N=5,010) were consistent: HR 1.30 (1.14--1.48). In the continuous model, each 10-point decrease in economic satisfaction was associated with 5% higher mortality (HR 1.050, 1.029--1.072; p<0.0001) while log household income was non-significant (HR 1.022, 0.988--1.057; p=0.20); this comparison partially addresses measurement asymmetry (see Limitations) because both measures are modeled continuously.
+In the multiply imputed joint model including all three objective indicators and economic satisfaction simultaneously (N=10,384; M=20; Supplementary Table 7), economic dissatisfaction remained associated with mortality (HR 1.29, 95% CI 1.19--1.40; p<0.001), though as noted in Methods, this may partly reflect mediation (income causing satisfaction) rather than true independence. None of the objective indicators in that MI joint model reached statistical significance: low income HR 0.93 (0.86--1.01), welfare receipt HR 1.07 (0.89--1.28), and low assets HR 0.98 (0.89--1.08). Complete-case results shown in Table 2 Panel C (N=5,010) were consistent: HR 1.30 (1.14--1.48). In the continuous complete-case model, each 10-point decrease in economic satisfaction was associated with 5% higher mortality (HR 1.050, 1.029--1.072; p<0.001) while log household income was non-significant (HR 1.022, 0.988--1.057; p=0.205); this comparison partially addresses measurement asymmetry (see Limitations) because both measures are modeled continuously.
@@
-### 3.4. Discordance between objective and subjective indicators
+### 3.4. Income-satisfaction discordance
@@
-Figure 2 presents the discordance analysis. Among 8,575 participants with complete data, those who reported low economic satisfaction despite adequate income had significantly elevated mortality compared to the reference group with neither indicator (HR 1.28, 95% CI 1.14--1.44; p<0.0001). Those with low income but adequate economic satisfaction had no excess mortality (HR 0.93, 0.82--1.06; p=0.30). Those with both low income and low satisfaction had borderline elevated risk (HR 1.14, 1.00--1.31; p=0.05); their lower hazard ratio compared to the subjective-only group may reflect the older age distribution and higher welfare receipt in this group.
+Figure 2 presents the income-satisfaction discordance analysis. Among 8,575 participants with complete data, those who reported low economic satisfaction despite adequate income had significantly elevated mortality compared to the reference group with neither indicator (HR 1.28, 95% CI 1.14--1.44; p<0.0001). Those with low income but adequate economic satisfaction had no excess mortality (HR 0.93, 0.82--1.06; p=0.30). Those with both low income and low satisfaction had borderline elevated risk (HR 1.14, 1.00--1.31; p=0.05); because this cross-classification conditions on two related measures, it should be interpreted descriptively rather than as identifying a causal risk stratum.
@@
-In time-varying models with exposures updated at each observed interview (Table 3), economic dissatisfaction (HR 1.22, 1.13--1.32; p<0.001) and low income (HR 1.15, 1.06--1.24; p=0.0006) were each significant in separate models. In the combined time-varying model, both were attenuated: low income remained marginally significant (HR 1.10, 1.00--1.21; p=0.04) while economic dissatisfaction was attenuated to borderline non-significance (HR 1.09, 0.99--1.20; p=0.09). This attenuation in the combined model likely reflects shared variance between the two measures rather than a qualitative reversal of the baseline finding. Wealth shocks were not significant (HR 0.97, 0.78--1.20; p=0.77), though power was limited (detectable HR >=1.41 at 80% power). In treatment-weighted marginal structural models (Supplementary Table 8), both measures retained significance in the combined model, though residual covariate imbalance and the absence of censoring weights limit interpretation of these estimates.
+In time-varying models with exposures updated at each observed interview (Table 3), economic dissatisfaction (HR 1.22, 1.13--1.32; p<0.001) and low income (HR 1.15, 1.06--1.24; p=0.0006) were each significant in separate models. In the combined time-varying model, both were attenuated: low income remained marginally significant (HR 1.10, 1.00--1.21; p=0.04) while economic dissatisfaction was attenuated to borderline non-significance (HR 1.09, 0.99--1.20; p=0.09). This attenuation in the combined model likely reflects shared variance between the two measures rather than a qualitative reversal of the baseline finding. Wealth shocks were not significant (HR 0.97, 0.78--1.20; p=0.77), though power was limited (detectable HR >=1.41 at 80% power). In treatment-weighted marginal structural models (Supplementary Table 8), both measures retained significance in the combined model, though residual covariate imbalance and the absence of censoring weights limit interpretation of these estimates. These time-varying and treatment-weighted analyses should therefore be read as secondary sensitivity analyses rather than as co-equal tests of the primary baseline association.
@@
-In this nationally representative cohort of older South Korean adults, perceived economic insecurity was more consistently associated with mortality than objective financial indicators. In jointly adjusted baseline models, economic dissatisfaction was the only significant predictor (HR 1.29, 95% CI 1.19--1.40), while household income, welfare receipt, and net assets were not. The discordance analysis provided descriptive support: adults who reported economic dissatisfaction despite adequate income had 28% higher mortality, while those with low income but no dissatisfaction had none. In time-varying models, both satisfaction and income were significant when modeled separately; in the combined model, both were attenuated, with income remaining marginally significant and satisfaction borderline. Together, these findings suggest that subjective appraisal of economic circumstances and objective resources both carry mortality-relevant information, but that they share variance and are partly but not fully interchangeable.
+In this nationally representative cohort of older South Korean adults, perceived economic dissatisfaction was more consistently associated with mortality than the objective financial indicators examined here. In jointly adjusted baseline models, economic dissatisfaction remained associated with mortality (HR 1.29, 95% CI 1.19--1.40), while household income, welfare receipt, and net assets did not reach statistical significance. The income-satisfaction discordance analysis provided descriptive support: adults who reported economic dissatisfaction despite adequate income had 28% higher mortality, while those with low income but no dissatisfaction had none. In time-varying models, both satisfaction and income were significant when modeled separately; in the combined model, both were attenuated, with income remaining marginally significant and satisfaction borderline. Together, these findings suggest that subjective appraisal of economic circumstances and objective resources capture overlapping but non-identical dimensions of later-life economic insecurity.
@@
-These institutional features suggest that economic dissatisfaction among Korean older adults may partly reflect genuine gaps between economic needs and available support---both public and familial---though personality-related reporting differences cannot be ruled out. The weakening of filial support norms creates a context in which older adults who expected to rely on adult children find themselves economically vulnerable in ways that income measures alone do not capture. It is possible, for instance, that an older adult who reports low economic satisfaction despite adequate household income is expressing disappointment that expected family support is not forthcoming---a source of distress tied to relational expectations rather than material deprivation. We cannot test this interpretation with the available data, but it is consistent with the broader stress process framework in which the meaning of economic circumstances is shaped by social context.
+These institutional features suggest that economic dissatisfaction among Korean older adults may partly reflect genuine gaps between economic needs and available support---both public and familial---though personality-related reporting differences cannot be ruled out. Changes in later-life family support may create a context in which some older adults feel economically vulnerable in ways that income measures alone do not capture. One possibility is that an older adult who reports low economic satisfaction despite adequate household income is expressing concern about whether expected support is actually available---a source of strain tied to relational expectations as well as material resources. We cannot test this interpretation with the available data, and we offer it as a hypothesis about institutional context rather than as direct evidence about Korean culture.
@@
-This cohort (born approximately 1920--1960) experienced the 1997 Asian Financial Crisis during their peak earning years, an event that devastated household savings and may have left lasting impressions about economic fragility. Whether such cohort-specific experiences amplify the salience of perceived economic insecurity in this population remains an open question.
+This cohort (born approximately 1920--1960) also lived through the 1997 Asian Financial Crisis during midlife, which may have heightened concern about economic fragility, though that possibility remains speculative in the present data.
@@
-These results extend two prior Asian studies. Lee and Huang found that consistently low economic satisfaction trajectories predicted mortality in Taiwanese older adults,^10^ and Wang and colleagues reported that subjective financial status was more strongly associated with mortality than objective status in Chinese older adults.^11^ Our study adds a discordance analysis showing that the subjective-objective gap itself is informative: it is not merely that subjective indicators are stronger predictors but that adults who feel economically insecure despite adequate resources represent a distinct risk group. In Western settings, Pool and colleagues reported that objective wealth shocks predicted mortality in US adults (HR 1.50),^1^ while Szanton and colleagues found that perceived financial strain predicted mortality in older women.^5^ The null finding for wealth shocks in our data should be interpreted cautiously given limited power, but the consistent finding across settings that subjective appraisals carry independent information suggests this is not unique to the Korean context.
+These results extend two prior Asian studies. Lee and Huang found that consistently low economic satisfaction trajectories predicted mortality in Taiwanese older adults,^10^ and Wang and colleagues reported that subjective financial status was more strongly associated with mortality than objective status in Chinese older adults.^11^ Our study adds an income-satisfaction discordance analysis showing that the mismatch between reported satisfaction and low income is descriptively informative: adults who reported dissatisfaction despite adequate income had higher mortality than the reference group, though this pattern should not be overinterpreted as identifying a distinct causal risk stratum because cross-classification of related measures may introduce collider bias. In Western settings, Pool and colleagues reported that objective wealth shocks predicted mortality in US adults (HR 1.50),^1^ while Szanton and colleagues found that perceived financial strain predicted mortality in older women.^5^ The null finding for wealth shocks in our data should be interpreted cautiously given limited power, but the consistent finding across settings that subjective appraisals carry mortality-relevant information suggests this is not unique to the Korean context.
@@
-The attenuation of the satisfaction coefficient in time-varying models is consistent with stable confounders (including personality) partly explaining the baseline association, though it is also consistent with measurement noise in within-person change scores. Exploratory treatment-weighted marginal structural models found both satisfaction and income significant in the combined model (Supplementary Table 8), but these estimates should be interpreted with caution: the models achieved only partial covariate balance, used treatment weights without censoring weights, and the resulting estimates are best understood as approximate sensitivity analyses rather than definitive total-effect estimates.
+The attenuation of the satisfaction coefficient in time-varying models is consistent with stable confounders (including personality) partly explaining the baseline association, though it is also consistent with measurement noise in within-person change scores. Exploratory treatment-weighted marginal structural models found both satisfaction and income significant in the combined model (Supplementary Table 8), but these estimates should be interpreted with caution: the models achieved only partial covariate balance, used treatment weights without censoring weights, and the resulting estimates are best understood as approximate sensitivity analyses rather than definitive total-effect estimates. More generally, the time-varying and treatment-weighted analyses should be read as exploratory sensitivity analyses rather than as clean within-person or total-effect estimates.
@@
-This study has limitations that affect interpretation. The comparison between subjective and objective indicators is inherently asymmetric: the subjective measure uses an 11-point scale while the objective measures were dichotomized at the bottom quintile, potentially favoring the subjective indicator. The continuous combined model, analyses across six alternative dichotomization thresholds, and restricted cubic spline results partially address this concern, as all yield consistent findings. We use "economic dissatisfaction" rather than "financial distress" for the subjective measure, as KLoSA measures satisfaction---a cognitive evaluation---rather than distress per se; these constructs may relate differently to health.
+This study has limitations that affect interpretation. The comparison between subjective and objective indicators is inherently asymmetric: the subjective measure is a graded 11-point appraisal scale, whereas the objective measures are represented primarily as coarse quintile/binary indicators, potentially favoring the subjective indicator. The continuous combined model, analyses across six alternative dichotomization thresholds, and restricted cubic spline results partially address this concern, as all yield consistent findings. We use "economic dissatisfaction" rather than "financial distress" for the subjective measure, as KLoSA measures satisfaction---a cognitive evaluation---rather than distress per se; these constructs may relate differently to health.
@@
-Mortality ascertainment via proxy exit interviews rather than death registry linkage means that deaths among those lost to follow-up are missed, and differential attrition was substantial (46% vs. 61% wave-9 retention by baseline satisfaction status). The ICC of 0.49 may partly reflect measurement noise rather than genuine instability; if so, baseline estimates are attenuated (the true association may exceed the observed HR) and within-person change scores are noisier, potentially explaining the attenuated time-varying result. Response distributions may also be culturally patterned, which could limit direct comparability of the satisfaction scale across settings. Household income was not equivalized for household size, though sensitivity analyses using OECD square-root equivalization yielded virtually identical results (Supplementary Table 4).
+Mortality ascertainment via proxy exit interviews rather than death registry linkage means that deaths among those lost to follow-up are missed, and differential attrition was substantial (46% vs. 61% wave-9 retention by baseline satisfaction status). The ICC of 0.49 may partly reflect measurement noise rather than genuine instability; if so, baseline estimates are attenuated (the true association may exceed the observed HR) and within-person change scores are noisier, potentially explaining the attenuated time-varying result. Response distributions may also be culturally patterned, which could limit direct comparability of the satisfaction scale across settings. Household income was not equivalized for household size, though a sensitivity analysis using OECD square-root equivalization did not materially change the separate-model estimate for low income (Supplementary Table 4).
@@
-Subjective and objective dimensions of economic insecurity were both informative, but they were not interchangeable. In this Korean cohort, perceived economic insecurity was associated with mortality beyond income, assets, and welfare receipt in baseline models, and the discordance analysis provided descriptive support for that pattern. We interpret subjective economic dissatisfaction as a potentially useful risk marker rather than as definitive causal evidence. Replication in other aging cohorts will be important for determining how strongly this pattern depends on Korea's institutional setting.
+Subjective and objective dimensions of economic insecurity were both informative, but they were not interchangeable. In this Korean cohort, economic dissatisfaction remained associated with mortality in baseline joint models after adjustment for income, assets, and welfare receipt, and the income-satisfaction discordance analysis provided descriptive support for that pattern. Time-varying and treatment-weighted analyses were mixed and are best interpreted as secondary sensitivity analyses. We interpret economic dissatisfaction as a potentially useful risk marker rather than as definitive causal evidence. Replication in other aging cohorts will be important for determining how strongly this pattern depends on Korea's institutional setting.
@@
-### Panel C: Combined model (all objective + subjective, health-adjusted)
+### Panel C: Combined model (complete-case; all objective + subjective, health-adjusted)
@@
-| Low HH income | 0.90 (0.79--1.03) | 0.12 |
-| Welfare receipt (NBLSS) | 1.21 (0.92--1.59) | 0.18 |
-| Low personal net assets | 0.96 (0.83--1.12) | 0.62 |
+| Low HH income | 0.91 (0.80--1.03) | 0.137 |
+| Welfare receipt (NBLSS) | 1.21 (0.92--1.59) | 0.177 |
+| Low personal net assets | 0.97 (0.83--1.12) | 0.654 |
@@
-### Panel D: Continuous combined model (health-adjusted)
+### Panel D: Continuous combined model (complete-case; health-adjusted)
@@
-| Econ dissatisfaction (per 10-pt decrease) | **1.048 (1.027--1.070)** | **<0.0001** |
-| Log HH income (per unit) | 1.021 (0.988--1.057) | 0.22 |
+| Econ dissatisfaction (per 10-pt decrease) | **1.050 (1.029--1.072)** | **<0.001** |
+| Log HH income (per unit) | 1.022 (0.988--1.057) | 0.205 |
```

## 2. `submission_ssm/supplementary_materials.md`

Note: this takes the conservative route for the income-equivalization block. Because the canonical JSON currently preserves full interval estimates only for the separate-model equivalized-income result, the cleanest submission-ready edit is to remove the incomplete combined-model rows rather than leave partial values.

```diff
--- a/submission_ssm/supplementary_materials.md
+++ b/submission_ssm/supplementary_materials.md
@@
 | **Income equivalisation (OECD square-root)** | | | | |
 | Low equivalised income (separate, health-adj) | 0.98 (0.88--1.08) | 0.62 | --- | --- |
-| Low equivalised income (combined model) | 0.93 | --- | --- | --- |
-| Economic dissatisfaction (combined, equiv income) | 1.30 | --- | --- | --- |
@@
 ## eTable 8. Marginal structural models with stabilised IPTW
@@
 | Exposure | Standard adjusted (direct effect) | MSM total effect (bootstrap 95% CI) |
 |:---|:---:|:---:|
-| Low econ satisfaction | 1.11 (1.02--1.20), p=0.013 | 1.62 (1.50--1.74), p<0.001 |
-| Low HH income | 1.15 (1.06--1.24), p=0.001 | 1.53 (1.41--1.65), p<0.001 |
+| Low econ satisfaction | 1.23 (1.13--1.33), p<0.001 | 1.91 (1.76--2.07), p=0.001 |
+| Low HH income | 1.15 (1.06--1.25), p<0.001 | 1.53 (1.42--1.66), p=0.001 |
@@
 | Exposure | Standard adjusted (direct effect) | MSM treatment-weighted (bootstrap 95% CI) |
 |:---|:---:|:---:|
-| Low econ satisfaction | 1.19 (1.10--1.30), p<0.001 | 1.80 (1.65--1.95), p<0.001 |
-| Low HH income | 1.12 (1.03--1.22), p=0.006 | 1.40 (1.28--1.53), p<0.001 |
+| Low econ satisfaction | 1.19 (1.10--1.30), p<0.001 | 1.80 (1.65--1.95), p=0.001 |
+| Low HH income | 1.12 (1.03--1.22), p=0.006 | 1.40 (1.28--1.53), p=0.001 |
@@
 | Model | Mean | SD | P1 | P99 | ESS | ESS/N |
 |:---|:---:|:---:|:---:|:---:|:---:|:---:|
-| Satisfaction (separate) | 1.00 | 0.26 | 0.43 | 2.18 | 59,238 | 93.8% |
+| Satisfaction (separate) | 1.00 | 0.26 | 0.41 | 2.27 | 59,112 | 93.6% |
 | Income (separate) | 0.98 | 0.30 | 0.34 | 2.52 | 57,791 | 91.5% |
-| Joint (combined) | 0.98 | 0.36 | 0.29 | 2.77 | 55,784 | 88.3% |
+| Joint (combined) | 0.98 | 0.37 | 0.27 | 2.84 | 55,445 | 87.8% |
```

## 3. `submission_ssm/MANUSCRIPT_PROVENANCE.md`

This expands the supplement section from a mostly script-based index into a true supplement-to-output map.

```diff
--- a/submission_ssm/MANUSCRIPT_PROVENANCE.md
+++ b/submission_ssm/MANUSCRIPT_PROVENANCE.md
@@
 ### Supplementary Table 1 -- Construct Validity
 
 | Field | Value |
 |---|---|
 | Script | `analysis/03_cox_models.py` |
+| Output | `output/supplementary/supplementary_results.json` (`construct_validity`) |
@@
 ### Supplementary Table 2 -- Subgroup Analyses
 
 | Field | Value |
 |---|---|
 | Script | `analysis/03_cox_models.py` |
+| Output | `output/tables/subgroup_analyses.csv` |
@@
 ### Supplementary Table 4 -- Sensitivity Analyses
 
 | Field | Value |
 |---|---|
 | Script | `analysis/07_extended_sensitivity.py` |
+| Output | `output/supplementary/supplementary_results.json` (`sensitivity_no_refreshment`, `healthy_baseline`, `dose_response`, `power_analysis`) |
+| Output (income equivalisation block) | `output/supplementary/income_equivalisation.json` |
@@
 ### Supplementary Table 5 -- Retention Analysis
 
 | Field | Value |
 |---|---|
 | Script | `analysis/04_subgroups_and_sensitivity.py` |
+| Output | `output/supplementary/supplementary_results.json` (`attrition`) |
@@
 ### Supplementary Table 6 -- Alternative Thresholds
 
 | Field | Value |
 |---|---|
 | Script | `analysis/10_measurement_sensitivity.py` |
+| Output | `output/supplementary/measurement_sensitivity.json` |
@@
 ### Supplementary Table 7 -- Multiple Imputation Results
 
 | Field | Value |
 |---|---|
 | Script | `analysis/09_multiple_imputation.py` |
+| Output | `output/supplementary/multiple_imputation_results.json` |
@@
 ### Supplementary Table 8 -- Marginal Structural Model Results
 
 | Field | Value |
 |---|---|
 | Script | `analysis/11_marginal_structural_models.py` |
+| Output | `output/supplementary/msm_results.json` |
@@
 ### Supplementary Table 9 -- Basic Pension Analysis
 
 | Field | Value |
 |---|---|
 | Script | `analysis/12_basic_pension_analysis.py` |
+| Output | `output/supplementary/basic_pension_analysis.json` |
@@
 ### Supplementary Figure 2 -- Kaplan-Meier Curves for Wealth Shock
 
 | Field | Value |
 |---|---|
 | Script | `analysis/06_wealth_shock_time_varying.py` |
+| Output | `output/figures/figure4_km_wealth_shock.png` |
@@
 ### Supplementary Figure 3 -- Dose-Response by Quintiles
 
 | Field | Value |
 |---|---|
 | Script | `analysis/03_cox_models.py` |
+| Output | `output/figures/figure3_dose_response.png` |
@@
 ### Supplementary Figure 4 -- Restricted Cubic Spline
 
 | Field | Value |
 |---|---|
 | Script | `analysis/10_measurement_sensitivity.py` |
+| Output | `output/figures/efigure4_spline_dose_response.png` |
```

## 4. `submission_ssm/CURRENT_FILES.md`

This one is not part of the submission package, but it should not keep advertising stale MSM status.

```diff
--- a/submission_ssm/CURRENT_FILES.md
+++ b/submission_ssm/CURRENT_FILES.md
@@
-Last updated: 2026-03-25 12:25 EDT
+Last updated: 2026-03-25 14:20 EDT
@@
-All files in `output/tables/` and `output/supplementary/` are from the 2026-03-25 rerun except:
-- `output/supplementary/msm_results.json` — still from 2026-03-20 (MSM rerun pending)
-- `output/_stale/` — quarantined legacy artifacts, do not use
+All files in `output/tables/` and `output/supplementary/` are from the 2026-03-25 rerun.
+- `output/_stale/` contains quarantined legacy artifacts and should not be used.
```

## 5. Order of operations

If you apply these, do it in this order:

1. `supplementary_materials.md`
2. `manuscript.md`
3. `MANUSCRIPT_PROVENANCE.md`
4. `CURRENT_FILES.md`

## 6. Two small cautions

1. The equivalized-income fix above is intentionally conservative. If you want the combined-model equivalized rows to remain in eTable 4, the better solution is to regenerate canonical output with full CIs/p-values rather than keep partial rows.
2. After applying the manuscript edits, re-check the inline references to `Table 2`, `Supplementary Table 4`, and `Supplementary Table 8` once more so the narrative still matches exactly.
