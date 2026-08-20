"""Общие FastAPI-зависимости: текущий пользователь и проверка прав."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from avanti.auth.models import User
from avanti.auth.repository import AuthRepository
from avanti.auth.security import decode_token
from avanti.db import get_session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

_credentials_error = HTTPException(
    status.HTTP_401_UNAUTHORIZED,
    "Не удалось подтвердить учётные данные",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    payload = decode_token(token)
    if payload is None:
        raise _credentials_error
    subject = payload.get("sub")
    if subject is None:
        raise _credentials_error

    user = await AuthRepository(session).get_by_id(int(subject))
    if user is None or not user.is_active:
        raise _credentials_error
    return user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_superuser:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Недостаточно прав")
    return current_user