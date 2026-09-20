from decimal import Decimal
from uuid import uuid4
from unittest.mock import Mock
import pytest
from datetime import datetime, timezone

from app.services.transaction_service import TransactionService
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.models.transaction import TransactionStatus
from app.exceptions import (
    InsufficientBalanceError, 
    TransactionAlreadyProcessedError, 
    TransactionAccessDeniedError
)


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

    historical_transaction = Mock()
    historical_transaction.amount = Decimal("500")
    historical_transaction.timestamp = datetime(
        2026, 9, 19, 10, 0, tzinfo=timezone.utc
    )

    transaction_repository.get_transaction_history.return_value = [
        historical_transaction
    ]

    fraud_service.evaluate_transaction.return_value = {
        "fraud_score": Decimal("0.0"),
        "fraud_decision": "approved",
    }

    transaction = TransactionCreate(
        account_id=uuid4(),
        amount=Decimal("3000"),
        merchant="Amazon",
        location="Delhi",
        transaction_type="online",
    )

    service = TransactionService(
        transaction_repository,
        account_repository,
        fraud_service,
    )

    service.create_transaction(
        transaction,
        user_id,
    )

    assert account.balance == Decimal("7000")

    fraud_service.evaluate_transaction.assert_called_once()

    call_kwargs = (
        fraud_service.evaluate_transaction.call_args.kwargs
    )

    assert call_kwargs["amount"] == transaction.amount
    assert (
        call_kwargs["transaction_type"]
        == transaction.transaction_type
    )
    assert isinstance(
        call_kwargs["timestamp"],
        datetime,
    )
    assert (
        call_kwargs["historical_transactions"]
        == [historical_transaction]
    )

    transaction_repository.create.assert_called_once()

    create_call = transaction_repository.create.call_args

    assert create_call.args[0] == transaction
    assert create_call.args[1] == {
        "fraud_score": Decimal("0.0"),
        "fraud_decision": "approved",
    }
    assert create_call.args[2] == TransactionStatus.APPROVED
    assert isinstance(create_call.kwargs["timestamp"], datetime,)

