"""Асинхронное подключение к БД: engine, фабрика сессий, декларативная база."""

from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from avanti.config import get_settings


class Base(DeclarativeBase):
    """Базовый класс для всех ORM-моделей."""


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