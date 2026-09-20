from pathlib import Path
import json

import joblib
import pandas as pd


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "xgboost_fraud_model.joblib"
METADATA_PATH = BASE_DIR / "models" / "model_metadata.json"


# --------------------------------------------------
# Load model and metadata
# --------------------------------------------------

model = joblib.load(MODEL_PATH)

with open(METADATA_PATH, "r") as f:
    metadata = json.load(f)


FEATURES = metadata["features"]
THRESHOLD = metadata["threshold"]


# --------------------------------------------------
# Prediction function
# --------------------------------------------------

def predict_fraud(features: dict) -> dict:
    """
    Generate fraud prediction for a single transaction.

    Parameters
    ----------
    features : dict
        Dictionary containing all required ML features.

    Returns
    -------
    dict
        Fraud score and fraud decision.
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

    # Ensure exact feature order
    input_data = pd.DataFrame(
        [[features[feature] for feature in FEATURES]],
        columns=FEATURES
    )

    # Fraud probability
    fraud_score = model.predict_proba(
        input_data
    )[0, 1]

    # Apply frozen threshold
    fraud_decision = (
        "fraud"
        if fraud_score >= THRESHOLD
        else "legitimate"
    )

    return {
        "fraud_score": float(fraud_score),
        "fraud_decision": fraud_decision,
        "threshold": THRESHOLD
    }


if __name__ == "__main__":

    sample = {
        "Time": 406.0,
        "V1": -1.359807,
        "V2": -0.072781,
        "V3": 2.536347,
        "V4": 1.378155,
        "V5": -0.338321,
        "V6": 0.462388,
        "V7": 0.239599,
        "V8": 0.098698,
        "V9": 0.363787,
        "V10": 0.090794,
        "V11": -0.551600,
        "V12": -0.617801,
        "V13": -0.991390,
        "V14": -0.311169,
        "V15": 1.468177,
        "V16": -0.470400,
        "V17": 0.207971,
        "V18": 0.025791,
        "V19": 0.403993,
        "V20": 0.251412,
        "V21": -0.018307,
        "V22": 0.277838,
        "V23": -0.110474,
        "V24": 0.066928,
        "V25": 0.128539,
        "V26": -0.189115,
        "V27": 0.133558,
        "V28": -0.021053,
        "Amount": 149.62
    }

    result = predict_fraud(sample)

    print(result)