"""Добавить или обновить три демонстрационные категории и по 20 товаров.

Изображения сохранены локально в ``media``: витрина не зависит от внешних CDN.
Повторный запуск синхронизирует только демонстрационные записи, не затрагивая
остальной каталог.
"""

import asyncio
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from avanti.catalog.models import Category, CategoryImage, Product, ProductImage
from avanti.db import get_sessionmaker


@dataclass(frozen=True)
class DemoCategory:
    name: str
    slug: str
    nouns: tuple[str, ...]
    description: str
    base_price: int
    images: tuple[str, ...]


SOFA_IMAGES = ("/media/products/demo-sofas.jpg",)
DINING_IMAGES = ("/media/products/demo-dining.jpg",)
BEDROOM_IMAGES = ("/media/products/demo-bedroom.jpg",)

CATEGORIES = (
    DemoCategory(
        name="Мягкая мебель",
        slug="upholstered-furniture",
        nouns=("Диван", "Кресло", "Пуф", "Кушетка"),
        description="Комфортная мягкая мебель для отдыха, встреч и уютных вечеров дома.",
        base_price=28900,
        images=SOFA_IMAGES,
    ),
    DemoCategory(
        name="Обеденные группы",
        slug="dining-sets",
        nouns=("Стол", "Стул", "Обеденная группа", "Скамья"),
        description="Столы и посадочные места для семейных ужинов и неспешных разговоров.",
        base_price=15900,
        images=DINING_IMAGES,
    ),
    DemoCategory(
        name="Мебель для спальни",
        slug="bedroom-furniture",
        nouns=("Кровать", "Тумба", "Комод", "Банкетка"),
        description="Спокойные и продуманные предметы для личного пространства и отдыха.",
        base_price=19900,
        images=BEDROOM_IMAGES,
    ),
)

COLLECTIONS = ("Луна", "Эстель", "Норд", "Терра", "Мира")
MATERIALS = ("натурального дуба", "рогожки", "велюра", "шпона ореха", "букле")


def product_images(spec: DemoCategory, name: str, image_count: int) -> list[ProductImage]:
    return [
        ProductImage(url=url, alt=name, position=position)
        for position, url in enumerate(spec.images[:image_count])
    ]


async def add_demo_catalog() -> None:
    added_categories = 0
    added_products = 0
    async with get_sessionmaker()() as session:
        for category_position, spec in enumerate(CATEGORIES, start=1):
            category = await session.scalar(
                select(Category)
                .where(Category.slug == spec.slug)
                .options(selectinload(Category.images))
            )
            if category is None:
                category = Category(
                    name=spec.name,
                    slug=spec.slug,
                    description=spec.description,
                    position=100 + category_position,
                )
                session.add(category)
                await session.flush()
                added_categories += 1
            category.images[:] = [CategoryImage(url=spec.images[0], alt=spec.name, position=0)]

            for index in range(20):
                noun = spec.nouns[index % len(spec.nouns)]
                collection = COLLECTIONS[index % len(COLLECTIONS)]
                name = f"{noun} «{collection} {index + 1:02d}»"
                slug = f"demo-{spec.slug}-{index + 1:02d}"
                existing = await session.scalar(
                    select(Product)
                    .where(Product.slug == slug)
                    .options(selectinload(Product.images))
                )
                image_count = index % 3 + 1
                if existing is not None:
                    existing.images[:] = product_images(spec, name, image_count)
                    continue
                material = MATERIALS[index % len(MATERIALS)]
                session.add(
                    Product(
                        category_id=category.id,
                        name=name,
                        slug=slug,
                        description=(
                            f"Модель из {material}: лаконичные линии, продуманные пропорции "
                            "и комфорт для ежедневного использования."
                        ),
                        price=Decimal(spec.base_price + index * 2450),
                        sku=f"DEMO-{category_position:02d}-{index + 1:03d}",
                        in_stock=index % 6 != 0,
                        images=product_images(spec, name, image_count),
                    )
                )
                added_products += 1
        await session.commit()
    print(f"Добавлено: {added_categories} категорий, {added_products} товаров")


if __name__ == "__main__":
    asyncio.run(add_demo_catalog())
