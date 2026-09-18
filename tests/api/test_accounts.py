from fastapi.testclient import TestClient
import uuid
from app.main import app

client = TestClient(app)


def get_auth_headers():
    """
    Login and return Authorization header.
    """
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


def test_get_accounts_unauthorized():
    """
    Request without JWT should return 401.
    """
    response = client.get("/accounts/")

    assert response.status_code == 401


def test_get_accounts_authorized():
    """
    Request with JWT should return user's accounts.
    """
    headers = get_auth_headers()

    response = client.get(
        "/accounts/",
        headers=headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_own_account():
    headers = get_auth_headers()

    account_id = "77c23e50-cada-4637-9ad6-7c50dace0aa1"

    response = client.get(
        f"/accounts/{account_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["id"] == account_id

def test_get_other_users_account():
    headers = get_auth_headers()

    other_account_id = "e8655968-d32f-4ab7-8054-dee852963be4"

    response = client.get(
        f"/accounts/{other_account_id}",
        headers=headers
    )

    assert response.status_code == 403

def test_get_nonexistent_account():
    headers = get_auth_headers()

    account_id = "00000000-0000-0000-0000-000000000000"

    response = client.get(
        f"/accounts/{account_id}",
        headers=headers
    )

    assert response.status_code == 404

def test_create_account_unauthorized():
    response = client.post(
        "/accounts/",
        json={
            "account_number": "ACC_TEST_001",
            "balance": 5000
        }
    )

    assert response.status_code == 401


def test_create_account_authorized():
    headers = get_auth_headers()

    account_number = f"ACC_API_{uuid.uuid4().hex[:8]}"

    response = client.post(
        "/accounts/",
        json={
            "account_number": account_number,
            "balance": 5000
        },
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["account_number"] == account_number
    assert data["balance"] == "5000.00"

def test_create_duplicate_account():
    headers = get_auth_headers()

    account_number = f"ACC_DUP_{uuid.uuid4().hex[:8]}"

    first_response = client.post(
        "/accounts/",
        json={
            "account_number": account_number,
            "balance": 5000
        },
        headers=headers
    )

    assert first_response.status_code == 200

    duplicate_response = client.post(
        "/accounts/",
        json={
            "account_number": account_number,
            "balance": 5000
        },
        headers=headers
    )

    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == "Account number already exists"

def test_update_account_unauthorized():
    account_id = "77c23e50-cada-4637-9ad6-7c50dace0aa1"

    response = client.put(
        f"/accounts/{account_id}",
        json={
            "account_number": "ACC_UPDATED_001"
        }
    )

    assert response.status_code == 401

def test_update_own_account():
    headers = get_auth_headers()

    account_id = "77c23e50-cada-4637-9ad6-7c50dace0aa1"

    response = client.put(
        f"/accounts/{account_id}",
        json={
            "account_number": "ACC_UPDATED_001"
        },
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == account_id
    assert data["account_number"] == "ACC_UPDATED_001"


def test_update_other_users_account():
    headers = get_auth_headers()

    account_id = "e8655968-d32f-4ab7-8054-dee852963be4"

    response = client.put(
        f"/accounts/{account_id}",
        json={
            "account_number": "ACC_OTHER_UPDATED"
        },
        headers=headers
    )

    assert response.status_code == 403

def test_update_nonexistent_account():
    headers = get_auth_headers()

    account_id = "00000000-0000-0000-0000-000000000000"

    response = client.put(
        f"/accounts/{account_id}",
        json={
            "account_number": "ACC_NOT_FOUND"
        },
        headers=headers
    )

    assert response.status_code == 404

def test_update_duplicate_account_number():
    headers = get_auth_headers()

    account_id = "77c23e50-cada-4637-9ad6-7c50dace0aa1"

    response = client.put(
        f"/accounts/{account_id}",
        json={
            "account_number": "ACC_API_TEST_003"
        },
        headers=headers
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Account number already exists"

def test_delete_account_unauthorized():
    account_id = "77c23e50-cada-4637-9ad6-7c50dace0aa1"

    response = client.delete(
        f"/accounts/{account_id}"
    )

    assert response.status_code == 401

def test_delete_own_account():
    headers = get_auth_headers()

    account_number = f"ACC_DELETE_{uuid.uuid4().hex[:8]}"

    create_response = client.post(
        "/accounts/",
        json={
            "account_number": account_number,
            "balance": 1000
        },
        headers=headers
    )

    assert create_response.status_code == 200

    account_id = create_response.json()["id"]

    response = client.delete(
        f"/accounts/{account_id}",
        headers=headers
    )

    assert response.status_code == 200
    assert response.json()["account_id"] == account_id

def test_delete_other_users_account():
    headers = get_auth_headers()

    account_id = "e8655968-d32f-4ab7-8054-dee852963be4"

    response = client.delete(
        f"/accounts/{account_id}",
        headers=headers
    )

    assert response.status_code == 403

def test_delete_nonexistent_account():
    headers = get_auth_headers()

    account_id = "00000000-0000-0000-0000-000000000000"

    response = client.delete(
        f"/accounts/{account_id}",
        headers=headers
    )

    assert response.status_code == 404

