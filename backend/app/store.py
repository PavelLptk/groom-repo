from __future__ import annotations

import re
import uuid
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from app.schemas_enums import (
    AppointmentStatus,
    NotificationChannel,
    NotificationStatus,
    PaymentMethod,
    PaymentStatus,
    PetSpecies,
    UserRole,
)


def normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 10 and digits.startswith("9"):
        digits = "7" + digits
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    return digits


def parse_time_hh_mm(value: str) -> time:
    h, m = value.split(":", 1)
    return time(int(h), int(m))


def minutes_since_midnight(t: time) -> int:
    return t.hour * 60 + t.minute


@dataclass
class MemoryStore:
    lock_slug: str = field(default_factory=lambda: str(uuid.uuid4()))
    salon: dict[str, Any] = field(default_factory=dict)
    services: dict[str, dict[str, Any]] = field(default_factory=dict)
    users: dict[str, dict[str, Any]] = field(default_factory=dict)
    users_by_phone: dict[str, str] = field(default_factory=dict)
    pets: dict[str, dict[str, Any]] = field(default_factory=dict)
    appointments: dict[str, dict[str, Any]] = field(default_factory=dict)
    payments: dict[str, dict[str, Any]] = field(default_factory=dict)
    notifications: dict[str, dict[str, Any]] = field(default_factory=dict)


store = MemoryStore()


def _uid() -> str:
    return str(uuid.uuid4())


