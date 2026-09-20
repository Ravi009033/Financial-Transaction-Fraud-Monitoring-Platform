from pathlib import Path
import json

import joblib
import pandas as pd


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "production_fraud_model_v3.joblib"
)

METADATA_PATH = (
    BASE_DIR
    / "models"
    / "production_model_v3_metadata.json"
)


# --------------------------------------------------
# Load model and metadata
# --------------------------------------------------

model = joblib.load(MODEL_PATH)

with open(METADATA_PATH, "r") as f:
    metadata = json.load(f)


FEATURES = metadata["features"]
THRESHOLD = metadata["threshold_selection"]["selected_threshold"]
MODEL_NAME = metadata["model_name"]
MODEL_VERSION = metadata["model_version"]


# --------------------------------------------------
# Prediction
# --------------------------------------------------

def predict_production_fraud(features: dict) -> dict:
    """
    Generate a fraud prediction using the
    production-oriented XGBoost model.
    """

    missing_features = [
        feature
        for feature in FEATURES
        if feature not in features
    ]

    if missing_features:
        raise ValueError(
            f"Missing features: {missing_features}"
        )

    # Preserve exact training feature order.
    input_data = pd.DataFrame(
        [[features[feature] for feature in FEATURES]],
        columns=FEATURES,
    )

    fraud_score = model.predict_proba(
        input_data
    )[0, 1]

    fraud_decision = (
        "fraud"
        if fraud_score >= THRESHOLD
        else "legitimate"
    )

    return {
        "fraud_score": float(fraud_score),
        "fraud_decision": fraud_decision,
        "threshold": THRESHOLD,
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
    }