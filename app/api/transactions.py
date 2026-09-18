from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.transaction_repository import TransactionRepository 
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate
from app.security.dependencies import get_current_user
from app.services.transaction_service import TransactionService
from app.services.fraud_service import FraudDetectionService
from app.repositories.account_repository import AccountRepository
from app.db.dependencies import get_db 
from uuid import UUID
from app.exceptions import (
    InsufficientBalanceError, 
    TransactionAlreadyProcessedError,
    TransactionAccessDeniedError
)


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.post("/", response_model=TransactionResponse)
def add_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    transaction_repository = TransactionRepository(db)
    account_repository = AccountRepository(db)
    fraud_service = FraudDetectionService()

    service = TransactionService(
        transaction_repository,
        account_repository,
        fraud_service
    )

    try:
        result = service.create_transaction(
            transaction,
            current_user.id
        )

    except InsufficientBalanceError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except TransactionAccessDeniedError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    return result

@router.get("/", response_model=list[TransactionResponse])
def get_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = TransactionRepository(db)
    account_repository = AccountRepository(db)
    fraud_service = FraudDetectionService()

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    return service.get_transactions_for_user(
        current_user.id
    )

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = TransactionRepository(db)
    account_repository = AccountRepository(db)
    fraud_service = FraudDetectionService()

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    try:
        transaction = service.get_transaction_for_user(
            transaction_id,
            current_user.id
        )

    except TransactionAccessDeniedError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return transaction

@router.get("/account/{account_id}")
def get_transactions_by_account(
    account_id: UUID,
    db: Session = Depends(get_db)
):
    repository = TransactionRepository(db)
    account_repository = AccountRepository(db)
    fraud_service = FraudDetectionService()

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    return service.get_transactions_by_account(account_id)


@router.put("/{transaction_id}")
def update_transaction(
    transaction_id: UUID,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = TransactionRepository(db)
    account_repository = AccountRepository(db)
    fraud_service = FraudDetectionService()

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    try:
        updated_transaction = service.update_transaction_for_user(
            transaction_id,
            transaction,
            current_user.id
        )

    except TransactionAccessDeniedError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )

    except TransactionAlreadyProcessedError as e:
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )

    if updated_transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return updated_transaction


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    repository = TransactionRepository(db)
    account_repository = AccountRepository(db)
    fraud_service = FraudDetectionService()

    service = TransactionService(
        repository,
        account_repository,
        fraud_service
    )

    try:
        deleted_transaction = service.delete_transaction_for_user(
            transaction_id,
            current_user.id
        )

    except TransactionAccessDeniedError as e:
        raise HTTPException(
            status_code=403,
            detail=str(e)
        )

    if deleted_transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return {
        "message": "Transaction deleted successfully",
        "transaction_id": transaction_id
    }