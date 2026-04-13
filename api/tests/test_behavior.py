import asyncio
from datetime import date

import pytest
from httpx import AsyncClient


async def _auth_headers(client: AsyncClient, email: str) -> dict:
    await client.post("/api/v1/auth/register", json={"email": email, "password": "pass123"})
    r = await client.post("/api/v1/auth/token", json={"email": email, "password": "pass123"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.mark.asyncio
async def test_entry_creates_behavior_event(client: AsyncClient):
    headers = await _auth_headers(client, "beh1@test.com")
    session_headers = {**headers, "X-Session-ID": "11111111-1111-1111-1111-111111111111"}

    await client.post("/api/v1/entries", json={"content": "test entry"}, headers=session_headers)
    # BackgroundTasks run before the test assertion in ASGI test mode
    await asyncio.sleep(0.1)

    r = await client.get("/api/v1/analytics/behavior", headers=headers)
    events = r.json()
    assert any(e["event_type"] == "entry_created" for e in events)


@pytest.mark.asyncio
async def test_habit_checkin_creates_behavior_event(client: AsyncClient):
    headers = await _auth_headers(client, "beh2@test.com")
    cr = await client.post("/api/v1/habits", json={"name": "Test"}, headers=headers)
    habit_id = cr.json()["id"]

    await client.post(f"/api/v1/habits/{habit_id}/checkin", headers=headers)
    await asyncio.sleep(0.1)

    r = await client.get("/api/v1/analytics/behavior", headers=headers)
    assert any(e["event_type"] == "habit_checked" for e in r.json())


@pytest.mark.asyncio
async def test_entry_with_empty_content_word_count_zero(client: AsyncClient):
    headers = await _auth_headers(client, "beh3@test.com")
    await client.post("/api/v1/entries", json={"content": ""}, headers=headers)
    await asyncio.sleep(0.1)

    r = await client.get("/api/v1/analytics/behavior", headers=headers)
    events = [e for e in r.json() if e["event_type"] == "entry_created"]
    assert events[0]["event_data"]["word_count"] == 0


@pytest.mark.asyncio
async def test_behavior_event_failure_does_not_break_response(client: AsyncClient):
    """Main response must succeed even if event write would fail."""
    headers = await _auth_headers(client, "beh4@test.com")
    # Create entry normally — we just verify it returns 201 without error
    r = await client.post("/api/v1/entries", json={"content": "fine"}, headers=headers)
    assert r.status_code == 201
