from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.auth_jwt import create_guest_manage_token
from app.config import get_settings
from app.deps import get_current_user, get_optional_user, parse_guest_appointment_token, require_admin
from app.schemas import (
    AppointmentCreateResponse,
    AppointmentCreateUnified,
    AppointmentPatch,
    AppointmentPublic,
    AppointmentStatusPatch,
    NotificationScheduledPublic,
    PaymentSummary,
)
from app.schemas_enums import AppointmentStatus, NotificationChannel, UserRole
from app.store import (
    attach_payment_summary,
    can_transition_status,
    compute_available_slots,
    ensure_user_for_phone,
    normalize_phone,
    salon_tz,
    schedule_reminder_notifications,
    store,
    _uid,
)

router = APIRouter(prefix="/appointments", tags=["appointments"])


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
    user: Annotated[dict | None, Depends(get_optional_user)],
    manage_token: str | None = Query(default=None),
):
    a = store.appointments.get(appointment_id)
    if not a:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="appointment_not_found")
    settings = get_settings()
    if user and user.get("role") == UserRole.admin.value:
        return _appointment_public(a)
    if user and a.get("client_id") == user["id"]:
        return _appointment_public(a)
    if manage_token:
        parsed = parse_guest_appointment_token(settings, manage_token)
        if parsed and parsed[0] == appointment_id:
            return _appointment_public(a)
    raise HTTPException(status.HTTP_403_FORBIDDEN, detail="forbidden")


@router.post("", response_model=AppointmentCreateResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    body: AppointmentCreateUnified,
    user: Annotated[dict | None, Depends(get_optional_user)],
):
    svc = store.services.get(body.service_id)
    if not svc or not svc.get("is_active"):
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="service_not_found")

    pet_id: str | None = body.pet_id
    client_id: str | None = None
    pet_snapshot: dict | None = None

    if body.pet_id:
        if not user or user.get("role") != UserRole.client.value:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="client_token_required")
        pet = store.pets.get(body.pet_id)
        if not pet or pet["owner_id"] != user["id"]:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="pet_not_owned")
        client_id = user["id"]
    else:
        assert body.contact and body.pet
        u = ensure_user_for_phone(
            body.contact.display_name,
            body.contact.phone,
            str(body.contact.email) if body.contact.email else None,
            None,
        )
        client_id = u["id"]
        pid = _uid()
        store.pets[pid] = {
            "id": pid,
            "owner_id": client_id,
            "name": body.pet.name,
            "species": body.pet.species.value,
            "breed": body.pet.breed,
            "size": body.pet.size,
            "age_label": body.pet.age_label,
            "notes": body.pet.notes,
        }
        pet_id = pid
        pet_snapshot = {
            "name": body.pet.name,
            "species": body.pet.species.value,
            "breed": body.pet.breed,
        }

    start = body.scheduled_start
    if start.tzinfo is None:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "validation_error", "details": [{"field": "scheduled_start", "code": "timezone_required", "message": "Укажите часовой пояс (например +03:00)."}]},
        )

    if not _start_in_available_slot(start, body.service_id, None):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="slot_unavailable",
        )

    end = start + timedelta(minutes=int(svc["duration_minutes"]))
    aid = _uid()
    row = {
        "id": aid,
        "client_id": client_id,
        "pet_id": pet_id,
        "pet_snapshot": pet_snapshot,
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

    settings = get_settings()
    manage_token: str | None = None
    msg: str | None = None
    if not user:
        phone_norm = normalize_phone(body.contact.phone) if body.contact else ""
        manage_token = create_guest_manage_token(settings, aid, phone_norm)
        msg = "Ссылка для управления записью (MVP): используйте manage_token в GET /appointments/{id}?manage_token=..."

    return AppointmentCreateResponse(
        id=aid,
        status=AppointmentStatus.pending_confirmation,
        prepay_required=row["prepay_required"],
        scheduled_start=start,
        scheduled_end=end,
        payment=_payment_model(attach_payment_summary(aid)),
        notifications_scheduled=notifications_scheduled,
        manage_token=manage_token,
        message=msg,
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
