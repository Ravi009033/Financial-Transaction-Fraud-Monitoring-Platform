def test_get_real_fraud_model_metrics(client):
    response = client.get("/ml/metrics")

    assert response.status_code == 200

    data = response.json()

    assert "validation_metrics" in data
    assert "test_metrics" in data


def test_validation_metrics(client):
    response = client.get("/ml/metrics")

    assert response.status_code == 200

    metrics = response.json()["validation_metrics"]

    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert "roc_auc" in metrics
    assert "pr_auc" in metrics


def test_test_metrics(client):
    response = client.get("/ml/metrics")

    assert response.status_code == 200

    metrics = response.json()["test_metrics"]

    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
    assert "roc_auc" in metrics
    assert "pr_auc" in metrics


def test_metrics_values_are_valid(client):
    response = client.get("/ml/metrics")

    assert response.status_code == 200

    data = response.json()

    for metrics in [
        data["validation_metrics"],
        data["test_metrics"],
    ]:
        assert 0 <= metrics["precision"] <= 1
        assert 0 <= metrics["recall"] <= 1
        assert 0 <= metrics["f1"] <= 1
        assert 0 <= metrics["roc_auc"] <= 1
        assert 0 <= metrics["pr_auc"] <= 1