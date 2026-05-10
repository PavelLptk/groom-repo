from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import get_settings
from app.deps import get_current_user, require_admin, require_client
from app.schemas import (
    AppointmentCreateBody,
    AppointmentCreateResponse,
    AppointmentPatch,
    AppointmentPublic,
    AppointmentStatusPatch,
    NotificationScheduledPublic,
    PaymentSummary,
)
from app.schemas_enums import AppointmentStatus, NotificationChannel, UserRole
from app.store import (
    _uid,
    attach_payment_summary,
    can_transition_status,
    compute_available_slots,
    salon_tz,
    schedule_reminder_notifications,
    store,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])

_SPECIES_RU = {"dog": "собаки", "cat": "кошки", "other": "других животных"}


def _species_allowed_message(pet_species: str, allowed: list[str]) -> str:
    species_ru = _SPECIES_RU.get(pet_species, pet_species)
    if not allowed:
        return f"Для этой услуги не заданы допустимые виды животных; выбранный питомец ({species_ru}) не может быть записан."
    allowed_ru = ", ".join(_SPECIES_RU.get(s, s) for s in allowed)
    return (
        f"Вид питомца ({species_ru}) не подходит к выбранной услуге. "
        f"Разрешены записи для: {allowed_ru}."
    )


def _assert_pet_species_allowed_for_service(pet: dict, svc: dict) -> None:
    allowed = list(svc.get("species_allowed") or [])
    ps = pet.get("species")
    if ps not in allowed:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=_species_allowed_message(str(ps), allowed),
        )


def _payment_model(raw: dict[str, Any] | None) -> PaymentSummary | None:
    if not raw:
        return None
    from app.schemas_enums import PaymentMethod, PaymentStatus

    return PaymentSummary(
        id=raw["id"],
        status=PaymentStatus(raw["status"]),
        amount=raw["amount"],
        currency=raw["currency"],
        method=PaymentMethod(raw["method"]),
    )


def _appointment_public(a: dict) -> AppointmentPublic:
    pet_display = ""
    if a.get("pet_id") and a["pet_id"] in store.pets:
        pet_display = store.pets[a["pet_id"]]["name"]
    elif a.get("pet_snapshot"):
        pet_display = a["pet_snapshot"].get("name", "")
    return AppointmentPublic(
        id=a["id"],
        client_id=a.get("client_id"),
        pet_id=a.get("pet_id"),
        pet_display_name=pet_display,
        service_id=a["service_id"],
        scheduled_start=a["scheduled_start"],
        scheduled_end=a["scheduled_end"],
        status=AppointmentStatus(a["status"]),
        salon_address_snapshot=a["salon_address_snapshot"],
        client_comment=a.get("client_comment") or "",
        prepay_required=bool(a.get("prepay_required")),
        amount=int(a["amount"]),
        payment=_payment_model(attach_payment_summary(a["id"])),
        created_at=a["created_at"],
        updated_at=a["updated_at"],
    )


def _start_in_available_slot(
    start: datetime,
    service_id: str,
    exclude_appointment_id: str | None = None,
) -> bool:
    day = start.astimezone(salon_tz()).date()
    settings = get_settings()
    pairs = compute_available_slots(
        day,
        service_id,
        settings.min_booking_lead_minutes,
        exclude_appointment_id,
    )
    for s, _ in pairs:
        if s == start:
            return True
    return False


@router.get("", response_model=list[AppointmentPublic])
def list_appointments(
    user: Annotated[dict, Depends(get_current_user)],
):
    if user.get("role") == UserRole.admin.value:
        rows = list(store.appointments.values())
    else:
        rows = [a for a in store.appointments.values() if a.get("client_id") == user["id"]]
    rows.sort(key=lambda a: a["scheduled_start"], reverse=True)
    return [_appointment_public(a) for a in rows]


@router.get("/{appointment_id}", response_model=AppointmentPublic)
def get_appointment(
    appointment_id: str,
    user: Annotated[dict, Depends(get_current_user)],
):
    a = store.appointments.get(appointment_id)
    if not a:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="appointment_not_found")
    if user.get("role") == UserRole.admin.value:
        return _appointment_public(a)
    if a.get("client_id") == user["id"]:
        return _appointment_public(a)
    raise HTTPException(status.HTTP_403_FORBIDDEN, detail="forbidden")


