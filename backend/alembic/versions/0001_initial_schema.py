"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-23

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ── Enum types ────────────────────────────────────────────────────────────
    op.execute("CREATE TYPE access_status_enum AS ENUM ('enabled', 'disabled')")
    op.execute(
        "CREATE TYPE billing_status_enum AS ENUM "
        "('trial', 'active', 'grace', 'late', 'suspended', 'cancelled')"
    )
    op.execute("CREATE TYPE billing_provider_enum AS ENUM ('manual_pix')")
    op.execute("CREATE TYPE user_role_enum AS ENUM ('owner', 'admin', 'operator')")
    op.execute(
        "CREATE TYPE appointment_status_enum AS ENUM "
        "('draft', 'awaiting_deposit', 'confirmed', 'completed', "
        "'no_show', 'cancelled')"
    )
    op.execute("CREATE TYPE charge_type_enum AS ENUM ('deposit', 'balance')")
    op.execute(
        "CREATE TYPE charge_status_enum AS ENUM "
        "('pending', 'paid', 'expired', 'cancelled')"
    )
    op.execute("CREATE TYPE reminder_status_enum AS ENUM ('pending', 'sent', 'failed')")

    # ── tenants ───────────────────────────────────────────────────────────────
    op.create_table(
        "tenants",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("slug", sa.String, nullable=False),
        sa.Column(
            "access_status",
            PgEnum(name="access_status_enum", create_type=False),
            nullable=False,
            server_default="enabled",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("slug", name="uq_tenants_slug"),
    )

    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "tenant_id",
            sa.UUID(),
            sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("email", sa.String, nullable=False),
        sa.Column("username", sa.String, nullable=False),
        sa.Column("hashed_password", sa.String, nullable=False),
        sa.Column(
            "role",
            PgEnum(name="user_role_enum", create_type=False),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
        sa.UniqueConstraint("tenant_id", "username", name="uq_users_tenant_username"),
    )

    # ── billing_accounts ──────────────────────────────────────────────────────
    op.create_table(
        "billing_accounts",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "tenant_id",
            sa.UUID(),
            sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
            unique=True,
            nullable=False,
        ),
        sa.Column("plan", sa.String, nullable=False),
        sa.Column("monthly_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("due_day", sa.Integer, nullable=False),
        sa.Column("grace_days", sa.Integer, nullable=False, server_default="5"),
        sa.Column(
            "billing_status",
            PgEnum(name="billing_status_enum", create_type=False),
            nullable=False,
            server_default="trial",
        ),
        sa.Column(
            "provider",
            PgEnum(name="billing_provider_enum", create_type=False),
            nullable=False,
            server_default="manual_pix",
        ),
        sa.Column("current_period_start", sa.Date, nullable=False),
        sa.Column("current_period_end", sa.Date, nullable=False),
        sa.Column("next_due_date", sa.Date, nullable=False),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # ── billing_payments ──────────────────────────────────────────────────────
    op.create_table(
        "billing_payments",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "billing_account_id",
            sa.UUID(),
            sa.ForeignKey("billing_accounts.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_by",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # ── customers ─────────────────────────────────────────────────────────────
    op.create_table(
        "customers",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "tenant_id",
            sa.UUID(),
            sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("phone", sa.String, nullable=False),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # ── services ──────────────────────────────────────────────────────────────
    op.create_table(
        "services",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "tenant_id",
            sa.UUID(),
            sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("duration_minutes", sa.Integer, nullable=False),
        sa.Column("total_price", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "deposit_amount", sa.Numeric(10, 2), nullable=False, server_default="0"
        ),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # ── appointments ──────────────────────────────────────────────────────────
    op.create_table(
        "appointments",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "tenant_id",
            sa.UUID(),
            sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "customer_id",
            sa.UUID(),
            sa.ForeignKey("customers.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "service_id",
            sa.UUID(),
            sa.ForeignKey("services.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("total_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("deposit_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("balance_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "status",
            PgEnum(name="appointment_status_enum", create_type=False),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # ── charges ───────────────────────────────────────────────────────────────
    op.create_table(
        "charges",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "tenant_id",
            sa.UUID(),
            sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "appointment_id",
            sa.UUID(),
            sa.ForeignKey("appointments.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "type",
            PgEnum(name="charge_type_enum", create_type=False),
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column(
            "status",
            PgEnum(name="charge_status_enum", create_type=False),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("external_ref", sa.String, nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # ── reminders ─────────────────────────────────────────────────────────────
    op.create_table(
        "reminders",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "tenant_id",
            sa.UUID(),
            sa.ForeignKey("tenants.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "appointment_id",
            sa.UUID(),
            sa.ForeignKey("appointments.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            PgEnum(name="reminder_status_enum", create_type=False),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("attempt_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # ── audit_logs ────────────────────────────────────────────────────────────
    op.create_table(
        "audit_logs",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "tenant_id",
            sa.UUID(),
            sa.ForeignKey("tenants.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "user_id",
            sa.UUID(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("entity_type", sa.String, nullable=False),
        sa.Column("entity_id", sa.UUID(), nullable=False),
        sa.Column("action", sa.String, nullable=False),
        sa.Column("before", sa.JSON, nullable=True),
        sa.Column("after", sa.JSON, nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("reminders")
    op.drop_table("charges")
    op.drop_table("appointments")
    op.drop_table("services")
    op.drop_table("customers")
    op.drop_table("billing_payments")
    op.drop_table("billing_accounts")
    op.drop_table("users")
    op.drop_table("tenants")

    op.execute("DROP TYPE reminder_status_enum")
    op.execute("DROP TYPE charge_status_enum")
    op.execute("DROP TYPE charge_type_enum")
    op.execute("DROP TYPE appointment_status_enum")
    op.execute("DROP TYPE user_role_enum")
    op.execute("DROP TYPE billing_provider_enum")
    op.execute("DROP TYPE billing_status_enum")
    op.execute("DROP TYPE access_status_enum")
