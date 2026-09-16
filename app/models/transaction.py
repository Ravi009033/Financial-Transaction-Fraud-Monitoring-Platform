from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4,UUID
from sqlalchemy import ForeignKey, String, Numeric, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from decimal import Decimal
from app.db.database import Base


class TransactionType(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"

class TransactionStatus(str, Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    BLOCKED = 'blocked'
    REVIEW = 'review'

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    account_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False) 
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    merchant: Mapped[str] = mapped_column(String(100), nullable=False) 
    location: Mapped[str] = mapped_column(String(100), nullable=False) 
    # Restricts database values to the TransactionType choices
    transaction_type: Mapped[TransactionType] = mapped_column(
        SQLEnum(TransactionType), 
        nullable=False
    )
    # Automatically tracks when the row is added using UTC time
    timestamp: Mapped[datetime] = mapped_column( 
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    status: Mapped[TransactionStatus] = mapped_column(
        SQLEnum(TransactionStatus), 
        default=TransactionStatus.PENDING,
        nullable=False
    )
    fraud_score: Mapped[Decimal | None] = mapped_column(Numeric(precision=5, scale=4), nullable=True) 
    fraud_decision: Mapped[str | None] = mapped_column(String(50), nullable=True) 
    created_at: Mapped[datetime] = mapped_column( 
            DateTime(timezone=True), 
            default=lambda: datetime.now(timezone.utc),
            nullable=False
        )