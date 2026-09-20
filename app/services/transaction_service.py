from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.repositories.account_repository import AccountRepository
from app.services.fraud_service import FraudDetectionService
from uuid import UUID
from app.exceptions import (
    InsufficientBalanceError,
    TransactionAlreadyProcessedError,
    TransactionAccessDeniedError
)
from app.models.transaction import TransactionStatus
from datetime import datetime, timezone


class TransactionService:
    def __init__(self, repository: TransactionRepository, 
                 account_repository: AccountRepository,
                 fraud_service: FraudDetectionService):
        self.repository = repository
        self.account_repository = account_repository
        self.fraud_service = fraud_service

    def create_transaction(
        self,
        transaction: TransactionCreate,
        user_id: UUID
    ):
        account = self.account_repository.get_by_id(
            transaction.account_id
        )

        if account is None:
            return None

        if account.user_id != user_id:
            raise TransactionAccessDeniedError(
                "You do not have access to this account"
            )

        if transaction.amount > account.balance:
            raise InsufficientBalanceError(
                "Insufficient account balance"
            )

        # Timestamp for the transaction being evaluated.
        transaction_timestamp = datetime.now(timezone.utc)

        # Retrieve only previous transactions for this account.
        historical_transactions = (
            self.repository.get_transaction_history(
                transaction.account_id
            )
        )

        # Run ML fraud detection using historical account behavior.
        fraud_result = self.fraud_service.evaluate_transaction(
            amount=transaction.amount,
            transaction_type=transaction.transaction_type,
            timestamp=transaction_timestamp,
            historical_transactions=historical_transactions,
        )

        fraud_decision = fraud_result["fraud_decision"]

        if fraud_decision == "approved":
            status = TransactionStatus.APPROVED

            # Deduct money only when transaction is approved.
            account.balance -= transaction.amount

        elif fraud_decision == "review":
            status = TransactionStatus.REVIEW

        elif fraud_decision == "blocked":
            status = TransactionStatus.BLOCKED

        else:
            status = TransactionStatus.PENDING

        return self.repository.create(
            transaction,
            fraud_result,
            status,
            timestamp=transaction_timestamp,
        )

    def get_all_transactions(self):
        return self.repository.get_all()

    def get_transaction(self, transaction_id: UUID):
        return self.repository.get_by_id(transaction_id)

    def get_transactions_by_account(self, account_id: UUID):
        return self.repository.get_by_account(account_id)

    def update_transaction(self, transaction_id: UUID, transaction: TransactionUpdate):
        db_transaction = self.repository.get_by_id(transaction_id)

        if db_transaction is None:
            return None

        if db_transaction.status != TransactionStatus.PENDING:
            raise TransactionAlreadyProcessedError(
                "Processed transactions cannot be modified"
            )

        return self.repository.update(
            transaction_id,
            transaction
        )

    def delete_transaction(self, transaction_id):
        return self.repository.delete(transaction_id)

    def get_transaction_for_user(self, transaction_id: UUID, user_id: UUID):
        transaction = self.repository.get_by_id(transaction_id)

        if transaction is None:
            return None

        account = self.account_repository.get_by_id(
            transaction.account_id
        )

        if account is None:
            return None

        if account.user_id != user_id:
            raise TransactionAccessDeniedError(
                "You do not have access to this transaction"
            )

        return transaction

    def get_transactions_for_user(
        self,
        user_id: UUID,
        page: int = 1,
        page_size: int = 10
    ):
        accounts = self.account_repository.get_by_user_id(user_id)

        if not accounts:
            return [], 0

        account_ids = [account.id for account in accounts]

        skip = (page - 1) * page_size

        transactions, total = self.repository.get_by_account_ids(
            account_ids,
            skip=skip,
            limit=page_size
        )

        return transactions, total

    def update_transaction_for_user(
        self,
        transaction_id: UUID,
        transaction: TransactionUpdate,
        user_id: UUID
    ):
        db_transaction = self.repository.get_by_id(transaction_id)

        if db_transaction is None:
            return None

        account = self.account_repository.get_by_id(
            db_transaction.account_id
        )

        if account is None:
            return None

        if account.user_id != user_id:
            raise TransactionAccessDeniedError(
                "You do not have access to this transaction"
            )

        if db_transaction.status != TransactionStatus.PENDING:
            raise TransactionAlreadyProcessedError(
                "Processed transactions cannot be modified"
            )

        return self.repository.update(
            transaction_id,
            transaction
        )

    def delete_transaction_for_user(
        self,
        transaction_id: UUID,
        user_id: UUID
    ):
        db_transaction = self.repository.get_by_id(transaction_id)

        if db_transaction is None:
            return None

        account = self.account_repository.get_by_id(
            db_transaction.account_id
        )

        if account is None:
            return None

        if account.user_id != user_id:
            raise TransactionAccessDeniedError(
                "You do not have access to this transaction"
            )

        return self.repository.delete(transaction_id)