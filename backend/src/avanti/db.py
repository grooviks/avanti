"""Асинхронное подключение к БД: engine, фабрика сессий, декларативная база."""

from collections.abc import AsyncIterator
from datetime import datetime
from functools import lru_cache

from sqlalchemy import DateTime, func
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from avanti.config import get_settings


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""


class TimestampMixin:
    """created_at / updated_at, проставляются на стороне БД."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


@lru_cache
def get_engine() -> AsyncEngine:
    settings = get_settings()
    # echo не включаем: SQL-эхо управляется уровнем логгера sqlalchemy.engine
    # в setup_logging и идёт единым потоком через loguru, без дублей.
    return create_async_engine(str(settings.database_url))


@lru_cache
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI-зависимость: сессия БД на время запроса."""
    async with get_sessionmaker()() as session:
        yield session