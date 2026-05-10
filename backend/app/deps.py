from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth_jwt import decode_token, try_decode
from app.config import Settings, get_settings
from app.schemas_enums import UserRole
from app.store import store

bearer = HTTPBearer(auto_error=False)


def get_settings_dep() -> Settings:
    return get_settings()


def _user_from_sub(user_id: str) -> dict | None:
    return store.users.get(user_id)


async def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
):
    if not credentials:
        return None
    try:
        payload = decode_token(settings, credentials.credentials)
    except Exception:
        return None
    uid = payload.get("sub")
    if not uid or payload.get("typ") == "guest_appointment":
        return None
    return _user_from_sub(str(uid))


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
):
    if not credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="not_authenticated")
    try:
        payload = decode_token(settings, credentials.credentials)
    except Exception as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="invalid_token") from exc
    if payload.get("typ") == "guest_appointment":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="use_client_token")
    uid = payload.get("sub")
    user = _user_from_sub(str(uid)) if uid else None
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="user_not_found")
    return user


async def require_admin(user: Annotated[dict, Depends(get_current_user)]):
    if user.get("role") != UserRole.admin.value:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="admin_only")
    return user


async def require_client_or_admin(user: Annotated[dict, Depends(get_current_user)]):
    if user.get("role") not in (UserRole.client.value, UserRole.admin.value):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="forbidden")
    return user


def parse_guest_appointment_token(settings: Settings, token: str) -> tuple[str, str] | None:
    payload = try_decode(settings, token)
    if not payload or payload.get("typ") != "guest_appointment":
        return None
    aid = payload.get("appointment_id")
    if not aid:
        return None
    return str(aid), str(payload.get("sub") or "")
