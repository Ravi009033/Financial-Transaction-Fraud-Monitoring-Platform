from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.transaction_service import TransactionService
from app.schemas.transaction import TransactionCreate
from app.db.dependencies import get_db
from app.repositories.transaction_repository import TransactionRepository  

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
    repository = TransactionRepository(db)
    service = TransactionService(repository)

    return service.create_transaction(transaction)