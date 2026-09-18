from app.db.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.security.password import verify_password

from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction

def test_get_user_by_email_and_verify_password():
    db = SessionLocal()

    try:
        repository = UserRepository(db)
        service = UserService(repository)

        user = service.get_user_by_email(
            "testuser@example.com"
        )

        assert user is not None
        assert user.email == "testuser@example.com"

        assert verify_password(
            "MySecurePassword123",
            user.password_hash
        )

        assert not verify_password(
            "WrongPassword123",
            user.password_hash
        )

    finally:
        db.close()

def test_authenticate_user_success():
    db = SessionLocal()

    try:
        repository = UserRepository(db)
        user_service = UserService(repository)
        auth_service = AuthService(user_service)

        user = auth_service.authenticate_user(
            "testuser@example.com",
            "MySecurePassword123"
        )

        assert user is not None
        assert user.email == "testuser@example.com"

    finally:
        db.close()


def test_authenticate_user_wrong_password():
    db = SessionLocal()

    try:
        repository = UserRepository(db)
        user_service = UserService(repository)
        auth_service = AuthService(user_service)

        user = auth_service.authenticate_user(
            "testuser@example.com",
            "WrongPassword123"
        )

        assert user is None

    finally:
        db.close()

def test_login_success():
    db = SessionLocal()

    try:
        repository = UserRepository(db)
        user_service = UserService(repository)
        auth_service = AuthService(user_service)

        token = auth_service.login(
            "testuser@example.com",
            "MySecurePassword123"
        )

        assert token is not None
        assert isinstance(token, str)

    finally:
        db.close()

def test_login_wrong_password():
    db = SessionLocal()

    try:
        repository = UserRepository(db)
        user_service = UserService(repository)
        auth_service = AuthService(user_service)

        token = auth_service.login(
            "testuser@example.com",
            "WrongPassword123"
        )

        assert token is None

    finally:
        db.close()