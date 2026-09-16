from sqlalchemy.orm import Session

from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate
from sqlalchemy.exc import IntegrityError
from app.exceptions import DuplicateAccountError

class AccountRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, account: AccountCreate):

        db_account = Account(
            account_number=account.account_number,
            user_id=account.user_id,
            balance=account.balance
        )

        self.db.add(db_account)
       
        try:
            self.db.commit()

        except IntegrityError:
            self.db.rollback()
            raise DuplicateAccountError("Account number already exists")


        self.db.refresh(db_account)

        return db_account

    def get_all(self):
        return self.db.query(Account).all()

    def get_by_id(self, account_id):
        return self.db.query(Account).filter(
            Account.id == account_id
        ).first()

    def get_by_account_number(self, account_number):
        return self.db.query(Account).filter(
            Account.account_number == account_number
        ).first()

    def update(self, account_id, account: AccountUpdate):

        db_account = self.get_by_id(account_id)

        if db_account is None:
            return None

        db_account.account_number = account.account_number
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise DuplicateAccountError("Account number already exists")
        
        self.db.refresh(db_account)

        return db_account

    def delete(self, account_id):

        db_account = self.get_by_id(account_id)

        if db_account is None:
            return None

        self.db.delete(db_account)
        self.db.commit()

        return db_account