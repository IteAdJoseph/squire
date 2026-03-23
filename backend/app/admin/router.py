import calendar
import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.admin.schemas import (
    BillingOut,
    CreateBillingIn,
    CreateTenantIn,
    CreateUserIn,
    PaymentIn,
    TenantDetail,
    TenantListItem,
    TenantOut,
    UserOut,
)
from app.core.security import hash_password
from app.database import get_db
from app.dependencies import AdminUser
from app.models.audit_log import AuditLog
from app.models.billing import BillingAccount, BillingPayment
from app.models.enums import AccessStatus, BillingStatus
from app.models.tenant import Tenant
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])

DbSession = Annotated[Session, Depends(get_db)]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _next_due_date(
    due_day: int, *, _today: date | None = None
) -> tuple[date, date, date]:
    """Return (period_start, period_end, next_due_date) for initial billing setup.

    Uses ``_today`` to allow deterministic unit-testing without patching.
    For advancing an existing cycle after payment use _advance_billing_cycle.
    """
    today = _today if _today is not None else date.today()
    year, month = today.year, today.month

    last_day = calendar.monthrange(year, month)[1]
    effective = min(due_day, last_day)

    if today.day <= effective:
        next_due = date(year, month, effective)
    else:
        if month == 12:
            ny, nm = year + 1, 1
        else:
            ny, nm = year, month + 1
        ld = calendar.monthrange(ny, nm)[1]
        next_due = date(ny, nm, min(due_day, ld))

    period_start = today
    period_end = next_due - timedelta(days=1)
    return period_start, period_end, next_due


def _advance_billing_cycle(
    current_due: date,
    due_day: int,
    *,
    _today: date | None = None,
) -> tuple[date, date, date]:
    """Avança o ciclo mês a mês a partir de current_due até next_due > today.

    Usado em record_payment: cada pagamento quita todos os ciclos em aberto.
    Quando o tenant está mais de 1 mês atrasado, avança múltiplos ciclos para
    garantir que o novo período começa depois da data do pagamento.
    _today permite testes determinísticos.
    """
    today = _today if _today is not None else date.today()
    year, month = current_due.year, current_due.month
    while True:
        if month == 12:
            ny, nm = year + 1, 1
        else:
            ny, nm = year, month + 1
        ld = calendar.monthrange(ny, nm)[1]
        next_due = date(ny, nm, min(due_day, ld))
        if next_due > today:
            break
        year, month = next_due.year, next_due.month
    return today, next_due - timedelta(days=1), next_due


def _audit(
    db: Session,
    *,
    admin_user_id: uuid.UUID,
    entity_type: str,
    entity_id: uuid.UUID,
    action: str,
    before: dict | None = None,
    after: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            tenant_id=None,
            user_id=admin_user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            before=before,
            after=after,
        )
    )


# ---------------------------------------------------------------------------
# UC-01: Create tenant
# ---------------------------------------------------------------------------


@router.post(
    "/tenants",
    response_model=TenantOut,
    status_code=status.HTTP_201_CREATED,
)
def create_tenant(body: CreateTenantIn, db: DbSession, admin: AdminUser) -> Tenant:
    if db.scalar(select(Tenant).where(Tenant.slug == body.slug)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Slug já existe",
        )
    tenant = Tenant(name=body.name, slug=body.slug)
    db.add(tenant)
    db.flush()
    _audit(
        db,
        admin_user_id=admin.id,
        entity_type="tenant",
        entity_id=tenant.id,
        action="create",
        after={"name": tenant.name, "slug": tenant.slug},
    )
    db.commit()
    db.refresh(tenant)
    return tenant


# ---------------------------------------------------------------------------
# UC-02: Create initial user for tenant
# ---------------------------------------------------------------------------


