from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.schemas import LoginIn, MeOut, TokenOut
from app.core.security import create_access_token, verify_password
from app.database import get_db
from app.dependencies import CurrentUser
from app.models.billing import BillingAccount
from app.models.enums import AccessStatus, BillingStatus
from app.models.tenant import Tenant
from app.models.user import User

_BLOCKED_BILLING = {
    BillingStatus.late,
    BillingStatus.suspended,
    BillingStatus.cancelled,
}

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    tenant = db.scalar(select(Tenant).where(Tenant.slug == body.tenant_slug))
    if tenant is None or tenant.access_status == AccessStatus.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )

    user = db.scalar(
        select(User).where(
            User.tenant_id == tenant.id,
            User.username == body.username,
        )
    )
    if (
        user is None
        or not user.is_active
        or not verify_password(body.password, user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
        )

    billing = db.scalar(
        select(BillingAccount).where(BillingAccount.tenant_id == tenant.id)
    )
    if billing is None or billing.billing_status in _BLOCKED_BILLING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso bloqueado: verifique o status da conta",
        )

    return TokenOut(access_token=create_access_token(str(user.id), str(tenant.id)))


@router.get("/me", response_model=MeOut)
def me(current_user: CurrentUser, db: Session = Depends(get_db)) -> MeOut:
    tenant = db.get(Tenant, current_user.tenant_id)
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Tenant não encontrado",
        )
    billing = db.scalar(
        select(BillingAccount).where(BillingAccount.tenant_id == current_user.tenant_id)
    )
    return MeOut(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        tenant_id=current_user.tenant_id,
        tenant_name=tenant.name,
        billing_status=billing.billing_status if billing else None,
    )
