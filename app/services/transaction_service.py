from app.repositories.transaction_repository import TransactionRepository
from app.schemas.transaction import TransactionCreate

class TransactionService:
    def __init__(self, repository: TransactionRepository):
        self.repository = repository

    def create_transaction(self, transaction: TransactionCreate):
        return self.repository.create(transaction)