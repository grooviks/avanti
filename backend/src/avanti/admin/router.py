"""Admin-роуты: write-CRUD каталога под аутентификацией суперпользователя.

Весь роутер закрыт зависимостью get_current_superuser.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from avanti.catalog.repository import CatalogRepository
from avanti.catalog.schemas import (
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
    ProductCreate,
    ProductOut,
    ProductUpdate,
)
from avanti.catalog.service import CatalogService
from avanti.db import get_session
from avanti.deps import get_current_superuser
from avanti.media.schemas import MediaOut
from avanti.media.storage import Storage


def get_service(session: Annotated[AsyncSession, Depends(get_session)]) -> CatalogService:
    return CatalogService(CatalogRepository(session))


ServiceDep = Annotated[CatalogService, Depends(get_service)]


def get_storage(request: Request) -> Storage:
    return request.app.state.media_storage


StorageDep = Annotated[Storage, Depends(get_storage)]

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


@router.post("/products", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(data: ProductCreate, service: ServiceDep) -> ProductOut:
    return await service.create_product(data)


@router.patch("/products/{product_id}", response_model=ProductOut)
async def update_product(product_id: int, data: ProductUpdate, service: ServiceDep) -> ProductOut:
    return await service.update_product(product_id, data)


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, service: ServiceDep) -> None:
    await service.delete_product(product_id)


@router.post("/media/{scope}", response_model=MediaOut, status_code=status.HTTP_201_CREATED)
async def upload_media(
    scope: str, file: Annotated[UploadFile, File(...)], storage: StorageDep
) -> MediaOut:
    """Загрузить изображение в раздел товара или категории.

    Ответный URL передаётся затем в ``images`` при создании/обновлении каталога.
    """
    return await storage.save(scope, file)


@router.delete("/media/{scope}/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(scope: str, filename: str, storage: StorageDep) -> None:
    storage.delete(scope, filename)
