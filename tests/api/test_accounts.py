import uuid


# -------------------------
# GET /accounts/
# -------------------------

def test_get_accounts_unauthorized(client):
    response = client.get("/accounts/")

    assert response.status_code == 401


def test_get_accounts_authorized(auth_client, test_account):
    response = auth_client.get("/accounts/")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == str(test_account.id)
    assert data[0]["account_number"] == test_account.account_number


# -------------------------
# GET /accounts/{account_id}
# -------------------------

def test_get_own_account(auth_client, test_account):
    response = auth_client.get(
        f"/accounts/{test_account.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(test_account.id)
    assert data["account_number"] == test_account.account_number


def test_get_other_users_account(auth_client, other_account):
    response = auth_client.get(
        f"/accounts/{other_account.id}"
    )

    assert response.status_code == 403


def test_get_nonexistent_account(auth_client):
    account_id = uuid.uuid4()

    response = auth_client.get(
        f"/accounts/{account_id}"
    )

    assert response.status_code == 404


# -------------------------
# POST /accounts/
# -------------------------

def test_create_account_unauthorized(client):
    response = client.post(
        "/accounts/",
        json={
            "account_number": "ACC_CREATE_001",
            "balance": 5000
        }
    )

    assert response.status_code == 401


def test_create_account_authorized(auth_client):
    account_number = f"ACC_API_{uuid.uuid4().hex[:8]}"

    response = auth_client.post(
        "/accounts/",
        json={
            "account_number": account_number,
            "balance": 5000
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["account_number"] == account_number
    assert data["balance"] == "5000.00"


def test_create_duplicate_account(auth_client):
    account_number = f"ACC_DUP_{uuid.uuid4().hex[:8]}"

    payload = {
        "account_number": account_number,
        "balance": 5000
    }

    first_response = auth_client.post(
        "/accounts/",
        json=payload
    )

    assert first_response.status_code == 200

    duplicate_response = auth_client.post(
        "/accounts/",
        json=payload
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == (
        "Account number already exists"
    )


# -------------------------
# PUT /accounts/{account_id}
# -------------------------

def test_update_account_unauthorized(client, test_account):
    response = client.put(
        f"/accounts/{test_account.id}",
        json={
            "account_number": "ACC_UPDATED_001"
        }
    )

    assert response.status_code == 401


def test_update_own_account(auth_client, test_account):
    new_account_number = (
        f"ACC_UPDATED_{uuid.uuid4().hex[:8]}"
    )

    response = auth_client.put(
        f"/accounts/{test_account.id}",
        json={
            "account_number": new_account_number
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(test_account.id)
    assert data["account_number"] == new_account_number


def test_update_other_users_account(auth_client, other_account):
    response = auth_client.put(
        f"/accounts/{other_account.id}",
        json={
            "account_number": "ACC_OTHER_UPDATED"
        }
    )

    assert response.status_code == 403


def test_update_nonexistent_account(auth_client):
    account_id = uuid.uuid4()

    response = auth_client.put(
        f"/accounts/{account_id}",
        json={
            "account_number": "ACC_NOT_FOUND"
        }
    )

    assert response.status_code == 404


def test_update_duplicate_account_number(
    auth_client,
    test_account
):
    duplicate_account_number = (
        f"ACC_DUP_{uuid.uuid4().hex[:8]}"
    )

    # Create another account with the number we will later reuse.
    create_response = auth_client.post(
        "/accounts/",
        json={
            "account_number": duplicate_account_number,
            "balance": 5000
        }
    )

    assert create_response.status_code == 200

    # Try changing test_account to the existing number.
    response = auth_client.put(
        f"/accounts/{test_account.id}",
        json={
            "account_number": duplicate_account_number
        }
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "Account number already exists"
    )


# -------------------------
# DELETE /accounts/{account_id}
# -------------------------

def test_delete_account_unauthorized(client, test_account):
    response = client.delete(
        f"/accounts/{test_account.id}"
    )

    assert response.status_code == 401


def test_delete_own_account(auth_client):
    account_number = (
        f"ACC_DELETE_{uuid.uuid4().hex[:8]}"
    )

    create_response = auth_client.post(
        "/accounts/",
        json={
            "account_number": account_number,
            "balance": 1000
        }
    )

    assert create_response.status_code == 200

    account_id = create_response.json()["id"]

    response = auth_client.delete(
        f"/accounts/{account_id}"
    )

    assert response.status_code == 200
    assert response.json()["account_id"] == account_id


def test_delete_other_users_account(
    auth_client,
    other_account
):
    response = auth_client.delete(
        f"/accounts/{other_account.id}"
    )

    assert response.status_code == 403


def test_delete_nonexistent_account(auth_client):
    account_id = uuid.uuid4()

    response = auth_client.delete(
        f"/accounts/{account_id}"
    )

    assert response.status_code == 404