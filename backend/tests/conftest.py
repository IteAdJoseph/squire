# ruff: noqa: E402, I001
# DATABASE_URL must be set before app imports so that app.config.Settings()
# and alembic env.py both pick up the test database URL.
import os

_TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql://localhost/reminda_test"
)
os.environ["DATABASE_URL"] = _TEST_DB_URL

import uuid
from collections.abc import Generator
from datetime import date, timedelta
from decimal import Decimal

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from app.core.security import create_access_token, hash_password
from app.database import get_db
from app.main import app
from app.models.billing import BillingAccount
from app.models.enums import BillingProvider, BillingStatus, UserRole
from app.models.tenant import Tenant
from app.models.user import User

_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(_HERE)

TEST_DB_URL = _TEST_DB_URL


@pytest.fixture(scope="session")
def _pg_engine():
    engine = create_engine(TEST_DB_URL)
    cfg = Config(os.path.join(_BACKEND_DIR, "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    command.upgrade(cfg, "head")
    yield engine
    command.downgrade(cfg, "base")
    engine.dispose()


@pytest.fixture
def db(_pg_engine) -> Generator[Session, None, None]:
    conn = _pg_engine.connect()
    trans = conn.begin()
    session = Session(conn, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        trans.rollback()
        conn.close()


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def _override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _create_tenant_headers(db: Session) -> dict[str, str]:
    suffix = uuid.uuid4().hex[:8]
    tenant = Tenant(name=f"Tenant {suffix}", slug=f"t-{suffix}")
    db.add(tenant)
    db.flush()

    user = User(
        tenant_id=tenant.id,
        email=f"owner-{suffix}@test.com",
        username=f"owner-{suffix}",
        hashed_password=hash_password("s3cr3t"),
        role=UserRole.owner,
        is_active=True,
    )
    db.add(user)
    db.flush()

    today = date.today()
    billing = BillingAccount(
        tenant_id=tenant.id,
        plan="basic",
        monthly_price=Decimal("99.00"),
        due_day=10,
        grace_days=5,
        billing_status=BillingStatus.trial,
        provider=BillingProvider.manual_pix,
        current_period_start=today,
        current_period_end=today + timedelta(days=30),
        next_due_date=today + timedelta(days=30),
    )
    db.add(billing)
    db.flush()

    token = create_access_token(str(user.id), str(tenant.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_headers(db: Session) -> dict[str, str]:
    return _create_tenant_headers(db)


@pytest.fixture
def second_auth_headers(db: Session) -> dict[str, str]:
    return _create_tenant_headers(db)
