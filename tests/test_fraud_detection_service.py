from app.services.fraud_detection_service import FraudDetectionService
from ml.src.predict import FEATURES


def test_fraud_detection_service():

    features = {
        feature: 0.0
        for feature in FEATURES
    }

    result = FraudDetectionService.predict(features)

    assert "fraud_score" in result
    assert "fraud_decision" in result
    assert "threshold" in result