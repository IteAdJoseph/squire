import uuid
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import BillingProvider, BillingStatus


class BillingAccount(Base):
    __tablename__ = "billing_accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
    )
    plan: Mapped[str] = mapped_column(sa.String, nullable=False)
    monthly_price: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    due_day: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    grace_days: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, server_default="5"
    )
    billing_status: Mapped[BillingStatus] = mapped_column(
        sa.Enum(BillingStatus, name="billing_status_enum", create_type=False),
        nullable=False,
        server_default=BillingStatus.trial.value,
    )
    provider: Mapped[BillingProvider] = mapped_column(
        sa.Enum(BillingProvider, name="billing_provider_enum", create_type=False),
        nullable=False,
        server_default=BillingProvider.manual_pix.value,
    )
    current_period_start: Mapped[sa.Date] = mapped_column(sa.Date, nullable=False)
    current_period_end: Mapped[sa.Date] = mapped_column(sa.Date, nullable=False)
    next_due_date: Mapped[sa.Date] = mapped_column(sa.Date, nullable=False)
    cancelled_at: Mapped[sa.DateTime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )
    updated_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )


class BillingPayment(Base):
    __tablename__ = "billing_payments"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    billing_account_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("billing_accounts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    paid_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )
