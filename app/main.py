from fastapi import FastAPI, Request
# Import all models so SQLAlchemy registers all tables
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction

from app.api.users import router as users_router
from app.api.accounts import router as account_router
from app.api.transactions import router as transaction_router
from app.api.auth import router as auth_router

from app.schemas.error import ErrorResponse
from fastapi.responses import JSONResponse
from app.exceptions import (
    DuplicateAccountError,
    InsufficientBalanceError,
    TransactionAlreadyProcessedError,
    AccountAccessDeniedError,
    TransactionAccessDeniedError,
)
import logging

logger = logging.getLogger(__name__)



app = FastAPI(
    title="Financial Fraud Monitoring Platform",
    version="1.0.0"
)

@app.exception_handler(DuplicateAccountError)
async def duplicate_account_handler(
    request: Request,
    exc: DuplicateAccountError
):
    return JSONResponse(
        status_code=409,
        content={
            "error": "DUPLICATE_ACCOUNT",
            "message": str(exc)
        }
    )


@app.exception_handler(InsufficientBalanceError)
async def insufficient_balance_handler(
    request: Request,
    exc: InsufficientBalanceError
):
    return JSONResponse(
        status_code=400,
        content={
            "error": "INSUFFICIENT_BALANCE",
            "message": str(exc)
        }
    )


@app.exception_handler(TransactionAlreadyProcessedError)
async def transaction_already_processed_handler(
    request: Request,
    exc: TransactionAlreadyProcessedError
):
    return JSONResponse(
        status_code=409,
        content={
            "error": "TRANSACTION_ALREADY_PROCESSED",
            "message": str(exc)
        }
    )


@app.exception_handler(AccountAccessDeniedError)
async def account_access_denied_handler(
    request: Request,
    exc: AccountAccessDeniedError
):
    return JSONResponse(
        status_code=403,
        content={
            "error": "ACCOUNT_ACCESS_DENIED",
            "message": str(exc)
        }
    )


@app.exception_handler(TransactionAccessDeniedError)
async def transaction_access_denied_handler(
    request: Request,
    exc: TransactionAccessDeniedError
):
    return JSONResponse(
        status_code=403,
        content={
            "error": "TRANSACTION_ACCESS_DENIED",
            "message": str(exc)
        }
    )


@app.exception_handler(Exception)
async def generic_exception_handler(
    request: Request,
    exc: Exception
):
    logger.exception(
        "Unhandled exception occurred while processing %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred"
        }
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
