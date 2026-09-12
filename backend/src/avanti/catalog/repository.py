"""Доступ к данным каталога. Только запросы к БД, без бизнес-логики и DTO."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from avanti.catalog.models import Category, CategoryImage, Product, ProductImage


class CatalogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_categories(self) -> list[Category]:
        """Все категории с картинками, отсортированные по position.

        Дерево из плоского списка собирает сервисный слой — для домена мебели
        категорий немного, отдельный рекурсивный обход БД избыточен.
        """
        stmt = (
            select(Category)
            .options(selectinload(Category.images))
            .order_by(Category.position, Category.id)
        )
        return list((await self._session.scalars(stmt)).all())

    async def get_category(self, category_id: int) -> Category | None:
        stmt = (
            select(Category)
            .where(Category.id == category_id)
            .options(selectinload(Category.images))
        )
        return await self._session.scalar(stmt)

    async def list_products(self, category_id: int) -> list[Product]:
        stmt = (
            select(Product)
            .where(Product.category_id == category_id)
            .options(selectinload(Product.images))
            .order_by(Product.id)
        )
        return list((await self._session.scalars(stmt)).all())

    async def get_product(self, product_id: int) -> Product | None:
        stmt = (
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.images))
        )
        return await self._session.scalar(stmt)

    async def get_category_by_slug(self, slug: str) -> Category | None:
        return await self._session.scalar(select(Category).where(Category.slug == slug))

    async def get_product_by_slug(self, slug: str) -> Product | None:
        return await self._session.scalar(select(Product).where(Product.slug == slug))

    async def get_product_by_sku(self, sku: str) -> Product | None:
        return await self._session.scalar(select(Product).where(Product.sku == sku))

    async def count_children(self, category_id: int) -> int:
        stmt = select(func.count()).select_from(Category).where(
            Category.parent_id == category_id
        )
        return await self._session.scalar(stmt) or 0

    async def count_products(self, category_id: int) -> int:
        stmt = select(func.count()).select_from(Product).where(
            Product.category_id == category_id
        )
        return await self._session.scalar(stmt) or 0

    async def create_category(self, **fields: Any) -> Category:
        images = fields.pop("images", [])
        category = Category(**fields)
        category.images = [CategoryImage(**image) for image in images]
        self._session.add(category)
        await self._session.commit()
        # Явно грузим images ([]), иначе pydantic полезет в ленивый relationship.
        await self._session.refresh(category, attribute_names=["images"])
        return category

    async def update_category(self, category: Category, **fields: Any) -> Category:
        images = fields.pop("images", None)
        for name, value in fields.items():
            setattr(category, name, value)
        if images is not None:
            category.images[:] = [CategoryImage(**image) for image in images]
        await self._session.commit()
        await self._session.refresh(category, attribute_names=["images"])
        return category

    async def delete_category(self, category: Category) -> None:
        await self._session.delete(category)
        await self._session.commit()

    async def create_product(self, **fields: Any) -> Product:
        images = fields.pop("images", [])
        product = Product(**fields)
        product.images = [ProductImage(**image) for image in images]
        self._session.add(product)
        await self._session.commit()
        await self._session.refresh(product, attribute_names=["images"])
        return product

    async def update_product(self, product: Product, **fields: Any) -> Product:
        images = fields.pop("images", None)
        for name, value in fields.items():
            setattr(product, name, value)
        if images is not None:
            product.images[:] = [ProductImage(**image) for image in images]
        await self._session.commit()
        await self._session.refresh(product, attribute_names=["images"])
        return product

    async def delete_product(self, product: Product) -> None:
        await self._session.delete(product)
        await self._session.commit()
