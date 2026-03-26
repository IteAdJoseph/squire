import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import ActiveTenantUser
from app.models.appointment import Appointment
from app.models.audit_log import AuditLog
from app.models.charge import Charge
from app.models.customer import Customer
from app.models.enums import AppointmentStatus, ChargeStatus, ChargeType
from app.models.service import Service
from app.models.user import User
from app.operational.schemas import (
    AppointmentCreateIn,
    AppointmentDetailOut,
    AppointmentOut,
    ChargeOut,
    ConfirmChargeIn,
    CustomerCreateIn,
    CustomerOut,
    CustomerUpdateIn,
    ServiceCreateIn,
    ServiceOut,
    ServiceUpdateIn,
)

router = APIRouter(tags=["operational"])
DbSession = Annotated[Session, Depends(get_db)]


def _audit(
    db: Session,
    *,
    user: User,
    entity_type: str,
    entity_id: uuid.UUID,
    action: str,
    before: dict | None = None,
    after: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            tenant_id=user.tenant_id,
            user_id=user.id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            before=before,
            after=after,
        )
    )


def _get_appointment_or_404(
    db: Session, tenant_id: uuid.UUID, appointment_id: uuid.UUID
) -> Appointment:
    appointment = db.scalar(
        select(Appointment).where(
            Appointment.id == appointment_id,
            Appointment.tenant_id == tenant_id,
        )
    )
    if appointment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado"
        )
    return appointment


@router.post(
    "/customers", response_model=CustomerOut, status_code=status.HTTP_201_CREATED
)
def create_customer(
    body: CustomerCreateIn, db: DbSession, current_user: ActiveTenantUser
) -> Customer:
    customer = Customer(
        tenant_id=current_user.tenant_id,
        name=body.name,
        phone=body.phone,
        notes=body.notes,
    )
    db.add(customer)
    db.flush()
    _audit(
        db,
        user=current_user,
        entity_type="customer",
        entity_id=customer.id,
        action="create",
        after={"name": customer.name, "phone": customer.phone},
    )
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/customers", response_model=list[CustomerOut])
def list_customers(db: DbSession, current_user: ActiveTenantUser) -> list[Customer]:
    return list(
        db.scalars(
            select(Customer)
            .where(
                Customer.tenant_id == current_user.tenant_id,
                Customer.is_active.is_(True),
            )
            .order_by(Customer.created_at.desc())
        ).all()
    )


@router.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: uuid.UUID, db: DbSession, current_user: ActiveTenantUser
) -> Customer:
    customer = db.scalar(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.tenant_id == current_user.tenant_id,
            Customer.is_active.is_(True),
        )
    )
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )
    return customer


@router.patch("/customers/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: uuid.UUID,
    body: CustomerUpdateIn,
    db: DbSession,
    current_user: ActiveTenantUser,
) -> Customer:
    customer = db.scalar(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.tenant_id == current_user.tenant_id,
            Customer.is_active.is_(True),
        )
    )
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )
    before = {"name": customer.name, "phone": customer.phone, "notes": customer.notes}
    if body.name is not None:
        customer.name = body.name
    if body.phone is not None:
        customer.phone = body.phone
    if "notes" in body.model_fields_set:
        customer.notes = body.notes
    db.flush()
    _audit(
        db,
        user=current_user,
        entity_type="customer",
        entity_id=customer.id,
        action="update",
        before=before,
        after={"name": customer.name, "phone": customer.phone, "notes": customer.notes},
    )
    db.commit()
    db.refresh(customer)
    return customer


@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(
    customer_id: uuid.UUID,
    db: DbSession,
    current_user: ActiveTenantUser,
) -> None:
    customer = db.scalar(
        select(Customer).where(
            Customer.id == customer_id,
            Customer.tenant_id == current_user.tenant_id,
            Customer.is_active.is_(True),
        )
    )
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )
    customer.is_active = False
    db.flush()
    _audit(
        db,
        user=current_user,
        entity_type="customer",
        entity_id=customer.id,
        action="deactivate",
        before={"is_active": True},
        after={"is_active": False},
    )
    db.commit()


