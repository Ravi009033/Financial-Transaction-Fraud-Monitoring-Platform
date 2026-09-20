from decimal import Decimal
import pandas as pd

from ml.src.features import build_transaction_features
from ml.src.production_predict import predict_production_fraud


class FraudDetectionService:

    def evaluate_transaction(
        self,
        amount: Decimal,
        transaction_type: str,
        timestamp,
        historical_transactions: list,
    ):
        # Convert SQLAlchemy transactions into the
        # historical format required by the feature builder.

        history_rows = [
            {
                "amount": transaction.amount,
                "timestamp": transaction.timestamp,
            }
            for transaction in historical_transactions
        ]

        historical_df = pd.DataFrame(
            history_rows,
            columns=["amount", "timestamp"],
        )

        transaction = {
            "amount": amount,
            "timestamp": timestamp,
            "transaction_type": transaction_type,
        }

        # Build features using only historical data.
        features = build_transaction_features(
            transaction,
            historical_df,
        )

        # Run production ML model.
        prediction = predict_production_fraud(
            features
        )

        fraud_score = Decimal(
            str(prediction["fraud_score"])
        )

        fraud_decision = self.make_decision(
            fraud_score
        )

        return {
            "fraud_score": fraud_score,
            "fraud_decision": fraud_decision,
        }

    def make_decision(
        self,
        score: Decimal
    ) -> str:

        if score >= Decimal("0.70"):
            return "blocked"

        elif score >= Decimal("0.33"):
            return "review"

        return "approved"