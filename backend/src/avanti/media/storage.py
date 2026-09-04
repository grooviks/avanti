"""Интерфейс и локальная реализация файлового хранилища.

Каталог знает только URL картинки. Поэтому переход с локального диска на S3/MinIO
затронет этот модуль и wiring приложения, но не доменные модели каталога.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol
from uuid import uuid4

from fastapi import UploadFile

from avanti.core.exceptions import DomainValidationError, NotFoundError
from avanti.media.schemas import MediaOut

_CHUNK_SIZE = 1024 * 1024
_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}
_SCOPES = frozenset({"categories", "products"})


class Storage(Protocol):
    async def save(self, scope: str, upload: UploadFile) -> MediaOut: ...

    def delete(self, scope: str, filename: str) -> None: ...


class LocalStorage:
    """Хранилище на локальном диске с проверкой MIME-типа, сигнатуры и размера."""

    def __init__(self, root: Path, url_prefix: str, max_upload_bytes: int) -> None:
        self._root = root.resolve()
        self._root.mkdir(parents=True, exist_ok=True)
        self._url_prefix = url_prefix.rstrip("/")
        self._max_upload_bytes = max_upload_bytes

    async def save(self, scope: str, upload: UploadFile) -> MediaOut:
        self._validate_scope(scope)
        content_type = upload.content_type or ""
        extension = _CONTENT_TYPES.get(content_type)
        if extension is None:
            raise DomainValidationError("Разрешены только JPEG, PNG, WebP и GIF изображения")

        first_chunk = await upload.read(_CHUNK_SIZE)
        if not first_chunk:
            raise DomainValidationError("Нельзя загрузить пустой файл")
        if not self._has_valid_signature(content_type, first_chunk):
            raise DomainValidationError(
                "Содержимое файла не соответствует заявленному типу изображения"
            )

        filename = f"{uuid4().hex}{extension}"
        destination = self._path_for(scope, filename)
        temporary = destination.with_suffix(f"{extension}.uploading")
        size = len(first_chunk)
        try:
            with temporary.open("wb") as target:
                target.write(first_chunk)
                while chunk := await upload.read(_CHUNK_SIZE):
                    size += len(chunk)
                    if size > self._max_upload_bytes:
                        raise DomainValidationError(
                            f"Размер изображения не должен превышать {self._max_upload_bytes} байт"
                        )
                    target.write(chunk)
            if size > self._max_upload_bytes:
                raise DomainValidationError(
                    f"Размер изображения не должен превышать {self._max_upload_bytes} байт"
                )
            temporary.replace(destination)
        except Exception:
            temporary.unlink(missing_ok=True)
            raise
        finally:
            await upload.close()

        return MediaOut(
            filename=filename,
            url=f"{self._url_prefix}/{scope}/{filename}",
            content_type=content_type,
            size=size,
        )

    def delete(self, scope: str, filename: str) -> None:
        self._validate_scope(scope)
        path = self._path_for(scope, filename)
        if not path.is_file():
            raise NotFoundError("Файл не найден")
        path.unlink()

    def _path_for(self, scope: str, filename: str) -> Path:
        path = (self._root / scope / filename).resolve()
        if not path.is_relative_to(self._root / scope) or path.name != filename:
            raise DomainValidationError("Недопустимое имя файла")
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    @staticmethod
    def _validate_scope(scope: str) -> None:
        if scope not in _SCOPES:
            raise DomainValidationError("Недопустимый раздел медиа")

    @staticmethod
    def _has_valid_signature(content_type: str, data: bytes) -> bool:
        signatures = {
            "image/jpeg": data.startswith(b"\xff\xd8\xff"),
            "image/png": data.startswith(b"\x89PNG\r\n\x1a\n"),
            "image/gif": data.startswith((b"GIF87a", b"GIF89a")),
            "image/webp": len(data) >= 12
            and data.startswith(b"RIFF")
            and data[8:12] == b"WEBP",
        }
        return signatures[content_type]
