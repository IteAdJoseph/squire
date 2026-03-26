import pytest
from starlette.testclient import TestClient

SCHEDULED_AT = "2026-06-01T10:00:00Z"
SCHEDULED_AT_2 = "2026-06-02T10:00:00Z"


# ---------------------------------------------------------------------------
# Helper fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def customer(client: TestClient, auth_headers: dict) -> dict:
    r = client.post(
        "/customers",
        json={"name": "Ana Lima", "phone": "+5511912345678"},
        headers=auth_headers,
    )
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def svc_deposit(client: TestClient, auth_headers: dict) -> dict:
    r = client.post(
        "/services",
        json={
            "name": "Corte",
            "duration_minutes": 60,
            "total_price": "100.00",
            "deposit_amount": "30.00",
        },
        headers=auth_headers,
    )
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def svc_free(client: TestClient, auth_headers: dict) -> dict:
    r = client.post(
        "/services",
        json={"name": "Consulta", "duration_minutes": 30, "total_price": "50.00"},
        headers=auth_headers,
    )
    assert r.status_code == 201
    return r.json()


@pytest.fixture
def appt_awaiting(
    client: TestClient, auth_headers: dict, customer: dict, svc_deposit: dict
) -> dict:
    r = client.post(
        "/appointments",
        json={
            "customer_id": customer["id"],
            "service_id": svc_deposit["id"],
            "scheduled_at": SCHEDULED_AT,
        },
        headers=auth_headers,
    )
    assert r.status_code == 201
    assert r.json()["status"] == "awaiting_deposit"
    return r.json()


@pytest.fixture
def appt_confirmed(
    client: TestClient, auth_headers: dict, customer: dict, svc_free: dict
) -> dict:
    r = client.post(
        "/appointments",
        json={
            "customer_id": customer["id"],
            "service_id": svc_free["id"],
            "scheduled_at": SCHEDULED_AT,
        },
        headers=auth_headers,
    )
    assert r.status_code == 201
    assert r.json()["status"] == "confirmed"
    return r.json()


@pytest.fixture
def appt_completed(
    client: TestClient, auth_headers: dict, appt_confirmed: dict
) -> dict:
    r = client.post(
        f"/appointments/{appt_confirmed['id']}/complete", headers=auth_headers
    )
    assert r.status_code == 200
    return r.json()


@pytest.fixture
def deposit_charge(client: TestClient, auth_headers: dict, appt_awaiting: dict) -> dict:
    r = client.post(
        f"/appointments/{appt_awaiting['id']}/charges/deposit", headers=auth_headers
    )
    assert r.status_code == 201
    return r.json()


# ---------------------------------------------------------------------------
# UC-05 Customers
# ---------------------------------------------------------------------------


