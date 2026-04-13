from datetime import date

import markdown as md
from flask import Blueprint, render_template, request, session

from web.app import api_client
from web.app.api_client import APIError
from web.app.auth.routes import login_required

journal_bp = Blueprint("journal", __name__, template_folder="templates")

JOURNAL_SUBTYPE = "journal"
JOURNAL_PROMPT = "What's one thing you want to remember about today?"


def _find_journal_entry(entries_data: dict) -> dict | None:
    for e in entries_data.get("items", []):
        attrs = e.get("attributes", {})
        if attrs.get("entry_subtype") == JOURNAL_SUBTYPE:
            return e
    return None


@journal_bp.get("/journal/<journal_date>")
@login_required
def journal_view(journal_date: str):
    try:
        date.fromisoformat(journal_date)
    except ValueError:
        journal_date = str(date.today())

    entries_data = api_client.list_entries(entry_date=journal_date, entry_type="note")
    existing = _find_journal_entry(entries_data or {})

    content = ""
    mood = None
    prompt_response = ""
    if existing:
        attrs = existing.get("attributes", {})
        content = existing.get("content", "")
        mood = attrs.get("mood")
        prompt_response = attrs.get("prompt_response", "")

    return render_template(
        "journal/journal.html",
        journal_date=journal_date,
        content=content,
        mood=mood,
        prompt_response=prompt_response,
        entry_id=existing["id"] if existing else None,
        prompt_text=JOURNAL_PROMPT,
    )


@journal_bp.post("/journal/<journal_date>")
@login_required
def journal_save(journal_date: str):
    """Auto-save endpoint — returns a small 'Saved' indicator partial."""
    content = request.form.get("content", "")
    mood_raw = request.form.get("mood")
    prompt_response = request.form.get("prompt_response", "")
    entry_id = request.form.get("entry_id")

    mood = int(mood_raw) if mood_raw and mood_raw.isdigit() else None
    attributes = {
        "entry_subtype": JOURNAL_SUBTYPE,
        "mood": mood,
        "prompt_response": prompt_response,
    }

    try:
        if entry_id:
            entry = api_client.update_entry(entry_id, {"content": content, "attributes": attributes})
        else:
            # Check again for existing to handle race
            entries_data = api_client.list_entries(entry_date=journal_date, entry_type="note")
            existing = _find_journal_entry(entries_data or {})
            if existing:
                entry = api_client.update_entry(existing["id"], {"content": content, "attributes": attributes})
            else:
                entry = api_client.create_entry({
                    "type": "note",
                    "content": content,
                    "entry_date": journal_date,
                    "attributes": attributes,
                    "review_status": "reviewed",
                })
    except APIError as e:
        return f'<span class="save-indicator error">Error saving</span>', e.status_code

    rendered_html = md.markdown(entry.get("content", ""), extensions=["extra"])
    return render_template(
        "journal/_journal_preview.html",
        entry=entry,
        rendered_html=rendered_html,
    )
