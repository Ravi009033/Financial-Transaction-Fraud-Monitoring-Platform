from fastapi import FastAPI
from app.api.transactions import router as transaction_router

app = FastAPI(
    title="Financial Fraud Monitoring Platform",
    version="1.0.0"
)

app.include_router(transaction_router)


@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "message": "Fraud Monitoring API is running"

    }