@router.post(
    "/services", response_model=ServiceOut, status_code=status.HTTP_201_CREATED
)
def create_service(
    body: ServiceCreateIn, db: DbSession, current_user: ActiveTenantUser
) -> Service:
    if body.deposit_amount > body.total_price:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="deposit_amount deve ser <= total_price",
        )
    service = Service(
        tenant_id=current_user.tenant_id,
        name=body.name,
        duration_minutes=body.duration_minutes,
        total_price=body.total_price,
        deposit_amount=body.deposit_amount,
    )
    db.add(service)
    db.flush()
    _audit(
        db,
        user=current_user,
        entity_type="service",
        entity_id=service.id,
        action="create",
        after={"name": service.name, "total_price": str(service.total_price)},
    )
    db.commit()
    db.refresh(service)
    return service


@router.get("/services", response_model=list[ServiceOut])
def list_services(db: DbSession, current_user: ActiveTenantUser) -> list[Service]:
    return list(
        db.scalars(
            select(Service)
            .where(
                Service.tenant_id == current_user.tenant_id,
                Service.is_active.is_(True),
            )
            .order_by(Service.created_at.desc())
        ).all()
    )


@router.get("/services/{service_id}", response_model=ServiceOut)
def get_service(
    service_id: uuid.UUID, db: DbSession, current_user: ActiveTenantUser
) -> Service:
    service = db.scalar(
        select(Service).where(
            Service.id == service_id,
            Service.tenant_id == current_user.tenant_id,
            Service.is_active.is_(True),
        )
    )
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado"
        )
    return service


@router.patch("/services/{service_id}", response_model=ServiceOut)
def update_service(
    service_id: uuid.UUID,
    body: ServiceUpdateIn,
    db: DbSession,
    current_user: ActiveTenantUser,
) -> Service:
    service = db.scalar(
        select(Service).where(
            Service.id == service_id,
            Service.tenant_id == current_user.tenant_id,
            Service.is_active.is_(True),
        )
    )
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado"
        )
    new_total = (
        body.total_price if body.total_price is not None else service.total_price
    )
    new_deposit = (
        body.deposit_amount
        if body.deposit_amount is not None
        else service.deposit_amount
    )
    if new_deposit > new_total:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="deposit_amount deve ser <= total_price",
        )
    before = {
        "name": service.name,
        "total_price": str(service.total_price),
        "deposit_amount": str(service.deposit_amount),
    }
    if body.name is not None:
        service.name = body.name
    if body.duration_minutes is not None:
        service.duration_minutes = body.duration_minutes
    if body.total_price is not None:
        service.total_price = body.total_price
    if body.deposit_amount is not None:
        service.deposit_amount = body.deposit_amount
    db.flush()
    _audit(
        db,
        user=current_user,
        entity_type="service",
        entity_id=service.id,
        action="update",
        before=before,
        after={"name": service.name, "total_price": str(service.total_price)},
    )
    db.commit()
    db.refresh(service)
    return service


@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: uuid.UUID,
    db: DbSession,
    current_user: ActiveTenantUser,
) -> None:
    service = db.scalar(
        select(Service).where(
            Service.id == service_id,
            Service.tenant_id == current_user.tenant_id,
            Service.is_active.is_(True),
        )
    )
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado"
        )
    service.is_active = False
    db.flush()
    _audit(
        db,
        user=current_user,
        entity_type="service",
        entity_id=service.id,
        action="deactivate",
        before={"is_active": True},
        after={"is_active": False},
    )
    db.commit()


@router.post(
    "/appointments", response_model=AppointmentOut, status_code=status.HTTP_201_CREATED
)
def create_appointment(
    body: AppointmentCreateIn, db: DbSession, current_user: ActiveTenantUser
) -> Appointment:
    customer = db.scalar(
        select(Customer).where(
            Customer.id == body.customer_id,
            Customer.tenant_id == current_user.tenant_id,
            Customer.is_active.is_(True),
        )
    )
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado"
        )

    service = db.scalar(
        select(Service).where(
            Service.id == body.service_id,
            Service.tenant_id == current_user.tenant_id,
            Service.is_active.is_(True),
        )
    )
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Serviço não encontrado"
        )

    if service.deposit_amount > service.total_price:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="deposit_amount deve ser <= total_price",
        )

    total = Decimal(service.total_price)
    deposit = Decimal(service.deposit_amount)
    balance = total - deposit
    initial_status = (
        AppointmentStatus.confirmed
        if deposit == Decimal("0")
        else AppointmentStatus.awaiting_deposit
    )

    appointment = Appointment(
        tenant_id=current_user.tenant_id,
        customer_id=customer.id,
        service_id=service.id,
        scheduled_at=body.scheduled_at,
        total_price=total,
        deposit_amount=deposit,
        balance_amount=balance,
        status=initial_status,
        notes=body.notes,
    )
    db.add(appointment)
    db.flush()

    _audit(
        db,
        user=current_user,
        entity_type="appointment",
        entity_id=appointment.id,
        action="create",
        after={
            "status": appointment.status.value,
            "total_price": str(total),
            "deposit_amount": str(deposit),
            "balance_amount": str(balance),
        },
    )

    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("/appointments", response_model=list[AppointmentOut])
