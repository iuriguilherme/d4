import uuid
from datetime import date

import pytest
from httpx import AsyncClient


async def _auth_headers(client: AsyncClient, email: str, password: str = "pass123") -> dict:
    await client.post("/api/v1/auth/register", json={"email": email, "password": password})
    r = await client.post("/api/v1/auth/token", json={"email": email, "password": password})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_entry_no_id(client: AsyncClient):
    headers = await _auth_headers(client, "e1@test.com")
    r = await client.post("/api/v1/entries", json={"type": "note", "content": "hello"}, headers=headers)
    assert r.status_code == 201
    body = r.json()
    assert "id" in body
    assert body["type"] == "note"
    assert body["review_status"] == "pending"


@pytest.mark.asyncio
async def test_create_entry_client_id(client: AsyncClient):
    headers = await _auth_headers(client, "e2@test.com")
    client_id = str(uuid.uuid4())
    r = await client.post("/api/v1/entries", json={"id": client_id, "content": "hi"}, headers=headers)
    assert r.status_code == 201
    assert r.json()["id"] == client_id


@pytest.mark.asyncio
async def test_create_entry_duplicate_id(client: AsyncClient):
    headers = await _auth_headers(client, "e3@test.com")
    client_id = str(uuid.uuid4())
    await client.post("/api/v1/entries", json={"id": client_id, "content": "first"}, headers=headers)
    r = await client.post("/api/v1/entries", json={"id": client_id, "content": "second"}, headers=headers)
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_list_entries_by_date(client: AsyncClient):
    headers = await _auth_headers(client, "e4@test.com")
    today = str(date.today())
    await client.post("/api/v1/entries", json={"content": "today entry", "entry_date": today}, headers=headers)
    r = await client.get(f"/api/v1/entries?entry_date={today}", headers=headers)
    assert r.status_code == 200
    items = r.json()["items"]
    assert any(e["content"] == "today entry" for e in items)


@pytest.mark.asyncio
async def test_patch_entry_type_updates_review_status(client: AsyncClient):
    headers = await _auth_headers(client, "e5@test.com")
    create = await client.post("/api/v1/entries", json={"type": "note", "content": "to be a task"}, headers=headers)
    entry_id = create.json()["id"]
    r = await client.patch(f"/api/v1/entries/{entry_id}", json={"type": "task"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["type"] == "task"
    assert r.json()["review_status"] == "reviewed"


@pytest.mark.asyncio
async def test_soft_delete_entry(client: AsyncClient):
    headers = await _auth_headers(client, "e6@test.com")
    create = await client.post("/api/v1/entries", json={"content": "delete me"}, headers=headers)
    entry_id = create.json()["id"]

    del_r = await client.delete(f"/api/v1/entries/{entry_id}", headers=headers)
    assert del_r.status_code == 204

    today = str(date.today())
    list_r = await client.get(f"/api/v1/entries?entry_date={today}", headers=headers)
    ids = [e["id"] for e in list_r.json()["items"]]
    assert entry_id not in ids


@pytest.mark.asyncio
async def test_list_entries_default_today(client: AsyncClient):
    headers = await _auth_headers(client, "e7@test.com")
    r = await client.get("/api/v1/entries", headers=headers)
    assert r.status_code == 200
    assert "items" in r.json()


@pytest.mark.asyncio
async def test_entry_integration(client: AsyncClient):
    """Create → list → delete → no longer in list."""
    headers = await _auth_headers(client, "e8@test.com")
    today = str(date.today())

    create = await client.post("/api/v1/entries", json={"content": "integration", "entry_date": today}, headers=headers)
    entry_id = create.json()["id"]

    list_r = await client.get(f"/api/v1/entries?entry_date={today}", headers=headers)
    assert any(e["id"] == entry_id for e in list_r.json()["items"])

    await client.delete(f"/api/v1/entries/{entry_id}", headers=headers)

    list_r2 = await client.get(f"/api/v1/entries?entry_date={today}", headers=headers)
    assert all(e["id"] != entry_id for e in list_r2.json()["items"])
