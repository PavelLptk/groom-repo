from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.auth_jwt import decode_token
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
    except JWTError:
        return None
    uid = payload.get("sub")
    if not uid:
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
    except JWTError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="invalid_token") from exc
    uid = payload.get("sub")
    if not uid:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="invalid_token")
    user = _user_from_sub(str(uid))
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


async def require_client(user: Annotated[dict, Depends(get_current_user)]):
    """Создание онлайн-записи — только для роли client."""
    if user.get("role") != UserRole.client.value:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Только клиенты могут создавать запись через этот метод.",
        )
    return user
