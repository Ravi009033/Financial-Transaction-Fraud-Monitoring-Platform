from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from uuid import UUID

class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, transaction: TransactionCreate, fraud_result, status):
        db_tx = Transaction(
        account_id=transaction.account_id,
        amount=transaction.amount,
        merchant = transaction.merchant,
        location = transaction.location,
        transaction_type=transaction.transaction_type,
        fraud_score=fraud_result["fraud_score"],
        fraud_decision=fraud_result["fraud_decision"],
        status=status
    )
        try:
            self.db.add(db_tx)
            self.db.commit()
            self.db.refresh(db_tx)
            return db_tx
        except Exception:
            self.db.rollback()
            raise

    def get_all(self):
            return self.db.query(Transaction).all()

    def get_by_id(self, transaction_id: UUID):
        return (
            self.db.query(Transaction)
            .filter(Transaction.id == transaction_id)
            .first()
        )

    def get_by_account(self, account_id: UUID):
        return (
            self.db.query(Transaction)
            .filter(Transaction.account_id == account_id)
            .all()
        )
    
    def update(self, transaction_id, transaction: TransactionUpdate):
        db_transaction = self.get_by_id(transaction_id)

        if db_transaction is None:
            return None

        db_transaction.merchant = transaction.merchant
        db_transaction.location = transaction.location

        self.db.commit()
        self.db.refresh(db_transaction)

        return db_transaction
    
    def delete(self, transaction_id):
        db_transaction = self.get_by_id(transaction_id)

        if db_transaction is None:
            return None

        self.db.delete(db_transaction)
        self.db.commit()

        return db_transaction