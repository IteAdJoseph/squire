"""Bootstrap: cria tenant admin + usuário owner inicial.

Uso (de qualquer diretório, sem instalar o app):
    python backend/scripts/bootstrap_admin.py "postgresql://user:pass@host/db"

Dependências necessárias no ambiente Python:
    pip install psycopg2-binary passlib[bcrypt] bcrypt==4.0.1

Idempotente: não recria registros que já existem.
"""

import sys
import uuid
from datetime import date

import psycopg2
import psycopg2.extras
from passlib.context import CryptContext

ADMIN_TENANT_SLUG = "reminda-admin"
ADMIN_TENANT_NAME = "Reminda Admin"
ADMIN_EMAIL = "admin@reminda.app"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "troque-esta-senha-123"

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def main(database_url: str) -> None:
    conn = psycopg2.connect(database_url, sslmode="require")
    conn.autocommit = False
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        # 1. Tenant admin
        cur.execute("SELECT id FROM tenants WHERE slug = %s", (ADMIN_TENANT_SLUG,))
        row = cur.fetchone()
        if row is None:
            tenant_id = str(uuid.uuid4())
            cur.execute(
                "INSERT INTO tenants (id, name, slug, access_status)"
                " VALUES (%s, %s, %s, 'enabled')",
                (tenant_id, ADMIN_TENANT_NAME, ADMIN_TENANT_SLUG),
            )
            print(f"Tenant criado  : slug={ADMIN_TENANT_SLUG}  id={tenant_id}")
        else:
            tenant_id = str(row["id"])
            print(f"Tenant ja existe: slug={ADMIN_TENANT_SLUG}  id={tenant_id}")

        # 2. Usuário owner
        cur.execute(
            "SELECT id FROM users WHERE tenant_id = %s AND username = %s",
            (tenant_id, ADMIN_USERNAME),
        )
        if cur.fetchone() is None:
            user_id = str(uuid.uuid4())
            hashed = _pwd_ctx.hash(ADMIN_PASSWORD)
            cur.execute(
                """
                INSERT INTO users
                    (id, tenant_id, email, username, hashed_password, role, is_active)
                VALUES (%s, %s, %s, %s, %s, 'owner', true)
                """,
                (user_id, tenant_id, ADMIN_EMAIL, ADMIN_USERNAME, hashed),
            )
            print(f"Usuario criado : username={ADMIN_USERNAME}  email={ADMIN_EMAIL}")
            print(f"Senha inicial  : {ADMIN_PASSWORD}")
            print("ATENCAO        : troque a senha apos o primeiro login.")
        else:
            print(f"Usuario ja existe: username={ADMIN_USERNAME}")

        # 3. BillingAccount do tenant admin (necessário para o login não ser bloqueado)
        cur.execute(
            "SELECT id FROM billing_accounts WHERE tenant_id = %s", (tenant_id,)
        )
        if cur.fetchone() is None:
            today = date.today()
            far_future = date(2099, 12, 31)
            cur.execute(
                """
                INSERT INTO billing_accounts
                    (id, tenant_id, plan, monthly_price, due_day,
                     billing_status, provider,
                     current_period_start, current_period_end, next_due_date)
                VALUES (%s, %s, 'admin', 0.00, 1,
                        'trial', 'manual_pix',
                        %s, %s, %s)
                """,
                (str(uuid.uuid4()), tenant_id, today, far_future, far_future),
            )
            print("BillingAccount criado: plan=admin  status=trial  expira=2099-12-31")
        else:
            print("BillingAccount ja existe")

        conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python bootstrap_admin.py \"postgresql://user:pass@host/db\"")
        sys.exit(1)
    main(sys.argv[1])
    sys.exit(0)
