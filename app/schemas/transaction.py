from datetime import datetime

from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum
from uuid import UUID
from typing import Generic, TypeVar

class TransactionType(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"

class TransactionCreate(BaseModel):
    account_id: UUID
    amount: Decimal = Field(gt=0, decimal_places=2)
    merchant: str = Field(min_length=2, max_length=100)
    location: str = Field(min_length=2, max_length=100)
    transaction_type: TransactionType


class TransactionResponse(BaseModel):
    id: UUID
    account_id: UUID
    amount: Decimal
    merchant: str
    location: str
    transaction_type: TransactionType
    timestamp: datetime
    status: str
    fraud_score: Decimal | None
    fraud_decision: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class TransactionUpdate(BaseModel):
    merchant: str = Field(min_length=2, max_length=100)
    location: str = Field(min_length=2, max_length=100)

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int