def list_appointments(
    db: DbSession,
    current_user: ActiveTenantUser,
    status_filter: AppointmentStatus | None = Query(default=None, alias="status"),
    date_from: datetime | None = Query(default=None),
    date_to: datetime | None = Query(default=None),
) -> list[Appointment]:
    conditions = [Appointment.tenant_id == current_user.tenant_id]
    if status_filter is not None:
        conditions.append(Appointment.status == status_filter)
    if date_from is not None:
        conditions.append(Appointment.scheduled_at >= date_from)
    if date_to is not None:
        conditions.append(Appointment.scheduled_at <= date_to)

    return list(
        db.scalars(
            select(Appointment)
            .where(and_(*conditions))
            .order_by(Appointment.scheduled_at.desc())
        ).all()
    )


@router.get("/appointments/{appointment_id}", response_model=AppointmentDetailOut)
def get_appointment(
    appointment_id: uuid.UUID,
    db: DbSession,
    current_user: ActiveTenantUser,
) -> AppointmentDetailOut:
    appointment = _get_appointment_or_404(db, current_user.tenant_id, appointment_id)
    charges = db.scalars(
        select(Charge)
        .where(
            Charge.appointment_id == appointment.id,
            Charge.tenant_id == current_user.tenant_id,
        )
        .order_by(Charge.created_at.desc())
    ).all()
    return AppointmentDetailOut(
        appointment=AppointmentOut.model_validate(appointment),
        charges=[ChargeOut.model_validate(c) for c in charges],
    )


@router.post(
    "/appointments/{appointment_id}/charges/deposit",
    response_model=ChargeOut,
    status_code=status.HTTP_201_CREATED,
)
def create_deposit_charge(
    appointment_id: uuid.UUID,
    db: DbSession,
    current_user: ActiveTenantUser,
) -> Charge:
    appointment = _get_appointment_or_404(db, current_user.tenant_id, appointment_id)

    if appointment.deposit_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Agendamento sem sinal"
        )

    if appointment.status not in {
        AppointmentStatus.awaiting_deposit,
        AppointmentStatus.confirmed,
    }:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Status do agendamento não permite cobrança de sinal",
        )

    existing = db.scalar(
        select(Charge).where(
            Charge.appointment_id == appointment.id,
            Charge.tenant_id == current_user.tenant_id,
            Charge.type == ChargeType.deposit,
            Charge.status.in_([ChargeStatus.pending, ChargeStatus.paid]),
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Cobrança de sinal já existe"
        )

    charge = Charge(
        tenant_id=current_user.tenant_id,
        appointment_id=appointment.id,
        type=ChargeType.deposit,
        amount=appointment.deposit_amount,
        status=ChargeStatus.pending,
    )
    db.add(charge)
    db.flush()
    _audit(
        db,
        user=current_user,
        entity_type="charge",
        entity_id=charge.id,
        action="create_deposit_charge",
        after={"amount": str(charge.amount), "status": charge.status.value},
    )
    db.commit()
    db.refresh(charge)
    return charge


@router.post(
    "/appointments/{appointment_id}/charges/deposit/confirm", response_model=ChargeOut
)
def confirm_deposit_charge(
    appointment_id: uuid.UUID,
    body: ConfirmChargeIn,
    db: DbSession,
    current_user: ActiveTenantUser,
) -> Charge:
    appointment = _get_appointment_or_404(db, current_user.tenant_id, appointment_id)

    charge = db.scalar(
        select(Charge).where(
            Charge.appointment_id == appointment.id,
            Charge.tenant_id == current_user.tenant_id,
            Charge.type == ChargeType.deposit,
        )
    )
    if charge is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cobrança de sinal não encontrada",
        )

    if charge.status == ChargeStatus.paid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Cobrança já está paga"
        )
    if charge.status != ChargeStatus.pending:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Somente cobranças pendentes podem ser confirmadas",
        )

    charge.status = ChargeStatus.paid
    charge.paid_at = body.paid_at or datetime.now(UTC)  # type: ignore[assignment]

    old_status = appointment.status
    if appointment.status == AppointmentStatus.awaiting_deposit:
        appointment.status = AppointmentStatus.confirmed

    db.flush()
    _audit(
        db,
        user=current_user,
        entity_type="charge",
        entity_id=charge.id,
        action="confirm_deposit_charge",
        before={"status": ChargeStatus.pending.value},
        after={"status": ChargeStatus.paid.value},
    )
    if old_status != appointment.status:
        _audit(
            db,
            user=current_user,
            entity_type="appointment",
            entity_id=appointment.id,
            action="status_changed",
            before={"status": old_status.value},
            after={"status": appointment.status.value},
        )

    db.commit()
    db.refresh(charge)
    return charge


