from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import get_settings
from app.deps import get_current_user, require_admin
from app.schemas import PaymentCreateBody, PaymentPublic
from app.schemas_enums import AppointmentStatus, PaymentMethod, PaymentStatus, UserRole
from app.store import _uid, store

router = APIRouter(tags=["payments"])


def _public(p: dict) -> PaymentPublic:
    settings = get_settings()
    mock_url = None
    if p["status"] == PaymentStatus.pending.value:
        mock_url = f"{settings.mock_payment_base_url.rstrip('/')}/{p['id']}"
    return PaymentPublic(
        id=p["id"],
        appointment_id=p["appointment_id"],
        amount=p["amount"],
        currency=p["currency"],
        method=PaymentMethod(p["method"]),
        status=PaymentStatus(p["status"]),
        mock_payment_url=mock_url,
    )


@router.post("/appointments/{appointment_id}/payments", response_model=PaymentPublic, status_code=status.HTTP_201_CREATED)
def create_payment(
    appointment_id: str,
    body: PaymentCreateBody,
    user: Annotated[dict, Depends(get_current_user)],
):
    a = store.appointments.get(appointment_id)
    if not a:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="appointment_not_found")
    if user.get("role") != UserRole.admin and a.get("client_id") != user["id"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="forbidden")
    if a["status"] == AppointmentStatus.cancelled.value:
        raise HTTPException(status.HTTP_409_CONFLICT, detail="appointment_cancelled")

    for p in store.payments.values():
        if p["appointment_id"] == appointment_id and p["status"] == PaymentStatus.pending.value:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="pending_payment_exists")

    pid = _uid()
    row = {
        "id": pid,
        "appointment_id": appointment_id,
        "amount": body.amount,
        "currency": "RUB",
        "method": body.method.value,
        "status": PaymentStatus.pending.value,
        "external_ref": None,
        "created_at": datetime.now(UTC),
    }
    store.payments[pid] = row
    return _public(row)


@router.post("/payments/{payment_id}/confirm", response_model=PaymentPublic)
def confirm_payment(
    payment_id: str,
    _: Annotated[dict, Depends(require_admin)],
):
    p = store.payments.get(payment_id)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="payment_not_found")
    p["status"] = PaymentStatus.succeeded.value
    a = store.appointments.get(p["appointment_id"])
    if a and a.get("prepay_required"):
        if a["status"] == AppointmentStatus.pending_confirmation.value:
            a["status"] = AppointmentStatus.confirmed.value
    return _public(p)
