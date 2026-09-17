from fastapi import APIRouter, Depends, HTTPException
from app.exceptions import DuplicateAccountError
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.dependencies import get_db
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.repositories.account_repository import AccountRepository
from app.services.account_service import AccountService
from app.repositories.user_repository import UserRepository


router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"]
)


@router.post("/", response_model=AccountResponse)
def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db)
):
    repository = AccountRepository(db)
    user_repository = UserRepository(db)
    service = AccountService(repository, user_repository)

    try:
        result = service.create_account(account)

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
    db: Session = Depends(get_db)
):
    repository = AccountRepository(db)
    user_repository = UserRepository(db)
    service = AccountService(repository, user_repository)

    return service.get_all_accounts()

@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: UUID,
    db: Session = Depends(get_db)
):
    repository = AccountRepository(db)
    user_repository = UserRepository(db)
    service = AccountService(repository, user_repository)
    account = service.get_account(account_id)

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
    db: Session = Depends(get_db)
):
    repository = AccountRepository(db)
    user_repository = UserRepository(db)
    service = AccountService(repository, user_repository)

    try:
        updated_account = service.update_account(
            account_id,
            account
        )

    except DuplicateAccountError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )

    if updated_account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    return updated_account

@router.delete("/{account_id}")
def delete_account(
    account_id: UUID,
    db: Session = Depends(get_db)
):
    repository = AccountRepository(db)
    user_repository = UserRepository(db)
    service = AccountService(repository, user_repository)

    deleted_account = service.delete_account(account_id)

    if deleted_account is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    return {
        "message": "Account deleted successfully",
        "account_id": account_id
    }