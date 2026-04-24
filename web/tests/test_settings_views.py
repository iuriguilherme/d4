from unittest.mock import patch
from web.app.api_client import APIError

def _logged_in(client):
    with client.session_transaction() as sess:
        sess["access_token"] = "fake-token"
    return client

def test_settings_view(client):
    _logged_in(client)
    mock_user = {"email": "test@example.com", "timezone": "UTC", "preferences": {"theme": "light"}}
    with patch("web.app.settings.routes.api_client.get_user_me", return_value=mock_user), \
         patch("web.app.api_client.get_current_user", return_value=mock_user):
        r = client.get("/settings")
        assert r.status_code == 200
        assert b"Settings" in r.data
        assert b"test@example.com" in r.data

def test_settings_save_success(client):
    _logged_in(client)
    mock_user = {"email": "test@example.com", "timezone": "UTC", "preferences": {"theme": "dark"}}
    with patch("web.app.settings.routes.api_client.update_user_me", return_value=mock_user), \
         patch("web.app.api_client.get_current_user", return_value=mock_user):
        r = client.post("/settings", data={"timezone": "UTC", "theme": "dark"}, follow_redirects=True)
        assert r.status_code == 200
        assert b"Settings saved." in r.data
        with client.session_transaction() as sess:
            assert sess["theme"] == "dark"

def test_settings_save_error(client):
    _logged_in(client)
    with patch("web.app.settings.routes.api_client.update_user_me", side_effect=APIError(400, "Invalid timezone")), \
         patch("web.app.api_client.get_current_user", return_value={"email": "test@example.com"}):
        r = client.post("/settings", data={"timezone": "Invalid", "theme": "light"}, follow_redirects=True)
        assert r.status_code == 200
        assert b"Invalid timezone" in r.data

def test_export_data(client):
    _logged_in(client)
    mock_content = b'{"data": "exported"}'
    with patch("web.app.settings.routes.api_client.export_data", return_value=mock_content), \
         patch("web.app.api_client.get_current_user", return_value={"email": "test@example.com"}):
        r = client.get("/settings/export")
        assert r.status_code == 200
        assert r.data == mock_content
        assert r.headers["Content-Disposition"] == "attachment; filename=hyppo-export.json"
        assert r.headers["Content-Type"] == "application/json"
