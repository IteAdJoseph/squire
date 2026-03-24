"""Bootstrap: cria tenant admin + usuário owner inicial.

Rodar UMA VEZ via Render Shell (dentro de backend/):
    python scripts/bootstrap_admin.py

Variáveis de ambiente usadas: DATABASE_URL, ADMIN_TENANT_SLUG (opcional).
"""

import sys

from sqlalchemy import select

from app.config import settings
from app.core.security import hash_password
from app.database import SessionLocal
from app.models.enums import UserRole
from app.models.tenant import Tenant
from app.models.user import User

ADMIN_EMAIL = "admin@reminda.app"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "troque-esta-senha-123"


def main() -> None:
    db = SessionLocal()
    try:
        # 1. Tenant admin
        tenant = db.scalar(select(Tenant).where(Tenant.slug == settings.admin_tenant_slug))
        if tenant is None:
            tenant = Tenant(name="Reminda Admin", slug=settings.admin_tenant_slug)
            db.add(tenant)
            db.flush()
            print(f"Tenant criado: slug={tenant.slug}  id={tenant.id}")
        else:
            print(f"Tenant ja existe: slug={tenant.slug}  id={tenant.id}")

        # 2. Usuário owner
        user = db.scalar(
            select(User).where(
                User.tenant_id == tenant.id,
                User.username == ADMIN_USERNAME,
            )
        )
        if user is None:
            user = User(
                tenant_id=tenant.id,
                email=ADMIN_EMAIL,
                username=ADMIN_USERNAME,
                hashed_password=hash_password(ADMIN_PASSWORD),
                role=UserRole.owner,
            )
            db.add(user)
            db.commit()
            print(f"Usuario criado: username={ADMIN_USERNAME}  email={ADMIN_EMAIL}")
            print(f"Senha inicial : {ADMIN_PASSWORD}")
            print("ATENCAO: troque a senha apos o primeiro login.")
        else:
            print(f"Usuario ja existe: username={user.username}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
    sys.exit(0)
