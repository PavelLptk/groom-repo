from datetime import date

from fastapi import APIRouter, HTTPException, Query, status

from app.config import get_settings
from app.schemas import SlotsResponse
from app.store import compute_available_slots, salon_tz, store

router = APIRouter(prefix="/slots", tags=["slots"])


@router.get("", response_model=SlotsResponse)
def get_slots(
    day: date = Query(..., alias="date"),
    service_id: str = Query(..., min_length=1),
):
    if service_id not in store.services:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="service_not_found")
    settings = get_settings()
    pairs = compute_available_slots(day, service_id, settings.min_booking_lead_minutes)
    tz = salon_tz()
    slots = [{"start": s.isoformat(), "end": e.isoformat()} for s, e in pairs]
    svc = store.services[service_id]
    return SlotsResponse(
        date=day.isoformat(),
        service_id=service_id,
        duration_minutes=int(svc["duration_minutes"]),
        slots=slots,
    )
