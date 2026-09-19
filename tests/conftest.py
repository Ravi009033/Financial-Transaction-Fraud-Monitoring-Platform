import os

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import Base
from app.db.dependencies import get_db

# Import all models so SQLAlchemy knows about every table.
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction


load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

test_engine = create_engine(
    TEST_DATABASE_URL,
    echo=False
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=test_engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    from app.models.user import User
    from app.security.password import hash_password

    user = User(
        name="Test User",
        email="testuser@example.com",
        phone="9876543210",
        address="Test Address",
        password_hash=hash_password("password123")
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@pytest.fixture
def test_account(db, test_user):
    from app.models.account import Account

    account = Account(
        account_number="ACC_TEST_001",
        user_id=test_user.id,
        balance=10000
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account

@pytest.fixture
def auth_client(db, test_user):
    from app.security.jwt import create_access_token

    token = create_access_token({
        "sub": str(test_user.id)
    })

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        test_client.headers.update({
            "Authorization": f"Bearer {token}"
        })
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture
def other_user(db):
    from app.models.user import User
    from app.security.password import hash_password

    user = User(
        name="Other User",
        email="otheruser@example.com",
        phone="9876543211",
        address="Other Address",
        password_hash=hash_password("password123")
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@pytest.fixture
def other_account(db, other_user):
    from app.models.account import Account

    account = Account(
        account_number="ACC_TEST_002",
        user_id=other_user.id,
        balance=5000
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account

@pytest.fixture
def test_transaction(db, test_account):
    from app.models.transaction import Transaction, TransactionStatus
    from app.models.transaction import TransactionType

    transaction = Transaction(
        account_id=test_account.id,
        amount=100,
        merchant="Test Merchant",
        location="Gurugram",
        transaction_type=TransactionType.OFFLINE,
        status=TransactionStatus.PENDING,
        fraud_score=None,
        fraud_decision=None
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction

@pytest.fixture
def other_transaction(db, other_account):
    from app.models.transaction import Transaction, TransactionStatus
    from app.models.transaction import TransactionType

    transaction = Transaction(
        account_id=other_account.id,
        amount=100,
        merchant="Other Merchant",
        location="Delhi",
        transaction_type=TransactionType.OFFLINE,
        status=TransactionStatus.PENDING,
        fraud_score=None,
        fraud_decision=None
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction

@pytest.fixture
def fraud_test_account(db, test_user):
    from app.models.account import Account

    account = Account(
        account_number="ACC_FRAUD_TEST_001",
        user_id=test_user.id,
        balance=200000
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account