def test_create_customer_ok(client: TestClient, auth_headers: dict) -> None:
    r = client.post(
        "/customers",
        json={"name": "João Silva", "phone": "+5511999999999"},
        headers=auth_headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "João Silva"
    assert data["phone"] == "+5511999999999"
    assert data["is_active"] is True


def test_create_customer_invalid_phone(client: TestClient, auth_headers: dict) -> None:
    r = client.post(
        "/customers",
        json={"name": "X", "phone": "11999999999"},
        headers=auth_headers,
    )
    assert r.status_code == 422


def test_list_customers(client: TestClient, auth_headers: dict, customer: dict) -> None:
    r = client.get("/customers", headers=auth_headers)
    assert r.status_code == 200
    ids = [c["id"] for c in r.json()]
    assert customer["id"] in ids


def test_get_customer_isolation(
    client: TestClient,
    auth_headers: dict,
    second_auth_headers: dict,
    customer: dict,
) -> None:
    r = client.get(f"/customers/{customer['id']}", headers=second_auth_headers)
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# UC-06 Services
# ---------------------------------------------------------------------------


def test_create_service_ok(client: TestClient, auth_headers: dict) -> None:
    r = client.post(
        "/services",
        json={"name": "Manicure", "duration_minutes": 45, "total_price": "60.00"},
        headers=auth_headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Manicure"
    assert data["is_active"] is True


def test_create_service_deposit_exceeds_total(
    client: TestClient, auth_headers: dict
) -> None:
    r = client.post(
        "/services",
        json={
            "name": "X",
            "duration_minutes": 30,
            "total_price": "50.00",
            "deposit_amount": "60.00",
        },
        headers=auth_headers,
    )
    assert r.status_code == 422


def test_list_services(
    client: TestClient, auth_headers: dict, svc_deposit: dict
) -> None:
    r = client.get("/services", headers=auth_headers)
    assert r.status_code == 200
    ids = [s["id"] for s in r.json()]
    assert svc_deposit["id"] in ids


# ---------------------------------------------------------------------------
# UC-07 Appointments
# ---------------------------------------------------------------------------


def test_create_appointment_with_deposit(
    client: TestClient, auth_headers: dict, customer: dict, svc_deposit: dict
) -> None:
    r = client.post(
        "/appointments",
        json={
            "customer_id": customer["id"],
            "service_id": svc_deposit["id"],
            "scheduled_at": SCHEDULED_AT,
        },
        headers=auth_headers,
    )
    assert r.status_code == 201
    data = r.json()
    assert data["status"] == "awaiting_deposit"
    assert data["deposit_amount"] == "30.00"
    assert data["balance_amount"] == "70.00"


def test_create_appointment_without_deposit(
    client: TestClient, auth_headers: dict, customer: dict, svc_free: dict
) -> None:
    r = client.post(
        "/appointments",
        json={
            "customer_id": customer["id"],
            "service_id": svc_free["id"],
            "scheduled_at": SCHEDULED_AT,
        },
        headers=auth_headers,
    )
    assert r.status_code == 201
    assert r.json()["status"] == "confirmed"


def test_create_appointment_wrong_tenant_customer(
    client: TestClient,
    auth_headers: dict,
    second_auth_headers: dict,
    customer: dict,
    svc_free: dict,
) -> None:
    # customer belongs to auth_headers tenant; second_auth_headers can't use it
    r = client.post(
        "/appointments",
        json={
            "customer_id": customer["id"],
            "service_id": svc_free["id"],
            "scheduled_at": SCHEDULED_AT,
        },
        headers=second_auth_headers,
    )
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# UC-08 Deposit charge
# ---------------------------------------------------------------------------


def test_create_deposit_charge_ok(
    client: TestClient, auth_headers: dict, appt_awaiting: dict
) -> None:
    r = client.post(
        f"/appointments/{appt_awaiting['id']}/charges/deposit", headers=auth_headers
    )
    assert r.status_code == 201
    data = r.json()
    assert data["type"] == "deposit"
    assert data["status"] == "pending"
    assert data["amount"] == "30.00"


def test_create_deposit_charge_no_deposit(
    client: TestClient, auth_headers: dict, appt_confirmed: dict
) -> None:
    # appt_confirmed uses svc_free which has deposit=0
    r = client.post(
        f"/appointments/{appt_confirmed['id']}/charges/deposit", headers=auth_headers
    )
    assert r.status_code == 409


def test_create_deposit_charge_already_exists(
    client: TestClient, auth_headers: dict, deposit_charge: dict, appt_awaiting: dict
) -> None:
    r = client.post(
        f"/appointments/{appt_awaiting['id']}/charges/deposit", headers=auth_headers
    )
    assert r.status_code == 409


# ---------------------------------------------------------------------------
# UC-09 Confirm deposit
# ---------------------------------------------------------------------------


def test_confirm_deposit_charge_ok(
    client: TestClient, auth_headers: dict, appt_awaiting: dict, deposit_charge: dict
) -> None:
    r = client.post(
        f"/appointments/{appt_awaiting['id']}/charges/deposit/confirm",
        json={},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["status"] == "paid"

    # Appointment should now be confirmed
    r = client.get(f"/appointments/{appt_awaiting['id']}", headers=auth_headers)
    assert r.json()["appointment"]["status"] == "confirmed"


def test_confirm_deposit_charge_already_paid(
    client: TestClient, auth_headers: dict, appt_awaiting: dict, deposit_charge: dict
) -> None:
    client.post(
        f"/appointments/{appt_awaiting['id']}/charges/deposit/confirm",
        json={},
        headers=auth_headers,
    )
    r = client.post(
        f"/appointments/{appt_awaiting['id']}/charges/deposit/confirm",
        json={},
        headers=auth_headers,
    )
    assert r.status_code == 409


# ---------------------------------------------------------------------------
# UC-11 Complete appointment
# ---------------------------------------------------------------------------


def test_complete_appointment_ok(
    client: TestClient, auth_headers: dict, appt_confirmed: dict
) -> None:
    r = client.post(
        f"/appointments/{appt_confirmed['id']}/complete", headers=auth_headers
    )
    assert r.status_code == 200
    assert r.json()["status"] == "completed"


def test_complete_appointment_not_confirmed(
    client: TestClient, auth_headers: dict, appt_awaiting: dict
) -> None:
    r = client.post(
        f"/appointments/{appt_awaiting['id']}/complete", headers=auth_headers
    )
    assert r.status_code == 409


# ---------------------------------------------------------------------------
# UC-12 Balance charge
# ---------------------------------------------------------------------------


def test_create_balance_charge_ok(
    client: TestClient, auth_headers: dict, appt_completed: dict
) -> None:
    r = client.post(
        f"/appointments/{appt_completed['id']}/charges/balance", headers=auth_headers
    )
    assert r.status_code == 201
    data = r.json()
    assert data["type"] == "balance"
    assert data["status"] == "pending"
    assert data["amount"] == "50.00"


def test_create_balance_charge_zero_balance(
    client: TestClient, auth_headers: dict
) -> None:
    r = client.post(
        "/services",
        json={"name": "Gratis", "duration_minutes": 10, "total_price": "0.00"},
        headers=auth_headers,
    )
    svc = r.json()
    r = client.post(
        "/customers",
        json={"name": "Zero", "phone": "+5511900000001"},
        headers=auth_headers,
    )
    cust = r.json()
    r = client.post(
        "/appointments",
        json={
            "customer_id": cust["id"],
            "service_id": svc["id"],
            "scheduled_at": SCHEDULED_AT_2,
        },
        headers=auth_headers,
    )
    appt = r.json()
    assert appt["status"] == "confirmed"
    client.post(f"/appointments/{appt['id']}/complete", headers=auth_headers)

    r = client.post(f"/appointments/{appt['id']}/charges/balance", headers=auth_headers)
    assert r.status_code == 409


def test_create_balance_charge_already_exists(
    client: TestClient, auth_headers: dict, appt_completed: dict
) -> None:
    client.post(
        f"/appointments/{appt_completed['id']}/charges/balance", headers=auth_headers
    )
    r = client.post(
        f"/appointments/{appt_completed['id']}/charges/balance", headers=auth_headers
    )
    assert r.status_code == 409


# ---------------------------------------------------------------------------
# Cancel appointment
# ---------------------------------------------------------------------------


def test_cancel_appointment_ok(
    client: TestClient, auth_headers: dict, appt_awaiting: dict, deposit_charge: dict
) -> None:
    r = client.post(f"/appointments/{appt_awaiting['id']}/cancel", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "cancelled"

    # Pending deposit charge should be cancelled too
    r = client.get(f"/appointments/{appt_awaiting['id']}", headers=auth_headers)
    charges = r.json()["charges"]
    assert all(c["status"] == "cancelled" for c in charges)


def test_cancel_completed_appointment(
    client: TestClient, auth_headers: dict, appt_completed: dict
) -> None:
    r = client.post(
        f"/appointments/{appt_completed['id']}/cancel", headers=auth_headers
    )
    assert r.status_code == 409


# ---------------------------------------------------------------------------
# PATCH /customers — update
# ---------------------------------------------------------------------------


def test_update_customer_name(
    client: TestClient, auth_headers: dict, customer: dict
) -> None:
    r = client.patch(
        f"/customers/{customer['id']}",
        json={"name": "Ana Souza"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Ana Souza"
    assert r.json()["phone"] == customer["phone"]


def test_update_customer_phone(
    client: TestClient, auth_headers: dict, customer: dict
) -> None:
    r = client.patch(
        f"/customers/{customer['id']}",
        json={"phone": "+5521987654321"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["phone"] == "+5521987654321"


def test_update_customer_notes_to_none(
    client: TestClient, auth_headers: dict, customer: dict
) -> None:
    # First set notes
    client.patch(
        f"/customers/{customer['id']}",
        json={"notes": "alguma nota"},
        headers=auth_headers,
    )
    # Then clear them
    r = client.patch(
        f"/customers/{customer['id']}",
        json={"notes": None},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["notes"] is None


def test_update_customer_invalid_phone(
    client: TestClient, auth_headers: dict, customer: dict
) -> None:
    r = client.patch(
        f"/customers/{customer['id']}",
        json={"phone": "not-a-phone"},
        headers=auth_headers,
    )
    assert r.status_code == 422


def test_update_customer_not_found(client: TestClient, auth_headers: dict) -> None:
    r = client.patch(
        "/customers/00000000-0000-0000-0000-000000000000",
        json={"name": "X"},
        headers=auth_headers,
    )
    assert r.status_code == 404


def test_update_customer_tenant_isolation(
    client: TestClient,
    auth_headers: dict,
    second_auth_headers: dict,
    customer: dict,
) -> None:
    r = client.patch(
        f"/customers/{customer['id']}",
        json={"name": "Invasor"},
        headers=second_auth_headers,
    )
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /customers — soft-delete
# ---------------------------------------------------------------------------


def test_delete_customer(
    client: TestClient, auth_headers: dict, customer: dict
) -> None:
    r = client.delete(f"/customers/{customer['id']}", headers=auth_headers)
    assert r.status_code == 204


def test_deleted_customer_not_in_list(
    client: TestClient, auth_headers: dict, customer: dict
) -> None:
    client.delete(f"/customers/{customer['id']}", headers=auth_headers)
    r = client.get("/customers", headers=auth_headers)
    assert r.status_code == 200
    ids = [c["id"] for c in r.json()]
    assert customer["id"] not in ids


def test_deleted_customer_get_returns_404(
    client: TestClient, auth_headers: dict, customer: dict
) -> None:
    client.delete(f"/customers/{customer['id']}", headers=auth_headers)
    r = client.get(f"/customers/{customer['id']}", headers=auth_headers)
    assert r.status_code == 404


def test_delete_customer_not_found(client: TestClient, auth_headers: dict) -> None:
    r = client.delete(
        "/customers/00000000-0000-0000-0000-000000000000", headers=auth_headers
    )
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /services — update
# ---------------------------------------------------------------------------


def test_update_service_name(
    client: TestClient, auth_headers: dict, svc_deposit: dict
) -> None:
    r = client.patch(
        f"/services/{svc_deposit['id']}",
        json={"name": "Corte Degradê"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Corte Degradê"


def test_update_service_price(
    client: TestClient, auth_headers: dict, svc_deposit: dict
) -> None:
    r = client.patch(
        f"/services/{svc_deposit['id']}",
        json={"total_price": "120.00"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert float(r.json()["total_price"]) == 120.0


def test_update_service_deposit_exceeds_total(
    client: TestClient, auth_headers: dict, svc_deposit: dict
) -> None:
    # svc_deposit has total=100, deposit=30 — try to set deposit > total
    r = client.patch(
        f"/services/{svc_deposit['id']}",
        json={"deposit_amount": "200.00"},
        headers=auth_headers,
    )
    assert r.status_code == 422


def test_update_service_not_found(client: TestClient, auth_headers: dict) -> None:
    r = client.patch(
        "/services/00000000-0000-0000-0000-000000000000",
        json={"name": "X"},
        headers=auth_headers,
    )
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /services — soft-delete
# ---------------------------------------------------------------------------


def test_delete_service(
    client: TestClient, auth_headers: dict, svc_deposit: dict
) -> None:
    r = client.delete(f"/services/{svc_deposit['id']}", headers=auth_headers)
    assert r.status_code == 204


def test_deleted_service_not_in_list(
    client: TestClient, auth_headers: dict, svc_deposit: dict
) -> None:
    client.delete(f"/services/{svc_deposit['id']}", headers=auth_headers)
    r = client.get("/services", headers=auth_headers)
    assert r.status_code == 200
    ids = [s["id"] for s in r.json()]
    assert svc_deposit["id"] not in ids


def test_deleted_service_get_returns_404(
    client: TestClient, auth_headers: dict, svc_deposit: dict
) -> None:
    client.delete(f"/services/{svc_deposit['id']}", headers=auth_headers)
    r = client.get(f"/services/{svc_deposit['id']}", headers=auth_headers)
    assert r.status_code == 404


def test_delete_service_not_found(client: TestClient, auth_headers: dict) -> None:
    r = client.delete(
        "/services/00000000-0000-0000-0000-000000000000", headers=auth_headers
    )
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


def test_unauthenticated_request(client: TestClient) -> None:
    r = client.get("/customers")
    assert r.status_code in (401, 403)
