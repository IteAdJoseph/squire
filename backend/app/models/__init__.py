# Importar todos os models garante que estejam registrados no Base.metadata
# antes do Alembic gerar/aplicar migrations.
from app.database import Base
from app.models.appointment import Appointment
from app.models.audit_log import AuditLog
from app.models.billing import BillingAccount, BillingPayment
from app.models.charge import Charge
from app.models.customer import Customer
from app.models.enums import (
    AccessStatus,
    AppointmentStatus,
    BillingProvider,
    BillingStatus,
    ChargeStatus,
    ChargeType,
    ReminderStatus,
    UserRole,
)
from app.models.reminder import Reminder
from app.models.service import Service
from app.models.tenant import Tenant
from app.models.user import User

__all__ = [
    "Base",
    "Tenant",
    "BillingAccount",
    "BillingPayment",
    "User",
    "Customer",
    "Service",
    "Appointment",
    "Charge",
    "Reminder",
    "AuditLog",
    "AccessStatus",
    "BillingStatus",
    "BillingProvider",
    "UserRole",
    "AppointmentStatus",
    "ChargeType",
    "ChargeStatus",
    "ReminderStatus",
]
