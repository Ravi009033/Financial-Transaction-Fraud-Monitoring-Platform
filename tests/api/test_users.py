import uuid


# ============================================================
# GET /users/
# ============================================================

def test_get_users_unauthorized(client):
    response = client.get("/users/")

    assert response.status_code == 401


def test_get_users_authorized(auth_client, test_user):
    response = auth_client.get("/users/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == str(test_user.id)
    assert data[0]["email"] == test_user.email


# ============================================================
# GET /users/{user_id}
# ============================================================

def test_get_own_user(auth_client, test_user):
    response = auth_client.get(
        f"/users/{test_user.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(test_user.id)
    assert data["email"] == test_user.email


def test_get_nonexistent_user(auth_client):
    user_id = uuid.uuid4()

    response = auth_client.get(
        f"/users/{user_id}"
    )

    assert response.status_code == 404


# ============================================================
# POST /users/
# ============================================================

def test_create_user(client):
    unique_email = f"user_{uuid.uuid4().hex[:8]}@example.com"

    response = client.post(
        "/users/",
        json={
            "name": "New User",
            "email": unique_email,
            "phone": "9876543212",
            "address": "Gurugram",
            "password": "SecurePassword123"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "New User"
    assert data["email"] == unique_email
    assert "password" not in data
    assert "password_hash" not in data


# ============================================================
# PUT /users/{user_id}
# ============================================================

def test_update_user(auth_client, test_user):
    response = auth_client.put(
        f"/users/{test_user.id}",
        json={
            "name": "Updated User",
            "email": test_user.email,
            "phone": "9876543213",
            "address": "Updated Address"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(test_user.id)
    assert data["name"] == "Updated User"
    assert data["phone"] == "9876543213"
    assert data["address"] == "Updated Address"


def test_update_nonexistent_user(auth_client):
    user_id = uuid.uuid4()

    response = auth_client.put(
        f"/users/{user_id}",
        json={
            "name": "Updated User",
            "email": "updated@example.com",
            "phone": "9876543213",
            "address": "Updated Address"
        }
    )

    assert response.status_code == 404


# ============================================================
# DELETE /users/{user_id}
# ============================================================

def test_delete_user(auth_client, test_user):
    response = auth_client.delete(
        f"/users/{test_user.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["user_id"] == str(test_user.id)


def test_delete_nonexistent_user(auth_client):
    user_id = uuid.uuid4()

    response = auth_client.delete(
        f"/users/{user_id}"
    )

    assert response.status_code == 404