@router.post(
    "/tenants/{tenant_id}/users",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    tenant_id: uuid.UUID,
    body: CreateUserIn,
    db: DbSession,
    admin: AdminUser,
) -> User:
    if db.get(Tenant, tenant_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant não encontrado",
        )
    if db.scalar(
        select(User).where(
            User.tenant_id == tenant_id,
            User.username == body.username,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username já existe neste tenant",
        )
    if db.scalar(
        select(User).where(
            User.tenant_id == tenant_id,
            User.email == body.email,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já existe neste tenant",
        )
    user = User(
        tenant_id=tenant_id,
        email=body.email,
        username=body.username,
        hashed_password=hash_password(body.password),
        role=body.role,
    )
    db.add(user)
    db.flush()
    _audit(
        db,
        admin_user_id=admin.id,
        entity_type="user",
        entity_id=user.id,
        action="create",
        after={
            "email": user.email,
            "username": user.username,
            "role": user.role.value,
        },
    )
    db.commit()
    db.refresh(user)
    return user


# ---------------------------------------------------------------------------
# UC-03: Configure billing for tenant
# ---------------------------------------------------------------------------


@router.post(
    "/tenants/{tenant_id}/billing",
    response_model=BillingOut,
    status_code=status.HTTP_201_CREATED,
)
def create_billing(
    tenant_id: uuid.UUID,
    body: CreateBillingIn,
    db: DbSession,
    admin: AdminUser,
) -> BillingAccount:
    if db.get(Tenant, tenant_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant não encontrado",
        )
    if db.scalar(select(BillingAccount).where(BillingAccount.tenant_id == tenant_id)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Billing já configurado para este tenant",
        )
    period_start, period_end, next_due = _next_due_date(body.due_day)
    billing = BillingAccount(
        tenant_id=tenant_id,
        plan=body.plan,
        monthly_price=body.monthly_price,
        due_day=body.due_day,
        grace_days=body.grace_days,
        provider=body.provider,
        billing_status=body.billing_status,
        current_period_start=period_start,
        current_period_end=period_end,
        next_due_date=next_due,
    )
    db.add(billing)
    db.flush()
    _audit(
        db,
        admin_user_id=admin.id,
        entity_type="billing_account",
        entity_id=billing.id,
        action="create",
        after={"plan": billing.plan, "due_day": billing.due_day},
    )
    db.commit()
    db.refresh(billing)
    return billing


# ---------------------------------------------------------------------------
# List tenants
# ---------------------------------------------------------------------------


@router.get("/tenants", response_model=list[TenantListItem])
def list_tenants(db: DbSession, admin: AdminUser) -> list[TenantListItem]:
    tenants = db.scalars(select(Tenant).order_by(Tenant.created_at.desc())).all()
    result: list[TenantListItem] = []
    for t in tenants:
        billing = db.scalar(
            select(BillingAccount).where(BillingAccount.tenant_id == t.id)
        )
        result.append(
            TenantListItem(
                id=t.id,
                name=t.name,
                slug=t.slug,
                access_status=t.access_status,
                billing_status=billing.billing_status if billing else None,
                created_at=t.created_at,  # type: ignore[arg-type]
            )
        )
    return result


# ---------------------------------------------------------------------------
# Tenant detail
# ---------------------------------------------------------------------------


@router.get("/tenants/{tenant_id}", response_model=TenantDetail)
def get_tenant(
    tenant_id: uuid.UUID,
    db: DbSession,
    admin: AdminUser,
) -> TenantDetail:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant não encontrado",
        )
    user = db.scalar(
        select(User).where(User.tenant_id == tenant_id).order_by(User.created_at)
    )
    billing = db.scalar(
        select(BillingAccount).where(BillingAccount.tenant_id == tenant_id)
    )
    return TenantDetail(
        tenant=TenantOut.model_validate(tenant),
        user=UserOut.model_validate(user) if user else None,
        billing=BillingOut.model_validate(billing) if billing else None,
    )


# ---------------------------------------------------------------------------
# UC-14: Record manual payment + reactivate
# ---------------------------------------------------------------------------


@router.post(
    "/tenants/{tenant_id}/billing/payments",
    response_model=BillingOut,
    status_code=status.HTTP_201_CREATED,
)
def record_payment(
    tenant_id: uuid.UUID,
    body: PaymentIn,
    db: DbSession,
    admin: AdminUser,
) -> BillingAccount:
    billing = db.scalar(
        select(BillingAccount).where(BillingAccount.tenant_id == tenant_id)
    )
    if billing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Billing não encontrado para este tenant",
        )
    db.add(
        BillingPayment(
            billing_account_id=billing.id,
            amount=body.amount,
            paid_at=body.paid_at,
            notes=body.notes,
            created_by=admin.id,
        )
    )
    old_status = billing.billing_status
    period_start, period_end, next_due = _advance_billing_cycle(
        billing.next_due_date,  # type: ignore[arg-type]
        billing.due_day,
    )
    billing.current_period_start = period_start  # type: ignore[assignment]
    billing.current_period_end = period_end  # type: ignore[assignment]
    billing.next_due_date = next_due  # type: ignore[assignment]
    if billing.billing_status in {
        BillingStatus.late,
        BillingStatus.suspended,
        BillingStatus.grace,
    }:
        billing.billing_status = BillingStatus.active
        reactivated_tenant = db.get(Tenant, tenant_id)
        if (
            reactivated_tenant is not None
            and reactivated_tenant.access_status == AccessStatus.disabled
        ):
            reactivated_tenant.access_status = AccessStatus.enabled
    db.flush()
    _audit(
        db,
        admin_user_id=admin.id,
        entity_type="billing_account",
        entity_id=billing.id,
        action="payment_recorded",
        before={"billing_status": old_status.value},
        after={
            "billing_status": billing.billing_status.value,
            "amount": str(body.amount),
            "next_due_date": str(next_due),
        },
    )
    db.commit()
    db.refresh(billing)
    return billing


# ---------------------------------------------------------------------------
# UC-15: Cancel tenant
# ---------------------------------------------------------------------------


@router.post("/tenants/{tenant_id}/cancel", response_model=TenantOut)
def cancel_tenant(
    tenant_id: uuid.UUID,
    db: DbSession,
    admin: AdminUser,
) -> Tenant:
    tenant = db.get(Tenant, tenant_id)
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant não encontrado",
        )
    old_status = tenant.access_status
    tenant.access_status = AccessStatus.disabled
    billing = db.scalar(
        select(BillingAccount).where(BillingAccount.tenant_id == tenant_id)
    )
    if billing is not None:
        billing.billing_status = BillingStatus.cancelled
        if billing.cancelled_at is None:
            billing.cancelled_at = datetime.now(UTC)  # type: ignore[assignment]
    db.flush()
    _audit(
        db,
        admin_user_id=admin.id,
        entity_type="tenant",
        entity_id=tenant.id,
        action="cancel",
        before={"access_status": old_status.value},
        after={"access_status": AccessStatus.disabled.value},
    )
    db.commit()
    db.refresh(tenant)
    return tenant
