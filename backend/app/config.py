from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# `.env` в каталоге `backend/` (путь не зависит от текущей рабочей директории).
_BACKEND_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8010, alias="API_PORT")
    secret_key: str = Field(default="dev-insecure-change-me", alias="SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60 * 24 * 7, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    guest_manage_token_expire_days: int = Field(default=30, alias="GUEST_MANAGE_TOKEN_EXPIRE_DAYS")
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        alias="CORS_ORIGINS",
    )
    salon_timezone: str = Field(default="Europe/Moscow", alias="SALON_TIMEZONE")
    slot_start_times: str = Field(
        default="09:00,10:30,12:30,15:00,17:30,19:00",
        alias="SLOT_START_TIMES",
    )
    workday_open: str = Field(default="09:00", alias="WORKDAY_OPEN")
    workday_close: str = Field(default="21:00", alias="WORKDAY_CLOSE")
    min_booking_lead_minutes: int = Field(default=15, alias="MIN_BOOKING_LEAD_MINUTES")
    mock_payment_base_url: str = Field(
        default="https://example.test/pay",
        alias="MOCK_PAYMENT_BASE_URL",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
