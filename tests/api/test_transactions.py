from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def get_auth_headers():
    response = client.post(
        "/auth/login",
        data={
            "username": "testuser@example.com",
            "password": "MySecurePassword123"
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


def test_create_transaction_unauthorized():
    response = client.post(
        "/transactions/",
        json={
            "account_id": "77c23e50-cada-4637-9ad6-7c50dace0aa1",
            "amount": 1000,
            "merchant": "Paytm",
            "location": "Delhi",
            "transaction_type": "online"
        }
    )

    assert response.status_code == 401


def test_create_transaction_authorized():
    headers = get_auth_headers()

    response = client.post(
        "/transactions/",
        json={
            "account_id": "77c23e50-cada-4637-9ad6-7c50dace0aa1",
            "amount": 100,
            "merchant": "Paytm",
            "location": "Delhi",
            "transaction_type": "online"
        },
        headers=headers
    )

    assert response.status_code == 200

def test_create_transaction_other_users_account():
    headers = get_auth_headers()

    other_account_id = "e8655968-d32f-4ab7-8054-dee852963be4"

    response = client.post(
        "/transactions/",
        json={
            "account_id": other_account_id,
            "amount": 100,
            "merchant": "Paytm",
            "location": "Delhi",
            "transaction_type": "online"
        },
        headers=headers
    )

    assert response.status_code == 403

def test_create_transaction_nonexistent_account():
    headers = get_auth_headers()

    account_id = "00000000-0000-0000-0000-000000000000"

    response = client.post(
        "/transactions/",
        json={
            "account_id": account_id,
            "amount": 100,
            "merchant": "Paytm",
            "location": "Delhi",
            "transaction_type": "online"
        },
        headers=headers
    )

    assert response.status_code == 404

def test_create_transaction_insufficient_balance():
    headers = get_auth_headers()

    response = client.post(
        "/transactions/",
        json={
            "account_id": "77c23e50-cada-4637-9ad6-7c50dace0aa1",
            "amount": 999999999,
            "merchant": "Paytm",
            "location": "Delhi",
            "transaction_type": "online"
        },
        headers=headers
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient account balance"

def test_create_transaction_invalid_amount():
    headers = get_auth_headers()

    response = client.post(
        "/transactions/",
        json={
            "account_id": "77c23e50-cada-4637-9ad6-7c50dace0aa1",
            "amount": 0,
            "merchant": "Paytm",
            "location": "Delhi",
            "transaction_type": "online"
        },
        headers=headers
    )

    assert response.status_code == 422

def test_create_transaction_invalid_type():
    headers = get_auth_headers()

    response = client.post(
        "/transactions/",
        json={
            "account_id": "77c23e50-cada-4637-9ad6-7c50dace0aa1",
            "amount": 100,
            "merchant": "Paytm",
            "location": "Delhi",
            "transaction_type": "invalid_type"
        },
        headers=headers
    )

    assert response.status_code == 422

def test_create_transaction_missing_amount():
    headers = get_auth_headers()

    response = client.post(
        "/transactions/",
        json={
            "account_id": "77c23e50-cada-4637-9ad6-7c50dace0aa1",
            "merchant": "Paytm",
            "location": "Delhi",
            "transaction_type": "online"
        },
        headers=headers
    )

    assert response.status_code == 422


def test_create_approved_transaction():
    headers = get_auth_headers()

    response = client.post(
        "/transactions/",
        json={
            "account_id": "4e98ba96-2ce7-48cc-a0a6-82ab980ad13d",
            "amount": 100,
            "merchant": "Amazon",
            "location": "Delhi",
            "transaction_type": "offline"
        },
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "approved"
    assert data["fraud_decision"] == "approved"
    assert float(data["fraud_score"]) == 0.0

def test_create_review_transaction():
    headers = get_auth_headers()

    response = client.post(
        "/transactions/",
        json={
            "account_id": "4e98ba96-2ce7-48cc-a0a6-82ab980ad13d",
            "amount": 50000,
            "merchant": "HighValue Store",
            "location": "Delhi",
            "transaction_type": "offline"
        },
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "review"
    assert data["fraud_decision"] == "review"
    assert float(data["fraud_score"]) == 0.4

def test_create_blocked_transaction():
    headers = get_auth_headers()

    response = client.post(
        "/transactions/",
        json={
            "account_id": "4e98ba96-2ce7-48cc-a0a6-82ab980ad13d",
            "amount": 100000,
            "merchant": "HighRisk Merchant",
            "location": "Delhi",
            "transaction_type": "online"
        },
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "blocked"
    assert data["fraud_decision"] == "blocked"
    assert float(data["fraud_score"]) == 0.7

def test_get_transactions_unauthorized():
    response = client.get("/transactions/")

    assert response.status_code == 401

def test_get_transactions_authorized():
    headers = get_auth_headers()

    response = client.get(
        "/transactions/",
        headers=headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_transactions_excludes_other_users_transactions():
    headers = get_auth_headers()

    response = client.get(
        "/transactions/",
        headers=headers
    )

    assert response.status_code == 200

    transactions = response.json()

    other_account_id = "e8655968-d32f-4ab7-8054-dee852963be4"

    for transaction in transactions:
        assert transaction["account_id"] != other_account_id


def test_get_transaction_unauthorized():
    transaction_id = "9d412948-45e4-447b-9c65-37fe227188bb"

    response = client.get(
        f"/transactions/{transaction_id}"
    )

    assert response.status_code == 401

def test_get_own_transaction():
    headers = get_auth_headers()

    create_response = client.post(
        "/transactions/",
        json={
            "account_id": "77c23e50-cada-4637-9ad6-7c50dace0aa1",
            "amount": 100,
            "merchant": "Test Merchant",
            "location": "Delhi",
            "transaction_type": "offline"
        },
        headers=headers
    )

    assert create_response.status_code == 200

    transaction_id = create_response.json()["id"]

    response = client.get(
        f"/transactions/{transaction_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == transaction_id

def test_get_other_users_transaction():
    headers = get_auth_headers()

    transaction_id = "52a0385a-bd6e-46b0-9d1c-d31d155ea186"

    response = client.get(
        f"/transactions/{transaction_id}",
        headers=headers
    )

    assert response.status_code == 403

def test_get_nonexistent_transaction():
    headers = get_auth_headers()

    transaction_id = "00000000-0000-0000-0000-000000000000"

    response = client.get(
        f"/transactions/{transaction_id}",
        headers=headers
    )

    assert response.status_code == 404

def test_update_transaction_unauthorized():
    transaction_id = "00000000-0000-0000-0000-000000000000"

    response = client.put(
        f"/transactions/{transaction_id}",
        json={
            "merchant": "Updated Merchant",
            "location": "Mumbai"
        }
    )

    assert response.status_code == 401

def test_update_other_users_transaction():
    headers = get_auth_headers()

    transaction_id = "52a0385a-bd6e-46b0-9d1c-d31d155ea186"

    response = client.put(
        f"/transactions/{transaction_id}",
        json={
            "merchant": "Updated Merchant",
            "location": "Mumbai"
        },
        headers=headers
    )

    assert response.status_code == 403

def test_update_nonexistent_transaction():
    headers = get_auth_headers()

    transaction_id = "00000000-0000-0000-0000-000000000000"

    response = client.put(
        f"/transactions/{transaction_id}",
        json={
            "merchant": "Updated Merchant",
            "location": "Mumbai"
        },
        headers=headers
    )

    assert response.status_code == 404

def test_update_processed_transaction():
    headers = get_auth_headers()

    transaction_id = "9b484aa3-6dee-410b-afd8-64f6de818288"

    response = client.put(
        f"/transactions/{transaction_id}",
        json={
            "merchant": "Updated Merchant",
            "location": "Mumbai"
        },
        headers=headers
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Processed transactions cannot be modified"

def test_delete_transaction_unauthorized():
    transaction_id = "00000000-0000-0000-0000-000000000000"

    response = client.delete(
        f"/transactions/{transaction_id}"
    )

    assert response.status_code == 401

def test_delete_own_transaction():
    headers = get_auth_headers()

    create_response = client.post(
        "/transactions/",
        json={
            "account_id": "4e98ba96-2ce7-48cc-a0a6-82ab980ad13d",
            "amount": 100,
            "merchant": "Delete Test",
            "location": "Delhi",
            "transaction_type": "offline"
        },
        headers=headers
    )

    assert create_response.status_code == 200

    transaction_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/transactions/{transaction_id}",
        headers=headers
    )

    assert delete_response.status_code == 200
    assert delete_response.json()["transaction_id"] == transaction_id

def test_delete_other_users_transaction():
    headers = get_auth_headers()

    transaction_id = "52a0385a-bd6e-46b0-9d1c-d31d155ea186"

    response = client.delete(
        f"/transactions/{transaction_id}",
        headers=headers
    )

    assert response.status_code == 403

def test_delete_nonexistent_transaction():
    headers = get_auth_headers()

    transaction_id = "00000000-0000-0000-0000-000000000000"

    response = client.delete(
        f"/transactions/{transaction_id}",
        headers=headers
    )

    assert response.status_code == 404

