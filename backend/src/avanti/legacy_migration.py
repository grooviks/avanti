"""Подготовка данных старого Flask-каталога к переносу в новую схему.

Модуль не выполняет I/O: его можно тестировать отдельно от MySQL и Postgres.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

_TRANSLITERATION = str.maketrans(
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
    "abvgdeejzijklmnoprstufhzcss_y_eua",
)


@dataclass(frozen=True)
class LegacyCategory:
    id: int
    parent_id: int | None
    name: str
    slug: str
    description: str | None


@dataclass(frozen=True)
class LegacyProduct:
    id: int
    category_id: int
    name: str
    slug: str
    description: str | None
    price: Decimal
    sku: str
    in_stock: bool


def slugify(value: str, fallback: str) -> str:
    """Сделать ASCII kebab-case из старого названия, включая кириллицу."""
    value = value.lower().translate(_TRANSLITERATION)
    slug = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return slug or fallback


def prepare_categories(rows: Iterable[Mapping[str, Any]]) -> list[LegacyCategory]:
    slugs: set[str] = set()
    result: list[LegacyCategory] = []
    for row in sorted(rows, key=lambda item: int(item["id"])):
        category_id = int(row["id"])
        base_slug = slugify(str(row.get("name") or ""), f"category-{category_id}")
        slug = _unique_slug(base_slug, category_id, slugs)
        result.append(
            LegacyCategory(
                id=category_id,
                parent_id=_as_id(row.get("parent_id")),
                name=str(row.get("name") or f"Категория {category_id}").strip(),
                slug=slug,
                description=_as_text(row.get("description")),
            )
        )
    return result


def prepare_products(
    rows: Iterable[Mapping[str, Any]], category_ids: set[int]
) -> tuple[list[LegacyProduct], list[int]]:
    slugs: set[str] = set()
    products: list[LegacyProduct] = []
    skipped: list[int] = []
    for row in sorted(rows, key=lambda item: int(item["id"])):
        product_id = int(row["id"])
        category_id = _as_id(row.get("category_id"))
        if category_id not in category_ids:
            skipped.append(product_id)
            continue
        base_slug = slugify(str(row.get("name") or ""), f"product-{product_id}")
        products.append(
            LegacyProduct(
                id=product_id,
                category_id=category_id,
                name=str(row.get("name") or f"Товар {product_id}").strip(),
                slug=_unique_slug(base_slug, product_id, slugs),
                description=_as_text(row.get("detail")),
                price=Decimal(str(row.get("price") or 0)).quantize(Decimal("0.01")),
                sku=f"LEGACY-{product_id}",
                in_stock=bool(row.get("is_avail", True)),
            )
        )
    return products, skipped


def _unique_slug(base: str, entity_id: int, used: set[str]) -> str:
    slug = base
    if slug in used:
        slug = f"{base}-{entity_id}"
    used.add(slug)
    return slug


def _as_id(value: Any) -> int | None:
    return int(value) if value is not None else None


def _as_text(value: Any) -> str | None:
    return str(value) if value is not None else None
