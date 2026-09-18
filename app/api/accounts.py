from fastapi import APIRouter, Depends, HTTPException
from app.exceptions import DuplicateAccountError, AccountAccessDeniedError
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.dependencies import get_db
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.repositories.account_repository import AccountRepository
from app.services.account_service import AccountService
from app.repositories.user_repository import UserRepository
from app.security.dependencies import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)


@router.post("/", response_model=AccountResponse)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = AccountRepository(db)
    user_repository = UserRepository(db)
    service = AccountService(repository, user_repository)

    try:
        result = service.create_account(account, current_user.id)

    except DuplicateAccountError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return result
    
@router.get("/", response_model=list[AccountResponse])
def get_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = AccountRepository(db)
    user_repository = UserRepository(db)
    service = AccountService(repository, user_repository)

    return service.get_accounts_by_user(current_user.id)

@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = AccountRepository(db)
    user_repository = UserRepository(db)
    service = AccountService(repository, user_repository)
    try:
        account = service.get_account_for_user(
            account_id,
            current_user.id
        )
    except AccountAccessDeniedError:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this account"
        )

    if account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    return account

@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: UUID,
    account: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = AccountRepository(db)
    user_repository = UserRepository(db)
    service = AccountService(repository, user_repository)

    try:
        # First verify ownership
        existing_account = service.get_account_for_user(
            account_id,
            current_user.id
        )
        if existing_account is None:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        # Then perform the update
        updated_account = service.update_account(
            account_id,
            account
        )
    except AccountAccessDeniedError:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this account"
        )

    except DuplicateAccountError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )

    return updated_account


@router.delete("/{account_id}")
def delete_account(
    account_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = AccountRepository(db)
    user_repository = UserRepository(db)
    service = AccountService(repository, user_repository)

    try:
        # Verify that the account belongs to the logged-in user
        account = service.get_account_for_user(
            account_id,
            current_user.id
        )

        if account is None:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        service.delete_account(account_id)

    except AccountAccessDeniedError:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this account"
        )

    return {
        "message": "Account deleted successfully",
        "account_id": account_id
    }