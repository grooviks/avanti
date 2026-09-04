"""Точка входа FastAPI-приложения: логирование, healthcheck, CORS, роутеры."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from avanti.admin.router import router as admin_router
from avanti.auth.router import router as auth_router
from avanti.catalog.router import router as catalog_router
from avanti.config import get_settings
from avanti.core.exceptions import (
    ConflictError,
    DomainError,
    DomainValidationError,
    NotFoundError,
)
from avanti.logging_setup import setup_logging
from avanti.media.storage import LocalStorage

# Доменное исключение → HTTP-статус.
_DOMAIN_STATUS: dict[type[DomainError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    ConflictError: status.HTTP_409_CONFLICT,
    DomainValidationError: status.HTTP_400_BAD_REQUEST,
}


def _register_exception_handlers(app: FastAPI) -> None:
    async def handle_domain_error(_: Request, exc: DomainError) -> JSONResponse:
        code = _DOMAIN_STATUS.get(type(exc), status.HTTP_400_BAD_REQUEST)
        return JSONResponse(status_code=code, content={"detail": exc.message})

    for exc_type in _DOMAIN_STATUS:
        app.add_exception_handler(exc_type, handle_domain_error)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logger.info("{} starting up (debug={})", settings.app_name, settings.debug)
    yield
    logger.info("{} shut down", settings.app_name)


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.debug)

    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.state.media_storage = LocalStorage(
        settings.media_root, settings.media_url_prefix, settings.media_max_upload_bytes
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _register_exception_handlers(app)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(catalog_router)
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.mount(
        settings.media_url_prefix,
        StaticFiles(directory=settings.media_root),
        name="media",
    )

    logger.debug("Application assembled, routers connected")
    return app


app = create_app()
