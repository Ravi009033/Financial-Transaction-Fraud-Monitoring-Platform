from uuid import UUID
from app.exceptions import DuplicateAccountError, AccountAccessDeniedError
from app.repositories.account_repository import AccountRepository
from app.schemas.account import AccountCreate, AccountUpdate
from app.repositories.user_repository import UserRepository


class AccountService:

    def __init__(self, repository: AccountRepository, user_repository: UserRepository):
        self.repository = repository
        self.user_repository = user_repository

    def create_account(self, account: AccountCreate, user_id: UUID):
        user = self.user_repository.get_by_id(user_id)

        if user is None:
            return None
        return self.repository.create(account, user_id)

    def get_all_accounts(self):
        return self.repository.get_all()

    def get_account(self, account_id):
        return self.repository.get_by_id(account_id)

    def update_account(self, account_id, account: AccountUpdate):
        # 1. Check whether target account exists
        db_account = self.repository.get_by_id(account_id)

        if db_account is None:
            return None

        # 2. Check whether account number belongs to another account
        existing_account = self.repository.get_by_account_number(account.account_number)

        if existing_account is not None:
            if existing_account.id != account_id:
                raise DuplicateAccountError("Account number already exists")
            
        return self.repository.update(account_id, account)

    def delete_account(self, account_id):
        return self.repository.delete(account_id)

    def get_accounts_by_user(self, user_id: UUID):
        return self.repository.get_by_user_id(user_id)

    def get_account_for_user(self, account_id: UUID, user_id: UUID):
        account = self.repository.get_by_id(account_id)

        if account is None:
            return None

        if account.user_id != user_id:
            raise AccountAccessDeniedError(
                "You do not have access to this account"
            )

        return account