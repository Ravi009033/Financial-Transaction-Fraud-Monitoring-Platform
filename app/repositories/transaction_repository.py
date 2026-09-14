from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate

class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, transaction: TransactionCreate):
        db_tx = Transaction(
        account_id=transaction.account_id,
        amount=transaction.amount,
        merchant = transaction.merchant,
        location = transaction.location,
        transaction_type=transaction.transaction_type
    )
        self.db.add(db_tx)
        self.db.commit()
        self.db.refresh(db_tx)
        return db_tx

    def get_by_id(self):
        pass
    def get_all(self):
        pass
    def update(self):
        pass
    def delete(self):
        pass