import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_cors_preflight_allowed(client: AsyncClient):
    # Test preflight request for a valid origin and method
    headers = {
        "Origin": "http://localhost:5000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Authorization,X-Session-ID",
    }
    r = await client.options("/api/v1/auth/register", headers=headers)
    assert r.status_code == 200
    assert r.headers["access-control-allow-origin"] == "http://localhost:5000"

    # Check allowed methods and headers
    allowed_methods = r.headers["access-control-allow-methods"].split(", ")
    assert set(allowed_methods) == {"GET", "POST", "PATCH", "DELETE"}

    allowed_headers = r.headers["access-control-allow-headers"].split(", ")
    assert "Authorization" in allowed_headers
    assert "X-Session-ID" in allowed_headers
    assert "Content-Type" in allowed_headers

@pytest.mark.asyncio
async def test_cors_preflight_forbidden_method(client: AsyncClient):
    headers = {
        "Origin": "http://localhost:5000",
        "Access-Control-Request-Method": "PUT",
    }
    r = await client.options("/api/v1/auth/register", headers=headers)
    # If method is not allowed, CORSMiddleware doesn't return CORS headers
    assert "access-control-allow-methods" not in r.headers

@pytest.mark.asyncio
async def test_cors_preflight_forbidden_header(client: AsyncClient):
    headers = {
        "Origin": "http://localhost:5000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "X-Malicious-Header",
    }
    r = await client.options("/api/v1/auth/register", headers=headers)
    assert "access-control-allow-headers" not in r.headers

@pytest.mark.asyncio
async def test_cors_preflight_unauthorized_origin(client: AsyncClient):
    headers = {
        "Origin": "http://malicious.com",
        "Access-Control-Request-Method": "GET",
    }
    r = await client.options("/api/v1/auth/me", headers=headers)
    assert "access-control-allow-origin" not in r.headers
