from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt

from app.core.config import get_settings

settings = get_settings()


def create_access_token(
    subject: str,
    email: str,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Genera un token JWT para el usuario autenticado.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.now(timezone.utc) + expires_delta

    payload: Dict[str, Any] = {
        "sub": subject,
        "email": email,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodifica y valida un token JWT.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as exc:
        raise ValueError("Invalid or expired token") from exc
