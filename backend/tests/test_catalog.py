"""Интеграционные тесты каталога."""

from httpx import AsyncClient


async def test_get_categories_returns_tree(
    client: AsyncClient, seed_categories: dict[str, int]
) -> None:
    resp = await client.get("/catalog/categories")

    assert resp.status_code == 200
    tree = resp.json()

    # На верхнем уровне — только корневая категория.
    roots = [c for c in tree if c["id"] == seed_categories["root"]]
    assert len(roots) == 1
    root = roots[0]
    assert root["parent_id"] is None
    assert root["slug"] == "test-living"

    # Дочерняя категория вложена в корневую, а не лежит в корне списка.
    assert all(c["id"] != seed_categories["child"] for c in tree)
    child_ids = [c["id"] for c in root["children"]]
    assert seed_categories["child"] in child_ids


async def test_get_missing_category_returns_404(client: AsyncClient) -> None:
    resp = await client.get("/catalog/categories/999999")
    assert resp.status_code == 404