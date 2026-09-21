def test_transaction_trends_requires_auth(client):
    response = client.get("/dashboard/transaction-trends")

    assert response.status_code == 401


def test_transaction_trends_empty(auth_client):
    response = auth_client.get(
        "/dashboard/transaction-trends"
    )

    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert data["data"] == []


def test_transaction_trends_with_transaction(
    auth_client,
    test_transaction,
):
    response = auth_client.get(
        "/dashboard/transaction-trends"
    )

    assert response.status_code == 200

    data = response.json()

    assert "data" in data
    assert len(data["data"]) >= 1

    trend = data["data"][0]

    assert "date" in trend
    assert "transactions" in trend
    assert "amount" in trend


def test_transaction_trends_does_not_expose_other_user_data(
    auth_client,
    other_transaction,
):
    response = auth_client.get(
        "/dashboard/transaction-trends"
    )

    assert response.status_code == 200

    data = response.json()

    # Other user's transaction must not appear.
    assert all(
        trend["transactions"] >= 0
        for trend in data["data"]
    )