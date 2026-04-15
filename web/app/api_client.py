"""
Single httpx boundary for all FastAPI communication.
This is the only file in web/ that imports httpx.
"""
from typing import Any

import httpx
from flask import current_app, session, flash


def _base_url() -> str:
    return current_app.config["FASTAPI_BASE_URL"]


def _headers() -> dict:
    headers = {}
    token = session.get("access_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    session_id = session.get("session_id")
    if session_id:
        headers["X-Session-ID"] = str(session_id)
    return headers


def _handle_response(response: httpx.Response) -> dict | None:
    if response.status_code == 401:
        session.clear()
        flash("Session expired. Please log in again.", "error")
        raise APIError(401, "session_expired")
    response.raise_for_status()
    if response.status_code == 204:
        return None
    return response.json()


class APIError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


# Auth

def login(email: str, password: str) -> dict:
    with httpx.Client(base_url=_base_url()) as client:
        r = client.post("/api/v1/auth/token", json={"email": email, "password": password})
        if r.status_code == 401:
            raise APIError(401, "Invalid credentials")
        r.raise_for_status()
        return r.json()


def register(email: str, password: str) -> dict:
    with httpx.Client(base_url=_base_url()) as client:
        r = client.post("/api/v1/auth/register", json={"email": email, "password": password})
        if r.status_code == 409:
            raise APIError(409, "Email already registered")
        r.raise_for_status()
        return r.json()


def logout() -> None:
    with httpx.Client(base_url=_base_url()) as client:
        client.delete("/api/v1/auth/token", headers=_headers())
    session.clear()


def get_current_user() -> dict | None:
    token = session.get("access_token")
    if not token:
        return None
    with httpx.Client(base_url=_base_url()) as client:
        r = client.get("/api/v1/auth/me", headers=_headers())
        if r.status_code in (401, 403):
            return None
        r.raise_for_status()
        return r.json()


# Entries

def list_entries(entry_date: str | None = None, entry_type: str | None = None, page: int = 1) -> dict:
    params: dict[str, Any] = {"page": page}
    if entry_date:
        params["entry_date"] = entry_date
    if entry_type:
        params["type"] = entry_type
    with httpx.Client(base_url=_base_url()) as client:
        r = client.get("/api/v1/entries", params=params, headers=_headers())
        return _handle_response(r)


def create_entry(data: dict) -> dict:
    with httpx.Client(base_url=_base_url()) as client:
        r = client.post("/api/v1/entries", json=data, headers=_headers())
        return _handle_response(r)


def update_entry(entry_id: str, data: dict) -> dict:
    with httpx.Client(base_url=_base_url()) as client:
        r = client.patch(f"/api/v1/entries/{entry_id}", json=data, headers=_headers())
        return _handle_response(r)


def delete_entry(entry_id: str) -> None:
    with httpx.Client(base_url=_base_url()) as client:
        r = client.delete(f"/api/v1/entries/{entry_id}", headers=_headers())
        _handle_response(r)


# Habits (stubs — implemented fully in Unit 7)

def list_habits() -> list:
    with httpx.Client(base_url=_base_url()) as client:
        r = client.get("/api/v1/habits", headers=_headers())
        return _handle_response(r)


def create_habit(data: dict) -> dict:
    with httpx.Client(base_url=_base_url()) as client:
        r = client.post("/api/v1/habits", json=data, headers=_headers())
        return _handle_response(r)


def checkin_habit(habit_id: str) -> dict:
    with httpx.Client(base_url=_base_url()) as client:
        r = client.post(f"/api/v1/habits/{habit_id}/checkin", headers=_headers())
        return _handle_response(r)


def delete_habit(habit_id: str) -> None:
    with httpx.Client(base_url=_base_url()) as client:
        r = client.delete(f"/api/v1/habits/{habit_id}", headers=_headers())
        _handle_response(r)


# Users

def get_user_me() -> dict:
    with httpx.Client(base_url=_base_url()) as client:
        r = client.get("/api/v1/users/me", headers=_headers())
        return _handle_response(r)


def update_user_me(data: dict) -> dict:
    with httpx.Client(base_url=_base_url()) as client:
        r = client.patch("/api/v1/users/me", json=data, headers=_headers())
        return _handle_response(r)


def export_data() -> bytes:
    with httpx.Client(base_url=_base_url(), timeout=30.0) as client:
        r = client.get("/api/v1/users/me/export", headers=_headers())
        r.raise_for_status()
        return r.content
