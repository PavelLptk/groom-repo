from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.deps import get_current_user, require_admin
from app.schemas import NotificationPublic
from app.schemas_enums import NotificationChannel, NotificationStatus, UserRole
from app.store import store

router = APIRouter(prefix="/notifications", tags=["notifications"])


def _public(n: dict) -> NotificationPublic:
    return NotificationPublic(
        id=n["id"],
        appointment_id=n["appointment_id"],
        channel=NotificationChannel(n["channel"]),
        template_key=n["template_key"],
        status=NotificationStatus(n["status"]),
        scheduled_at=n["scheduled_at"],
        sent_at=n.get("sent_at"),
        error_message=n.get("error_message"),
    )


@router.get("", response_model=list[NotificationPublic])
def list_notifications(
    user: Annotated[dict, Depends(get_current_user)],
    appointment_id: str | None = Query(default=None),
):
    rows = list(store.notifications.values())
    if user.get("role") == UserRole.admin.value:
        if appointment_id:
            rows = [r for r in rows if r["appointment_id"] == appointment_id]
    else:
        my_appts = {a["id"] for a in store.appointments.values() if a.get("client_id") == user["id"]}
        rows = [r for r in rows if r["appointment_id"] in my_appts]
        if appointment_id:
            rows = [r for r in rows if r["appointment_id"] == appointment_id]
    rows.sort(key=lambda r: r["scheduled_at"], reverse=True)
    return [_public(r) for r in rows]
