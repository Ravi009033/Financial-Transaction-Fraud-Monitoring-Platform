import uuid

# ============================================================
# POST /transactions/
# ============================================================

def test_create_transaction_unauthorized(client, test_account):
    response = client.post(
        "/transactions/",
        json={
            "account_id": str(test_account.id),
            "amount": 1000,
            "merchant": "Paytm",
            "location": "Delhi",
            "transaction_type": "online"
        }
    )

    assert response.status_code == 401


def test_create_transaction_authorized(auth_client, test_account):
    response = auth_client.post(
        "/transactions/",
        json={
            "account_id": str(test_account.id),
            "amount": 100,
            "merchant": "Paytm",
            "location": "Delhi",
            "transaction_type": "online"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["account_id"] == str(test_account.id)
    assert data["status"] in ["approved", "review", "blocked"]
    assert data["fraud_decision"] is not None


def test_create_transaction_other_users_account(
    auth_client,
    other_account
):
    response = auth_client.post(
        "/transactions/",
        json={
            "account_id": str(other_account.id),
            "amount": 100,
            "merchant": "Paytm",
            "location": "Delhi",
            "transaction_type": "online"
        }
    )

    assert response.status_code == 403


def test_create_transaction_nonexistent_account(auth_client):
    account_id = uuid.uuid4()

    response = auth_client.post(
        "/transactions/",
        json={
            "account_id": str(account_id),
            "amount": 100,
            "merchant": "Paytm",
            "location": "Delhi",
            "transaction_type": "online"
        }
    )

    assert response.status_code == 404


def test_create_transaction_insufficient_balance(
    auth_client,
    test_account
):
    response = auth_client.post(
        "/transactions/",
        json={
            "account_id": str(test_account.id),
            "amount": 999999999,
            "merchant": "Paytm",
            "location": "Delhi",
            "transaction_type": "online"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient account balance"


def test_create_transaction_invalid_amount(
    auth_client,
    test_account
):
    response = auth_client.post(
        "/transactions/",
        json={
            "account_id": str(test_account.id),
            "amount": 0,
            "merchant": "Paytm",
            "location": "Delhi",
            "transaction_type": "online"
        }
    )

    assert response.status_code == 422


def test_create_transaction_invalid_type(
    auth_client,
    test_account
):
    response = auth_client.post(
        "/transactions/",
        json={
            "account_id": str(test_account.id),
            "amount": 100,
            "merchant": "Paytm",
            "location": "Delhi",
            "transaction_type": "invalid_type"
        }
    )

    assert response.status_code == 422


def test_create_transaction_missing_amount(
    auth_client,
    test_account
):
    response = auth_client.post(
        "/transactions/",
        json={
            "account_id": str(test_account.id),
            "merchant": "Paytm",
            "location": "Delhi",
            "transaction_type": "online"
        }
    )

    assert response.status_code == 422


# ============================================================
# Fraud Detection
# ============================================================

def test_create_transaction_with_ml_fraud_prediction(
    auth_client,
    test_account,
):
    response = auth_client.post(
        "/transactions/",
        json={
            "account_id": str(test_account.id),
            "amount": 100,
            "merchant": "Amazon",
            "location": "Delhi",
            "transaction_type": "offline",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["account_id"] == str(test_account.id)

    assert data["fraud_score"] is not None
    assert 0 <= float(data["fraud_score"]) <= 1

    assert data["fraud_decision"] in {
        "approved",
        "review",
        "blocked",
    }

    assert data["status"] in {
        "approved",
        "review",
        "blocked",
    }

# ============================================================
# GET /transactions/
# ============================================================

def test_get_transactions_unauthorized(client):
    response = client.get("/transactions/")

    assert response.status_code == 401

def test_get_transactions_authorized(
    auth_client,
    test_transaction
):
    response = auth_client.get("/transactions/")

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total"] == 1
    assert data["total_pages"] == 1

    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == str(test_transaction.id)


def test_get_transactions_excludes_other_users_transactions(
    auth_client,
    test_transaction,
    other_transaction
):
    response = auth_client.get("/transactions/")

    assert response.status_code == 200

    data = response.json()

    transactions = data["items"]

    transaction_ids = [
        transaction["id"]
        for transaction in transactions
    ]

    assert str(test_transaction.id) in transaction_ids
    assert str(other_transaction.id) not in transaction_ids

    assert data["total"] == 1
    assert data["total_pages"] == 1


# ============================================================
# GET /transactions/{transaction_id}
# ============================================================

def test_get_transaction_unauthorized(
    client,
    test_transaction
):
    response = client.get(
        f"/transactions/{test_transaction.id}"
    )

    assert response.status_code == 401


def test_get_own_transaction(
    auth_client,
    test_transaction
):
    response = auth_client.get(
        f"/transactions/{test_transaction.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(test_transaction.id)
    assert data["account_id"] == str(test_transaction.account_id)


def test_get_other_users_transaction(
    auth_client,
    other_transaction
):
    response = auth_client.get(
        f"/transactions/{other_transaction.id}"
    )

    assert response.status_code == 403


def test_get_nonexistent_transaction(auth_client):
    transaction_id = uuid.uuid4()

    response = auth_client.get(
        f"/transactions/{transaction_id}"
    )

    assert response.status_code == 404


# ============================================================
# PUT /transactions/{transaction_id}
# ============================================================

def test_update_transaction_unauthorized(
    client,
    test_transaction
):
    response = client.put(
        f"/transactions/{test_transaction.id}",
        json={
            "merchant": "Updated Merchant",
            "location": "Mumbai"
        }
    )

    assert response.status_code == 401


def test_update_own_pending_transaction(
    auth_client,
    test_transaction
):
    response = auth_client.put(
        f"/transactions/{test_transaction.id}",
        json={
            "merchant": "Updated Merchant",
            "location": "Mumbai"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(test_transaction.id)
    assert data["merchant"] == "Updated Merchant"
    assert data["location"] == "Mumbai"


def test_update_other_users_transaction(
    auth_client,
    other_transaction
):
    response = auth_client.put(
        f"/transactions/{other_transaction.id}",
        json={
            "merchant": "Updated Merchant",
            "location": "Mumbai"
        }
    )

    assert response.status_code == 403


def test_update_nonexistent_transaction(auth_client):
    transaction_id = uuid.uuid4()

    response = auth_client.put(
        f"/transactions/{transaction_id}",
        json={
            "merchant": "Updated Merchant",
            "location": "Mumbai"
        }
    )

    assert response.status_code == 404


def test_update_processed_transaction(
    auth_client,
    processed_transaction,
):
    response = auth_client.put(
        f"/transactions/{processed_transaction.id}",
        json={
            "merchant": "Updated Merchant",
            "location": "Mumbai",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Processed transactions cannot be modified"
    )

# ============================================================
# DELETE /transactions/{transaction_id}
# ============================================================

def test_delete_transaction_unauthorized(
    client,
    test_transaction
):
    response = client.delete(
        f"/transactions/{test_transaction.id}"
    )

    assert response.status_code == 401


def test_delete_own_transaction(
    auth_client,
    test_transaction
):
    response = auth_client.delete(
        f"/transactions/{test_transaction.id}"
    )

    assert response.status_code == 200
    assert response.json()["transaction_id"] == str(
        test_transaction.id
    )


def test_delete_other_users_transaction(
    auth_client,
    other_transaction
):
    response = auth_client.delete(
        f"/transactions/{other_transaction.id}"
    )

    assert response.status_code == 403


def test_delete_nonexistent_transaction(auth_client):
    transaction_id = uuid.uuid4()

    response = auth_client.delete(
        f"/transactions/{transaction_id}"
    )

    assert response.status_code == 404


# ============================================================
# test pagination
# ============================================================

def test_get_transactions_with_page_size(auth_client, test_transaction):
    response = auth_client.get("/transactions/?page_size=2")

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["total"] == 1
    assert data["total_pages"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == str(test_transaction.id)


def test_get_transactions_page_2(auth_client, test_transaction):
    response = auth_client.get("/transactions/?page=2&page_size=1")

    assert response.status_code == 200

    data = response.json()

    assert data["page"] == 2
    assert data["page_size"] == 1
    assert data["total"] == 1
    assert data["total_pages"] == 1
    assert data["items"] == []

def test_get_transactions_invalid_page(auth_client):
    response = auth_client.get("/transactions/?page=0")

    assert response.status_code == 422


def test_get_transactions_invalid_page_size_zero(auth_client):
    response = auth_client.get("/transactions/?page_size=0")

    assert response.status_code == 422


def test_get_transactions_invalid_page_size_too_large(auth_client):
    response = auth_client.get("/transactions/?page_size=101")

    assert response.status_code == 422


# ============================================================
# test transactions by account number
# ============================================================
def test_get_transactions_by_account_authorized(
    auth_client,
    test_account,
    test_transaction
):
    response = auth_client.get(
        f"/transactions/account/{test_account.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == str(test_transaction.id)

def test_get_transactions_by_account_forbidden(
    auth_client,
    other_account
):
    response = auth_client.get(
        f"/transactions/account/{other_account.id}"
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have access to this account"

def test_get_transactions_by_account_not_found(auth_client):
    from uuid import uuid4

    response = auth_client.get(
        f"/transactions/account/{uuid4()}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Account not found"

def test_get_transactions_by_account_unauthorized(test_account, client):
    response = client.get(
        f"/transactions/account/{test_account.id}"
    )

    assert response.status_code == 401


def test_get_transactions_filter_by_status(
    auth_client,
    test_transaction,
):
    response = auth_client.get(
        "/transactions/?status=pending"
    )

    assert response.status_code == 200

    data = response.json()

    for transaction in data["items"]:
        assert transaction["status"] == "pending"

def test_get_transactions_filter_no_results(
    auth_client,
):
    response = auth_client.get(
        "/transactions/?status=blocked"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] >= 0
    assert "items" in data