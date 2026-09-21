def test_fraud_distribution_requires_auth(client):
    response = client.get(
        "/dashboard/fraud-distribution"
    )

    assert response.status_code == 401


def test_fraud_distribution_empty(auth_client):
    response = auth_client.get(
        "/dashboard/fraud-distribution"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["data"] == []


def test_fraud_distribution_with_transaction(
    auth_client,
    test_transaction,
):
    response = auth_client.get(
        "/dashboard/fraud-distribution"
    )

    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert len(data["data"]) >= 1

    item = data["data"][0]

    assert "status" in item
    assert "count" in item
    assert item["count"] >= 1


def test_fraud_distribution_contains_valid_statuses(
    auth_client,
    test_transaction,
):
    response = auth_client.get(
        "/dashboard/fraud-distribution"
    )

    assert response.status_code == 200

    data = response.json()

    valid_statuses = {
        "pending",
        "approved",
        "review",
        "blocked",
    }

    for item in data["data"]:
        assert item["status"] in valid_statuses
        assert item["count"] >= 1