def test_review_transaction():
    account_repository = Mock()
    transaction_repository = Mock()
    fraud_service = Mock()

    account = Mock()
    account.balance = Decimal("100000")
    user_id = uuid4()
    account.user_id = user_id

    account_repository.get_by_id.return_value = account

    transaction_repository.get_transaction_history.return_value = []

    fraud_service.evaluate_transaction.return_value = {
        "fraud_score": Decimal("0.5"),
        "fraud_decision": "review",
    }

    transaction = TransactionCreate(
        account_id=uuid4(),
        amount=Decimal("50000"),
        merchant="Amazon",
        location="Delhi",
        transaction_type="online",
    )

    service = TransactionService(
        transaction_repository,
        account_repository,
        fraud_service,
    )

    service.create_transaction(
        transaction,
        user_id,
    )

    # Review transactions must NOT deduct money.
    assert account.balance == Decimal("100000")

    create_call = transaction_repository.create.call_args

    assert create_call.args[0] == transaction
    assert create_call.args[1]["fraud_decision"] == "review"
    assert create_call.args[2] == TransactionStatus.REVIEW

    assert isinstance(
        create_call.kwargs["timestamp"],
        datetime,
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

    transaction_repository.get_transaction_history.return_value = []

    fraud_service.evaluate_transaction.return_value = {
        "fraud_score": Decimal("0.7"),
        "fraud_decision": "blocked",
    }

    transaction = TransactionCreate(
        account_id=uuid4(),
        amount=Decimal("100000"),
        merchant="Amazon",
        location="Delhi",
        transaction_type="online",
    )

    service = TransactionService(
        transaction_repository,
        account_repository,
        fraud_service,
    )

    service.create_transaction(
        transaction,
        user_id,
    )

    # Blocked transactions must NOT deduct money.
    assert account.balance == Decimal("100000")

    create_call = transaction_repository.create.call_args

    assert create_call.args[0] == transaction
    assert create_call.args[1]["fraud_decision"] == "blocked"
    assert create_call.args[2] == TransactionStatus.BLOCKED

    assert isinstance(
        create_call.kwargs["timestamp"],
        datetime,
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

def test_pending_transaction_for_unknown_fraud_decision():
    account_repository = Mock()
    transaction_repository = Mock()
    fraud_service = Mock()

    account = Mock()
    account.balance = Decimal("10000")

    user_id = uuid4()
    account.user_id = user_id

    account_repository.get_by_id.return_value = account

    fraud_service.evaluate_transaction.return_value = {
        "fraud_score": Decimal("0.2"),
        "fraud_decision": "unknown"
    }

    transaction_repository.create.return_value = Mock()

    transaction = TransactionCreate(
        account_id=uuid4(),
        amount=Decimal("100"),
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

    transaction_repository.create.assert_called_once()

    args = transaction_repository.create.call_args

    assert args.args[0] == transaction
    assert args.args[1]["fraud_decision"] == "unknown"
    assert args.args[2] == TransactionStatus.PENDING

    assert isinstance(
        args.kwargs["timestamp"],
        datetime,
    )

def test_get_all_transactions():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    transactions = [Mock(), Mock()]
    repository.get_all.return_value = transactions

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    result = service.get_all_transactions()

    assert result == transactions
    repository.get_all.assert_called_once()

def test_get_transaction():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    transaction_id = uuid4()
    transaction = Mock()

    repository.get_by_id.return_value = transaction

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    result = service.get_transaction(transaction_id)

    assert result == transaction
    repository.get_by_id.assert_called_once_with(transaction_id)

def test_get_transactions_by_account():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    account_id = uuid4()
    transactions = [Mock(), Mock()]

    repository.get_by_account.return_value = transactions

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    result = service.get_transactions_by_account(account_id)

    assert result == transactions
    repository.get_by_account.assert_called_once_with(account_id)

def test_update_transaction_nonexistent():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    transaction_id = uuid4()

    repository.get_by_id.return_value = None

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    update = TransactionUpdate(
        merchant="Updated Merchant",
        location="Mumbai"
    )

    result = service.update_transaction(
        transaction_id,
        update
    )

    assert result is None
    repository.update.assert_not_called()

def test_update_pending_transaction():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    transaction_id = uuid4()

    db_transaction = Mock()
    db_transaction.status = TransactionStatus.PENDING

    updated_transaction = Mock()

    repository.get_by_id.return_value = db_transaction
    repository.update.return_value = updated_transaction

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    update = TransactionUpdate(
        merchant="Updated Merchant",
        location="Mumbai"
    )

    result = service.update_transaction(
        transaction_id,
        update
    )

    assert result == updated_transaction

    repository.update.assert_called_once_with(
        transaction_id,
        update
    )

def test_delete_transaction():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    transaction_id = uuid4()
    deleted_transaction = Mock()

    repository.delete.return_value = deleted_transaction

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    result = service.delete_transaction(transaction_id)

    assert result == deleted_transaction

    repository.delete.assert_called_once_with(
        transaction_id
    )

def test_get_transaction_for_user_nonexistent():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    transaction_id = uuid4()
    user_id = uuid4()

    repository.get_by_id.return_value = None

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    result = service.get_transaction_for_user(
        transaction_id,
        user_id
    )

    assert result is None
    account_repository.get_by_id.assert_not_called()

def test_get_transaction_for_user_missing_account():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    transaction_id = uuid4()
    user_id = uuid4()
    account_id = uuid4()

    transaction = Mock()
    transaction.account_id = account_id

    repository.get_by_id.return_value = transaction
    account_repository.get_by_id.return_value = None

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    result = service.get_transaction_for_user(
        transaction_id,
        user_id
    )

    assert result is None

def test_get_transaction_for_user_access_denied():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    transaction_id = uuid4()
    owner_id = uuid4()
    attacker_id = uuid4()
    account_id = uuid4()

    transaction = Mock()
    transaction.account_id = account_id

    account = Mock()
    account.user_id = owner_id

    repository.get_by_id.return_value = transaction
    account_repository.get_by_id.return_value = account

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    with pytest.raises(TransactionAccessDeniedError):
        service.get_transaction_for_user(
            transaction_id,
            attacker_id
        )

def test_get_transactions_for_user_no_accounts():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    user_id = uuid4()

    account_repository.get_by_user_id.return_value = []

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    transactions, total = service.get_transactions_for_user(user_id)

    assert transactions == []
    assert total == 0

    repository.get_by_account_ids.assert_not_called()

def test_get_transactions_for_user():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    user_id = uuid4()

    account1 = Mock()
    account1.id = uuid4()

    account2 = Mock()
    account2.id = uuid4()

    transactions = [Mock(), Mock()]

    account_repository.get_by_user_id.return_value = [
        account1,
        account2
    ]

    repository.get_by_account_ids.return_value = (
        transactions,
        2
    )

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    result, total = service.get_transactions_for_user(user_id)

    assert result == transactions
    assert total == 2

    repository.get_by_account_ids.assert_called_once_with(
        [account1.id, account2.id],
        skip=0,
        limit=10
    )

    
def test_update_transaction_for_user_nonexistent():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    transaction_id = uuid4()
    user_id = uuid4()

    repository.get_by_id.return_value = None

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    update = TransactionUpdate(
        merchant="Updated Merchant",
        location="Mumbai"
    )

    result = service.update_transaction_for_user(
        transaction_id,
        update,
        user_id
    )

    assert result is None

def test_update_transaction_for_user_missing_account():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    transaction_id = uuid4()
    user_id = uuid4()

    db_transaction = Mock()
    db_transaction.account_id = uuid4()

    repository.get_by_id.return_value = db_transaction
    account_repository.get_by_id.return_value = None

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    update = TransactionUpdate(
        merchant="Updated Merchant",
        location="Mumbai"
    )

    result = service.update_transaction_for_user(
        transaction_id,
        update,
        user_id
    )

    assert result is None

def test_update_transaction_for_user_access_denied():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    transaction_id = uuid4()
    owner_id = uuid4()
    attacker_id = uuid4()

    db_transaction = Mock()
    db_transaction.account_id = uuid4()

    account = Mock()
    account.user_id = owner_id

    repository.get_by_id.return_value = db_transaction
    account_repository.get_by_id.return_value = account

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    update = TransactionUpdate(
        merchant="Updated Merchant",
        location="Mumbai"
    )

    with pytest.raises(TransactionAccessDeniedError):
        service.update_transaction_for_user(
            transaction_id,
            update,
            attacker_id
        )

def test_delete_transaction_for_user_nonexistent():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    transaction_id = uuid4()
    user_id = uuid4()

    repository.get_by_id.return_value = None

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    result = service.delete_transaction_for_user(
        transaction_id,
        user_id
    )

    assert result is None

def test_delete_transaction_for_user_missing_account():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    transaction_id = uuid4()
    user_id = uuid4()

    db_transaction = Mock()
    db_transaction.account_id = uuid4()

    repository.get_by_id.return_value = db_transaction
    account_repository.get_by_id.return_value = None

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    result = service.delete_transaction_for_user(
        transaction_id,
        user_id
    )

    assert result is None

def test_delete_transaction_for_user_access_denied():
    repository = Mock()
    account_repository = Mock()
    fraud_service = Mock()

    transaction_id = uuid4()
    owner_id = uuid4()
    attacker_id = uuid4()

    db_transaction = Mock()
    db_transaction.account_id = uuid4()

    account = Mock()
    account.user_id = owner_id

    repository.get_by_id.return_value = db_transaction
    account_repository.get_by_id.return_value = account

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    with pytest.raises(TransactionAccessDeniedError):
        service.delete_transaction_for_user(
            transaction_id,
            attacker_id
        )