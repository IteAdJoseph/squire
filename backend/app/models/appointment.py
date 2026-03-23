import uuid
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import AppointmentStatus


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("services.id", ondelete="RESTRICT"),
        nullable=False,
    )
    scheduled_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )
    # Snapshot de valores no momento da criação (RB-10)
    total_price: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    deposit_amount: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    balance_amount: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        sa.Enum(AppointmentStatus, name="appointment_status_enum", create_type=False),
        nullable=False,
        server_default=AppointmentStatus.draft.value,
    )
    notes: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
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
