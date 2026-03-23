import uuid

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        sa.UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
        sa.UniqueConstraint("tenant_id", "username", name="uq_users_tenant_username"),
    )

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
    email: Mapped[str] = mapped_column(sa.String, nullable=False)
    username: Mapped[str] = mapped_column(sa.String, nullable=False)
    hashed_password: Mapped[str] = mapped_column(sa.String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        sa.Enum(UserRole, name="user_role_enum", create_type=False),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.true()
    )
    created_at: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        server_default=sa.func.now(),
    )
