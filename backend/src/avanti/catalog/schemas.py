"""Pydantic-схемы (DTO) каталога — то, что отдаётся наружу через API."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# slug: строчные буквы/цифры, разделённые дефисами (kebab-case).
Slug = Annotated[str, Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=255)]


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


class CategoryCreate(BaseModel):
    """Входные данные для создания категории (admin)."""

    name: str = Field(min_length=1, max_length=255)
    slug: Slug
    description: str | None = None
    position: int = 0
    parent_id: int | None = None


class CategoryUpdate(BaseModel):
    """Частичное обновление категории (admin) — все поля опциональны."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    slug: Slug | None = None
    description: str | None = None
    position: int | None = None
    parent_id: int | None = None