from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import String, DateTime
from sqlalchemy.orm import mapped_column, Mapped
from app.db.database import Base
from uuid import uuid4,UUID

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False)
    phone: Mapped[str] = mapped_column(String(15), nullable=False)
    address: Mapped[str] = mapped_column(String(50), nullable=False)

    created_at: Mapped[datetime] = mapped_column( 
                DateTime(timezone=True), 
                default=lambda: datetime.now(timezone.utc),
                nullable=False
            )