"""Импорт снимка старого Flask/MySQL-каталога в новый Postgres.

На старой ВМ ``export_legacy_catalog.py`` формирует JSON-снимок и загружает
файлы в S3. Этот скрипт запускается на новой ВМ: в Postgres попадают данные
снимка, а в БД записываются публичные S3 URL.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import shutil
from collections import defaultdict
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any
from urllib.parse import quote
from uuid import uuid4

from sqlalchemy import MetaData, Table, func, select, text
from sqlalchemy.engine import create_engine

from avanti.catalog.models import Category, CategoryImage, Product, ProductImage
from avanti.config import get_settings
from avanti.db import get_sessionmaker
from avanti.legacy_migration import prepare_categories, prepare_products

LEGACY_TABLES = ("categories", "products", "category_images", "product_images")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Перенос старого каталога Avanti")
    parser.add_argument("--apply", action="store_true", help="выполнить импорт вместо dry-run")
    parser.add_argument(
        "--legacy-snapshot", type=Path, help="JSON-снимок от export_legacy_catalog.py"
    )
    parser.add_argument(
        "--legacy-images-root", type=Path, help="локальная папка images для старого режима"
    )
    parser.add_argument(
        "--s3-public-base-url", help="например https://storage.yandexcloud.net/bucket"
    )
    parser.add_argument("--s3-prefix", help="префикс объектов из экспортного манифеста")
    return parser.parse_args()


def load_legacy_rows(database_url: str) -> dict[str, list[Mapping[str, Any]]]:
    engine = create_engine(database_url)
    try:
        metadata = MetaData()
        tables = {name: Table(name, metadata, autoload_with=engine) for name in LEGACY_TABLES}
        with engine.connect() as connection:
            return {
                name: [
                    dict(row)
                    for row in connection.execute(select(table).order_by(table.c.id)).mappings()
                ]
                for name, table in tables.items()
            }
    finally:
        engine.dispose()


def load_snapshot(path: Path) -> dict[str, list[Mapping[str, Any]]]:
    try:
        tables = json.loads(path.read_text(encoding="utf-8"))["tables"]
        if not all(isinstance(tables[name], list) for name in LEGACY_TABLES):
            raise ValueError
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        raise SystemExit(f"Некорректный снимок {path}: {error}") from error
    return {name: tables[name] for name in LEGACY_TABLES}


def image_rows_with_positions(
    rows: Iterable[Mapping[str, Any]], foreign_key: str, *, basic_first: bool = False
) -> list[tuple[Mapping[str, Any], int]]:
    """Нумерует картинки внутри сущности; legacy basic_image становится обложкой."""
    grouped: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        if row.get(foreign_key) is not None:
            grouped[int(row[foreign_key])].append(row)
    result: list[tuple[Mapping[str, Any], int]] = []
    for entity_id in sorted(grouped):
        ordered = sorted(
            grouped[entity_id],
            key=lambda row: (
                not bool(row.get("basic_image", False)) if basic_first else False,
                int(row["id"]),
            ),
        )
        result.extend((row, position) for position, row in enumerate(ordered))
    return result


def s3_url(base_url: str, prefix: str, scope: str, filename: str) -> str:
    parts = [quote(part.strip("/"), safe="/") for part in (prefix, scope, filename) if part]
    return f"{base_url.rstrip('/')}/{'/'.join(parts)}"


def validate_image_source(
    rows: dict[str, list[Mapping[str, Any]]], images_root: Path
) -> list[Path]:
    missing: list[Path] = []
    for table_name, scope in (("category_images", "categories"), ("product_images", "products")):
        for row in rows[table_name]:
            filename = row.get("filename")
            path = images_root / scope / str(filename)
            if not filename or not path.is_file():
                missing.append(path)
    return missing


async def target_is_empty() -> bool:
    async with get_sessionmaker()() as session:
        categories = await session.scalar(select(func.count()).select_from(Category))
        products = await session.scalar(select(func.count()).select_from(Product))
    return categories == 0 and products == 0


async def import_catalog(
    categories: Iterable[Any],
    products: Iterable[Any],
    image_rows: dict[str, list[Mapping[str, Any]]],
    *,
    images_root: Path | None,
    s3_base_url: str | None,
    s3_prefix: str | None,
) -> int:
    settings = get_settings()
    category_list, product_list = list(categories), list(products)
    entity_ids = {
        "category_id": {item.id for item in category_list},
        "product_id": {item.id for item in product_list},
    }
    imported_images = 0

    def image_url(scope: str, filename: str) -> str:
        nonlocal imported_images
        imported_images += 1
        if s3_base_url:
            return s3_url(s3_base_url, s3_prefix or "", scope, filename)
        assert images_root is not None
        source = images_root / scope / filename
        destination_name = f"{uuid4().hex}{source.suffix.lower()}"
        destination = settings.media_root / scope / destination_name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return f"{settings.media_url_prefix}/{scope}/{destination_name}"

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
        for table_name, model, scope, foreign_key, basic_first in (
            ("category_images", CategoryImage, "categories", "category_id", False),
            ("product_images", ProductImage, "products", "product_id", True),
        ):
            for row, position in image_rows_with_positions(
                image_rows[table_name], foreign_key, basic_first=basic_first
            ):
                entity_id, filename = int(row[foreign_key]), str(row["filename"])
                if entity_id in entity_ids[foreign_key]:
                    session.add(
                        model(
                            **{foreign_key: entity_id},
                            url=image_url(scope, filename),
                            position=position,
                        )
                    )
        await session.commit()
        for table_name in ("categories", "products"):
            await session.execute(
                text(
                    "SELECT setval(pg_get_serial_sequence(:table_name, 'id'), "
                    f"COALESCE((SELECT MAX(id) FROM {table_name}), 1), true)"
                ),
            )
        await session.commit()
    return imported_images


async def main() -> None:
    args, settings = parse_args(), get_settings()
    if args.s3_public_base_url and not args.s3_prefix:
        raise SystemExit("Для S3 задайте --s3-prefix из экспорта")
    if args.legacy_snapshot:
        rows = load_snapshot(args.legacy_snapshot)
    elif settings.legacy_database_url:
        rows = load_legacy_rows(settings.legacy_database_url)
    else:
        raise SystemExit("Задайте --legacy-snapshot или AVANTI_LEGACY_DATABASE_URL")
    categories = prepare_categories(rows["categories"])
    products, skipped_products = prepare_products(
        rows["products"], {item.id for item in categories}
    )
    image_count = len(rows["category_images"]) + len(rows["product_images"])
    print(f"Legacy: {len(categories)} categories, {len(products)} products, {image_count} images")
    if skipped_products:
        print(f"Skipped products without a valid category: {skipped_products}")
    if not args.apply:
        print("Dry-run complete. Re-run with --apply to write into an empty Postgres database.")
        return
    if not await target_is_empty():
        raise SystemExit("Целевая БД не пуста: перенос отменён")
    if image_count and not args.s3_public_base_url:
        if not args.legacy_images_root:
            raise SystemExit("Для фотографий задайте S3 URL/префикс или --legacy-images-root")
        missing = validate_image_source(rows, args.legacy_images_root)
        if missing:
            raise SystemExit(f"Не найдены {len(missing)} файлов изображений; импорт отменён")
    imported = await import_catalog(
        categories,
        products,
        rows,
        images_root=args.legacy_images_root,
        s3_base_url=args.s3_public_base_url,
        s3_prefix=args.s3_prefix,
    )
    print(f"Migration complete: images={imported}")


if __name__ == "__main__":
    asyncio.run(main())
