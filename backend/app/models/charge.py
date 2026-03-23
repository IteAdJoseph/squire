import uuid
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import ChargeStatus, ChargeType


class Charge(Base):
    __tablename__ = "charges"

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
    appointment_id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("appointments.id", ondelete="RESTRICT"),
        nullable=False,
    )
    type: Mapped[ChargeType] = mapped_column(
        sa.Enum(ChargeType, name="charge_type_enum", create_type=False),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(sa.Numeric(10, 2), nullable=False)
    status: Mapped[ChargeStatus] = mapped_column(
        sa.Enum(ChargeStatus, name="charge_status_enum", create_type=False),
        nullable=False,
        server_default=ChargeStatus.pending.value,
    )
    # Reservado para integração futura com PSP (Asaas, etc.)
    # sem migration destrutiva (RB-06)
    external_ref: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    paid_at: Mapped[sa.DateTime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    expires_at: Mapped[sa.DateTime | None] = mapped_column(
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
