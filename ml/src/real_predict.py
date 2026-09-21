from pathlib import Path
import json

import joblib
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "real_fraud_model.joblib"
)

METADATA_PATH = (
    BASE_DIR
    / "models"
    / "real_model_metadata.json"
)


model = joblib.load(MODEL_PATH)

with open(METADATA_PATH, "r") as f:
    metadata = json.load(f)


FEATURES = metadata["dataset"]["features"]

MODEL_NAME = metadata["model_name"]
MODEL_VERSION = metadata["model_version"]

THRESHOLD = metadata[
    "threshold_selection"
]["selected_threshold"]


def predict_real_fraud(features: dict) -> dict:
    """
    Generate a fraud prediction using the
    real credit-card fraud XGBoost model.
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
        "threshold": float(THRESHOLD),
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
    }