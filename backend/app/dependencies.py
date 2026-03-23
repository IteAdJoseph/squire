import uuid
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User

_bearer = HTTPBearer()


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


CurrentUser = Annotated[User, Depends(get_current_user)]
