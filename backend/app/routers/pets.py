from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.deps import get_current_user
from app.schemas import PetCreate, PetPatch, PetPublic
from app.schemas_enums import PetSpecies, UserRole
from app.store import _uid, store

router = APIRouter(prefix="/pets", tags=["pets"])


def _public(p: dict) -> PetPublic:
    return PetPublic(
        id=p["id"],
        owner_id=p["owner_id"],
        name=p["name"],
        species=PetSpecies(p["species"]),
        breed=p.get("breed", ""),
        size=p.get("size", ""),
        age_label=p.get("age_label", ""),
        notes=p.get("notes", ""),
    )


@router.get("", response_model=list[PetPublic])
def list_pets(user: Annotated[dict, Depends(get_current_user)]):
    if user.get("role") == UserRole.admin.value:
        return [_public(p) for p in store.pets.values()]
    return [_public(p) for p in store.pets.values() if p["owner_id"] == user["id"]]


@router.post("", response_model=PetPublic, status_code=status.HTTP_201_CREATED)
def create_pet(user: Annotated[dict, Depends(get_current_user)], body: PetCreate):
    if user.get("role") != UserRole.client.value:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="clients_only")
    pid = _uid()
    row = {
        "id": pid,
        "owner_id": user["id"],
        "name": body.name,
        "species": body.species.value,
        "breed": body.breed,
        "size": body.size,
        "age_label": body.age_label,
        "notes": body.notes,
    }
    store.pets[pid] = row
    return _public(row)


@router.patch("/{pet_id}", response_model=PetPublic)
def patch_pet(
    pet_id: str,
    body: PetPatch,
    user: Annotated[dict, Depends(get_current_user)],
):
    p = store.pets.get(pet_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="pet_not_found")
    if user.get("role") != UserRole.admin.value and p["owner_id"] != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="forbidden")
    for k, v in body.model_dump(exclude_unset=True).items():
        if v is not None:
            if k == "species" and hasattr(v, "value"):
                p[k] = v.value
            else:
                p[k] = v
    return _public(p)


@router.delete("/{pet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pet(pet_id: str, user: Annotated[dict, Depends(get_current_user)]):
    p = store.pets.get(pet_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="pet_not_found")
    if user.get("role") != UserRole.admin.value and p["owner_id"] != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="forbidden")
    del store.pets[pet_id]
    return None
