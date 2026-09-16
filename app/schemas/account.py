from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    account_number: str = Field(
        min_length=5,
        max_length=50
    )

    user_id: UUID

    balance: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2
    )


class AccountResponse(BaseModel):
    id: UUID
    account_number: str
    user_id: UUID
    balance: Decimal
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AccountUpdate(BaseModel):
    account_number: str = Field(
        min_length=5,
        max_length=50
    )