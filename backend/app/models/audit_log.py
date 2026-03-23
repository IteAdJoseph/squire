import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    # Nullable: ações globais do admin (A1) não pertencem a um tenant
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("tenants.id", ondelete="SET NULL"),
        nullable=True,
    )
    # Nullable: ações do sistema não têm usuário
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        sa.UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    entity_type: Mapped[str] = mapped_column(sa.String, nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(sa.UUID(as_uuid=True), nullable=False)
    action: Mapped[str] = mapped_column(sa.String, nullable=False)
    before: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    after: Mapped[dict | None] = mapped_column(sa.JSON, nullable=True)
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )
