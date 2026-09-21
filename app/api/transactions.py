from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.transaction_repository import TransactionRepository 
from app.schemas.transaction import (
    TransactionCreate, 
    TransactionResponse, 
    TransactionUpdate,
    PaginatedResponse,
    
)
from app.models.transaction import TransactionStatus
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
from app.schemas.error import ErrorResponse


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.post("/",
    response_model=TransactionResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
    }
)
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

@router.get("/",
    response_model=PaginatedResponse[TransactionResponse],
    responses={
        401: {"model": ErrorResponse},
    }
)
def get_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: TransactionStatus | None = None,
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

    transactions, total = service.get_transactions_for_user(
        current_user.id,
        page,
        page_size
    )

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": transactions,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages
    }

@router.get("/{transaction_id}",
    response_model=TransactionResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    }
)
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

@router.get("/account/{account_id}",
    response_model=list[TransactionResponse],
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    }
)
def get_transactions_by_account(
    account_id: UUID,
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
        account = account_repository.get_by_id(account_id)

        if account is None:
            raise HTTPException(
                status_code=404,
                detail="Account not found"
            )

        if account.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You do not have access to this account"
            )

        return service.get_transactions_by_account(account_id)

    except HTTPException:
        raise

@router.put("/{transaction_id}",
    response_model=TransactionResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    }
)
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


@router.delete("/{transaction_id}",
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    }
)
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