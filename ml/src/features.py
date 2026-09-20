import pandas as pd


PRODUCTION_FEATURES = [
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


def get_feature_names() -> list[str]:
    return PRODUCTION_FEATURES.copy()


def build_transaction_features(
    transaction: dict,
    historical_transactions: pd.DataFrame,
) -> dict:
    """
    Build ML features for a transaction using only
    historical transactions that occurred before it.
    """

    amount = float(transaction["amount"])
    timestamp = pd.Timestamp(transaction["timestamp"])

    # --------------------------------------------------
    # Basic transaction features
    # --------------------------------------------------

    transaction_hour = timestamp.hour
    transaction_day_of_week = timestamp.dayofweek
    is_weekend = int(transaction_day_of_week >= 5)

    is_online = int(
        transaction["transaction_type"].lower() == "online"
    )

    # --------------------------------------------------
    # Historical transactions
    # --------------------------------------------------

    if historical_transactions.empty:
        account_transaction_count = 0
        account_avg_amount = 0.0
        account_max_amount = 0.0
        transactions_last_24h = 0

    else:
        historical = historical_transactions.copy()

        historical["timestamp"] = pd.to_datetime(
            historical["timestamp"]
        )

        # Only transactions BEFORE current transaction
        historical = historical[
            historical["timestamp"] < timestamp
        ]

        if historical.empty:
            account_transaction_count = 0
            account_avg_amount = 0.0
            account_max_amount = 0.0
            transactions_last_24h = 0

        else:
            account_transaction_count = len(historical)

            account_avg_amount = float(
                historical["amount"].mean()
            )

            account_max_amount = float(
                historical["amount"].max()
            )

            last_24h = timestamp - pd.Timedelta(hours=24)

            transactions_last_24h = int(
                (
                    historical["timestamp"] >= last_24h
                ).sum()
            )

    # --------------------------------------------------
    # Derived feature
    # --------------------------------------------------

    if account_avg_amount > 0:
        amount_vs_avg_ratio = (
            amount / account_avg_amount
        )
    else:
        amount_vs_avg_ratio = 0.0

    # --------------------------------------------------
    # Final feature vector
    # --------------------------------------------------

    features = {
        "amount": amount,
        "transaction_hour": transaction_hour,
        "transaction_day_of_week": transaction_day_of_week,
        "is_weekend": is_weekend,
        "is_online": is_online,
        "account_transaction_count": account_transaction_count,
        "account_avg_amount": account_avg_amount,
        "account_max_amount": account_max_amount,
        "amount_vs_avg_ratio": amount_vs_avg_ratio,
        "transactions_last_24h": transactions_last_24h,
    }

    return features