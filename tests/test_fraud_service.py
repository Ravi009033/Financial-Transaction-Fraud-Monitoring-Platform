from decimal import Decimal

from app.services.fraud_service import FraudDetectionService

def test_low_value_transaction():
    service = FraudDetectionService()

    result = service.evaluate_transaction(
        Decimal("10000"),
        "offline"
    )

    assert result["fraud_score"] == Decimal("0.0")
    assert result["fraud_decision"] == "approved"

def test_medium_value_online_transaction():
    service = FraudDetectionService()

    result = service.evaluate_transaction(
        Decimal("60000"),
        "online"
    )

    assert result["fraud_score"] == Decimal("0.5")
    assert result["fraud_decision"] == "review"

def test_high_value_online_transaction():
    service = FraudDetectionService()

    result = service.evaluate_transaction(
        Decimal("100000"),
        "online"
    )

    assert result["fraud_score"] == Decimal("0.7")
    assert result["fraud_decision"] == "blocked"