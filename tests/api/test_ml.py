def get_valid_features():
    return {
        "Time": 0.0,
        "V1": 0.0,
        "V2": 0.0,
        "V3": 0.0,
        "V4": 0.0,
        "V5": 0.0,
        "V6": 0.0,
        "V7": 0.0,
        "V8": 0.0,
        "V9": 0.0,
        "V10": 0.0,
        "V11": 0.0,
        "V12": 0.0,
        "V13": 0.0,
        "V14": 0.0,
        "V15": 0.0,
        "V16": 0.0,
        "V17": 0.0,
        "V18": 0.0,
        "V19": 0.0,
        "V20": 0.0,
        "V21": 0.0,
        "V22": 0.0,
        "V23": 0.0,
        "V24": 0.0,
        "V25": 0.0,
        "V26": 0.0,
        "V27": 0.0,
        "V28": 0.0,
        "Amount": 100.0,
    }


def test_real_ml_prediction(client):

    response = client.post(
        "/ml/predict",
        json=get_valid_features(),
    )

    assert response.status_code == 200

    data = response.json()

    assert 0.0 <= data["fraud_score"] <= 1.0

    assert data["fraud_decision"] in {
        "fraud",
        "legitimate",
    }

    assert data["model_name"]
    assert data["model_version"]

    assert 0.0 < data["threshold"] < 1.0


def test_real_ml_prediction_invalid_amount(client):

    features = get_valid_features()
    features["Amount"] = -1

    response = client.post(
        "/ml/predict",
        json=features,
    )

    assert response.status_code == 422


def test_real_ml_prediction_missing_feature(client):

    features = get_valid_features()
    features.pop("V14")

    response = client.post(
        "/ml/predict",
        json=features,
    )

    assert response.status_code == 422