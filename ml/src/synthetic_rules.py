SYNTHETIC_FRAUD_RULES = {
    "late_night_start": 0,
    "late_night_end": 5,

    # Base probability is intentionally low.
    "base_logit": -4.8,

    # Behavioral risk weights.
    "amount_ratio_risk": 1.5,
    "velocity_risk": 0.25,
    "late_night_risk": 0.5,
    "online_risk": 0.15,

    # Extra risk when multiple suspicious behaviors occur.
    "combined_risk": 0.7,

}



def get_synthetic_rules() -> dict:
    return SYNTHETIC_FRAUD_RULES.copy()