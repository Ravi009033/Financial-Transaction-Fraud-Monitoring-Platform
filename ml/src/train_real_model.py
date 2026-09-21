from pathlib import Path
import json

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from sklearn.metrics import (
    average_precision_score,
    classification_report,
    confusion_matrix,
    precision_recall_curve,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "creditcard.csv"

MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "real_fraud_model.joblib"
METADATA_PATH = MODEL_DIR / "real_model_metadata.json"

ROC_CURVE_PATH = MODEL_DIR / "real_roc_curve.png"
PR_CURVE_PATH = MODEL_DIR / "real_pr_curve.png"
CONFUSION_MATRIX_PATH = MODEL_DIR / "real_confusion_matrix.png"
SHAP_SUMMARY_PATH = MODEL_DIR / "real_shap_summary.png"


RANDOM_STATE = 42


# ============================================================
# Load and clean data
# ============================================================

def load_data():
    print("Loading dataset...")

    df = pd.read_csv(DATA_PATH)

    print(f"Original shape: {df.shape}")

    duplicate_count = df.duplicated().sum()

    print(f"Exact duplicate rows: {duplicate_count}")

    df = df.drop_duplicates().copy()

    print(f"Shape after removing duplicates: {df.shape}")

    print("\nClass distribution:")
    print(df["Class"].value_counts())

    print("\nFraud rate:")
    print(df["Class"].mean())

    return df


# ============================================================
# Split data
# ============================================================

def prepare_data(df):

    X = df.drop(columns=["Class"])
    y = df["Class"]

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

    print("\nDataset split:")

    print(f"Train: {X_train.shape}")
    print(f"Validation: {X_val.shape}")
    print(f"Test: {X_test.shape}")

    print("\nFraud counts:")

    print(
        f"Train fraud: {y_train.sum()} / {len(y_train)}"
    )

    print(
        f"Validation fraud: {y_val.sum()} / {len(y_val)}"
    )

    print(
        f"Test fraud: {y_test.sum()} / {len(y_test)}"
    )

    return (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
    )


# ============================================================
# Train XGBoost
# ============================================================

def train_model(X_train, y_train):

    negative_count = (y_train == 0).sum()
    positive_count = (y_train == 1).sum()

    scale_pos_weight = negative_count / positive_count

    print(
        f"\nscale_pos_weight: {scale_pos_weight:.4f}"
    )

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

    print("\nTraining XGBoost...")

    model.fit(X_train, y_train)

    return model, scale_pos_weight


# ============================================================
# Threshold selection
# ============================================================

def select_threshold(model, X_val, y_val):

    probabilities = model.predict_proba(X_val)[:, 1]

    best_threshold = None
    best_f1 = -1

    threshold_results = []

    for threshold in np.arange(
        0.01,
        0.51,
        0.01,
    ):

        predictions = (
            probabilities >= threshold
        ).astype(int)

        precision = precision_score(
            y_val,
            predictions,
            zero_division=0,
        )

        recall = recall_score(
            y_val,
            predictions,
            zero_division=0,
        )

        f1 = f1_score(
            y_val,
            predictions,
            zero_division=0,
        )

        threshold_results.append(
            {
                "threshold": float(threshold),
                "precision": float(precision),
                "recall": float(recall),
                "f1": float(f1),
            }
        )

        # Preserve our previous model-selection criterion:
        # recall >= 0.80, then minimize false positives.
        if recall >= 0.80:

            tn, fp, fn, tp = confusion_matrix(
                y_val,
                predictions,
            ).ravel()

            if (
                best_threshold is None
                or fp < best_threshold["false_positives"]
                or (
                    fp == best_threshold["false_positives"]
                    and f1 > best_threshold["f1"]
                )
            ):
                best_threshold = {
                    "threshold": float(threshold),
                    "precision": float(precision),
                    "recall": float(recall),
                    "f1": float(f1),
                    "false_positives": int(fp),
                    "false_negatives": int(fn),
                    "true_positives": int(tp),
                    "true_negatives": int(tn),
                }

    if best_threshold is None:
        raise RuntimeError(
            "No threshold satisfied recall >= 0.80"
        )

    print("\nSelected threshold:")
    print(best_threshold)

    return best_threshold, threshold_results


# ============================================================
# Evaluate model
# ============================================================

def evaluate_model(
    model,
    X,
    y,
    threshold,
    dataset_name,
):

    probabilities = model.predict_proba(X)[:, 1]

    predictions = (
        probabilities >= threshold
    ).astype(int)

    precision = precision_score(
        y,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        y,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y,
        predictions,
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y,
        probabilities,
    )

    pr_auc = average_precision_score(
        y,
        probabilities,
    )

    tn, fp, fn, tp = confusion_matrix(
        y,
        predictions,
    ).ravel()

    print(f"\n{dataset_name} metrics")

    print(f"Precision: {precision:.4f}")
    print(f"Recall:    {recall:.4f}")
    print(f"F1:        {f1:.4f}")
    print(f"ROC-AUC:   {roc_auc:.4f}")
    print(f"PR-AUC:    {pr_auc:.4f}")

    print("\nConfusion matrix:")
    print(
        np.array(
            [
                [tn, fp],
                [fn, tp],
            ]
        )
    )

    return {
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "true_positives": int(tp),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
    }


# ============================================================
# ROC curve
# ============================================================

def save_roc_curve(model, X_test, y_test):

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    fpr, tpr, _ = roc_curve(
        y_test,
        probabilities,
    )

    auc = roc_auc_score(
        y_test,
        probabilities,
    )

    plt.figure(figsize=(8, 6))

    plt.plot(
        fpr,
        tpr,
        label=f"XGBoost (AUC = {auc:.3f})",
    )

    plt.plot(
        [0, 1],
        [0, 1],
        linestyle="--",
    )

    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Real Credit Card Fraud - ROC Curve")
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        ROC_CURVE_PATH,
        dpi=150,
    )

    plt.close()


