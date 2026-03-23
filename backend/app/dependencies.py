import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.billing import BillingAccount
from app.models.enums import AccessStatus, BillingStatus
from app.models.tenant import Tenant
from app.models.user import User

_bearer = HTTPBearer()

_BLOCKED_BILLING = {
    BillingStatus.late,
    BillingStatus.suspended,
    BillingStatus.cancelled,
}


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = str(payload["sub"])
    except (JWTError, KeyError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
        )
    user = db.get(User, uuid.UUID(user_id))
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
        )
    return user


def require_active_tenant(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> User:
    """Usado em endpoints operacionais. Revalida acesso do tenant a cada request."""
    tenant = db.get(Tenant, current_user.tenant_id)
    if tenant is None or tenant.access_status == AccessStatus.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso bloqueado",
        )
    billing = db.scalar(
        select(BillingAccount).where(BillingAccount.tenant_id == current_user.tenant_id)
    )
    if billing is None or billing.billing_status in _BLOCKED_BILLING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso bloqueado: verifique o status da conta",
        )
    return current_user


CurrentUser = Annotated[User, Depends(get_current_user)]
ActiveTenantUser = Annotated[User, Depends(require_active_tenant)]
