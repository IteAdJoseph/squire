import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import AppointmentStatus, ChargeStatus, ChargeType


class CustomerCreateIn(BaseModel):
    name: str
    phone: str
    notes: str | None = None


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    phone: str
    notes: str | None
    is_active: bool
    created_at: datetime


class ServiceCreateIn(BaseModel):
    name: str
    duration_minutes: Annotated[int, Field(gt=0)]
    total_price: Annotated[Decimal, Field(ge=0)]
    deposit_amount: Annotated[Decimal, Field(ge=0)] = Decimal("0")

    @field_validator("deposit_amount")
    @classmethod
    def validate_deposit(cls, value: Decimal, info: object) -> Decimal:
        total = getattr(info, "data", {}).get("total_price")
        if total is not None and value > total:
            raise ValueError("deposit_amount deve ser <= total_price")
        return value


class ServiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    duration_minutes: int
    total_price: Decimal
    deposit_amount: Decimal
    is_active: bool
    created_at: datetime


class AppointmentCreateIn(BaseModel):
    customer_id: uuid.UUID
    service_id: uuid.UUID
    scheduled_at: datetime
    notes: str | None = None


class ChargeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    appointment_id: uuid.UUID
    type: ChargeType
    amount: Decimal
    status: ChargeStatus
    external_ref: str | None
    paid_at: datetime | None
    expires_at: datetime | None
    created_at: datetime
    updated_at: datetime


class AppointmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    customer_id: uuid.UUID
    service_id: uuid.UUID
    scheduled_at: datetime
    total_price: Decimal
    deposit_amount: Decimal
    balance_amount: Decimal
    status: AppointmentStatus
    notes: str | None
    created_at: datetime
    updated_at: datetime


class AppointmentDetailOut(BaseModel):
    appointment: AppointmentOut
    charges: list[ChargeOut]


class AppointmentListFilters(BaseModel):
    status: AppointmentStatus | None = None
    date_from: date | None = None
    date_to: date | None = None


class ConfirmChargeIn(BaseModel):
    paid_at: datetime | None = None
