from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.transaction_service import TransactionService
from app.schemas.transaction import TransactionCreate
from app.db.dependencies import get_db

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"]
)

@router.get("/")
def get_transactions():
    return {
        "transactions": []
    }

@router.post("/")
def add_transaction(transaction: TransactionCreate, db: Session=Depends(get_db)):
    transaction_service = TransactionService(
        transaction.amount, 
        transaction.merchant,
        transaction.location,
        transaction.transaction_type
        )
    return transaction_service.create_transaction()