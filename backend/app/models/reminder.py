import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import ReminderStatus


class Reminder(Base):
    __tablename__ = "reminders"

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
    scheduled_for: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )
    sent_at: Mapped[sa.DateTime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    status: Mapped[ReminderStatus] = mapped_column(
        sa.Enum(ReminderStatus, name="reminder_status_enum", create_type=False),
        nullable=False,
        server_default=ReminderStatus.pending.value,
    )
    attempt_count: Mapped[int] = mapped_column(
        sa.Integer, nullable=False, server_default="0"
    )
    last_error: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )
