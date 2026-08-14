"""Фикстуры интеграционных тестов.

Тесты ходят в реальный Postgres (docker-compose, порт 5433) — это осознанно
интеграционный слой: проверяем связку API ↔ БД целиком, а не моки.
"""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from avanti.catalog.models import Category, Product
from avanti.db import get_engine, get_sessionmaker
from avanti.main import app


@pytest.fixture(autouse=True)
async def _dispose_engine() -> AsyncIterator[None]:
    """Сбрасываем пул после каждого теста.

    pytest-asyncio даёт каждому тесту свой event loop, а кэшированный engine
    держит соединения от предыдущего loop — без dispose второй тест словил бы
    'attached to a different loop'.
    """
    yield
    await get_engine().dispose()


@pytest.fixture
async def seed_categories() -> AsyncIterator[dict[str, int]]:
    """Кладёт минимальное дерево (root → child) и отдаёт их id.

    Чистит таблицы каталога и до, и после — тест не зависит от ручного seed
    и не оставляет мусора.
    """
    async with get_sessionmaker()() as session:
        await session.execute(delete(Product))
        await session.execute(delete(Category))

        root = Category(name="Тестовая гостиная", slug="test-living", position=1)
        child = Category(name="Тестовые диваны", slug="test-sofas", position=1, parent=root)
        session.add_all([root, child])
        await session.flush()
        ids = {"root": root.id, "child": child.id}
        await session.commit()

    yield ids

    async with get_sessionmaker()() as session:
        await session.execute(delete(Product))
        await session.execute(delete(Category))
        await session.commit()


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c