from app.db.database import SessionLocal
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction


def test_user_account_transaction_relationship():
    db = SessionLocal()

    try:
        user = db.query(User).first()

        assert user is not None

        print("\nUser:", user.name)
        print("Number of accounts:", len(user.accounts))

        for account in user.accounts:
            print("Account:", account.account_number)
            print("Balance:", account.balance)

            print("Transactions:", len(account.transactions))

            for transaction in account.transactions:
                print(
                    "Transaction:",
                    transaction.id,
                    transaction.amount,
                    transaction.status
                )

    finally:
        db.close()