from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.config import Settings


def create_access_token(settings: Settings, subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": int(expire.timestamp())}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(settings: Settings, token: str) -> dict[str, Any]:
    """Проверка подписи и срока JWT. Ошибки — JWTError (для 401 в зависимостях)."""
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])


__all__ = ["JWTError", "create_access_token", "decode_token"]
