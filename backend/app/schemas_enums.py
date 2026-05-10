from enum import Enum


class UserRole(str, Enum):
    client = "client"
    admin = "admin"


class AppointmentStatus(str, Enum):
    draft = "draft"
    pending_confirmation = "pending_confirmation"
    confirmed = "confirmed"
    paid = "paid"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"


class PaymentMethod(str, Enum):
    card = "card"
    sbp = "sbp"


class PaymentStatus(str, Enum):
    pending = "pending"
    succeeded = "succeeded"
    failed = "failed"
    refunded = "refunded"


class NotificationChannel(str, Enum):
    email = "email"
    telegram = "telegram"
    sms = "sms"
    push_stub = "push_stub"


class NotificationStatus(str, Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"


class PetSpecies(str, Enum):
    dog = "dog"
    cat = "cat"
    other = "other"
