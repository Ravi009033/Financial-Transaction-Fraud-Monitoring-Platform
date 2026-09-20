from decimal import Decimal
from datetime import datetime, timezone
from app.services.fraud_service import FraudDetectionService

def test_low_value_transaction():
    service = FraudDetectionService()

    result = service.evaluate_transaction(
        amount=Decimal("1000"),
        transaction_type="offline",
        timestamp=datetime.now(timezone.utc),
        historical_transactions=[],
    )

    assert "fraud_score" in result
    assert "fraud_decision" in result
    assert isinstance(result["fraud_score"], Decimal)
    assert Decimal("0") <= result["fraud_score"] <= Decimal("1")
    assert result["fraud_decision"] in {
        "approved",
        "review",
        "blocked",
    }

def test_medium_value_online_transaction():
    service = FraudDetectionService()
    
    result = service.evaluate_transaction(
        amount=Decimal("60000"),
        transaction_type="offline",
        timestamp=datetime.now(timezone.utc),
        historical_transactions=[],
    )

    assert "fraud_score" in result
    assert "fraud_decision" in result
    assert isinstance(result["fraud_score"], Decimal)
    assert Decimal("0") <= result["fraud_score"] <= Decimal("1")
    assert result["fraud_decision"] in {
        "approved",
        "review",
        "blocked",
    }

def test_high_value_online_transaction():
    service = FraudDetectionService()
    
    result = service.evaluate_transaction(
        amount=Decimal("10000"),
        transaction_type="online",
        timestamp=datetime.now(timezone.utc),
        historical_transactions=[],
    )

    assert "fraud_score" in result
    assert "fraud_decision" in result
    assert isinstance(result["fraud_score"], Decimal)
    assert Decimal("0") <= result["fraud_score"] <= Decimal("1")
    assert result["fraud_decision"] in {
        "approved",
        "review",
        "blocked",
    }

def test_make_decision_approved():
    service = FraudDetectionService()

    assert service.make_decision(Decimal("0.20")) == "approved"


def test_make_decision_review():
    service = FraudDetectionService()

    assert service.make_decision(Decimal("0.50")) == "review"


def test_make_decision_blocked():
    service = FraudDetectionService()

    assert service.make_decision(Decimal("0.80")) == "blocked"