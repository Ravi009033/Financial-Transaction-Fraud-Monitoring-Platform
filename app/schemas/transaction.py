from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4, UUID

class TransactionType(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"

class TransactionCreate(BaseModel):
    transaction_id: UUID = Field(default_factory=uuid4)
    account_id: str = Field(..., description="Associated account identifier")
    amount: Decimal = Field(gt=0) 
    merchant: str = Field(min_length=2, max_length=100)
    location: str = Field(min_length=2, max_length=100)
    transaction_type: TransactionType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))