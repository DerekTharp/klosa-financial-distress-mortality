# SSM Final Polish Diff Edits

**Date:** 2026-03-25  
**Target file:** `submission_ssm/manuscript.md`  
**Goal:** improve final presentation, readability, and emphasis **without changing scientific meaning, evidentiary hierarchy, or the current title**

Boundaries for this pass:

- keep the current title
- do not change results or interpretation hierarchy
- do not strengthen causal language
- do not remove key caveats
- focus on prose polish, emphasis, and label consistency

## Recommended Diff

```diff
--- a/submission_ssm/manuscript.md
+++ b/submission_ssm/manuscript.md
@@
 ## Highlights
 
- Perceived economic insecurity predicted mortality after adjustment for objective indicators
- Adults with low satisfaction despite adequate income had elevated mortality
+ Economic dissatisfaction remained associated with mortality in joint baseline models
+ Adults reporting low economic satisfaction despite adequate income had elevated mortality
 - Low income without dissatisfaction was not associated with excess mortality
- In time-updated models, low income remained associated after joint adjustment and satisfaction was attenuated
+ In time-updated joint models, income remained marginally associated and satisfaction was attenuated
 - Subjective appraisal and objective resources were related but not interchangeable
@@
-**Methods:** We analyzed nine waves (2006--2022) of the Korean Longitudinal Study of Aging (N=10,384; 3,074 deaths; mean follow-up 12.5 years). We compared three objective indicators (household income, welfare receipt, personal net assets) with subjective economic satisfaction as predictors of all-cause mortality using Cox proportional hazards models, an income-satisfaction discordance analysis cross-classifying participants by income and satisfaction, and time-varying models with biennially updated exposures.
+**Methods:** We analyzed nine waves (2006--2022) of the Korean Longitudinal Study of Aging (N=10,384; 3,074 deaths; mean follow-up 12.5 years). We used Cox models in three steps: separate models, joint models, and discordance/time-varying sensitivity analyses. We compared three objective indicators (household income, welfare receipt, personal net assets) with subjective economic satisfaction as predictors of all-cause mortality.
@@
-**Results:** In multiply imputed joint models, economic dissatisfaction remained associated with mortality (HR 1.29, 95% CI 1.19--1.40; p<0.001), whereas none of the objective indicators in that joint model reached statistical significance. Among participants cross-classified by income and satisfaction, those with low satisfaction despite adequate income had elevated mortality (HR 1.28, 1.14--1.44), while those with low income but adequate satisfaction did not (HR 0.93, 0.82--1.07). In time-varying joint models, both income (HR 1.10, 1.00--1.21; p=0.04) and satisfaction (HR 1.09, 0.99--1.20; p=0.09) were attenuated, providing mixed secondary support.
+**Results:** In multiply imputed joint models, economic dissatisfaction remained associated with mortality (HR 1.29, 95% CI 1.19--1.40; p<0.001), whereas none of the objective indicators in that joint model reached statistical significance. Among participants cross-classified by income and satisfaction, those with low satisfaction despite adequate income had elevated mortality (HR 1.28, 1.14--1.44), while those with low income but adequate satisfaction did not (HR 0.93, 0.82--1.06). In time-varying joint models, income (HR 1.10, 1.00--1.21; p=0.04) and satisfaction (HR 1.09, 0.99--1.20; p=0.09) were both attenuated, providing mixed secondary support.
@@
-**Conclusions:** In this Korean aging cohort, perceived economic dissatisfaction was associated with mortality in baseline models after adjustment for objective financial indicators. Income-satisfaction discordance was descriptively suggestive: economic dissatisfaction in the absence of low income was associated with elevated mortality, while low income without dissatisfaction was not. These findings are consistent with stress process theory and suggest that appraised economic insecurity deserves attention alongside objective measures in population health research.
+**Conclusions:** In this Korean aging cohort, perceived economic dissatisfaction was associated with mortality in baseline models after adjustment for objective financial indicators. Income-satisfaction discordance was descriptively suggestive: economic dissatisfaction in the absence of low income was associated with elevated mortality, while low income without dissatisfaction was not. These findings are consistent with stress process theory and suggest that appraised economic insecurity may complement objective measures in population health research.
@@
-The jointly adjusted model is the primary analysis because it asks whether each dimension predicts mortality beyond the other.
+The jointly adjusted model is the primary analysis because it tests whether each dimension adds information beyond the other.
@@
-Table 2 presents associations for each financial indicator modeled separately. Low economic satisfaction showed robust associations with mortality across all adjustment levels: unadjusted HR 1.87 (95% CI 1.74--2.01), demographically adjusted HR 1.44 (1.34--1.55), and health-adjusted HR 1.27 (1.17--1.39). In contrast, low household income was strongly associated with mortality when unadjusted (HR 1.59, 1.46--1.74) but was fully attenuated by demographic adjustment (HR 1.01, 0.92--1.10; p=0.90), suggesting that age and education capture most of the between-person income variation relevant to mortality. Low personal net assets showed a paradoxical inverse unadjusted association (HR 0.87, 0.77--0.98) that disappeared after demographic adjustment (HR 0.99, 0.88--1.12; p=0.85). Welfare receipt retained a modest association after health adjustment (HR 1.23, 1.01--1.51; p=0.04), attenuating with further adjustment for potential mediators (HR 1.21, 0.98--1.48; p=0.07).
+Table 2 presents associations for each financial indicator modeled separately. Low economic satisfaction showed robust associations with mortality across all adjustment levels: unadjusted HR 1.87 (95% CI 1.74--2.01), demographically adjusted HR 1.44 (1.34--1.55), and health-adjusted HR 1.27 (1.17--1.39). In contrast, low household income was strongly associated with mortality when unadjusted (HR 1.59, 1.46--1.74) but was fully attenuated by demographic adjustment (HR 1.01, 0.92--1.10; p=0.90), suggesting that demographic differences account for much of the crude income-mortality association. Low personal net assets showed an inverse unadjusted association (HR 0.87, 0.77--0.98) that disappeared after demographic adjustment (HR 0.99, 0.88--1.12; p=0.85). Welfare receipt retained a modest association after health adjustment (HR 1.23, 1.01--1.51; p=0.04), attenuating with further adjustment for potential mediators (HR 1.21, 0.98--1.48; p=0.07).
@@
-This primary joint model is shown in Table 2, Panel C. When all three objective indicators and economic satisfaction were modeled simultaneously (N=10,384 with multiple imputation, M=20; Supplementary Table 7), economic dissatisfaction remained associated with mortality (HR 1.29, 95% CI 1.19--1.40; p<0.001), though as noted in Methods, this estimates association net of the other measures rather than a clean causal effect. Low income (HR 0.93, 0.86--1.01), welfare receipt (HR 1.07, 0.89--1.28), and low assets (HR 0.98, 0.89--1.08) were all non-significant. Complete-case results (N=5,010) were consistent: HR 1.30 (1.14--1.48). In the continuous model, each 10-point decrease in economic satisfaction was associated with 5% higher mortality (HR 1.050, 1.029--1.072; p<0.001), while log household income was non-significant (HR 1.022, 0.988--1.057; p=0.20). This comparison partially addresses measurement asymmetry (see Limitations) because both measures are modeled continuously.
+This primary joint model is shown in Table 2, Panel C. When all three objective indicators and economic satisfaction were modeled simultaneously (N=10,384 with multiple imputation, M=20; Supplementary Table 7), economic dissatisfaction remained associated with mortality (HR 1.29, 95% CI 1.19--1.40; p<0.001). Low income (HR 0.93, 0.86--1.01), welfare receipt (HR 1.07, 0.89--1.28), and low assets (HR 0.98, 0.89--1.08) were all non-significant. Complete-case results (N=5,010) were consistent: HR 1.30 (1.14--1.48). In the continuous model, each 10-point decrease in economic satisfaction was associated with 5% higher mortality (HR 1.050, 1.029--1.072; p<0.001), while log household income was non-significant (HR 1.022, 0.988--1.057; p=0.20). This comparison partly mitigates measurement asymmetry (see Limitations) because both measures are modeled continuously.
@@
-In time-varying models with exposures updated at each observed interview (Table 3), economic dissatisfaction (HR 1.22, 1.13--1.32; p<0.001) and low income (HR 1.15, 1.06--1.24; p=0.0006) were each significant in separate models. In the combined time-varying model, low income remained marginally significant (HR 1.10, 1.00--1.21; p=0.04), while economic dissatisfaction was attenuated to borderline non-significance (HR 1.09, 0.99--1.20; p=0.09). Both measures were therefore weakened once modeled together. This attenuation likely reflects shared variance between the two measures rather than a qualitative reversal of the baseline finding. Wealth shocks were not significant (HR 0.97, 0.78--1.20; p=0.77), though power was limited (detectable HR >=1.41 at 80% power). In treatment-weighted marginal structural models (Supplementary Table 8), both measures retained significance in the combined model, though residual covariate imbalance and the absence of censoring weights limit interpretation of these estimates. These time-varying and treatment-weighted analyses should therefore be read as secondary sensitivity analyses rather than as co-equal tests of the primary baseline association.
+In time-varying models with exposures updated at each observed interview (Table 3), economic dissatisfaction (HR 1.22, 1.13--1.32; p<0.001) and low income (HR 1.15, 1.06--1.24; p=0.0006) were each significant in separate models. In the combined time-varying model, low income remained marginally significant (HR 1.10, 1.00--1.21; p=0.04), whereas economic dissatisfaction was attenuated to borderline non-significance (HR 1.09, 0.99--1.20; p=0.09). This pattern may reflect shared variance between the two measures rather than a qualitative reversal of the baseline finding. Wealth shocks were not significant (HR 0.97, 0.78--1.20; p=0.77), though power was limited (detectable HR >=1.41 at 80% power). In treatment-weighted marginal structural models (Supplementary Table 8), both measures retained significance in the combined model, though residual covariate imbalance and the absence of censoring weights limit interpretation of these estimates. These time-varying and treatment-weighted analyses should be interpreted as secondary sensitivity analyses rather than as co-equal tests of the primary baseline association.
@@
-The central finding is that perceived economic dissatisfaction was more consistently associated with mortality than the objective financial indicators examined here. In jointly adjusted baseline models, economic dissatisfaction remained associated with mortality (HR 1.29, 95% CI 1.19--1.40), while household income, welfare receipt, and net assets did not reach statistical significance. The income-satisfaction discordance analysis provided descriptive support: adults who reported economic dissatisfaction despite adequate income had 28% higher mortality, while those with low income but no dissatisfaction had none. In time-varying models, both satisfaction and income were significant when modeled separately; in the combined model, both were attenuated, with income remaining marginally significant and satisfaction borderline. Together, these findings suggest that subjective appraisal of economic circumstances and objective resources capture overlapping but non-identical dimensions of later-life economic insecurity.
+The central finding is that perceived economic dissatisfaction was more consistently associated with mortality than the objective financial indicators examined here. In jointly adjusted baseline models, economic dissatisfaction remained associated with mortality (HR 1.29, 95% CI 1.19--1.40), while household income, welfare receipt, and net assets did not reach statistical significance. The income-satisfaction discordance analysis was consistent with this pattern: adults who reported economic dissatisfaction despite adequate income had 28% higher mortality, while those with low income but no dissatisfaction did not. In time-varying models, both satisfaction and income were significant when modeled separately; in the combined model, both were attenuated, with income remaining marginally significant and satisfaction borderline. Together, these findings suggest that subjective appraisal of economic circumstances and objective resources capture overlapping but non-identical dimensions of later-life economic insecurity.
@@
-The most important alternative explanation is confounding by personality.
+A key alternative explanation is confounding by personality.
@@
-The null finding for wealth shocks in our data should be interpreted cautiously given limited power, but the consistent finding across settings that subjective appraisals carry independent information suggests this is not unique to the Korean context.
+The null finding for wealth shocks in our data should be interpreted cautiously given limited power, but the consistent finding across settings that subjective appraisals carry independent information suggests that similar processes may extend beyond Korea.
@@
-This study has limitations that affect interpretation.
+This study has several limitations.
@@
-Subjective and objective dimensions of economic insecurity were both informative, but they were not interchangeable. In this Korean cohort, economic dissatisfaction remained associated with mortality in baseline joint models after adjustment for income, assets, and welfare receipt, and the income-satisfaction discordance analysis provided descriptive support for that pattern. Time-varying and treatment-weighted analyses were mixed and are best interpreted as secondary sensitivity analyses. We treat economic dissatisfaction as a useful risk marker, not causal proof. Replication in other aging cohorts will be important for determining how strongly this pattern depends on Korea's institutional setting.
+Subjective and objective dimensions of economic insecurity were both informative, but they were not interchangeable. In this Korean cohort, economic dissatisfaction remained associated with mortality in baseline joint models after adjustment for income, assets, and welfare receipt, and the income-satisfaction discordance analysis was consistent with that pattern. Time-varying and treatment-weighted analyses were mixed and should be interpreted as secondary sensitivity analyses. We treat economic dissatisfaction as a risk marker, not causal proof. Replication in other aging cohorts will be important for determining how strongly this pattern depends on Korea's institutional setting.
@@
-| Characteristic | Overall (N=10,384) | Low econ sat (Q1) (N=3,053) | Higher econ sat (Q2--Q5) (N=7,331) | P |
+| Characteristic | Overall (N=10,384) | Low economic satisfaction (Q1) (N=3,053) | Higher economic satisfaction (Q2--Q5) (N=7,331) | P |
@@
-| HH income (10K won), mean (SD) | 2219.8 (2799.1) | 1142.3 (1526.8) | 2653.3 (3065.0) | <0.001 |
+| Household income (10K won), mean (SD) | 2219.8 (2799.1) | 1142.3 (1526.8) | 2653.3 (3065.0) | <0.001 |
@@
-| Low econ sat (Q1) | 1.87 (1.74--2.01) | 1.44 (1.34--1.55) | 1.27 (1.17--1.39) | 1.23 (1.13--1.35) |
+| Low economic satisfaction (Q1) | 1.87 (1.74--2.01) | 1.44 (1.34--1.55) | 1.27 (1.17--1.39) | 1.23 (1.13--1.35) |
@@
-| Low HH income | 1.59 (1.46--1.74) | 1.01 (0.92--1.10) | 0.94 (0.85--1.03) | 0.95 (0.86--1.04) |
+| Low household income | 1.59 (1.46--1.74) | 1.01 (0.92--1.10) | 0.94 (0.85--1.03) | 0.95 (0.86--1.04) |
@@
-| Low econ sat (Q1) | **1.30 (1.14--1.48)** | **<0.001** |
-| Low HH income | 0.90 (0.79--1.03) | 0.12 |
+| Low economic satisfaction (Q1) | **1.30 (1.14--1.48)** | **<0.001** |
+| Low household income | 0.90 (0.79--1.03) | 0.12 |
@@
-| Econ dissatisfaction (per 10-pt decrease) | **1.048 (1.027--1.070)** | **<0.0001** |
-| Log HH income (per unit) | 1.021 (0.988--1.057) | 0.22 |
+| Economic dissatisfaction (per 10-pt decrease) | **1.048 (1.027--1.070)** | **<0.0001** |
+| Log household income (per unit) | 1.021 (0.988--1.057) | 0.22 |
@@
-| Low econ sat (time-varying) | 1.09 (0.99--1.20) | 0.09 |
-| Low HH income (time-varying) | **1.10 (1.00--1.21)** | **0.04** |
-| HH wealth shock (time-varying) | 0.97 (0.78--1.20) | 0.77 |
+| Low economic satisfaction (time-varying) | 1.09 (0.99--1.20) | 0.09 |
+| Low household income (time-varying) | **1.10 (1.00--1.21)** | **0.04** |
+| Household wealth shock (time-varying) | 0.97 (0.78--1.20) | 0.77 |
```

## Why These Edits

These are the highest-value polish changes from the final SSM-facing review:

- they make the baseline joint model even more clearly primary
- they let the discordance result land cleanly without overselling it
- they reduce repeated caution in Results and Discussion
- they keep time-varying and MSM analyses clearly secondary
- they remove a few table/text shorthand labels that still feel draft-like

## Notes

- I am **not** recommending a title change.
- I am **not** recommending new analyses or new framing.
- The abstract `0.93, 0.82--1.06` edit is a consistency fix so the Abstract matches the Results text and Figure 2 caption.

## Safest Subset If You Want An Ultra-Conservative Pass

If you want the smallest possible pass, I would prioritize only these edits:

1. Highlights first and fourth bullets
2. Abstract Methods and Results
3. Results sections 3.2, 3.3, and 3.6
4. Discussion opening and final conclusion paragraph
5. Table-label expansions from `econ sat` / `HH income` to full terms
