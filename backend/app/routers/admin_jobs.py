from typing import Annotated

from fastapi import APIRouter, Depends

from app.deps import require_admin
from app.schemas import NotificationPublic
from app.schemas_enums import NotificationChannel, NotificationStatus
from app.store import store

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/process-notifications", response_model=list[NotificationPublic])
def process_notifications(_: Annotated[dict, Depends(require_admin)]):
    from datetime import UTC, datetime

    now = datetime.now(UTC)
    updated: list[dict] = []
    for n in store.notifications.values():
        if n["status"] != NotificationStatus.pending.value:
            continue
        if n["scheduled_at"] <= now:
            n["status"] = NotificationStatus.sent.value
            n["sent_at"] = now
            updated.append(n)
    return [
        NotificationPublic(
            id=n["id"],
            appointment_id=n["appointment_id"],
            channel=NotificationChannel(n["channel"]),
            template_key=n["template_key"],
            status=NotificationStatus(n["status"]),
            scheduled_at=n["scheduled_at"],
            sent_at=n.get("sent_at"),
            error_message=n.get("error_message"),
        )
        for n in updated
    ]
