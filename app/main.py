from fastapi import FastAPI
# Import all models so SQLAlchemy registers all tables
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction

from app.api.users import router as users_router
from app.api.accounts import router as account_router
from app.api.transactions import router as transaction_router
from app.api.auth import router as auth_router

app = FastAPI(
    title="Financial Fraud Monitoring Platform",
    version="1.0.0"
)

app.include_router(transaction_router)
app.include_router(users_router)
app.include_router(account_router)
app.include_router(auth_router)

@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "message": "Fraud Monitoring API is running"

    }
