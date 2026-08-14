"""Pydantic-схемы (DTO) каталога — то, что отдаётся наружу через API."""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    alt: str | None = None
    position: int


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    name: str
    slug: str
    description: str | None = None
    price: Decimal
    sku: str | None = None
    in_stock: bool
    images: list[ImageOut] = []


class CategoryOut(BaseModel):
    """Категория без вложенных детей — для плоских ответов."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    parent_id: int | None = None
    name: str
    slug: str
    description: str | None = None
    position: int
    images: list[ImageOut] = []


class CategoryTreeOut(CategoryOut):
    """Категория с рекурсивно вложенными детьми — для дерева."""

    children: list[CategoryTreeOut] = []