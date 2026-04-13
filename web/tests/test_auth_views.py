import pytest
from unittest.mock import patch

from web.app.api_client import APIError


def test_get_login(client):
    r = client.get("/login")
    assert r.status_code == 200
    assert b"Login" in r.data


def test_login_success(client):
    with patch("web.app.auth.routes.api_client.login") as mock_login, \
         patch("web.app.auth.routes.api_client.get_current_user", return_value=None):
        mock_login.return_value = {"access_token": "fake-token"}
        r = client.post("/login", data={"email": "a@test.com", "password": "pass"}, follow_redirects=False)
        assert r.status_code == 302


def test_login_wrong_credentials(client):
    with patch("web.app.auth.routes.api_client.login") as mock_login, \
         patch("web.app.auth.routes.api_client.get_current_user", return_value=None):
        mock_login.side_effect = APIError(401, "Invalid credentials")
        r = client.post("/login", data={"email": "bad@test.com", "password": "wrong"})
        assert r.status_code == 400
        assert b"Invalid" in r.data


def test_logout(client):
    with client.session_transaction() as sess:
        sess["access_token"] = "fake-token"
    with patch("web.app.auth.routes.api_client.logout"), \
         patch("web.app.auth.routes.api_client.get_current_user", return_value=None):
        r = client.get("/logout", follow_redirects=False)
        assert r.status_code == 302
        assert "/login" in r.headers["Location"]


def test_protected_without_session(client):
    with patch("web.app.api_client.get_current_user", return_value=None):
        r = client.get("/", follow_redirects=False)
        # / is not yet defined — will be a 404 or redirect when log bp added
        # For now just verify no crash
        assert r.status_code in (302, 404)


def test_register_page(client):
    r = client.get("/register")
    assert r.status_code == 200
    assert b"Create Account" in r.data
