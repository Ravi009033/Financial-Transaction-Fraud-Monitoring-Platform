from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: str = Field(min_length=5, max_length=50)
    phone: str = Field(min_length=10, max_length=15)
    address: str = Field(min_length=2, max_length=50)

class UserUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: str = Field(min_length=5, max_length=50)
    phone: str = Field(min_length=10, max_length=15)
    address: str = Field(min_length=2, max_length=50)

class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    phone: str
    address: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)