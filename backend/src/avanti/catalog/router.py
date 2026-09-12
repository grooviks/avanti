"""HTTP-роуты каталога и сборка зависимостей (session → repo → service)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from avanti.catalog.repository import CatalogRepository
from avanti.catalog.schemas import CategoryOut, CategoryTreeOut, ProductOut
from avanti.catalog.service import CatalogService
from avanti.db import get_session


def get_service(session: Annotated[AsyncSession, Depends(get_session)]) -> CatalogService:
    return CatalogService(CatalogRepository(session))


ServiceDep = Annotated[CatalogService, Depends(get_service)]

router = APIRouter(prefix="/catalog", tags=["catalog"])


@router.get("/categories", response_model=list[CategoryTreeOut])
async def list_categories(service: ServiceDep) -> list[CategoryTreeOut]:
    """Дерево категорий целиком."""
    return await service.get_category_tree()


@router.get("/categories/{category_id}", response_model=CategoryOut)
async def get_category(category_id: int, service: ServiceDep) -> CategoryOut:
    category = await service.get_category(category_id)
    if category is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Категория не найдена")
    return category


@router.get("/categories/{category_id}/products", response_model=list[ProductOut])
async def list_category_products(category_id: int, service: ServiceDep) -> list[ProductOut]:
    products = await service.get_category_products(category_id)
    if products is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Категория не найдена")
    return products


@router.get("/products/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, service: ServiceDep) -> ProductOut:
    product = await service.get_product(product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Товар не найден")
    return product
