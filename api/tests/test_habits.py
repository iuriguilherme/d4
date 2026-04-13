import pytest
from httpx import AsyncClient


async def _auth_headers(client: AsyncClient, email: str) -> dict:
    await client.post("/api/v1/auth/register", json={"email": email, "password": "pass123"})
    r = await client.post("/api/v1/auth/token", json={"email": email, "password": "pass123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.mark.asyncio
async def test_create_habit(client: AsyncClient):
    headers = await _auth_headers(client, "h1@test.com")
    r = await client.post("/api/v1/habits", json={"name": "Morning run"}, headers=headers)
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Morning run"
    assert body["streak"] == 0


@pytest.mark.asyncio
async def test_checkin_creates_streak(client: AsyncClient):
    headers = await _auth_headers(client, "h2@test.com")
    cr = await client.post("/api/v1/habits", json={"name": "Meditate"}, headers=headers)
    habit_id = cr.json()["id"]

    r = await client.post(f"/api/v1/habits/{habit_id}/checkin", headers=headers)
    assert r.status_code == 200
    assert r.json()["streak"] == 1


@pytest.mark.asyncio
async def test_checkin_idempotent(client: AsyncClient):
    headers = await _auth_headers(client, "h3@test.com")
    cr = await client.post("/api/v1/habits", json={"name": "Read"}, headers=headers)
    habit_id = cr.json()["id"]

    r1 = await client.post(f"/api/v1/habits/{habit_id}/checkin", headers=headers)
    r2 = await client.post(f"/api/v1/habits/{habit_id}/checkin", headers=headers)

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["entry_id"] == r2.json()["entry_id"]
    assert r2.json()["streak"] == 1


@pytest.mark.asyncio
async def test_max_habits_limit(client: AsyncClient):
    headers = await _auth_headers(client, "h4@test.com")
    for i in range(5):
        r = await client.post("/api/v1/habits", json={"name": f"Habit {i}"}, headers=headers)
        assert r.status_code == 201

    r = await client.post("/api/v1/habits", json={"name": "6th habit"}, headers=headers)
    assert r.status_code == 400


@pytest.mark.asyncio
async def test_delete_habit(client: AsyncClient):
    headers = await _auth_headers(client, "h5@test.com")
    cr = await client.post("/api/v1/habits", json={"name": "Yoga"}, headers=headers)
    habit_id = cr.json()["id"]

    del_r = await client.delete(f"/api/v1/habits/{habit_id}", headers=headers)
    assert del_r.status_code == 204

    list_r = await client.get("/api/v1/habits", headers=headers)
    assert all(h["id"] != habit_id for h in list_r.json())


@pytest.mark.asyncio
async def test_habit_checkin_appears_in_daily_log(client: AsyncClient):
    from datetime import date
    headers = await _auth_headers(client, "h6@test.com")
    cr = await client.post("/api/v1/habits", json={"name": "Walk"}, headers=headers)
    habit_id = cr.json()["id"]
    await client.post(f"/api/v1/habits/{habit_id}/checkin", headers=headers)

    today = str(date.today())
    log_r = await client.get(f"/api/v1/entries?entry_date={today}", headers=headers)
    items = log_r.json()["items"]
    assert any(e["type"] == "habit_checkin" for e in items)
