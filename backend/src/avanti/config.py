"""Конфигурация приложения. Всё берётся из окружения — секретов в коде нет."""

from functools import lru_cache

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="AVANTI_",
        extra="ignore",
    )

    # Приложение
    app_name: str = "Avanti API"
    debug: bool = False
    secret_key: str = "change-me-in-env"  # переопределяется через AVANTI_SECRET_KEY

    # База данных
    database_url: PostgresDsn = (
        "postgresql+asyncpg://avanti:password@localhost:5433/avanti"  # type: ignore[assignment]
    )

    # CORS — источники фронтенда
    cors_origins: list[str] = ["http://localhost:3000"]

    # JWT
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30


@lru_cache
def get_settings() -> Settings:
    """Кэшированный синглтон настроек."""
    return Settings()