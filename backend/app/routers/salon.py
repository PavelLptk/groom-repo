from typing import Annotated

from fastapi import APIRouter, Depends

from app.deps import get_settings_dep, require_admin
from app.schemas import SalonPublic, SalonUpdate
from app.store import store

router = APIRouter(prefix="/salon", tags=["salon"])


def _salon_public() -> SalonPublic:
    s = store.salon
    return SalonPublic(
        id=s["id"],
        name=s["name"],
        tagline=s["tagline"],
        address=s["address"],
        phone=s["phone"],
        email=s["email"],
        telegram=s["telegram"],
        hours=s["hours"],
        socials=list(s["socials"]),
        timezone=s["timezone"],
    )


@router.get("", response_model=SalonPublic)
def get_salon():
    return _salon_public()


@router.patch("", response_model=SalonPublic)
def patch_salon(
    body: SalonUpdate,
    _: Annotated[dict, Depends(require_admin)],
):
    s = store.salon
    data = body.model_dump(exclude_unset=True)
    for k, v in data.items():
        if v is not None:
            s[k] = v
    return _salon_public()
