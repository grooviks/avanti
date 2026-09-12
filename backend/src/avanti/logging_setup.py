"""Единое логирование через loguru.

Перехватываем стандартный logging (uvicorn, sqlalchemy, alembic пишут туда),
чтобы весь вывод шёл одним цветным потоком loguru, а не вперемешку.
"""

import logging
import sys

from loguru import logger

# Логгеры, которые нужно завернуть в loguru: снимаем их родные хендлеры
# и гасим propagate, иначе строки задвоятся.
_INTERCEPTED = (
    "uvicorn",
    "uvicorn.error",
    "uvicorn.access",
    "sqlalchemy.engine",
    "alembic",
)

_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
    "<level>{level: <8}</level> "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
    "- <level>{message}</level>"
)


class InterceptHandler(logging.Handler):
    """Переливает записи стандартного logging в loguru, сохраняя уровень и источник."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Имя/функцию/строку берём прямо из stdlib-записи — так в логе виден
        # реальный источник (uvicorn.access и т.п.), а не внутренности logging.
        patched = logger.patch(
            lambda r: r.update(
                name=record.name,
                function=record.funcName,
                line=record.lineno,
            )
        )
        patched.opt(exception=record.exc_info).log(level, record.getMessage())


def setup_logging(debug: bool = False) -> None:
    """Настроить loguru как единый sink и перехватить стандартный logging.

    debug=True → уровень DEBUG и diagnose (подробные трейсбеки с переменными);
    в проде diagnose выключаем, чтобы не светить значения в логах.
    """
    level = "DEBUG" if debug else "INFO"

    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(level)
    for name in _INTERCEPTED:
        intercepted = logging.getLogger(name)
        intercepted.handlers = [InterceptHandler()]
        intercepted.propagate = False

    # SQL-эхо шумное — показываем его только в debug (SQLAlchemy пишет SQL на INFO).
    logging.getLogger("sqlalchemy.engine").setLevel("INFO" if debug else "WARNING")

    logger.remove()
    logger.add(
        sys.stderr,
        level=level,
        format=_FORMAT,
        colorize=True,
        backtrace=True,
        diagnose=debug,
    )