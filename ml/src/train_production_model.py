from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
)

from xgboost import XGBClassifier


RANDOM_STATE = 42
SELECTED_THRESHOLD = 0.11

DATA_PATH = Path("ml/data/production_training_data.csv")
MODEL_PATH = Path("ml/models/production_fraud_model.joblib")
METADATA_PATH = Path("ml/models/production_model_metadata.json")

FEATURES = [
    "amount",
    "transaction_hour",
    "transaction_day_of_week",
    "is_weekend",
    "is_online",
    "account_transaction_count",
    "account_avg_amount",
    "account_max_amount",
    "amount_vs_avg_ratio",
    "transactions_last_24h",
]

TARGET = "Class"


def calculate_metrics(y_true, probabilities, threshold):
    """Calculate classification metrics at a fixed threshold."""

    predictions = (
        probabilities >= threshold
    ).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predictions,
    ).ravel()

    return {
        "precision": float(
            precision_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "recall": float(
            recall_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "f1": float(
            f1_score(
                y_true,
                predictions,
                zero_division=0,
            )
        ),
        "roc_auc": float(
            roc_auc_score(
                y_true,
                probabilities,
            )
        ),
        "pr_auc": float(
            average_precision_score(
                y_true,
                probabilities,
            )
        ),
        "true_positives": int(tp),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
    }


def main():

    # ---------------------------------------------------------
    # Load dataset
    # ---------------------------------------------------------

    df = pd.read_csv(DATA_PATH)

    X = df[FEATURES]
    y = df[TARGET]

    print("Dataset shape:", df.shape)

    print("\nClass distribution:")
    print(y.value_counts())

    # ---------------------------------------------------------
    # Train / validation / test split
    # ---------------------------------------------------------

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        stratify=y,
        random_state=RANDOM_STATE,
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        stratify=y_temp,
        random_state=RANDOM_STATE,
    )

    print("\nSplit sizes:")
    print("Train:", X_train.shape)
    print("Validation:", X_val.shape)
    print("Test:", X_test.shape)

    # ---------------------------------------------------------
    # Class imbalance
    # ---------------------------------------------------------

    negative_count = (y_train == 0).sum()
    positive_count = (y_train == 1).sum()

    scale_pos_weight = (
        negative_count / positive_count
    )

    print(
        "\nScale pos weight:",
        scale_pos_weight,
    )

    # ---------------------------------------------------------
    # Train XGBoost
    # ---------------------------------------------------------

    model = XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        objective="binary:logistic",
        eval_metric="aucpr",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    model.fit(
        X_train,
        y_train,
    )

    # ---------------------------------------------------------
    # Validation evaluation
    # ---------------------------------------------------------

    val_probabilities = (
        model.predict_proba(X_val)[:, 1]
    )

    val_metrics = calculate_metrics(
        y_val,
        val_probabilities,
        SELECTED_THRESHOLD,
    )

    print("\nValidation metrics")
    print("------------------")

    for key, value in val_metrics.items():
        print(f"{key}: {value}")

    # ---------------------------------------------------------
    # IMPORTANT:
    # Threshold 0.11 was selected using validation data.
    # We now freeze it and DO NOT tune it using test data.
    # ---------------------------------------------------------

    test_probabilities = (
        model.predict_proba(X_test)[:, 1]
    )

    test_metrics = calculate_metrics(
        y_test,
        test_probabilities,
        SELECTED_THRESHOLD,
    )

    test_predictions = (
        test_probabilities >= SELECTED_THRESHOLD
    ).astype(int)

    print("\nTest metrics")
    print("------------")

    for key, value in test_metrics.items():
        print(f"{key}: {value}")

    print("\nTest classification report:")
    print(
        classification_report(
            y_test,
            test_predictions,
            digits=4,
        )
    )

    print("\nTest confusion matrix:")
    print(
        confusion_matrix(
            y_test,
            test_predictions,
        )
    )

    # ---------------------------------------------------------
    # Save model
    # ---------------------------------------------------------

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    # ---------------------------------------------------------
    # Save metadata
    # ---------------------------------------------------------

    metadata = {
        "model_name": "Production Fraud Detection Model",
        "model_type": "XGBClassifier",
        "model_version": "2.0",
        "data_type": "synthetic_demonstration_data",
        "random_state": RANDOM_STATE,
        "features": FEATURES,
        "threshold": SELECTED_THRESHOLD,
        "training": {
            "n_estimators": 300,
            "max_depth": 5,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "scale_pos_weight": float(
                scale_pos_weight
            ),
        },
        "threshold_selection": {
            "dataset": "validation",
            "criterion": (
                "Recall >= 0.80 while "
                "minimizing false positives"
            ),
            "selected_threshold": SELECTED_THRESHOLD,
        },
        "validation_metrics": val_metrics,
        "test_metrics": test_metrics,
    }

    with open(
        METADATA_PATH,
        "w",
    ) as f:
        import json

        json.dump(
            metadata,
            f,
            indent=2,
        )

    print(
        f"\nModel saved to: {MODEL_PATH}"
    )

    print(
        f"Metadata saved to: {METADATA_PATH}"
    )


if __name__ == "__main__":
    main()