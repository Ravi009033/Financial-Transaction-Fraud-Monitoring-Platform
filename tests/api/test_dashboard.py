

def test_dashboard_summary(auth_client):
    response = auth_client.get("/dashboard/summary")

    assert response.status_code == 200

    data = response.json()

    assert "total_transactions" in data
    assert "total_amount" in data
    assert "approved_transactions" in data
    assert "review_transactions" in data
    assert "blocked_transactions" in data
    assert "pending_transactions" in data
    assert "fraud_transactions" in data
    assert "fraud_rate" in data

def test_dashboard_summary_empty(auth_client):
    response = auth_client.get("/dashboard/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_transactions"] == 0
    assert data["fraud_transactions"] == 0
    assert data["fraud_rate"] == 0

def test_dashboard_summary_requires_auth(client):
    response = client.get("/dashboard/summary")

    assert response.status_code == 401

def test_dashboard_summary_with_transaction(
    auth_client,
    test_transaction,
):
    response = auth_client.get("/dashboard/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_transactions"] >= 1
    assert data["total_amount"] is not None

def test_dashboard_fraud_count_includes_review_and_blocked(
    auth_client,
):
    response = auth_client.get(
        "/dashboard/summary"
    )

    assert response.status_code == 200

    data = response.json()

    expected_fraud_transactions = (
        data["review_transactions"]
        + data["blocked_transactions"]
    )

    assert (
        data["fraud_transactions"]
        == expected_fraud_transactions
    )

def test_dashboard_fraud_rate(
    auth_client,
):
    response = auth_client.get(
        "/dashboard/summary"
    )

    assert response.status_code == 200

    data = response.json()

    if data["total_transactions"] > 0:
        expected_rate = (
            data["fraud_transactions"]
            / data["total_transactions"]
        ) * 100
    else:
        expected_rate = 0.0

    assert abs(
        data["fraud_rate"] - expected_rate
    ) < 0.0001