"""Admin-роуты: write-CRUD каталога под аутентификацией суперпользователя.

Весь роутер закрыт зависимостью get_current_superuser. Пока — категории;
товары и картинки добавим следующими шагами.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from avanti.catalog.repository import CatalogRepository
from avanti.catalog.schemas import CategoryCreate, CategoryOut, CategoryUpdate
from avanti.catalog.service import CatalogService
from avanti.db import get_session
from avanti.deps import get_current_superuser


def get_service(session: Annotated[AsyncSession, Depends(get_session)]) -> CatalogService:
    return CatalogService(CatalogRepository(session))


ServiceDep = Annotated[CatalogService, Depends(get_service)]

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_superuser)],
)


@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryCreate, service: ServiceDep) -> CategoryOut:
    return await service.create_category(data)


@router.patch("/categories/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: int, data: CategoryUpdate, service: ServiceDep
) -> CategoryOut:
    return await service.update_category(category_id, data)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, service: ServiceDep) -> None:
    await service.delete_category(category_id)