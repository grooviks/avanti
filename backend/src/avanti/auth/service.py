"""Бизнес-логика auth."""

from __future__ import annotations

from avanti.auth.models import User
from avanti.auth.repository import AuthRepository
from avanti.auth.security import verify_password


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self._repo = repository

    async def authenticate(self, email: str, password: str) -> User | None:
        """Вернуть пользователя, если email существует, пароль верен и аккаунт активен."""
        user = await self._repo.get_by_email(email)
        if user is None or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user