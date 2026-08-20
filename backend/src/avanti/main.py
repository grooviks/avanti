"""Точка входа FastAPI-приложения: логирование, healthcheck, CORS, роутеры."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from avanti.admin.router import router as admin_router
from avanti.auth.router import router as auth_router
from avanti.catalog.router import router as catalog_router
from avanti.config import get_settings
from avanti.logging_setup import setup_logging


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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(catalog_router)
    app.include_router(auth_router)
    app.include_router(admin_router)

    logger.debug("Application assembled, routers connected")
    return app


app = create_app()