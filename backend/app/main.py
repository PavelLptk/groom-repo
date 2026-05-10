from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.schemas import ValidationErrorBody, ValidationErrorDetail
from app.store import seed_store


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    slot_starts = [x.strip() for x in settings.slot_start_times.split(",") if x.strip()]
    seed_store(settings.salon_timezone, slot_starts, settings.workday_open, settings.workday_close)
    yield


app = FastAPI(title="GroomCare Booking API", version="0.1.0", lifespan=lifespan)


@app.get("/")
def root():
    """Корень API — удобная подсказка при открытии корня в браузере (иначе FastAPI отдаёт 404)."""
    return {
        "service": app.title,
        "version": app.version,
        "health": "/health",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "api_v1": "/api/v1",
    }


@app.get("/api")
def api_prefix_hint():
    """Без /v1 путь не существует — частая путаница при проверке прокси или API в браузере."""
    return {
        "message": "Используйте префикс /api/v1",
        "api_v1": "/api/v1",
        "example": "/api/v1/salon",
        "docs": "/docs",
    }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    details = []
    for err in exc.errors():
        loc = err.get("loc", ())
        field = ".".join(str(x) for x in loc if x not in ("body", "query", "path"))
        if not field:
            field = ".".join(str(x) for x in loc)
        details.append(
            ValidationErrorDetail(
                field=field or "request",
                code=str(err.get("type", "invalid")),
                message=str(err.get("msg", "Invalid value")),
            )
        )
    body = ValidationErrorBody(details=details)
    return JSONResponse(status_code=422, content=body.model_dump())


settings = get_settings()
_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins if _origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import (  # noqa: E402
    admin_jobs,
    appointments,
    auth_api,
    catalog,
    health,
    me,
    notifications,
    payments,
    pets,
    salon,
    slots,
)

app.include_router(health.router)
v1 = APIRouter(prefix="/api/v1")
v1.include_router(salon.router)
v1.include_router(catalog.router)
v1.include_router(slots.router)
v1.include_router(auth_api.router)
v1.include_router(me.router)
v1.include_router(pets.router)
v1.include_router(payments.router)
v1.include_router(appointments.router)
v1.include_router(notifications.router)
v1.include_router(admin_jobs.router)
app.include_router(v1)
