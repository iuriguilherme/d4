import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    r = await client.post("/api/v1/auth/register", json={"email": "a@test.com", "password": "pass123"})
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "a@test.com"
    assert "id" in body
    assert "password_hash" not in body


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={"email": "dup@test.com", "password": "pass123"})
    r = await client.post("/api/v1/auth/register", json={"email": "dup@test.com", "password": "pass123"})
    assert r.status_code == 409


@pytest.mark.asyncio
async def test_register_malformed_email(client: AsyncClient):
    r = await client.post("/api/v1/auth/register", json={"email": "not-an-email", "password": "pass123"})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={"email": "login@test.com", "password": "secret"})
    r = await client.post("/api/v1/auth/token", json={"email": "login@test.com", "password": "secret"})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={"email": "badpass@test.com", "password": "correct"})
    r = await client.post("/api/v1/auth/token", json={"email": "badpass@test.com", "password": "wrong"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_protected_without_token(client: AsyncClient):
    r = await client.get("/api/v1/auth/me")
    assert r.status_code == 403  # HTTPBearer returns 403 when no credentials


@pytest.mark.asyncio
async def test_protected_with_invalid_token(client: AsyncClient):
    r = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_protected_with_valid_token(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={"email": "valid@test.com", "password": "pass"})
    login = await client.post("/api/v1/auth/token", json={"email": "valid@test.com", "password": "pass"})
    token = login.json()["access_token"]

    r = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["email"] == "valid@test.com"
