import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import (
    AccessStatus,
    BillingProvider,
    BillingStatus,
    UserRole,
)

# --- Input schemas ---


class CreateTenantIn(BaseModel):
    name: str
    slug: str


class CreateUserIn(BaseModel):
    email: str
    username: str
    password: str
    role: UserRole = UserRole.owner


class CreateBillingIn(BaseModel):
    plan: str
    monthly_price: Decimal
    due_day: int
    grace_days: int = 5
    provider: BillingProvider = BillingProvider.manual_pix

    @field_validator("due_day")
    @classmethod
    def validate_due_day(cls, v: int) -> int:
        if not 1 <= v <= 28:
            raise ValueError("due_day must be between 1 and 28")
        return v


class PaymentIn(BaseModel):
    amount: Annotated[Decimal, Field(gt=0)]
    paid_at: datetime
    notes: str | None = None


# --- Output schemas ---


class TenantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    access_status: AccessStatus
    created_at: datetime


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    username: str
    role: UserRole
    is_active: bool
    created_at: datetime


class BillingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    plan: str
    monthly_price: Decimal
    due_day: int
    grace_days: int
    billing_status: BillingStatus
    provider: BillingProvider
    current_period_start: date
    current_period_end: date
    next_due_date: date
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TenantListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    slug: str
    access_status: AccessStatus
    billing_status: BillingStatus | None
    created_at: datetime


class TenantDetail(BaseModel):
    tenant: TenantOut
    user: UserOut | None
    billing: BillingOut | None