def seed_store(
    timezone_name: str,
    slot_start_labels: list[str],
    work_open: str,
    work_close: str,
) -> None:
    if store.salon:
        return

    tz = ZoneInfo(timezone_name)
    store.salon = {
        "id": "salon-1",
        "name": "GroomCare",
        "tagline": "Онлайн-запись на бережный груминг домашних животных",
        "address": "Москва, ул. Лапкина, 12",
        "phone": "+7 999 123-45-67",
        "email": "hello@groomcare.ru",
        "telegram": "@groomcare",
        "hours": "Пн-Вс: 09:00-21:00",
        "socials": ["Instagram", "VK", "Telegram"],
        "timezone": timezone_name,
        "_slot_starts": slot_start_labels,
        "_work_open": work_open,
        "_work_close": work_close,
    }

    def add_service(
        sid: str,
        title: str,
        description: str,
        duration_minutes: int,
        duration_label: str,
        price: int,
        species: list[str],
        sort_order: int,
        requires_prepay: bool = False,
        recommendations: str = "",
        restrictions: str = "",
    ) -> None:
        store.services[sid] = {
            "id": sid,
            "title": title,
            "description": description,
            "duration_minutes": duration_minutes,
            "duration_label": duration_label,
            "price": price,
            "species_allowed": species,
            "is_active": True,
            "requires_prepay": requires_prepay,
            "sort_order": sort_order,
            "recommendations": recommendations,
            "restrictions": restrictions,
        }

    add_service(
        "haircut",
        "Стрижка",
        "Модельная или гигиеническая стрижка с учетом породы.",
        90,
        "90 мин",
        2500,
        ["dog"],
        1,
        recommendations="Перед визитом не кормите питомца плотно за 2 часа.",
        restrictions="Не подходит для агрессивных животных без предварительной консультации.",
    )
    add_service(
        "wash",
        "Мытье",
        "Шампунь по типу шерсти, сушка и расчесывание.",
        60,
        "60 мин",
        1600,
        ["dog", "cat"],
        2,
        recommendations="Сообщите мастеру об аллергиях и чувствительной коже.",
        restrictions="Не проводится при кожных воспалениях без разрешения ветеринара.",
    )
    add_service(
        "full",
        "Комплексный груминг",
        "Полный уход: мытье, стрижка, когти, уши и укладка.",
        150,
        "150 мин",
        3900,
        ["dog", "cat"],
        3,
        requires_prepay=True,
        recommendations="Лучший выбор для первого знакомства с салоном.",
        restrictions="Для сильно спутанной шерсти может потребоваться доплата.",
    )
    add_service(
        "nails",
        "Стрижка когтей",
        "Быстрая и безопасная обработка когтей.",
        20,
        "20 мин",
        700,
        ["dog", "cat"],
        4,
    )
    add_service(
        "ears",
        "Уход за ушами",
        "Очищение ушных раковин и бережный осмотр.",
        25,
        "25 мин",
        900,
        ["dog", "cat"],
        5,
    )

    admin_id = _uid()
    client_id = _uid()
    store.users[admin_id] = {
        "id": admin_id,
        "role": UserRole.admin.value,
        "display_name": "Администратор",
        "phone": normalize_phone("+79000000001"),
        "email": "admin@groomcare.local",
        "telegram_username": None,
        "created_at": datetime.now(UTC),
    }
    store.users_by_phone[store.users[admin_id]["phone"]] = admin_id

    store.users[client_id] = {
        "id": client_id,
        "role": UserRole.client.value,
        "display_name": "Анна Смирнова",
        "phone": normalize_phone("+79991234567"),
        "email": "anna@example.com",
        "telegram_username": None,
        "created_at": datetime.now(UTC),
    }
    store.users_by_phone[store.users[client_id]["phone"]] = client_id

    p1 = _uid()
    p2 = _uid()
    store.pets[p1] = {
        "id": p1,
        "owner_id": client_id,
        "name": "Бублик",
        "species": PetSpecies.dog.value,
        "breed": "Корги",
        "size": "Средний",
        "age_label": "3 года",
        "notes": "Боится фена",
    }
    store.pets[p2] = {
        "id": p2,
        "owner_id": client_id,
        "name": "Марс",
        "species": PetSpecies.cat.value,
        "breed": "Мейн-кун",
        "size": "Крупный",
        "age_label": "5 лет",
        "notes": "Нужны паузы",
    }

    def make_dt(d: date, hm: str) -> datetime:
        h, m = hm.split(":")
        return datetime(d.year, d.month, d.day, int(h), int(m), tzinfo=tz)

    # Demo appointments (fixed dates)
    d_demo = date(2026, 5, 18)
    a1 = _uid()
    store.appointments[a1] = {
        "id": a1,
        "client_id": client_id,
        "pet_id": p1,
        "pet_snapshot": None,
        "service_id": "full",
        "scheduled_start": make_dt(d_demo, "12:30"),
        "scheduled_end": make_dt(d_demo, "12:30") + timedelta(minutes=150),
        "status": AppointmentStatus.confirmed.value,
        "salon_address_snapshot": store.salon["address"],
        "internal_comment": None,
        "client_comment": "",
        "prepay_required": True,
        "amount": 3900,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }


def salon_tz() -> ZoneInfo:
    name = store.salon.get("timezone", "Europe/Moscow")
    return ZoneInfo(str(name))


def list_active_appointments_for_day(day: date) -> list[dict[str, Any]]:
    tz = salon_tz()
    start = datetime(day.year, day.month, day.day, 0, 0, tzinfo=tz)
    end = start + timedelta(days=1)
    out: list[dict[str, Any]] = []
    for a in store.appointments.values():
        if a["status"] == AppointmentStatus.cancelled.value:
            continue
        s: datetime = a["scheduled_start"]
        if start <= s < end:
            out.append(a)
    return out


