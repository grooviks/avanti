"""Создать/обновить суперпользователя из окружения.

Идемпотентно: если пользователь с таким email есть — обновляет пароль и поднимает
права до суперпользователя; иначе создаёт нового.

Креды берутся из env (с dev-дефолтами):
  AVANTI_ADMIN_EMAIL    (default admin@avanti.local)
  AVANTI_ADMIN_PASSWORD (default admin12345)

Запуск: uv run python scripts/create_admin.py
"""

import asyncio
import os

from avanti.auth.models import User
from avanti.auth.security import hash_password
from avanti.db import get_sessionmaker

ADMIN_EMAIL = os.getenv("AVANTI_ADMIN_EMAIL", "admin@avanti.app")
ADMIN_PASSWORD = os.getenv("AVANTI_ADMIN_PASSWORD", "admin12345")


async def create_admin() -> None:
    async with get_sessionmaker()() as session:
        from sqlalchemy import select

        user = await session.scalar(select(User).where(User.email == ADMIN_EMAIL))
        if user is None:
            user = User(email=ADMIN_EMAIL, hashed_password=hash_password(ADMIN_PASSWORD))
            session.add(user)
            action = "создан"
        else:
            user.hashed_password = hash_password(ADMIN_PASSWORD)
            action = "обновлён"
        user.is_active = True
        user.is_superuser = True
        await session.commit()
        print(f"Суперпользователь {ADMIN_EMAIL} {action}")


if __name__ == "__main__":
    asyncio.run(create_admin())