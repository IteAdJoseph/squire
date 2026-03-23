import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import AccessStatus


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        sa.UUID(as_uuid=True),
        primary_key=True,
        server_default=sa.text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    slug: Mapped[str] = mapped_column(sa.String, unique=True, nullable=False)
    access_status: Mapped[AccessStatus] = mapped_column(
        sa.Enum(AccessStatus, name="access_status_enum", create_type=False),
        nullable=False,
        server_default=AccessStatus.enabled.value,
    )
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )
