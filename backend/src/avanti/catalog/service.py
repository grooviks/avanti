"""Бизнес-логика каталога: сборка дерева категорий, маппинг в DTO."""

from __future__ import annotations

from avanti.catalog.models import Category
from avanti.catalog.repository import CatalogRepository
from avanti.catalog.schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryTreeOut,
    CategoryUpdate,
    ImageOut,
    ProductCreate,
    ProductOut,
    ProductUpdate,
)
from avanti.core.exceptions import (
    ConflictError,
    DomainValidationError,
    NotFoundError,
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

    # --- write (admin) ---

    async def create_category(self, data: CategoryCreate) -> CategoryOut:
        if await self._repo.get_category_by_slug(data.slug) is not None:
            raise ConflictError(f"Категория со slug «{data.slug}» уже существует")
        if data.parent_id is not None and await self._repo.get_category(data.parent_id) is None:
            raise DomainValidationError(f"Родительская категория {data.parent_id} не найдена")

        category = await self._repo.create_category(
            name=data.name,
            slug=data.slug,
            description=data.description,
            position=data.position,
            parent_id=data.parent_id,
        )
        return CategoryOut.model_validate(category)

    async def update_category(self, category_id: int, data: CategoryUpdate) -> CategoryOut:
        category = await self._repo.get_category(category_id)
        if category is None:
            raise NotFoundError(f"Категория {category_id} не найдена")

        fields = data.model_dump(exclude_unset=True)

        new_slug = fields.get("slug")
        if new_slug is not None and new_slug != category.slug:
            existing = await self._repo.get_category_by_slug(new_slug)
            if existing is not None and existing.id != category_id:
                raise ConflictError(f"Категория со slug «{new_slug}» уже существует")

        if "parent_id" in fields and fields["parent_id"] != category.parent_id:
            new_parent_id = fields["parent_id"]
            if new_parent_id is not None:
                if await self._repo.get_category(new_parent_id) is None:
                    raise DomainValidationError(
                        f"Родительская категория {new_parent_id} не найдена"
                    )
                await self._ensure_no_cycle(category_id, new_parent_id)

        updated = await self._repo.update_category(category, **fields)
        return CategoryOut.model_validate(updated)

    async def delete_category(self, category_id: int) -> None:
        category = await self._repo.get_category(category_id)
        if category is None:
            raise NotFoundError(f"Категория {category_id} не найдена")
        if await self._repo.count_children(category_id) > 0:
            raise ConflictError("Нельзя удалить категорию с подкатегориями")
        if await self._repo.count_products(category_id) > 0:
            raise ConflictError("Нельзя удалить категорию с товарами")
        await self._repo.delete_category(category)

    async def _ensure_no_cycle(self, category_id: int, new_parent_id: int) -> None:
        """Запретить назначать родителем саму категорию или её потомка.

        Поднимаемся от нового родителя вверх по дереву: если встретили саму
        категорию — назначение создало бы цикл.
        """
        parent_of = {c.id: c.parent_id for c in await self._repo.list_categories()}
        node: int | None = new_parent_id
        while node is not None:
            if node == category_id:
                raise DomainValidationError(
                    "Нельзя переместить категорию внутрь её же поддерева"
                )
            node = parent_of.get(node)

    async def create_product(self, data: ProductCreate) -> ProductOut:
        await self._ensure_product_fields_are_available(data.slug, data.sku)
        await self._ensure_category_exists(data.category_id)
        product = await self._repo.create_product(
            category_id=data.category_id,
            name=data.name,
            slug=data.slug,
            description=data.description,
            price=data.price,
            sku=data.sku,
            in_stock=data.in_stock,
            images=[image.model_dump() for image in data.images],
        )
        return ProductOut.model_validate(product)

    async def update_product(self, product_id: int, data: ProductUpdate) -> ProductOut:
        product = await self._repo.get_product(product_id)
        if product is None:
            raise NotFoundError(f"Товар {product_id} не найден")

        fields = data.model_dump(exclude_unset=True)
        if "category_id" in fields:
            await self._ensure_category_exists(fields["category_id"])

        new_slug = fields.get("slug")
        new_sku = fields.get("sku")
        await self._ensure_product_fields_are_available(
            new_slug, new_sku, exclude_product_id=product_id
        )
        updated = await self._repo.update_product(product, **fields)
        return ProductOut.model_validate(updated)

    async def delete_product(self, product_id: int) -> None:
        product = await self._repo.get_product(product_id)
        if product is None:
            raise NotFoundError(f"Товар {product_id} не найден")
        await self._repo.delete_product(product)

    async def _ensure_category_exists(self, category_id: int) -> None:
        if await self._repo.get_category(category_id) is None:
            raise DomainValidationError(f"Категория {category_id} не найдена")

    async def _ensure_product_fields_are_available(
        self, slug: str | None, sku: str | None, *, exclude_product_id: int | None = None
    ) -> None:
        if slug is not None:
            existing = await self._repo.get_product_by_slug(slug)
            if existing is not None and existing.id != exclude_product_id:
                raise ConflictError(f"Товар со slug «{slug}» уже существует")
        if sku is not None:
            existing = await self._repo.get_product_by_sku(sku)
            if existing is not None and existing.id != exclude_product_id:
                raise ConflictError(f"Товар с SKU «{sku}» уже существует")
