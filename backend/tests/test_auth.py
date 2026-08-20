"""Интеграционные тесты auth и защиты admin."""

from httpx import AsyncClient


async def _login(client: AsyncClient, email: str, password: str) -> str:
    resp = await client.post("/auth/login", data={"username": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


async def test_login_success_and_me(
    client: AsyncClient, superuser: dict[str, str]
) -> None:
    token = await _login(client, superuser["email"], superuser["password"])

    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["email"] == superuser["email"]
    assert body["is_superuser"] is True


async def test_login_wrong_password(client: AsyncClient, superuser: dict[str, str]) -> None:
    resp = await client.post(
        "/auth/login",
        data={"username": superuser["email"], "password": "definitely-wrong"},
    )
    assert resp.status_code == 401


async def test_me_requires_auth(client: AsyncClient) -> None:
    assert (await client.get("/auth/me")).status_code == 401
    resp = await client.get("/auth/me", headers={"Authorization": "Bearer garbage"})
    assert resp.status_code == 401


async def test_admin_requires_token(client: AsyncClient, superuser: dict[str, str]) -> None:
    # без токена — закрыто
    assert (await client.get("/admin/ping")).status_code == 401

    # с токеном суперпользователя — открыто
    token = await _login(client, superuser["email"], superuser["password"])
    resp = await client.get("/admin/ping", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == {"status": "pong"}