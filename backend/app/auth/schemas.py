import uuid

from pydantic import BaseModel

from app.models.enums import BillingStatus, UserRole


class LoginIn(BaseModel):
    tenant_slug: str
    username: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeOut(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    role: UserRole
    tenant_id: uuid.UUID
    tenant_name: str
    billing_status: BillingStatus | None
