from unittest.mock import patch

MOCK_HABITS = [
    {"id": "h-1", "name": "Run", "streak": 3, "color": "#6366f1",
     "description": "", "frequency": "daily", "target_value": 1,
     "unit": "", "icon": "", "created_at": "2026-04-07T00:00:00Z", "archived_at": None},
]


def _logged_in(client):
    with client.session_transaction() as sess:
        sess["access_token"] = "fake-token"
    return client


def test_habit_board(client):
    _logged_in(client)
    with patch("web.app.habits.routes.api_client.list_habits", return_value=MOCK_HABITS), \
         patch("web.app.api_client.get_current_user", return_value={"email": "a@t.com"}):
        r = client.get("/habits")
        assert r.status_code == 200
        assert b"Run" in r.data


def test_create_habit(client):
    _logged_in(client)
    new_habit = {"id": "h-new", "name": "Meditate", "streak": 0, "color": "#6366f1",
                 "description": "", "frequency": "daily", "target_value": 1,
                 "unit": "", "icon": "", "created_at": "2026-04-07T00:00:00Z", "archived_at": None}
    with patch("web.app.habits.routes.api_client.create_habit", return_value=new_habit), \
         patch("web.app.habits.routes.api_client.list_habits", return_value=[new_habit]), \
         patch("web.app.api_client.get_current_user", return_value={"email": "a@t.com"}):
        r = client.post("/habits", data={"name": "Meditate"}, follow_redirects=True)
        assert r.status_code == 200


def test_checkin_htmx(client):
    _logged_in(client)
    checkin_result = {"entry_id": "e-1", "habit_id": "h-1", "streak": 4, "entry_date": "2026-04-07"}
    habit_with_streak = {**MOCK_HABITS[0], "streak": 4}
    with patch("web.app.habits.routes.api_client.checkin_habit", return_value=checkin_result), \
         patch("web.app.habits.routes.api_client.list_habits", return_value=[habit_with_streak]), \
         patch("web.app.api_client.get_current_user", return_value={"email": "a@t.com"}):
        r = client.post("/habits/h-1/checkin")
        assert r.status_code == 200
        assert b"4" in r.data  # streak count