@router.post("", response_model=AppointmentCreateResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    body: AppointmentCreateBody,
    user: Annotated[dict, Depends(require_client)],
):
    svc = store.services.get(body.service_id)
    if not svc or not svc.get("is_active"):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="service_not_found")

    pet = store.pets.get(body.pet_id)
    if not pet or pet["owner_id"] != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="pet_not_owned")

    _assert_pet_species_allowed_for_service(pet, svc)

    start = body.scheduled_start
    if start.tzinfo is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "validation_error",
                "details": [
                    {
                        "field": "scheduled_start",
                        "code": "timezone_required",
                        "message": "Укажите часовой пояс (например +03:00).",
                    }
                ],
            },
        )

    if not _start_in_available_slot(start, body.service_id, None):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="slot_unavailable",
        )

    end = start + timedelta(minutes=int(svc["duration_minutes"]))
    aid = _uid()
    client_id = user["id"]
    row = {
        "id": aid,
        "client_id": client_id,
        "pet_id": body.pet_id,
        "pet_snapshot": None,
        "service_id": body.service_id,
        "scheduled_start": start,
        "scheduled_end": end,
        "status": AppointmentStatus.pending_confirmation.value,
        "salon_address_snapshot": store.salon["address"],
        "internal_comment": None,
        "client_comment": body.client_comment,
        "prepay_required": bool(svc.get("requires_prepay")),
        "amount": int(svc["price"]),
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    store.appointments[aid] = row

    scheduled_rows = schedule_reminder_notifications(aid, body.notification_channel, start)
    notifications_scheduled = [
        NotificationScheduledPublic(
            id=r["id"],
            channel=NotificationChannel(r["channel"]),
            scheduled_at=r["scheduled_at"],
            template_key=r["template_key"],
        )
        for r in scheduled_rows
    ]

    return AppointmentCreateResponse(
        id=aid,
        status=AppointmentStatus.pending_confirmation,
        prepay_required=row["prepay_required"],
        scheduled_start=start,
        scheduled_end=end,
        payment=_payment_model(attach_payment_summary(aid)),
        notifications_scheduled=notifications_scheduled,
    )


@router.patch("/{appointment_id}", response_model=AppointmentPublic)
def patch_appointment(
    appointment_id: str,
    body: AppointmentPatch,
    user: Annotated[dict, Depends(get_current_user)],
):
    a = store.appointments.get(appointment_id)
    if not a:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="appointment_not_found")
    actor = UserRole(user["role"])
    if actor != UserRole.admin and a.get("client_id") != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="forbidden")

    if body.cancel:
        if not can_transition_status(a["status"], AppointmentStatus.cancelled.value, actor):
            raise HTTPException(status.HTTP_409_CONFLICT, detail="invalid_status_transition")
        a["status"] = AppointmentStatus.cancelled.value
        a["updated_at"] = datetime.now(UTC)
        return _appointment_public(a)

    if body.scheduled_start:
        svc = store.services.get(a["service_id"])
        if not svc:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="service_missing")
        if body.service_id and body.service_id != a["service_id"]:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="use_service_patch_separately")
        new_start = body.scheduled_start
        if new_start.tzinfo is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail="timezone_required")
        if not _start_in_available_slot(new_start, a["service_id"], appointment_id):
            raise HTTPException(status.HTTP_409_CONFLICT, detail="slot_unavailable")
        a["scheduled_start"] = new_start
        a["scheduled_end"] = new_start + timedelta(minutes=int(svc["duration_minutes"]))

    if body.service_id and body.service_id != a["service_id"]:
        if actor != UserRole.admin:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="admin_only_service_change")
        new_svc = store.services.get(body.service_id)
        if not new_svc or not new_svc.get("is_active"):
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="service_not_found")
        pid = a.get("pet_id")
        if pid:
            pet = store.pets.get(pid)
            if pet:
                _assert_pet_species_allowed_for_service(pet, new_svc)
        if not _start_in_available_slot(a["scheduled_start"], body.service_id, appointment_id):
            raise HTTPException(status.HTTP_409_CONFLICT, detail="slot_unavailable_for_new_service")
        a["service_id"] = body.service_id
        a["amount"] = int(new_svc["price"])
        a["prepay_required"] = bool(new_svc.get("requires_prepay"))
        a["scheduled_end"] = a["scheduled_start"] + timedelta(minutes=int(new_svc["duration_minutes"]))

    if body.client_comment is not None:
        a["client_comment"] = body.client_comment

    a["updated_at"] = datetime.now(UTC)
    return _appointment_public(a)


@router.patch("/{appointment_id}/status", response_model=AppointmentPublic)
def patch_status(
    appointment_id: str,
    body: AppointmentStatusPatch,
    admin: Annotated[dict, Depends(require_admin)],
):
    a = store.appointments.get(appointment_id)
    if not a:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="appointment_not_found")
    if not can_transition_status(a["status"], body.status.value, UserRole.admin):
        raise HTTPException(status.HTTP_409_CONFLICT, detail="invalid_status_transition")
    a["status"] = body.status.value
    a["updated_at"] = datetime.now(UTC)
    return _appointment_public(a)
