from app.security.password import hash_password, verify_password


def test_password_hashing():
    password = "MySecurePassword123"

    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash)


def test_wrong_password_fails():
    password = "MySecurePassword123"
    wrong_password = "WrongPassword123"

    password_hash = hash_password(password)

    assert not verify_password(
        wrong_password,
        password_hash
    )