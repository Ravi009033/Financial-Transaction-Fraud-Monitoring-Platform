import pandas as pd

from ml.src.features import (
    build_transaction_features,
    get_feature_names,
)


def test_feature_names():
    features = get_feature_names()

    assert len(features) == 10
    assert "amount" in features
    assert "amount_vs_avg_ratio" in features
    assert "transactions_last_24h" in features


def test_feature_engineering_with_history():

    historical = pd.DataFrame([
        {
            "amount": 500,
            "timestamp": "2026-09-19 10:00:00",
        },
        {
            "amount": 700,
            "timestamp": "2026-09-19 15:00:00",
        },
        {
            "amount": 300,
            "timestamp": "2026-09-20 08:00:00",
        },
    ])

    transaction = {
        "amount": 5000,
        "timestamp": "2026-09-20 10:00:00",
        "transaction_type": "online",
    }

    features = build_transaction_features(
        transaction,
        historical,
    )

    assert features["amount"] == 5000.0
    assert features["transaction_hour"] == 10
    assert features["is_online"] == 1
    assert features["is_weekend"] == 1

    assert features["account_transaction_count"] == 3
    assert features["account_avg_amount"] == 500.0
    assert features["account_max_amount"] == 700.0
    assert features["amount_vs_avg_ratio"] == 10.0


def test_future_transactions_are_excluded():

    historical = pd.DataFrame([
        {
            "amount": 500,
            "timestamp": "2026-09-20 09:00:00",
        },
        {
            "amount": 10000,
            "timestamp": "2026-09-20 12:00:00",
        },
    ])

    transaction = {
        "amount": 1000,
        "timestamp": "2026-09-20 10:00:00",
        "transaction_type": "offline",
    }

    features = build_transaction_features(
        transaction,
        historical,
    )

    # Only the 09:00 transaction is available
    # when predicting the 10:00 transaction.

    assert features["account_transaction_count"] == 1
    assert features["account_avg_amount"] == 500.0
    assert features["account_max_amount"] == 500.0


def test_empty_history():

    historical = pd.DataFrame(
        columns=["amount", "timestamp"]
    )

    transaction = {
        "amount": 1000,
        "timestamp": "2026-09-20 10:00:00",
        "transaction_type": "online",
    }

    features = build_transaction_features(
        transaction,
        historical,
    )

    assert features["account_transaction_count"] == 0
    assert features["account_avg_amount"] == 0.0
    assert features["account_max_amount"] == 0.0
    assert features["transactions_last_24h"] == 0
    assert features["amount_vs_avg_ratio"] == 0.0


def test_offline_transaction():

    historical = pd.DataFrame(
        columns=["amount", "timestamp"]
    )

    transaction = {
        "amount": 500,
        "timestamp": "2026-09-20 10:00:00",
        "transaction_type": "offline",
    }

    features = build_transaction_features(
        transaction,
        historical,
    )

    assert features["is_online"] == 0


def test_transactions_last_24_hours():

    historical = pd.DataFrame([
        {
            "amount": 100,
            "timestamp": "2026-09-19 09:00:00",
        },
        {
            "amount": 200,
            "timestamp": "2026-09-19 11:00:00",
        },
        {
            "amount": 300,
            "timestamp": "2026-09-20 09:30:00",
        },
        {
            "amount": 400,
            "timestamp": "2026-09-20 10:30:00",
        },
    ])

    transaction = {
        "amount": 500,
        "timestamp": "2026-09-20 11:00:00",
        "transaction_type": "online",
    }

    features = build_transaction_features(
        transaction,
        historical,
    )

    # Transactions from 2026-09-19 11:00 onward
    # fall within the previous 24 hours.
    assert features["transactions_last_24h"] == 3