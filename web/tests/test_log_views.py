from datetime import date
from unittest.mock import patch


def _logged_in_client(client):
    with client.session_transaction() as sess:
        sess["access_token"] = "fake-token"
        sess["session_id"] = "test-session"
    return client


MOCK_ENTRIES = {
    "items": [
        {"id": "abc-1", "type": "note", "content": "entry one", "entry_date": str(date.today()),
         "attributes": {}, "tags": [], "review_status": "pending", "created_at": "2026-04-07T10:00:00Z",
         "updated_at": "2026-04-07T10:00:00Z", "deleted_at": None, "user_id": "u1",
         "content_rich": None, "parent_id": None},
    ],
    "total": 1, "page": 1, "per_page": 50,
}


def test_log_today_redirect(client):
    _logged_in_client(client)
    with patch("web.app.log.routes.api_client.list_entries", return_value=MOCK_ENTRIES), \
         patch("web.app.api_client.get_current_user", return_value={"email": "a@t.com"}):
        r = client.get("/", follow_redirects=True)
        assert r.status_code == 200
        assert b"entry one" in r.data


def test_log_for_date(client):
    _logged_in_client(client)
    with patch("web.app.log.routes.api_client.list_entries", return_value=MOCK_ENTRIES), \
         patch("web.app.api_client.get_current_user", return_value={"email": "a@t.com"}):
        r = client.get("/2026-01-01")
        assert r.status_code == 200


def test_log_empty_state(client):
    _logged_in_client(client)
    empty = {"items": [], "total": 0, "page": 1, "per_page": 50}
    with patch("web.app.log.routes.api_client.list_entries", return_value=empty), \
         patch("web.app.api_client.get_current_user", return_value={"email": "a@t.com"}):
        r = client.get(f"/{date.today()}")
        assert r.status_code == 200
        assert b"Nothing here yet" in r.data


def test_capture_entry(client):
    _logged_in_client(client)
    new_entry = {
        "id": "new-id", "type": "note", "content": "captured", "entry_date": str(date.today()),
        "attributes": {}, "tags": [], "review_status": "pending", "created_at": "2026-04-07T10:00:00Z",
        "updated_at": "2026-04-07T10:00:00Z", "deleted_at": None, "user_id": "u1",
        "content_rich": None, "parent_id": None,
    }
    with patch("web.app.log.routes.api_client.create_entry", return_value=new_entry), \
         patch("web.app.api_client.get_current_user", return_value={"email": "a@t.com"}):
        r = client.post("/entries", data={"content": "captured", "type": "note", "log_date": str(date.today())})
        assert r.status_code == 200
        assert b"captured" in r.data


def test_task_complete(client):
    _logged_in_client(client)
    updated_entry = {
        "id": "task-1", "type": "task", "content": "do thing", "entry_date": str(date.today()),
        "attributes": {"completed": True}, "tags": [], "review_status": None,
        "created_at": "2026-04-07T10:00:00Z", "updated_at": "2026-04-07T10:00:00Z",
        "deleted_at": None, "user_id": "u1", "content_rich": None, "parent_id": None,
    }
    with patch("web.app.log.routes.api_client.update_entry", return_value=updated_entry), \
         patch("web.app.api_client.get_current_user", return_value={"email": "a@t.com"}):
        r = client.patch("/entries/task-1",
                         data='{"attributes": {"completed": true}}',
                         content_type="application/json")
        assert r.status_code == 200
        assert b"completed" in r.data
