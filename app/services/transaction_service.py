from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.repositories.account_repository import AccountRepository
from uuid import UUID

class TransactionService:
    def __init__(self, repository: TransactionRepository, account_repository: AccountRepository):
        self.repository = repository
        self.account_repository = account_repository

    def create_transaction(self, transaction: TransactionCreate):
        account = self.account_repository.get_by_id(
            transaction.account_id
        )

        if account is None:
            return None
        return self.repository.create(transaction)

    def get_all_transactions(self):
        return self.repository.get_all()

    def get_transaction(self, transaction_id: UUID):
        return self.repository.get_by_id(transaction_id)

    def get_transactions_by_account(self, account_id: UUID):
        return self.repository.get_by_account(account_id)

    def update_transaction(self, transaction_id, transaction: TransactionUpdate):
        return self.repository.update(transaction_id, transaction)

    def delete_transaction(self, transaction_id):
        return self.repository.delete(transaction_id)