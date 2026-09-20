from datetime import datetime, timezone
from decimal import Decimal

from app.services.fraud_service import FraudDetectionService


def test_fraud_detection_service():

    service = FraudDetectionService()

    result = service.evaluate_transaction(
        amount=Decimal("500.00"),
        transaction_type="online",
        timestamp=datetime.now(timezone.utc),
        historical_transactions=[],
    )

    assert "fraud_score" in result
    assert "fraud_decision" in result

    assert isinstance(
        result["fraud_score"],
        Decimal
    )

    assert Decimal("0") <= result["fraud_score"] <= Decimal("1")

    assert result["fraud_decision"] in {
        "approved",
        "review",
        "blocked",
    }