import json
from datetime import date

import pytest
from httpx import AsyncClient


async def _auth_headers(client: AsyncClient, email: str) -> dict:
    await client.post("/api/v1/auth/register", json={"email": email, "password": "pass123"})
    r = await client.post("/api/v1/auth/token", json={"email": email, "password": "pass123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.mark.asyncio
async def test_patch_timezone(client: AsyncClient):
    headers = await _auth_headers(client, "u1@test.com")
    r = await client.patch("/api/v1/users/me", json={"timezone": "America/Sao_Paulo"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["timezone"] == "America/Sao_Paulo"


@pytest.mark.asyncio
async def test_patch_invalid_timezone(client: AsyncClient):
    headers = await _auth_headers(client, "u2@test.com")
    r = await client.patch("/api/v1/users/me", json={"timezone": "Not/Real"}, headers=headers)
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_patch_theme(client: AsyncClient):
    headers = await _auth_headers(client, "u3@test.com")
    r = await client.patch("/api/v1/users/me", json={"preferences": {"theme": "dark"}}, headers=headers)
    assert r.status_code == 200
    assert r.json()["preferences"]["theme"] == "dark"


@pytest.mark.asyncio
async def test_export_empty(client: AsyncClient):
    headers = await _auth_headers(client, "u4@test.com")
    r = await client.get("/api/v1/users/me/export", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["entries"] == []
    assert data["habits"] == []
    assert data["tags"] == []
    assert "user" in data
    assert "exported_at" in data


@pytest.mark.asyncio
async def test_export_with_data(client: AsyncClient):
    headers = await _auth_headers(client, "u5@test.com")
    today = str(date.today())
    await client.post("/api/v1/entries", json={"content": "entry 1", "entry_date": today}, headers=headers)
    await client.post("/api/v1/entries", json={"content": "entry 2", "entry_date": today}, headers=headers)
    await client.post("/api/v1/habits", json={"name": "Run"}, headers=headers)

    r = await client.get("/api/v1/users/me/export", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data["entries"]) == 2
    assert len(data["habits"]) == 1

    # JSON must be valid and parseable
    reparsed = json.loads(r.text)
    assert reparsed["entries"][0]["content"] in ("entry 1", "entry 2")
