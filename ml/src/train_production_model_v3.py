from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report,
)

from xgboost import XGBClassifier


# --------------------------------------------------
# Paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / "production_training_data.csv"
MODEL_PATH = BASE_DIR / "models" / "production_fraud_model_v3.joblib"
METADATA_PATH = BASE_DIR / "models" / "production_model_v3_metadata.json"


# --------------------------------------------------
# Configuration
# --------------------------------------------------

RANDOM_STATE = 42

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


# --------------------------------------------------
# Load data
# --------------------------------------------------

df = pd.read_csv(DATA_PATH)

df["timestamp"] = pd.to_datetime(df["timestamp"])

# Important:
# Explicitly sort chronologically before splitting.
df = df.sort_values("timestamp").reset_index(drop=True)


print("Dataset shape:", df.shape)
print("Date range:")
print("Start:", df["timestamp"].min())
print("End:", df["timestamp"].max())


# --------------------------------------------------
# Time-based split
# --------------------------------------------------

n = len(df)

train_end = int(n * 0.70)
val_end = int(n * 0.85)

train_df = df.iloc[:train_end]
val_df = df.iloc[train_end:val_end]
test_df = df.iloc[val_end:]


print("\nTime-based split:")
print("Train:", train_df.shape)
print("Validation:", val_df.shape)
print("Test:", test_df.shape)

print("\nTime ranges:")

print(
    "Train:",
    train_df["timestamp"].min(),
    "->",
    train_df["timestamp"].max(),
)

print(
    "Validation:",
    val_df["timestamp"].min(),
    "->",
    val_df["timestamp"].max(),
)

print(
    "Test:",
    test_df["timestamp"].min(),
    "->",
    test_df["timestamp"].max(),
)


# --------------------------------------------------
# Prepare X / y
# --------------------------------------------------

X_train = train_df[FEATURES]
y_train = train_df[TARGET]

X_val = val_df[FEATURES]
y_val = val_df[TARGET]

X_test = test_df[FEATURES]
y_test = test_df[TARGET]


print("\nClass distribution:")

print("Train:")
print(y_train.value_counts())

print("\nValidation:")
print(y_val.value_counts())

print("\nTest:")
print(y_test.value_counts())


# --------------------------------------------------
# Handle class imbalance
# --------------------------------------------------

negative_count = (y_train == 0).sum()
positive_count = (y_train == 1).sum()

scale_pos_weight = negative_count / positive_count

print("\nscale_pos_weight:", scale_pos_weight)


# --------------------------------------------------
# Train XGBoost
# --------------------------------------------------

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


# --------------------------------------------------
# Validation probabilities
# --------------------------------------------------

val_probabilities = model.predict_proba(X_val)[:, 1]



# --------------------------------------------------
# Validation ranking performance
# --------------------------------------------------

val_roc_auc = roc_auc_score(
    y_val,
    val_probabilities,
)

val_pr_auc = average_precision_score(
    y_val,
    val_probabilities,
)

print("\nValidation ROC-AUC:", val_roc_auc)
print("Validation PR-AUC:", val_pr_auc)


# --------------------------------------------------
# Threshold analysis
# --------------------------------------------------

print("\nThreshold analysis:")

threshold_results = []

for threshold in np.arange(0.01, 0.51, 0.01):

    val_predictions = (
        val_probabilities >= threshold
    ).astype(int)

    precision = precision_score(
        y_val,
        val_predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_val,
        val_predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_val,
        val_predictions,
        zero_division=0,
    )

    tn, fp, fn, tp = confusion_matrix(
        y_val,
        val_predictions,
    ).ravel()

    threshold_results.append(
        {
            "threshold": round(float(threshold), 2),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
            "true_negatives": int(tn),
        }
    )


threshold_df = pd.DataFrame(threshold_results)


# --------------------------------------------------
# Show useful threshold candidates
# --------------------------------------------------

print(
    threshold_df[
        threshold_df["recall"] >= 0.70
    ].to_string(index=False)
)


# --------------------------------------------------
# Select threshold
# --------------------------------------------------

