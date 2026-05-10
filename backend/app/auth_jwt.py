from datetime import UTC, datetime, timedelta
from typing import Any

from jose import jwt

from app.config import Settings


def create_access_token(settings: Settings, subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {"sub": subject, "exp": int(expire.timestamp())}
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_guest_manage_token(
    settings: Settings,
    appointment_id: str,
    phone_normalized: str,
) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.guest_manage_token_expire_days)
    payload: dict[str, Any] = {
        "typ": "guest_appointment",
        "sub": phone_normalized,
        "appointment_id": appointment_id,
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_token(settings: Settings, token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])


def try_decode(settings: Settings, token: str) -> dict[str, Any] | None:
    try:
        return decode_token(settings, token)
    except Exception:
        return None
