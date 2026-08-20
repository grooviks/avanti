"""Интеграционные тесты admin CRUD категорий и защиты доступа."""

from httpx import AsyncClient


async def _auth(client: AsyncClient, superuser: dict[str, str]) -> dict[str, str]:
    resp = await client.post(
        "/auth/login",
        data={"username": superuser["email"], "password": superuser["password"]},
    )
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


async def test_create_requires_auth(client: AsyncClient, seed_categories: dict[str, int]) -> None:
    resp = await client.post("/admin/categories", json={"name": "X", "slug": "x-cat"})
    assert resp.status_code == 401


async def test_create_category(
    client: AsyncClient, superuser: dict[str, str], seed_categories: dict[str, int]
) -> None:
    headers = await _auth(client, superuser)
    resp = await client.post(
        "/admin/categories",
        json={"name": "Кухни", "slug": "kitchens", "position": 3},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["slug"] == "kitchens"

    # появилась в дереве
    tree = (await client.get("/catalog/categories")).json()
    assert any(c["slug"] == "kitchens" for c in tree)


async def test_create_duplicate_slug(
    client: AsyncClient, superuser: dict[str, str], seed_categories: dict[str, int]
) -> None:
    headers = await _auth(client, superuser)
    # slug "test-living" уже занят seed-категорией
    resp = await client.post(
        "/admin/categories", json={"name": "Dup", "slug": "test-living"}, headers=headers
    )
    assert resp.status_code == 409


async def test_create_invalid_slug(
    client: AsyncClient, superuser: dict[str, str], seed_categories: dict[str, int]
) -> None:
    headers = await _auth(client, superuser)
    resp = await client.post(
        "/admin/categories", json={"name": "Bad", "slug": "Плохой Слаг"}, headers=headers
    )
    assert resp.status_code == 422


async def test_create_nonexistent_parent(
    client: AsyncClient, superuser: dict[str, str], seed_categories: dict[str, int]
) -> None:
    headers = await _auth(client, superuser)
    resp = await client.post(
        "/admin/categories",
        json={"name": "Orphan", "slug": "orphan", "parent_id": 999999},
        headers=headers,
    )
    assert resp.status_code == 400


async def test_update_name_and_cycle(
    client: AsyncClient, superuser: dict[str, str], seed_categories: dict[str, int]
) -> None:
    headers = await _auth(client, superuser)
    root_id = seed_categories["root"]
    child_id = seed_categories["child"]

    # обычное обновление
    resp = await client.patch(
        f"/admin/categories/{root_id}", json={"name": "Обновлённая"}, headers=headers
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Обновлённая"

    # попытка сделать родителем собственного потомка → цикл
    resp = await client.patch(
        f"/admin/categories/{root_id}", json={"parent_id": child_id}, headers=headers
    )
    assert resp.status_code == 400


async def test_delete_conflict_then_ok(
    client: AsyncClient, superuser: dict[str, str], seed_categories: dict[str, int]
) -> None:
    headers = await _auth(client, superuser)
    root_id = seed_categories["root"]
    child_id = seed_categories["child"]

    # у root есть child → удаление запрещено
    resp = await client.delete(f"/admin/categories/{root_id}", headers=headers)
    assert resp.status_code == 409

    # пустого потомка удалить можно
    resp = await client.delete(f"/admin/categories/{child_id}", headers=headers)
    assert resp.status_code == 204

    # теперь root пуст → удаляется
    resp = await client.delete(f"/admin/categories/{root_id}", headers=headers)
    assert resp.status_code == 204