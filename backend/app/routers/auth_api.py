from fastapi import APIRouter, HTTPException, status

from app.auth_jwt import create_access_token
from app.config import get_settings
from app.schemas import LoginBody, RegisterBody, TokenResponse
from app.schemas_enums import UserRole
from app.store import _uid, normalize_phone, store

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(body: RegisterBody):
    key = normalize_phone(body.phone)
    if key in store.users_by_phone:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="phone_already_registered")
    uid = _uid()
    from datetime import UTC, datetime

    store.users[uid] = {
        "id": uid,
        "role": UserRole.client.value,
        "display_name": body.display_name,
        "phone": key,
        "email": str(body.email) if body.email else None,
        "telegram_username": body.telegram_username,
        "created_at": datetime.now(UTC),
    }
    store.users_by_phone[key] = uid
    u = store.users[uid]
    settings = get_settings()
    token = create_access_token(settings, u["id"], {"role": u["role"]})
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginBody):
    key = normalize_phone(body.phone)
    uid = store.users_by_phone.get(key)
    if not uid:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="user_not_found")
    u = store.users[uid]
    settings = get_settings()
    token = create_access_token(settings, u["id"], {"role": u["role"]})
    return TokenResponse(access_token=token)
