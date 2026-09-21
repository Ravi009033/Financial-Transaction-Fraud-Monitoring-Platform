from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    TransactionTrendsResponse,
    FraudDistributionResponse,
)
from app.services.dashboard_service import DashboardService
from app.repositories.transaction_repository import TransactionRepository
from app.security.dependencies import get_current_user


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    repository = TransactionRepository(db)
    service = DashboardService(repository)

    return service.get_summary(current_user.id)


@router.get(
    "/transaction-trends",
    response_model=TransactionTrendsResponse,
)
def get_transaction_trends(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    repository = TransactionRepository(db)
    service = DashboardService(repository)

    data = service.get_transaction_trends(current_user.id)

    return {"data": data}

@router.get(
    "/fraud-distribution",
    response_model=FraudDistributionResponse,
)
def get_fraud_distribution(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    repository = TransactionRepository(db)
    service = DashboardService(repository)

    data = service.get_fraud_distribution(current_user.id)

    return {"data": data}