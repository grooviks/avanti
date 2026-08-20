"""Доменные исключения. Сервисный слой не знает про HTTP — бросает их,
а маппинг в HTTP-коды делают обработчики в main.py.
"""

from __future__ import annotations


class DomainError(Exception):
    """Базовое доменное исключение с человекочитаемым сообщением."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    """Сущность не найдена (→ 404)."""


class ConflictError(DomainError):
    """Конфликт состояния: занятый slug, удаление непустого узла (→ 409)."""


class DomainValidationError(DomainError):
    """Нарушение бизнес-правила: несуществующий родитель, цикл в дереве (→ 400)."""