from app.db.database import SessionLocal
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.security.jwt import create_access_token
from app.security.dependencies import get_current_user

from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction

import pytest
from fastapi import HTTPException


def test_get_current_user():
    db = SessionLocal()

    try:
        repository = UserRepository(db)
        user_service = UserService(repository)

        user = user_service.get_user_by_email(
            "testuser@example.com"
        )

        assert user is not None

        token = create_access_token({
            "sub": str(user.id)
        })

        current_user = get_current_user(
            token=token,
            db=db
        )

        assert current_user is not None
        assert current_user.id == user.id
        assert current_user.email == "testuser@example.com"

    finally:
        db.close()

def test_invalid_token():
    db = SessionLocal()

    try:
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(
                token="invalid.jwt.token",
                db=db
            )

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid or expired token"

    finally:
        db.close()

def test_token_without_user_id():
    db = SessionLocal()

    try:
        token = create_access_token({
            "email": "testuser@example.com"
        })

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(
                token=token,
                db=db
            )

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token payload"

    finally:
        db.close()