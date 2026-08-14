"""Бизнес-логика каталога: сборка дерева категорий, маппинг в DTO."""

from __future__ import annotations

from avanti.catalog.models import Category
from avanti.catalog.repository import CatalogRepository
from avanti.catalog.schemas import (
    CategoryOut,
    CategoryTreeOut,
    ImageOut,
    ProductOut,
)


class CatalogService:
    def __init__(self, repository: CatalogRepository) -> None:
        self._repo = repository

    @staticmethod
    def _to_tree_node(category: Category) -> CategoryTreeOut:
        """ORM → DTO без обращения к relationship `children`.

        Дерево связываем сами, поэтому children оставляем пустыми — иначе
        pydantic полез бы в ленивый ORM-атрибут и словил MissingGreenlet.
        Картинки уже подгружены через selectinload, читать их безопасно.
        """
        return CategoryTreeOut(
            id=category.id,
            parent_id=category.parent_id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            position=category.position,
            images=[ImageOut.model_validate(i) for i in category.images],
            children=[],
        )

    async def get_category_tree(self) -> list[CategoryTreeOut]:
        """Полное дерево категорий: собираем из плоского списка по parent_id."""
        categories = await self._repo.list_categories()

        nodes: dict[int, CategoryTreeOut] = {
            c.id: self._to_tree_node(c) for c in categories
        }
        roots: list[CategoryTreeOut] = []
        for category in categories:
            node = nodes[category.id]
            if category.parent_id is None:
                roots.append(node)
            else:
                parent = nodes.get(category.parent_id)
                # Родитель-сирота (битый parent_id) — трактуем узел как корневой.
                (parent.children if parent else roots).append(node)
        return roots

    async def get_category(self, category_id: int) -> CategoryOut | None:
        category = await self._repo.get_category(category_id)
        return CategoryOut.model_validate(category) if category else None

    async def get_category_products(self, category_id: int) -> list[ProductOut] | None:
        """Товары категории. None — если самой категории не существует."""
        category = await self._repo.get_category(category_id)
        if category is None:
            return None
        products = await self._repo.list_products(category_id)
        return [ProductOut.model_validate(p) for p in products]

    async def get_product(self, product_id: int) -> ProductOut | None:
        product = await self._repo.get_product(product_id)
        return ProductOut.model_validate(product) if product else None
