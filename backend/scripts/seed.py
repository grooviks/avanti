"""Засеять каталог тестовыми данными для ручной проверки.

Идемпотентно: перед вставкой чистит таблицы каталога.
Запуск: uv run python scripts/seed.py
"""

import asyncio
from decimal import Decimal

from sqlalchemy import delete

from avanti.catalog.models import Category, Product, ProductImage
from avanti.db import get_sessionmaker


async def seed() -> None:
    async with get_sessionmaker()() as session:
        # Чистим в порядке зависимостей (products/images уйдут каскадом, но явно надёжнее).
        await session.execute(delete(Product))
        await session.execute(delete(Category))

        living = Category(name="Гостиная", slug="living-room", position=1)
        sofas = Category(name="Диваны", slug="sofas", position=1, parent=living)
        tables = Category(name="Столы", slug="tables", position=2, parent=living)
        bedroom = Category(name="Спальня", slug="bedroom", position=2)

        session.add_all([living, sofas, tables, bedroom])
        await session.flush()

        session.add_all(
            [
                Product(
                    name="Диван «Осло»",
                    slug="sofa-oslo",
                    description="Трёхместный диван, серый велюр",
                    price=Decimal("54990.00"),
                    sku="SOFA-OSLO-3",
                    category=sofas,
                    images=[
                        ProductImage(
                            url="https://example.com/oslo-1.jpg",
                            alt="Осло вид спереди",
                            position=1,
                        ),
                    ],
                ),
                Product(
                    name="Диван «Берген»",
                    slug="sofa-bergen",
                    description="Угловой диван, бежевая рогожка",
                    price=Decimal("72990.00"),
                    sku="SOFA-BERGEN-L",
                    category=sofas,
                ),
                Product(
                    name="Стол обеденный «Норд»",
                    slug="table-nord",
                    description="Дубовый стол, 180×90",
                    price=Decimal("39990.00"),
                    sku="TABLE-NORD-180",
                    category=tables,
                ),
            ]
        )

        await session.commit()
        print("Засеяно: 4 категории, 3 товара")


if __name__ == "__main__":
    asyncio.run(seed())
