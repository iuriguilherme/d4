from unittest.mock import patch


def _logged_in(client):
    with client.session_transaction() as sess:
        sess["access_token"] = "fake-token"
    return client


EMPTY_ENTRIES = {"items": [], "total": 0, "page": 1, "per_page": 50}

EXISTING_JOURNAL = {
    "items": [{
        "id": "j-1", "type": "note", "content": "my day",
        "attributes": {"entry_subtype": "journal", "mood": 4, "prompt_response": "great"},
        "entry_date": "2026-04-07", "tags": [], "review_status": "reviewed",
        "created_at": "2026-04-07T10:00:00Z", "updated_at": "2026-04-07T10:00:00Z",
        "deleted_at": None, "user_id": "u1", "content_rich": None, "parent_id": None,
    }],
    "total": 1, "page": 1, "per_page": 50,
}


def test_journal_blank(client):
    _logged_in(client)
    with patch("web.app.journal.routes.api_client.list_entries", return_value=EMPTY_ENTRIES), \
         patch("web.app.api_client.get_current_user", return_value={"email": "a@t.com"}):
        r = client.get("/journal/2026-04-07")
        assert r.status_code == 200
        assert b"Journal" in r.data


def test_journal_existing(client):
    _logged_in(client)
    with patch("web.app.journal.routes.api_client.list_entries", return_value=EXISTING_JOURNAL), \
         patch("web.app.api_client.get_current_user", return_value={"email": "a@t.com"}):
        r = client.get("/journal/2026-04-07")
        assert r.status_code == 200
        assert b"my day" in r.data


def test_journal_autosave_creates(client):
    _logged_in(client)
    new_entry = {
        "id": "j-new", "type": "note", "content": "fresh",
        "attributes": {"entry_subtype": "journal", "mood": 3, "prompt_response": ""},
        "entry_date": "2026-04-07", "tags": [], "review_status": "reviewed",
        "created_at": "2026-04-07T10:00:00Z", "updated_at": "2026-04-07T10:00:00Z",
        "deleted_at": None, "user_id": "u1", "content_rich": None, "parent_id": None,
    }
    with patch("web.app.journal.routes.api_client.list_entries", return_value=EMPTY_ENTRIES), \
         patch("web.app.journal.routes.api_client.create_entry", return_value=new_entry), \
         patch("web.app.api_client.get_current_user", return_value={"email": "a@t.com"}):
        r = client.post("/journal/2026-04-07", data={"content": "fresh", "mood": "3"})
        assert r.status_code == 200
        assert b"Saved" in r.data


def test_journal_autosave_updates(client):
    _logged_in(client)
    updated_entry = EXISTING_JOURNAL["items"][0].copy()
    updated_entry["content"] = "updated"
    with patch("web.app.journal.routes.api_client.update_entry", return_value=updated_entry), \
         patch("web.app.api_client.get_current_user", return_value={"email": "a@t.com"}):
        r = client.post("/journal/2026-04-07",
                        data={"content": "updated", "entry_id": "j-1", "mood": "4"})
        assert r.status_code == 200
        assert b"Saved" in r.data


def test_journal_upsert_no_duplicate(client):
    """Second save with entry_id updates, does not create new entry."""
    _logged_in(client)
    updated = EXISTING_JOURNAL["items"][0].copy()
    with patch("web.app.journal.routes.api_client.update_entry", return_value=updated) as mock_update, \
         patch("web.app.journal.routes.api_client.create_entry") as mock_create, \
         patch("web.app.api_client.get_current_user", return_value={"email": "a@t.com"}):
        client.post("/journal/2026-04-07", data={"content": "x", "entry_id": "j-1"})
        mock_update.assert_called_once()
        mock_create.assert_not_called()
