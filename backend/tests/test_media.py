"""Интеграционные тесты admin API для локального хранилища изображений."""

from pathlib import Path

import pytest
from httpx import AsyncClient

from avanti.admin.router import get_storage
from avanti.main import app
from avanti.media.storage import LocalStorage

_PNG = b"\x89PNG\r\n\x1a\n" + b"test-image"


async def _auth(client: AsyncClient, superuser: dict[str, str]) -> dict[str, str]:
    response = await client.post(
        "/auth/login",
        data={"username": superuser["email"], "password": superuser["password"]},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def media_storage(tmp_path: Path) -> LocalStorage:
    storage = LocalStorage(tmp_path, "/media", 1024)
    app.dependency_overrides[get_storage] = lambda: storage
    yield storage
    app.dependency_overrides.pop(get_storage, None)


async def test_upload_and_delete_image(
    client: AsyncClient, superuser: dict[str, str], media_storage: LocalStorage
) -> None:
    headers = await _auth(client, superuser)
    uploaded = await client.post(
        "/admin/media/products",
        files={"file": ("sofa.png", _PNG, "image/png")},
        headers=headers,
    )
    assert uploaded.status_code == 201
    media = uploaded.json()
    assert media["url"].startswith("/media/products/")
    assert (media_storage._root / "products" / media["filename"]).is_file()

    deleted = await client.delete(
        f"/admin/media/products/{media['filename']}", headers=headers
    )
    assert deleted.status_code == 204
    assert not (media_storage._root / "products" / media["filename"]).exists()


async def test_upload_requires_auth_and_valid_image(
    client: AsyncClient, superuser: dict[str, str], media_storage: LocalStorage
) -> None:
    no_auth = await client.post(
        "/admin/media/products", files={"file": ("sofa.png", _PNG, "image/png")}
    )
    assert no_auth.status_code == 401

    headers = await _auth(client, superuser)
    invalid = await client.post(
        "/admin/media/products",
        files={"file": ("not-image.png", b"not a PNG", "image/png")},
        headers=headers,
    )
    assert invalid.status_code == 400
