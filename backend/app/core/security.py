from datetime import UTC, datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from app.config import settings

ALGORITHM = "HS256"
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def create_access_token(user_id: str, tenant_id: str) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": user_id, "tenant_id": tenant_id, "exp": expire}
    return str(jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM))


def decode_access_token(token: str) -> dict[str, object]:
    result = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    return dict(result)
