from pathlib import Path
import numpy as np
import pandas as pd
import math

from ml.src.synthetic_rules import get_synthetic_rules
from ml.src.features import build_transaction_features

INPUT_PATH = Path("ml/data/production_transactions_raw.csv")
OUTPUT_PATH = Path("ml/data/production_training_data.csv")

RANDOM_STATE = 42
rng = np.random.default_rng(RANDOM_STATE)

def generate_training_data(
    input_path: Path = INPUT_PATH,
    output_path: Path = OUTPUT_PATH,
) -> pd.DataFrame:

    df = pd.read_csv(input_path)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Always process chronologically
    df = df.sort_values("timestamp").reset_index(drop=True)

    rules = get_synthetic_rules()

    feature_rows = []
    labels = []

    # Historical transactions for each account
    account_history = {}

    for _, row in df.iterrows():

        account_id = row["account_id"]

        historical = account_history.get(
            account_id,
            []
        )

        historical_df = pd.DataFrame(
            historical,
            columns=["amount", "timestamp"]
        )

        transaction = {
            "amount": row["amount"],
            "timestamp": row["timestamp"],
            "transaction_type": row["transaction_type"],
        }

        # Build features using ONLY previous transactions
        features = build_transaction_features(
            transaction,
            historical_df,
        )

        feature_rows.append(features)

        # --------------------------------------------------
        # Synthetic fraud-label generation
        # --------------------------------------------------

       


        hour = features["transaction_hour"]


        # Synthetic fraud scenario:
        #
        # 1. Very unusual amount
        # 2. High transaction velocity
        # 3. Combination of unusual amount + late night
        #
        # These are synthetic rules for demonstrating
        # the production ML pipeline.

        
        risk_score = rules["base_logit"]
        amount_ratio = features["amount_vs_avg_ratio"]

        if amount_ratio > 1:
            risk_score += (
                rules["amount_ratio_risk"]
                * math.log(amount_ratio - 1)
            )
                
        # Transaction velocity.
        velocity = features["transactions_last_24h"]

        risk_score += (
            rules["velocity_risk"]
            * min(velocity, 5)
        )

        late_night = (
            rules["late_night_start"]
            <= hour
            < rules["late_night_end"]
        )

        if late_night:
            risk_score += rules["late_night_risk"]

        # Online transactions have slightly higher synthetic risk.
        if features["is_online"] == 1:
            risk_score += rules["online_risk"]

        # Combined suspicious behavior.
        if amount_ratio >= 2 and velocity >= 2:
            risk_score += (
                rules["combined_risk"]
                * min(
                    amount_ratio / 2,
                    4,
                )
            )

        if amount_ratio >= 4 and velocity >= 4:

            risk_score += 1.0


        # Convert risk score into probability
        fraud_probability = 1 / (1 + math.exp(-risk_score))
        

        # Randomly generate the fraud label
        fraud = int(rng.random() < fraud_probability)

        labels.append(fraud)

        
        # Add current transaction to history AFTER
        # generating its features and label.
        account_history.setdefault(
            account_id,
            []
        ).append(
            {
                "amount": row["amount"],
                "timestamp": row["timestamp"],
            }
        )

    # --------------------------------------------------
    # Combine features and labels
    # --------------------------------------------------

    features_df = pd.DataFrame(feature_rows)

    features_df["Class"] = labels

    # Keep timestamp/account_id for auditing and
    # chronological splitting, but they are not ML features.
    features_df["account_id"] = df["account_id"].values
    features_df["timestamp"] = df["timestamp"].values

    # Preserve a useful column order
    columns = [
        "account_id",
        "timestamp",
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
        "Class",
    ]

    features_df = features_df[columns]

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    features_df.to_csv(
        output_path,
        index=False,
    )

    return features_df


if __name__ == "__main__":

    training_df = generate_training_data()

    print(
        f"Generated {len(training_df)} training rows"
    )

    print("\nShape:")
    print(training_df.shape)

    print("\nClass distribution:")
    print(training_df["Class"].value_counts())

    print("\nFraud rate:")
    print(training_df["Class"].mean())

    print("\nSample:")
    print(training_df.head())

    print(
        f"\nSaved to: {OUTPUT_PATH}"
    )