@router.post("/appointments/{appointment_id}/complete", response_model=AppointmentOut)
def complete_appointment(
    appointment_id: uuid.UUID,
    db: DbSession,
    current_user: ActiveTenantUser,
) -> Appointment:
    appointment = _get_appointment_or_404(db, current_user.tenant_id, appointment_id)
    if appointment.status != AppointmentStatus.confirmed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Somente agendamento confirmado pode ser concluído",
        )
    old_status = appointment.status
    appointment.status = AppointmentStatus.completed
    db.flush()
    _audit(
        db,
        user=current_user,
        entity_type="appointment",
        entity_id=appointment.id,
        action="status_changed",
        before={"status": old_status.value},
        after={"status": appointment.status.value},
    )
    db.commit()
    db.refresh(appointment)
    return appointment


@router.post(
    "/appointments/{appointment_id}/charges/balance",
    response_model=ChargeOut,
    status_code=status.HTTP_201_CREATED,
)
def create_balance_charge(
    appointment_id: uuid.UUID,
    db: DbSession,
    current_user: ActiveTenantUser,
) -> Charge:
    appointment = _get_appointment_or_404(db, current_user.tenant_id, appointment_id)
    if appointment.status != AppointmentStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Somente agendamento concluído pode gerar cobrança de saldo",
        )
    if appointment.balance_amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Agendamento sem saldo pendente",
        )

    existing = db.scalar(
        select(Charge).where(
            Charge.appointment_id == appointment.id,
            Charge.tenant_id == current_user.tenant_id,
            Charge.type == ChargeType.balance,
            Charge.status.in_([ChargeStatus.pending, ChargeStatus.paid]),
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Cobrança de saldo já existe"
        )

    charge = Charge(
        tenant_id=current_user.tenant_id,
        appointment_id=appointment.id,
        type=ChargeType.balance,
        amount=appointment.balance_amount,
        status=ChargeStatus.pending,
    )
    db.add(charge)
    db.flush()
    _audit(
        db,
        user=current_user,
        entity_type="charge",
        entity_id=charge.id,
        action="create_balance_charge",
        after={"amount": str(charge.amount), "status": charge.status.value},
    )
    db.commit()
    db.refresh(charge)
    return charge


@router.post("/appointments/{appointment_id}/cancel", response_model=AppointmentOut)
def cancel_appointment(
    appointment_id: uuid.UUID,
    db: DbSession,
    current_user: ActiveTenantUser,
) -> Appointment:
    appointment = _get_appointment_or_404(db, current_user.tenant_id, appointment_id)

    if appointment.status in {AppointmentStatus.completed, AppointmentStatus.cancelled}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Status atual não permite cancelamento",
        )

    old_status = appointment.status
    appointment.status = AppointmentStatus.cancelled

    pending_charges = db.scalars(
        select(Charge).where(
            Charge.appointment_id == appointment.id,
            Charge.tenant_id == current_user.tenant_id,
            Charge.status == ChargeStatus.pending,
        )
    ).all()
    for charge in pending_charges:
        charge.status = ChargeStatus.cancelled

    db.flush()
    _audit(
        db,
        user=current_user,
        entity_type="appointment",
        entity_id=appointment.id,
        action="status_changed",
        before={"status": old_status.value},
        after={"status": appointment.status.value},
    )
    db.commit()
    db.refresh(appointment)
    return appointment
