import pytest

from ml.src.predict import predict_fraud, FEATURES, THRESHOLD


def get_valid_features():
    return {
        feature: 0.0
        for feature in FEATURES
    }


def test_prediction_returns_required_fields():

    features = get_valid_features()

    result = predict_fraud(features)

    assert "fraud_score" in result
    assert "fraud_decision" in result
    assert "threshold" in result


def test_prediction_score_is_valid():

    features = get_valid_features()

    result = predict_fraud(features)

    assert 0.0 <= result["fraud_score"] <= 1.0


def test_prediction_uses_expected_threshold():

    features = get_valid_features()

    result = predict_fraud(features)

    assert result["threshold"] == THRESHOLD


def test_missing_feature_raises_error():

    features = get_valid_features()

    features.pop("V14")

    with pytest.raises(ValueError, match="Missing features"):
        predict_fraud(features)