"""create initial database schema

Revision ID: be5564fec090
Revises:
Create Date: 2026-09-19 14:18:08.731260

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "be5564fec090"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema."""

    transaction_type = postgresql.ENUM(
        "ONLINE",
        "OFFLINE",
        name="transactiontype",
        create_type=False,
    )

    transaction_status = postgresql.ENUM(
        "PENDING",
        "APPROVED",
        "BLOCKED",
        "REVIEW",
        name="transactionstatus",
        create_type=False,
    )

    transaction_type.create(
        op.get_bind(),
        checkfirst=True,
    )

    transaction_status.create(
        op.get_bind(),
        checkfirst=True,
    )

    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "phone",
            sa.String(length=15),
            nullable=False,
        ),
        sa.Column(
            "address",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "accounts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "account_number",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "balance",
            sa.Numeric(
                precision=12,
                scale=2,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_number"),
    )

    op.create_table(
        "transactions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "account_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "amount",
            sa.Numeric(
                precision=12,
                scale=2,
            ),
            nullable=False,
        ),
        sa.Column(
            "merchant",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "location",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "transaction_type",
            transaction_type,
            nullable=False,
        ),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "status",
            transaction_status,
            nullable=False,
        ),
        sa.Column(
            "fraud_score",
            sa.Numeric(
                precision=5,
                scale=4,
            ),
            nullable=True,
        ),
        sa.Column(
            "fraud_decision",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["account_id"],
            ["accounts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Drop initial database schema."""

    op.drop_table("transactions")
    op.drop_table("accounts")
    op.drop_table("users")

    transaction_status = postgresql.ENUM(
        "PENDING",
        "APPROVED",
        "BLOCKED",
        "REVIEW",
        name="transactionstatus",
    )

    transaction_type = postgresql.ENUM(
        "ONLINE",
        "OFFLINE",
        name="transactiontype",
    )

    transaction_status.drop(
        op.get_bind(),
        checkfirst=True,
    )

    transaction_type.drop(
        op.get_bind(),
        checkfirst=True,
    )