from fastapi.testclient import TestClient

from app.main import app
from app.exceptions import (
    DuplicateAccountError,
    InsufficientBalanceError,
    TransactionAlreadyProcessedError,
    AccountAccessDeniedError,
    TransactionAccessDeniedError,
)
from unittest.mock import patch


client = TestClient(app)


def test_duplicate_account_exception_handler():
    @app.get("/test-duplicate-account")
    def raise_duplicate_account():
        raise DuplicateAccountError("Account number already exists")

    response = client.get("/test-duplicate-account")

    assert response.status_code == 409
    assert response.json() == {
        "error": "DUPLICATE_ACCOUNT",
        "message": "Account number already exists",
    }


def test_insufficient_balance_exception_handler():
    @app.get("/test-insufficient-balance")
    def raise_insufficient_balance():
        raise InsufficientBalanceError("Insufficient account balance")

    response = client.get("/test-insufficient-balance")

    assert response.status_code == 400
    assert response.json() == {
        "error": "INSUFFICIENT_BALANCE",
        "message": "Insufficient account balance",
    }


def test_transaction_already_processed_exception_handler():
    @app.get("/test-transaction-processed")
    def raise_transaction_processed():
        raise TransactionAlreadyProcessedError(
            "Transaction has already been processed"
        )

    response = client.get("/test-transaction-processed")

    assert response.status_code == 409
    assert response.json() == {
        "error": "TRANSACTION_ALREADY_PROCESSED",
        "message": "Transaction has already been processed",
    }


def test_account_access_denied_exception_handler():
    @app.get("/test-account-access")
    def raise_account_access_denied():
        raise AccountAccessDeniedError("You do not have access to this account")

    response = client.get("/test-account-access")

    assert response.status_code == 403
    assert response.json() == {
        "error": "ACCOUNT_ACCESS_DENIED",
        "message": "You do not have access to this account",
    }


def test_transaction_access_denied_exception_handler():
    @app.get("/test-transaction-access")
    def raise_transaction_access_denied():
        raise TransactionAccessDeniedError(
            "You do not have access to this transaction"
        )

    response = client.get("/test-transaction-access")

    assert response.status_code == 403
    assert response.json() == {
        "error": "TRANSACTION_ACCESS_DENIED",
        "message": "You do not have access to this transaction",
    }

def test_health_check(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "message": "Fraud Monitoring API is running"
    }

def test_generic_exception_handler():
    @app.get("/test-unexpected-error")
    def raise_unexpected_error():
        raise RuntimeError("Database connection details")

    client = TestClient(
        app,
        raise_server_exceptions=False
    )

    response = client.get("/test-unexpected-error")

    assert response.status_code == 500
    assert response.json() == {
        "error": "INTERNAL_SERVER_ERROR",
        "message": "An unexpected error occurred"
    }   

def test_readiness_check():
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready"
    }

def test_readiness_check_database_unavailable():
    with patch("app.main.engine.connect") as mock_connect:
        mock_connect.side_effect = Exception("Database unavailable")

        response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "not_ready"
    }