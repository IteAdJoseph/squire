from enum import Enum


class AccessStatus(str, Enum):
    enabled = "enabled"
    disabled = "disabled"


class BillingStatus(str, Enum):
    trial = "trial"
    active = "active"
    grace = "grace"
    late = "late"
    suspended = "suspended"
    cancelled = "cancelled"


class BillingProvider(str, Enum):
    manual_pix = "manual_pix"


class UserRole(str, Enum):
    owner = "owner"
    admin = "admin"
    operator = "operator"


class AppointmentStatus(str, Enum):
    draft = "draft"
    awaiting_deposit = "awaiting_deposit"
    confirmed = "confirmed"
    completed = "completed"
    no_show = "no_show"
    cancelled = "cancelled"


class ChargeType(str, Enum):
    deposit = "deposit"
    balance = "balance"


class ChargeStatus(str, Enum):
    pending = "pending"
    paid = "paid"
    expired = "expired"
    cancelled = "cancelled"


class ReminderStatus(str, Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"
