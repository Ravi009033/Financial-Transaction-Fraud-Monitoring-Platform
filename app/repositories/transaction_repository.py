from decimal import Decimal

from sqlalchemy.orm import Session
from app.models.transaction import Transaction, TransactionStatus
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from uuid import UUID
from sqlalchemy import func, Integer, cast, Date
from app.models.account import Account


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        transaction: TransactionCreate,
        fraud_result,
        status,
        timestamp,
    ):
        db_tx = Transaction(
            account_id=transaction.account_id,
            amount=transaction.amount,
            merchant=transaction.merchant,
            location=transaction.location,
            transaction_type=transaction.transaction_type,
            timestamp=timestamp,
            fraud_score=fraud_result["fraud_score"],
            fraud_decision=fraud_result["fraud_decision"],
            model_version=fraud_result.get("model_version"),
            model_threshold=fraud_result.get("model_threshold"),
            status=status,
        )

        try:
            self.db.add(db_tx)
            self.db.commit()
            self.db.refresh(db_tx)
            return db_tx

        except Exception:
            self.db.rollback()
            raise

    def get_all(
        self,
        user_id,
        page: int = 1,
        page_size: int = 10,
        status: TransactionStatus | None = None,
    ):
        query = (
            self.db.query(Transaction)
            .join(Account, Transaction.account_id == Account.id)
            .filter(Account.user_id == user_id)
        )

        if status is not None:
            query = query.filter(
                Transaction.status == status
            )

        total = query.count()

        transactions = (
            query
            .order_by(Transaction.timestamp.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        return transactions, total

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

    def get_transaction_history(self, account_id: UUID):
            return (
                self.db.query(Transaction)
                .filter(Transaction.account_id == account_id)
                .order_by(Transaction.timestamp.asc())
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

    def get_by_account_ids(
        self,
        account_ids: list[UUID],
        skip: int = 0,
        limit: int = 10
    ):
        query = (
            self.db.query(Transaction)
            .filter(Transaction.account_id.in_(account_ids))
        )

        total = query.count()

        transactions = (
            query
            .offset(skip)
            .limit(limit)
            .all()
        )

        return transactions, total

    def get_transaction_history(
        self,
        account_id: UUID
    ):
        return (
            self.db.query(Transaction)
            .filter(
                Transaction.account_id == account_id
            )
            .order_by(
                Transaction.timestamp.asc()
            )
            .all()
        )

    def get_dashboard_summary(self, user_id):
        result = (
            self.db.query(
                func.count(Transaction.id).label("total_transactions"),
                func.coalesce(
                    func.sum(Transaction.amount),
                    0,
                ).label("total_amount"),

                func.sum(
                    func.cast(
                        Transaction.status == TransactionStatus.APPROVED,
                        Integer,
                    )
                ).label("approved_transactions"),

                func.sum(
                    func.cast(
                        Transaction.status == TransactionStatus.REVIEW,
                        Integer,
                    )
                ).label("review_transactions"),

                func.sum(
                    func.cast(
                        Transaction.status == TransactionStatus.BLOCKED,
                        Integer,
                    )
                ).label("blocked_transactions"),

                func.sum(
                    func.cast(
                        Transaction.status == TransactionStatus.PENDING,
                        Integer,
                    )
                ).label("pending_transactions"),
            )
            .join(
                Account,
                Transaction.account_id == Account.id,
            )
            .filter(Account.user_id == user_id)
            .one()
        )

        total_transactions = result.total_transactions or 0

        approved_transactions = (
            result.approved_transactions or 0
        )

        review_transactions = (
            result.review_transactions or 0
        )

        blocked_transactions = (
            result.blocked_transactions or 0
        )

        pending_transactions = (
            result.pending_transactions or 0
        )

        # In the application fraud workflow,
        # REVIEW and BLOCKED represent suspicious transactions.
        fraud_transactions = (
            review_transactions + blocked_transactions
        )

        fraud_rate = (
            (fraud_transactions / total_transactions) * 100
            if total_transactions > 0
            else 0.0
        )

        return {
            "total_transactions": total_transactions,
            "total_amount": result.total_amount or Decimal("0.00"),

            "approved_transactions": approved_transactions,
            "review_transactions": review_transactions,
            "blocked_transactions": blocked_transactions,
            "pending_transactions": pending_transactions,

            "fraud_transactions": fraud_transactions,
            "fraud_rate": fraud_rate,
        }

    def get_transaction_trends(self, user_id):
        results = (
            self.db.query(
                cast(Transaction.timestamp, Date).label("date"),
                func.count(Transaction.id).label("transactions"),
                func.coalesce(func.sum(Transaction.amount), 0).label("amount"),
            )
            .join(
                Account,
                Transaction.account_id == Account.id,
            )
            .filter(Account.user_id == user_id)
            .group_by(cast(Transaction.timestamp, Date))
            .order_by(cast(Transaction.timestamp, Date))
            .all()
        )

        return [
            {
                "date": row.date,
                "transactions": row.transactions,
                "amount": row.amount,
            }
            for row in results
        ]

    def get_fraud_distribution(self, user_id):
        results = (
            self.db.query(
                Transaction.status.label("status"),
                func.count(Transaction.id).label("count"),
            )
            .join(
                Account,
                Transaction.account_id == Account.id,
            )
            .filter(Account.user_id == user_id)
            .group_by(Transaction.status)
            .order_by(Transaction.status)
            .all()
        )

        return [
            {
                "status": row.status.value
                if hasattr(row.status, "value")
                else row.status,
                "count": row.count,
            }
            for row in results
        ]