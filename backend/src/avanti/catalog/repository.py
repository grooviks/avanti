"""Доступ к данным каталога. Только запросы к БД, без бизнес-логики и DTO."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from avanti.catalog.models import Category, Product


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