from pydantic import BaseModel, Field
from decimal import Decimal
from enum import Enum
from uuid import UUID

class TransactionType(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"

class TransactionCreate(BaseModel):
    account_id: UUID
    amount: Decimal = Field(gt=0)
    merchant: str = Field(min_length=2, max_length=100)
    location: str = Field(min_length=2, max_length=100)
    transaction_type: TransactionType
   