# For this experiment we first maximize F1.
# We will NOT force recall >= 0.80 if the
# validation data cannot support it.

best_row = threshold_df.loc[
    threshold_df["f1"].idxmax()
]

selected_threshold = float(
    best_row["threshold"]
)

print("\nSelected threshold:", selected_threshold)

print("\nSelected validation metrics:")

for key, value in best_row.items():
    print(f"{key}: {value}")


# --------------------------------------------------
# Final validation predictions
# --------------------------------------------------

val_predictions = (
    val_probabilities >= selected_threshold
).astype(int)

print("\nValidation confusion matrix:")

print(
    confusion_matrix(
        y_val,
        val_predictions,
    )
)


# --------------------------------------------------
# Final validation evaluation
# --------------------------------------------------

val_predictions = (
    val_probabilities >= selected_threshold
).astype(int)




# --------------------------------------------------
# Test evaluation
# --------------------------------------------------

# IMPORTANT:
# Threshold is already frozen.
# Do NOT tune using test data.

test_probabilities = model.predict_proba(X_test)[:, 1]

test_predictions = (
    test_probabilities >= selected_threshold
).astype(int)


test_precision = precision_score(
    y_test,
    test_predictions,
    zero_division=0,
)

test_recall = recall_score(
    y_test,
    test_predictions,
    zero_division=0,
)

test_f1 = f1_score(
    y_test,
    test_predictions,
    zero_division=0,
)

test_roc_auc = roc_auc_score(
    y_test,
    test_probabilities,
)

test_pr_auc = average_precision_score(
    y_test,
    test_probabilities,
)

tn, fp, fn, tp = confusion_matrix(
    y_test,
    test_predictions,
).ravel()


# --------------------------------------------------
# Test results
# --------------------------------------------------

print("\n==============================")
print("TEST RESULTS")
print("==============================")

print("Precision:", test_precision)
print("Recall:", test_recall)
print("F1:", test_f1)
print("ROC-AUC:", test_roc_auc)
print("PR-AUC:", test_pr_auc)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        y_test,
        test_predictions,
    )
)

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        test_predictions,
        digits=4,
        zero_division=0,
    )
)


# --------------------------------------------------
# Save model
# --------------------------------------------------

joblib.dump(model, MODEL_PATH)


# --------------------------------------------------
# Save metadata
# --------------------------------------------------

metadata = {
    "model_name": "Production Fraud Detection Model v3",
    "model_type": "XGBClassifier",
    "model_version": "3.0",

    "split_strategy": "time_based",
    "train_ratio": 0.70,
    "validation_ratio": 0.15,
    "test_ratio": 0.15,

    "features": FEATURES,

    "training": {
        "random_state": RANDOM_STATE,
        "n_estimators": 300,
        "max_depth": 5,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "scale_pos_weight": float(scale_pos_weight),
    },

    "threshold_selection": {
        "dataset": "validation",
        "criterion": "Maximum F1 score on validation data",
        "selected_threshold": float(selected_threshold),
    },

    "validation_metrics": {
        "threshold": float(selected_threshold),
        "precision": float(best_row["precision"]),
        "recall": float(best_row["recall"]),
        "f1": float(best_row["f1"]),
        "false_positives": int(best_row["false_positives"]),
        "false_negatives": int(best_row["false_negatives"]),
        "true_positives": int(best_row["true_positives"]),
        "true_negatives": int(best_row["true_negatives"]),
        "roc_auc": float(val_roc_auc),
        "pr_auc": float(val_pr_auc),
    },

    "test_metrics": {
        "precision": float(test_precision),
        "recall": float(test_recall),
        "f1": float(test_f1),
        "roc_auc": float(test_roc_auc),
        "pr_auc": float(test_pr_auc),
        "true_positives": int(tp),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
    },
}

with open(METADATA_PATH, "w") as f:
    json.dump(
        metadata,
        f,
        indent=2,
    )


print("\nModel saved to:")
print(MODEL_PATH)

print("\nMetadata saved to:")
print(METADATA_PATH)