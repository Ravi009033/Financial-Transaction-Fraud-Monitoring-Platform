import pytest

from ml.src.real_predict import (
    predict_real_fraud,
    FEATURES,
    THRESHOLD,
    MODEL_NAME,
    MODEL_VERSION,
)


def get_valid_features():
    return {
        feature: 0.0
        for feature in FEATURES
    }


def test_real_prediction_returns_required_fields():

    features = get_valid_features()

    result = predict_real_fraud(features)

    assert "fraud_score" in result
    assert "fraud_decision" in result
    assert "threshold" in result
    assert "model_name" in result
    assert "model_version" in result


def test_real_prediction_score_is_valid():

    features = get_valid_features()

    result = predict_real_fraud(features)

    assert 0.0 <= result["fraud_score"] <= 1.0


def test_real_prediction_uses_expected_threshold():

    features = get_valid_features()

    result = predict_real_fraud(features)

    assert result["threshold"] == THRESHOLD


def test_real_prediction_model_metadata():

    features = get_valid_features()

    result = predict_real_fraud(features)

    assert result["model_name"] == MODEL_NAME
    assert result["model_version"] == MODEL_VERSION


def test_real_prediction_missing_feature():

    features = get_valid_features()

    features.pop("V14")

    with pytest.raises(
        ValueError,
        match="Missing features",
    ):
        predict_real_fraud(features)