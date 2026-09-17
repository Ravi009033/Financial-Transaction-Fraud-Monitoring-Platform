from datetime import datetime, timezone
from uuid import uuid4,UUID
from sqlalchemy import ForeignKey, Numeric, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from decimal import Decimal
from app.db.database import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.transaction import Transaction

class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    account_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True),ForeignKey("users.id"), nullable=False) 
    balance: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column( 
            DateTime(timezone=True), 
            default=lambda: datetime.now(timezone.utc),
            nullable=False
        )
    user: Mapped["User"] = relationship("User", back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(
                                    "Transaction",
                                    back_populates="account"
                                )