def compute_available_slots(
    day: date,
    service_id: str,
    min_booking_lead_minutes: int,
    exclude_appointment_id: str | None = None,
) -> list[tuple[datetime, datetime]]:
    svc = store.services.get(service_id)
    if not svc or not svc.get("is_active"):
        return []

    tz = salon_tz()
    open_t = parse_time_hh_mm(str(store.salon["_work_open"]))
    close_t = parse_time_hh_mm(str(store.salon["_work_close"]))
    open_m = minutes_since_midnight(open_t)
    close_m = minutes_since_midnight(close_t)
    duration = int(svc["duration_minutes"])
    now_local = datetime.now(tz)
    min_start = now_local + timedelta(minutes=min_booking_lead_minutes)

    busy: list[tuple[datetime, datetime]] = []
    for a in store.appointments.values():
        if exclude_appointment_id and a["id"] == exclude_appointment_id:
            continue
        if a["status"] == AppointmentStatus.cancelled.value:
            continue
        busy.append((a["scheduled_start"], a["scheduled_end"]))

    result: list[tuple[datetime, datetime]] = []
    for label in store.salon["_slot_starts"]:
        hm = label.strip()
        slot_time = parse_time_hh_mm(hm)
        start_dt = datetime(day.year, day.month, day.day, slot_time.hour, slot_time.minute, tzinfo=tz)
        end_dt = start_dt + timedelta(minutes=duration)
        slot_end_m = minutes_since_midnight(slot_time) + duration
        if minutes_since_midnight(slot_time) < open_m or slot_end_m > close_m:
            continue
        if start_dt < min_start:
            continue
        overlap = False
        for b0, b1 in busy:
            if not (end_dt <= b0 or start_dt >= b1):
                overlap = True
                break
        if not overlap:
            result.append((start_dt, end_dt))
    return result


def ensure_user_for_phone(
    display_name: str,
    phone_raw: str,
    email: str | None,
    telegram_username: str | None = None,
) -> dict[str, Any]:
    key = normalize_phone(phone_raw)
    uid_existing = store.users_by_phone.get(key)
    if uid_existing:
        u = store.users[uid_existing]
        if email:
            u["email"] = email
        if telegram_username:
            u["telegram_username"] = telegram_username
        return u
    uid = _uid()
    u = {
        "id": uid,
        "role": UserRole.client.value,
        "display_name": display_name,
        "phone": key,
        "email": email,
        "telegram_username": telegram_username,
        "created_at": datetime.now(UTC),
    }
    store.users[uid] = u
    store.users_by_phone[key] = uid
    return u


def can_transition_status(current: str, new: str, actor: UserRole) -> bool:
    if current == new:
        return True
    if actor == UserRole.admin:
        allowed = {
            AppointmentStatus.pending_confirmation.value: {
                AppointmentStatus.confirmed.value,
                AppointmentStatus.cancelled.value,
            },
            AppointmentStatus.confirmed.value: {
                AppointmentStatus.paid.value,
                AppointmentStatus.completed.value,
                AppointmentStatus.cancelled.value,
                AppointmentStatus.no_show.value,
            },
            AppointmentStatus.paid.value: {
                AppointmentStatus.completed.value,
                AppointmentStatus.cancelled.value,
            },
            AppointmentStatus.draft.value: {AppointmentStatus.pending_confirmation.value, AppointmentStatus.cancelled.value},
        }
        return new in allowed.get(current, set())
    # client
    if new == AppointmentStatus.cancelled.value and current in (
        AppointmentStatus.pending_confirmation.value,
        AppointmentStatus.confirmed.value,
    ):
        return True
    return False


def attach_payment_summary(appointment_id: str) -> dict[str, Any] | None:
    for p in store.payments.values():
        if p["appointment_id"] == appointment_id:
            return {
                "id": p["id"],
                "status": p["status"],
                "amount": p["amount"],
                "currency": p["currency"],
                "method": p["method"],
            }
    return None


def schedule_reminder_notifications(
    appointment_id: str,
    channel: NotificationChannel,
    start: datetime,
) -> list[dict[str, Any]]:
    scheduled: list[dict[str, Any]] = []
    remind_at = start - timedelta(hours=3)
    remind_at_utc = remind_at.astimezone(UTC)
    if remind_at_utc > datetime.now(UTC):
        nid = _uid()
        row = {
            "id": nid,
            "appointment_id": appointment_id,
            "channel": channel.value,
            "template_key": "reminder_3h",
            "payload": {},
            "status": NotificationStatus.pending.value,
            "scheduled_at": remind_at_utc,
            "sent_at": None,
            "error_message": None,
        }
        store.notifications[nid] = row
        scheduled.append(row)
    return scheduled
