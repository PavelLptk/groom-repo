from typing import Annotated

from fastapi import APIRouter, Depends

from app.deps import get_current_user
from app.schemas import UserPublic
from app.schemas_enums import UserRole

router = APIRouter(prefix="/me", tags=["me"])


@router.get("", response_model=UserPublic)
def me(user: Annotated[dict, Depends(get_current_user)]):
    return UserPublic(
        id=user["id"],
        role=UserRole(user["role"]),
        display_name=user["display_name"],
        phone=user["phone"],
        email=user.get("email"),
        telegram_username=user.get("telegram_username"),
    )
