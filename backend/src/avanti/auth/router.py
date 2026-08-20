"""HTTP-роуты auth: вход и данные текущего пользователя."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from avanti.auth.models import User
from avanti.auth.repository import AuthRepository
from avanti.auth.schemas import Token, UserOut
from avanti.auth.security import create_access_token
from avanti.auth.service import AuthService
from avanti.db import get_session
from avanti.deps import get_current_user


def get_service(session: Annotated[AsyncSession, Depends(get_session)]) -> AuthService:
    return AuthService(AuthRepository(session))


ServiceDep = Annotated[AuthService, Depends(get_service)]

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    service: ServiceDep,
) -> Token:
    # form.username несёт email (поле стандартной OAuth2-формы).
    user = await service.authenticate(form.username, form.password)
    if user is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(access_token=create_access_token(subject=str(user.id)))


@router.get("/me", response_model=UserOut)
async def me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    return current_user