# ============================================================
# Precision-Recall curve
# ============================================================

def save_pr_curve(model, X_test, y_test):

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    precision, recall, _ = precision_recall_curve(
        y_test,
        probabilities,
    )

    pr_auc = average_precision_score(
        y_test,
        probabilities,
    )

    plt.figure(figsize=(8, 6))

    plt.plot(
        recall,
        precision,
        label=f"XGBoost (PR-AUC = {pr_auc:.3f})",
    )

    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title(
        "Real Credit Card Fraud - Precision-Recall Curve"
    )

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        PR_CURVE_PATH,
        dpi=150,
    )

    plt.close()


# ============================================================
# Confusion matrix
# ============================================================

def save_confusion_matrix(
    model,
    X_test,
    y_test,
    threshold,
):

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    predictions = (
        probabilities >= threshold
    ).astype(int)

    matrix = confusion_matrix(
        y_test,
        predictions,
    )

    plt.figure(figsize=(6, 5))

    plt.imshow(matrix)

    plt.title(
        "Real Credit Card Fraud - Confusion Matrix"
    )

    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    plt.xticks(
        [0, 1],
        ["Legitimate", "Fraud"],
    )

    plt.yticks(
        [0, 1],
        ["Legitimate", "Fraud"],
    )

    for i in range(2):
        for j in range(2):
            plt.text(
                j,
                i,
                matrix[i, j],
                ha="center",
                va="center",
            )

    plt.colorbar()
    plt.tight_layout()

    plt.savefig(
        CONFUSION_MATRIX_PATH,
        dpi=150,
    )

    plt.close()


# ============================================================
# SHAP
# ============================================================

def save_shap_summary(
    model,
    X_test,
):

    print("\nGenerating SHAP explanation...")

    # Use a sample so the explanation remains manageable.
    sample_size = min(
        2000,
        len(X_test),
    )

    X_sample = X_test.sample(
        n=sample_size,
        random_state=RANDOM_STATE,
    )

    explainer = shap.TreeExplainer(model)

    shap_values = explainer.shap_values(
        X_sample
    )

    plt.figure(figsize=(10, 8))

    shap.summary_plot(
        shap_values,
        X_sample,
        show=False,
    )

    plt.tight_layout()

    plt.savefig(
        SHAP_SUMMARY_PATH,
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()


# ============================================================
# Main
# ============================================================

def main():

    df = load_data()

    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
    ) = prepare_data(df)

    model, scale_pos_weight = train_model(
        X_train,
        y_train,
    )

    (
        threshold_info,
        threshold_results,
    ) = select_threshold(
        model,
        X_val,
        y_val,
    )

    threshold = threshold_info[
        "threshold"
    ]

    validation_metrics = evaluate_model(
        model,
        X_val,
        y_val,
        threshold,
        "Validation",
    )

    test_metrics = evaluate_model(
        model,
        X_test,
        y_test,
        threshold,
        "Test",
    )

    save_roc_curve(
        model,
        X_test,
        y_test,
    )

    save_pr_curve(
        model,
        X_test,
        y_test,
    )

    save_confusion_matrix(
        model,
        X_test,
        y_test,
        threshold,
    )

    save_shap_summary(
        model,
        X_test,
    )

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    joblib.dump(
        model,
        MODEL_PATH,
    )

    # --------------------------------------------------------
    # Save metadata
    # --------------------------------------------------------

    metadata = {
        "model_name": "Real Credit Card Fraud XGBoost Model",
        "model_type": "XGBClassifier",
        "model_version": "1.0",
        "dataset": {
            "name": "Credit Card Fraud Detection",
            "source": "Kaggle",
            "rows_after_deduplication": int(len(df)),
            "features": list(X_train.columns),
            "target": "Class",
        },
        "training": {
            "random_state": RANDOM_STATE,
            "n_estimators": 300,
            "max_depth": 5,
            "learning_rate": 0.05,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "scale_pos_weight": float(
                scale_pos_weight
            ),
        },
        "split": {
            "train_size": int(len(X_train)),
            "validation_size": int(len(X_val)),
            "test_size": int(len(X_test)),
        },
        "threshold_selection": {
            "criterion": (
                "Recall >= 0.80 while minimizing "
                "validation false positives"
            ),
            "selected_threshold": threshold,
            "validation_result": threshold_info,
        },
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
        "artifacts": {
            "roc_curve": ROC_CURVE_PATH.name,
            "pr_curve": PR_CURVE_PATH.name,
            "confusion_matrix": CONFUSION_MATRIX_PATH.name,
            "shap_summary": SHAP_SUMMARY_PATH.name,
        },
    }

    with open(
        METADATA_PATH,
        "w",
    ) as f:
        json.dump(
            metadata,
            f,
            indent=2,
        )

    print("\nModel saved:")
    print(MODEL_PATH)

    print("\nMetadata saved:")
    print(METADATA_PATH)

    print("\nTraining completed successfully.")


if __name__ == "__main__":
    main()