def test_get_real_fraud_model_info(client):
    response = client.get("/ml/model-info")

    assert response.status_code == 200

    data = response.json()

    assert "model_name" in data
    assert "model_type" in data
    assert "model_version" in data
    assert "threshold" in data
    assert "features" in data
    assert "training" in data
    assert "validation_metrics" in data
    assert "test_metrics" in data
    assert "threshold_selection" in data


def test_real_fraud_model_info_features(client):
    response = client.get("/ml/model-info")

    assert response.status_code == 200

    features = response.json()["features"]

    assert len(features) == 30
    assert features[0] == "Time"
    assert features[-1] == "Amount"
    assert "V14" in features


def test_real_fraud_model_info_threshold(client):
    response = client.get("/ml/model-info")

    assert response.status_code == 200

    data = response.json()

    assert data["threshold"] == 0.33


def test_real_fraud_model_info_metrics(client):
    response = client.get("/ml/model-info")

    assert response.status_code == 200

    data = response.json()

    validation = data["validation_metrics"]
    test = data["test_metrics"]

    assert "precision" in validation
    assert "recall" in validation
    assert "f1" in validation

    assert "precision" in test
    assert "recall" in test
    assert "f1" in test
    assert "roc_auc" in test
    assert "pr_auc" in test