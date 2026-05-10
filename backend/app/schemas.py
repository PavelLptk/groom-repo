from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas_enums import (
    AppointmentStatus,
    NotificationChannel,
    NotificationStatus,
    PaymentMethod,
    PaymentStatus,
    PetSpecies,
    UserRole,
)


class ValidationErrorDetail(BaseModel):
    field: str
    code: str
    message: str


class ValidationErrorBody(BaseModel):
    error: str = "validation_error"
    details: list[ValidationErrorDetail]


# --- Salon
class SalonPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    tagline: str
    address: str
    phone: str
    email: str
    telegram: str
    hours: str
    socials: list[str]
    timezone: str


class SalonUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    tagline: str | None = Field(default=None, max_length=500)
    address: str | None = Field(default=None, max_length=500)
    phone: str | None = Field(default=None, max_length=40)
    email: str | None = Field(default=None, max_length=200)
    telegram: str | None = Field(default=None, max_length=120)
    hours: str | None = Field(default=None, max_length=200)
    socials: list[str] | None = None
    timezone: str | None = Field(default=None, max_length=80)


# --- Service
class ServicePublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    duration_minutes: int
    duration_label: str
    price: int
    species_allowed: list[str]
    is_active: bool
    requires_prepay: bool
    sort_order: int
    recommendations: str = ""
    restrictions: str = ""


class ServiceCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=10_000)
    duration_minutes: int = Field(ge=1, le=24 * 60)
    price: int = Field(ge=0)
    species_allowed: list[str] = Field(default_factory=lambda: ["dog", "cat"])
    is_active: bool = True
    requires_prepay: bool = False
    sort_order: int = 0
    recommendations: str = Field(default="", max_length=5000)
    restrictions: str = Field(default="", max_length=5000)


class ServicePatch(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    description: str | None = Field(default=None, max_length=10_000)
    duration_minutes: int | None = Field(default=None, ge=1, le=24 * 60)
    price: int | None = Field(default=None, ge=0)
    species_allowed: list[str] | None = None
    is_active: bool | None = None
    requires_prepay: bool | None = None
    sort_order: int | None = None
    recommendations: str | None = Field(default=None, max_length=5000)
    restrictions: str | None = Field(default=None, max_length=5000)


# --- Auth / User
class UserPublic(BaseModel):
    id: str
    role: UserRole
    display_name: str
    phone: str
    email: str | None
    telegram_username: str | None


class RegisterBody(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    phone: str = Field(min_length=5, max_length=40)
    email: EmailStr | None = None
    telegram_username: str | None = Field(default=None, max_length=120)


class LoginBody(BaseModel):
    phone: str = Field(min_length=5, max_length=40)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Pet
class PetPublic(BaseModel):
    id: str
    owner_id: str
    name: str
    species: PetSpecies
    breed: str
    size: str
    age_label: str
    notes: str


class PetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    species: PetSpecies
    breed: str = Field(default="", max_length=120)
    size: str = Field(default="", max_length=40)
    age_label: str = Field(default="", max_length=80)
    notes: str = Field(default="", max_length=2000)


class PetPatch(BaseModel):
    name: str | None = Field(default=None, max_length=80)
    species: PetSpecies | None = None
    breed: str | None = Field(default=None, max_length=120)
    size: str | None = Field(default=None, max_length=40)
    age_label: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None, max_length=2000)


# --- Appointment
class AppointmentCreateBody(BaseModel):
    """Создание записи только для авторизованного клиента (pet_id обязателен)."""

    service_id: str = Field(min_length=1, max_length=80)
    scheduled_start: datetime
    pet_id: str = Field(min_length=1, max_length=80)
    client_comment: str = Field(default="", max_length=2000)
    notification_channel: NotificationChannel = NotificationChannel.email


class PaymentSummary(BaseModel):
    id: str
    status: PaymentStatus
    amount: int
    currency: str
    method: PaymentMethod


class NotificationScheduledPublic(BaseModel):
    id: str
    channel: NotificationChannel
    scheduled_at: datetime
    template_key: str


class AppointmentPublic(BaseModel):
    id: str
    client_id: str | None
    pet_id: str | None
    pet_display_name: str
    service_id: str
    scheduled_start: datetime
    scheduled_end: datetime
    status: AppointmentStatus
    salon_address_snapshot: str
    client_comment: str
    prepay_required: bool
    amount: int
    payment: PaymentSummary | None
    created_at: datetime
    updated_at: datetime


class AppointmentCreateResponse(BaseModel):
    id: str
    status: AppointmentStatus
    prepay_required: bool
    scheduled_start: datetime
    scheduled_end: datetime
    payment: PaymentSummary | None
    notifications_scheduled: list[NotificationScheduledPublic]


class AppointmentPatch(BaseModel):
    scheduled_start: datetime | None = None
    service_id: str | None = Field(default=None, max_length=80)
    client_comment: str | None = Field(default=None, max_length=2000)
    cancel: bool | None = None


class AppointmentStatusPatch(BaseModel):
    status: AppointmentStatus


class SlotsResponse(BaseModel):
    date: str
    service_id: str
    duration_minutes: int
    slots: list[dict[str, Any]]


class PaymentCreateBody(BaseModel):
    method: PaymentMethod
    amount: int = Field(ge=1)


class PaymentPublic(BaseModel):
    id: str
    appointment_id: str
    amount: int
    currency: str
    method: PaymentMethod
    status: PaymentStatus
    mock_payment_url: str | None = None


class NotificationPublic(BaseModel):
    id: str
    appointment_id: str
    channel: NotificationChannel
    template_key: str
    status: NotificationStatus
    scheduled_at: datetime
    sent_at: datetime | None
    error_message: str | None


class HealthResponse(BaseModel):
    ok: bool = True
    service: str = "groom-booking-api"

