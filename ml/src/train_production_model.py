from pathlib import Path

import joblib
import pandas as pd
import numpy as np

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

DATA_PATH = Path("ml/data/production_training_data.csv")

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


def main():

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

    scale_pos_weight = negative_count / positive_count

    print("\nScale pos weight:", scale_pos_weight)

    # ---------------------------------------------------------
    # XGBoost
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
    # Validation
    # ---------------------------------------------------------

    val_probabilities = model.predict_proba(X_val)[:, 1]

    # ---------------------------------------------------------
    # Threshold tuning on validation set
    # Goal:
    #   Recall >= 0.80
    #   Minimize false positives
    # ---------------------------------------------------------


    threshold_results = []

    for threshold in np.arange(0.10, 0.51, 0.01):

        y_pred = (
            val_probabilities >= threshold
        ).astype(int)

        tn, fp, fn, tp = confusion_matrix(
            y_val,
            y_pred,
        ).ravel()

        precision = precision_score(
            y_val,
            y_pred,
            zero_division=0,
        )

        recall = recall_score(
            y_val,
            y_pred,
            zero_division=0,
        )

        f1 = f1_score(
            y_val,
            y_pred,
            zero_division=0,
        )

        threshold_results.append(
            {
                "threshold": round(float(threshold), 2),
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "false_positives": fp,
                "false_negatives": fn,
                "true_positives": tp,
                "true_negatives": tn,
            }
        )


    threshold_df = pd.DataFrame(threshold_results)


    # Only consider thresholds satisfying recall >= 80%
    eligible = threshold_df[
        threshold_df["recall"] >= 0.80
    ]


    if eligible.empty:
        print(
            "\nNo threshold achieved recall >= 0.80"
        )

    else:

        # Minimize false positives.
        # If tied, prefer higher F1.
        best_threshold = eligible.sort_values(
            by=[
                "false_positives",
                "f1",
            ],
            ascending=[
                True,
                False,
            ],
        ).iloc[0]

        print("\nThreshold tuning results:")
        print(
            threshold_df[
                [
                    "threshold",
                    "precision",
                    "recall",
                    "f1",
                    "false_positives",
                    "false_negatives",
                ]
            ].to_string(index=False)
        )

        print("\nSelected threshold:")
        print(best_threshold)

        threshold = 0.5

        y_val_pred = (
            val_probabilities >= threshold
        ).astype(int)

        print("\nValidation metrics:")
        print(
            classification_report(
                y_val,
                y_val_pred,
                digits=4,
            )
        )

        print("Confusion matrix:")
        print(
            confusion_matrix(
                y_val,
                y_val_pred,
            )
        )

        print(
            "Precision:",
            precision_score(
                y_val,
                y_val_pred,
                zero_division=0,
            ),
        )

        print(
            "Recall:",
            recall_score(
                y_val,
                y_val_pred,
                zero_division=0,
            ),
        )

        print(
            "F1:",
            f1_score(
                y_val,
                y_val_pred,
                zero_division=0,
            ),
        )

        print(
            "ROC-AUC:",
            roc_auc_score(
                y_val,
                val_probabilities,
            ),
        )

        print(
            "PR-AUC:",
            average_precision_score(
                y_val,
                val_probabilities,
            ),
        )


if __name__ == "__main__":
    main()