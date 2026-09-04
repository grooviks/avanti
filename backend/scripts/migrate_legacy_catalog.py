"""Перенос каталога старого Flask/MySQL в новый Postgres.

По умолчанию работает в dry-run: читает обе схемы и выводит план, не меняя
Postgres и файловое хранилище. Реальный перенос требует ``--apply`` и пустую
целевую БД. Учётные записи не переносятся: прежние пароли несовместимы с argon2.

Пример:
    uv run python scripts/migrate_legacy_catalog.py \
      --legacy-images-root ../avanti/app/static/images --apply
"""

from __future__ import annotations

import argparse
import asyncio
import shutil
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy import MetaData, Table, func, select, text
from sqlalchemy.engine import create_engine

from avanti.catalog.models import Category, CategoryImage, Product, ProductImage
from avanti.config import get_settings
from avanti.db import get_sessionmaker
from avanti.legacy_migration import prepare_categories, prepare_products


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Перенос старого каталога Avanti")
    parser.add_argument("--apply", action="store_true", help="выполнить перенос вместо dry-run")
    parser.add_argument(
        "--legacy-images-root",
        type=Path,
        help="путь к старой avanti/app/static/images; нужен для переноса файлов",
    )
    return parser.parse_args()


def load_legacy_rows(
    database_url: str,
) -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]], dict[str, list[Mapping[str, Any]]]]:
    engine = create_engine(database_url)
    try:
        metadata = MetaData()
        tables = {
            name: Table(name, metadata, autoload_with=engine)
            for name in ("categories", "products", "category_images", "product_images")
        }
        with engine.connect() as connection:
            rows = {
                name: [dict(row) for row in connection.execute(select(table)).mappings()]
                for name, table in tables.items()
            }
    finally:
        engine.dispose()
    return rows["categories"], rows["products"], rows


async def target_is_empty() -> bool:
    async with get_sessionmaker()() as session:
        categories = await session.scalar(select(func.count()).select_from(Category))
        products = await session.scalar(select(func.count()).select_from(Product))
    return categories == 0 and products == 0


async def import_catalog(
    categories: Iterable[Any],
    products: Iterable[Any],
    image_rows: dict[str, list[Mapping[str, Any]]],
    images_root: Path | None,
) -> tuple[int, int]:
    settings = get_settings()
    copied_images = 0
    skipped_images = 0
    category_list = list(categories)
    product_list = list(products)
    entity_ids = {
        "category_id": {item.id for item in category_list},
        "product_id": {item.id for item in product_list},
    }
    async with get_sessionmaker()() as session:
        session.add_all(
            [
                Category(
                    id=item.id,
                    parent_id=item.parent_id,
                    name=item.name,
                    slug=item.slug,
                    description=item.description,
                )
                for item in category_list
            ]
        )
        session.add_all(
            [
                Product(
                    id=item.id,
                    category_id=item.category_id,
                    name=item.name,
                    slug=item.slug,
                    description=item.description,
                    price=item.price,
                    sku=item.sku,
                    in_stock=item.in_stock,
                )
                for item in product_list
            ]
        )
        if images_root is not None:
            for table_name, model, scope, foreign_key in (
                ("category_images", CategoryImage, "categories", "category_id"),
                ("product_images", ProductImage, "products", "product_id"),
            ):
                for position, row in enumerate(image_rows[table_name]):
                    if int(row[foreign_key]) not in entity_ids[foreign_key]:
                        skipped_images += 1
                        continue
                    source = images_root / scope / str(row["filename"])
                    if not source.is_file():
                        skipped_images += 1
                        continue
                    filename = f"{uuid4().hex}{source.suffix.lower()}"
                    destination = settings.media_root / scope / filename
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source, destination)
                    session.add(
                        model(
                            **{foreign_key: int(row[foreign_key])},
                            url=f"{settings.media_url_prefix}/{scope}/{filename}",
                            position=position,
                        )
                    )
                    copied_images += 1
        await session.commit()
        # Явные id сохраняют связи со старым каталогом. Синхронизируем sequence,
        # иначе следующая вставка администратором может получить уже занятый id.
        for table_name in ("categories", "products"):
            await session.execute(
                text(
                    "SELECT setval(pg_get_serial_sequence(:table_name, 'id'), "
                    "COALESCE((SELECT MAX(id) FROM " + table_name + "), 1), true)"
                ),
                {"table_name": table_name},
            )
        await session.commit()
    return copied_images, skipped_images


async def main() -> None:
    args = parse_args()
    settings = get_settings()
    if not settings.legacy_database_url:
        raise SystemExit("Задайте AVANTI_LEGACY_DATABASE_URL в .env")
    category_rows, product_rows, image_rows = load_legacy_rows(settings.legacy_database_url)
    categories = prepare_categories(category_rows)
    products, skipped_products = prepare_products(product_rows, {item.id for item in categories})
    print(f"Legacy: {len(categories)} categories, {len(products)} products")
    if skipped_products:
        print(f"Skipped products without a valid category: {skipped_products}")
    image_count = len(image_rows["category_images"]) + len(image_rows["product_images"])
    print(f"Legacy images: {image_count}")
    if not args.apply:
        print("Dry-run complete. Re-run with --apply to write into an empty Postgres database.")
        return
    if not await target_is_empty():
        raise SystemExit("Целевая БД не пуста: перенос отменён")
    copied, skipped = await import_catalog(
        categories, products, image_rows, args.legacy_images_root
    )
    print(f"Migration complete: copied images={copied}, skipped missing images={skipped}")


if __name__ == "__main__":
    asyncio.run(main())
