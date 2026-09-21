from decimal import Decimal
from datetime import date
from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    total_transactions: int
    total_amount: Decimal
    approved_transactions: int
    review_transactions: int
    blocked_transactions: int
    pending_transactions: int
    fraud_transactions: int
    fraud_rate: float

class TransactionTrend(BaseModel):
    date: date
    transactions: int
    amount: Decimal


class TransactionTrendsResponse(BaseModel):
    data: list[TransactionTrend]

class FraudDistributionItem(BaseModel):
    status: str
    count: int

class FraudDistributionResponse(BaseModel):
    data: list[FraudDistributionItem]