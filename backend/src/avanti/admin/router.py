"""Admin-роутер. Пока заготовка: один защищённый эндпоинт для проверки доступа.

Весь роутер требует суперпользователя. Реальный write-CRUD каталога — следующий шаг.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from avanti.deps import get_current_superuser

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_superuser)],
)


@router.get("/ping")
async def ping() -> dict[str, str]:
    return {"status": "pong"}