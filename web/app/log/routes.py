from datetime import date, timedelta

from flask import Blueprint, render_template, request, redirect, url_for, session

from web.app import api_client
from web.app.api_client import APIError
from web.app.auth.routes import login_required

log_bp = Blueprint("log", __name__, template_folder="templates")


@log_bp.get("/")
@login_required
def daily_log():
    today = str(date.today())
    return redirect(url_for("log.log_for_date", log_date=today))


@log_bp.get("/<log_date>")
@login_required
def log_for_date(log_date: str):
    try:
        log_dt = date.fromisoformat(log_date)
    except ValueError:
        return redirect(url_for("log.daily_log"))

    entries_data = api_client.list_entries(entry_date=log_date)
    entries = entries_data.get("items", []) if entries_data else []

    prev_date = str(log_dt - timedelta(days=1))
    next_date = str(log_dt + timedelta(days=1))
    today = str(date.today())

    return render_template(
        "log/log.html",
        entries=entries,
        log_date=log_date,
        prev_date=prev_date,
        next_date=next_date,
        is_today=(log_date == today),
    )


@log_bp.post("/entries")
@login_required
def capture_entry():
    content = request.form.get("content", "").strip()
    entry_type = request.form.get("type", "note")
    log_date = request.form.get("log_date") or str(date.today())

    if not content:
        return "", 400

    try:
        entry = api_client.create_entry({
            "content": content,
            "type": entry_type,
            "entry_date": log_date,
        })
    except APIError as e:
        return str(e.detail), e.status_code

    # HTMX expects an HTML fragment
    return render_template("log/_entry.html", entry=entry)


@log_bp.patch("/entries/<entry_id>")
@login_required
def update_entry(entry_id: str):
    data = request.get_json(force=True) or {}
    try:
        entry = api_client.update_entry(entry_id, data)
    except APIError as e:
        return str(e.detail), e.status_code
    return render_template("log/_entry.html", entry=entry)
