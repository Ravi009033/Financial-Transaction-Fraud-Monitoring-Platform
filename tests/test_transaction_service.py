from decimal import Decimal
from uuid import uuid4
from unittest.mock import Mock

import pytest

from app.services.transaction_service import TransactionService
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.models.transaction import TransactionStatus
from app.exceptions import InsufficientBalanceError, TransactionAlreadyProcessedError


def test_insufficient_balance():
    account_repository = Mock()
    transaction_repository = Mock()
    fraud_service = Mock()

    account = Mock()
    account.balance = Decimal("10000")
    user_id = uuid4()
    account.user_id = user_id

    account_repository.get_by_id.return_value = account

    transaction = TransactionCreate(
        account_id=uuid4(),
        amount=Decimal("15000"),
        merchant="Amazon",
        location="Delhi",
        transaction_type="online"
    )

    service = TransactionService(
        transaction_repository,
        account_repository,
        fraud_service
    )

    with pytest.raises(InsufficientBalanceError):
        service.create_transaction(transaction, user_id)

    transaction_repository.create.assert_not_called()
    fraud_service.evaluate_transaction.assert_not_called()

def test_approved_transaction():
    account_repository = Mock()
    transaction_repository = Mock()
    fraud_service = Mock()

    account = Mock()
    account.balance = Decimal("10000")
    user_id = uuid4()
    account.user_id = user_id

    account_repository.get_by_id.return_value = account

    fraud_service.evaluate_transaction.return_value = {
        "fraud_score": Decimal("0.0"),
        "fraud_decision": "approved"
    }

    transaction = TransactionCreate(
        account_id=uuid4(),
        amount=Decimal("3000"),
        merchant="Amazon",
        location="Delhi",
        transaction_type="online"
    )

    service = TransactionService(
        transaction_repository,
        account_repository,
        fraud_service
    )

    service.create_transaction(transaction,user_id)

    assert account.balance == Decimal("7000")

    fraud_service.evaluate_transaction.assert_called_once_with(
        transaction.amount,
        transaction.transaction_type
    )

    transaction_repository.create.assert_called_once_with(
        transaction,
        {
            "fraud_score": Decimal("0.0"),
            "fraud_decision": "approved"
        },
        TransactionStatus.APPROVED
    )

def test_review_transaction():
    account_repository = Mock()
    transaction_repository = Mock()
    fraud_service = Mock()

    account = Mock()
    account.balance = Decimal("100000")
    user_id = uuid4()
    account.user_id = user_id

    account_repository.get_by_id.return_value = account

    fraud_service.evaluate_transaction.return_value = {
        "fraud_score": Decimal("0.5"),
        "fraud_decision": "review"
    }

    transaction = TransactionCreate(
        account_id=uuid4(),
        amount=Decimal("50000"),
        merchant="Amazon",
        location="Delhi",
        transaction_type="online"
    )

    service = TransactionService(
        transaction_repository,
        account_repository,
        fraud_service
    )

    service.create_transaction(transaction, user_id)

    # Balance should NOT change for a review transaction
    assert account.balance == Decimal("100000")

    transaction_repository.create.assert_called_once_with(
        transaction,
        {
            "fraud_score": Decimal("0.5"),
            "fraud_decision": "review"
        },
        TransactionStatus.REVIEW
    )

def test_blocked_transaction():
    account_repository = Mock()
    transaction_repository = Mock()
    fraud_service = Mock()

    account = Mock()
    account.balance = Decimal("100000")
    user_id = uuid4()
    account.user_id = user_id
    account_repository.get_by_id.return_value = account

    fraud_service.evaluate_transaction.return_value = {
        "fraud_score": Decimal("0.7"),
        "fraud_decision": "blocked"
    }

    transaction = TransactionCreate(
        account_id=uuid4(),
        amount=Decimal("100000"),
        merchant="Amazon",
        location="Delhi",
        transaction_type="online"
    )

    service = TransactionService(
        transaction_repository,
        account_repository,
        fraud_service
    )

    service.create_transaction(transaction, user_id)

    # Blocked transactions must not deduct money
    assert account.balance == Decimal("100000")

    transaction_repository.create.assert_called_once_with(
        transaction,
        {
            "fraud_score": Decimal("0.7"),
            "fraud_decision": "blocked"
        },
        TransactionStatus.BLOCKED
    )

def test_nonexistent_account():
    account_repository = Mock()
    transaction_repository = Mock()
    fraud_service = Mock()

    account_repository.get_by_id.return_value = None
    user_id = uuid4()

    transaction = TransactionCreate(
        account_id=uuid4(),
        amount=Decimal("5000"),
        merchant="Amazon",
        location="Delhi",
        transaction_type="online"
    )

    service = TransactionService(
        transaction_repository,
        account_repository,
        fraud_service
    )

    result = service.create_transaction(transaction, user_id)

    assert result is None

    fraud_service.evaluate_transaction.assert_not_called()
    transaction_repository.create.assert_not_called()

def test_processed_transaction_cannot_be_updated():
    account_repository = Mock()
    transaction_repository = Mock()
    fraud_service = Mock()

    transaction_repository.get_by_id.return_value = Mock(
        status=TransactionStatus.BLOCKED
    )

    transaction_update = TransactionUpdate(
        merchant="Changed Merchant",
        location="Mumbai"
    )

    transaction_id = uuid4()

    service = TransactionService(
        transaction_repository,
        account_repository,
        fraud_service
    )

    with pytest.raises(TransactionAlreadyProcessedError):
        service.update_transaction(
            transaction_id,
            transaction_update
        )

    transaction_repository.update.assert_not_called()