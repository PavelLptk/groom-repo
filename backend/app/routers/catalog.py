from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_optional_user, require_admin
from app.schemas import ServiceCreate, ServicePatch, ServicePublic
from app.schemas_enums import UserRole
from app.store import _uid, store

router = APIRouter(prefix="/services", tags=["services"])


def _to_public(row: dict) -> ServicePublic:
    return ServicePublic(
        id=row["id"],
        title=row["title"],
        description=row["description"],
        duration_minutes=row["duration_minutes"],
        duration_label=row["duration_label"],
        price=row["price"],
        species_allowed=list(row["species_allowed"]),
        is_active=row["is_active"],
        requires_prepay=row["requires_prepay"],
        sort_order=row["sort_order"],
        recommendations=row.get("recommendations", ""),
        restrictions=row.get("restrictions", ""),
    )


@router.get("", response_model=list[ServicePublic])
def list_services(user: Annotated[dict | None, Depends(get_optional_user)]):
    rows = list(store.services.values())
    if not user or user.get("role") != UserRole.admin.value:
        rows = [r for r in rows if r.get("is_active")]
    rows.sort(key=lambda r: r.get("sort_order", 0))
    return [_to_public(r) for r in rows]


@router.post("", response_model=ServicePublic, status_code=status.HTTP_201_CREATED)
def create_service(body: ServiceCreate, _: Annotated[dict, Depends(require_admin)]):
    new_id = _uid()
    row = {
        "id": new_id,
        "title": body.title,
        "description": body.description,
        "duration_minutes": body.duration_minutes,
        "duration_label": f"{body.duration_minutes} мин",
        "price": body.price,
        "species_allowed": body.species_allowed,
        "is_active": body.is_active,
        "requires_prepay": body.requires_prepay,
        "sort_order": body.sort_order,
        "recommendations": body.recommendations,
        "restrictions": body.restrictions,
    }
    store.services[new_id] = row
    return _to_public(row)


@router.patch("/{service_id}", response_model=ServicePublic)
def patch_service(
    service_id: str,
    body: ServicePatch,
    _: Annotated[dict, Depends(require_admin)],
):
    row = store.services.get(service_id)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="service_not_found")
    for k, v in body.model_dump(exclude_unset=True).items():
        if v is not None:
            row[k] = v
    if body.duration_minutes is not None:
        row["duration_label"] = f"{row['duration_minutes']} мин"
    return _to_public(row)
