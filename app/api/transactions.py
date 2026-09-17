from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.repositories.transaction_repository import TransactionRepository 
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate
from app.services.transaction_service import TransactionService
from app.services.fraud_service import FraudDetectionService
from app.repositories.account_repository import AccountRepository
from app.db.dependencies import get_db 
from uuid import UUID
from app.exceptions import InsufficientBalanceError, TransactionAlreadyProcessedError


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.post("/", response_model=TransactionResponse)
def add_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
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
        result = service.create_transaction(transaction)
    except InsufficientBalanceError as e:
        raise HTTPException(
            status_code=400,
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

    return service.get_all_transactions()

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: UUID,
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

    transaction = service.get_transaction(transaction_id)

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
    try:
        updated_transaction = service.update_transaction(
            transaction_id,
            transaction
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

    deleted_transaction = service.delete_transaction(transaction_id)

    if deleted_transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return {
        "message": "Transaction deleted successfully",
        "transaction_id": transaction_id
    }