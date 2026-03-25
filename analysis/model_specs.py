"""
model_specs.py
Centralized covariate definitions for all analysis scripts.
Ensures consistency across the pipeline.
"""

# Demographic confounders (all models)
DEMO_COVS = [
    "age_10", "female", "married",
    "edu_middle", "edu_high", "edu_college",
]

# Health covariates — original set (scripts 03, 06 baseline)
HEALTH_COVS_ORIG = [
    "self_rated_health", "chronic_count", "bmi",
    "current_smoker", "ever_smoker",
]

# Health covariates — expanded set (scripts 07, 08 and manuscript primary models)
# Adds drinking (from wave 2) and exercise
HEALTH_COVS_EXPANDED = HEALTH_COVS_ORIG + [
    "current_drinker", "regular_exercise",
]

# Potential mediators
MEDIATOR_COVS = ["cesd_score", "iadl"]

# Full covariate sets
FULL_COVS_ORIG = DEMO_COVS + HEALTH_COVS_ORIG + ["depression", "iadl"]
FULL_COVS_EXPANDED = DEMO_COVS + HEALTH_COVS_EXPANDED + ["depression", "iadl"]

# Time-varying model covariates (person-period data)
TV_DEMO = DEMO_COVS.copy()
TV_HEALTH = ["self_rated_health", "chronic_count", "bmi", "current_smoker"]
TV_FULL = TV_DEMO + TV_HEALTH + ["depression", "iadl"]

# Exposure threshold
ECON_SAT_THRESHOLD = 30  # Bottom quintile: scores <= 30 (four lowest categories)
