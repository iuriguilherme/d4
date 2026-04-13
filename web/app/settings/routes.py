import httpx
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, Response

from web.app import api_client
from web.app.api_client import APIError, _headers, _base_url
from web.app.auth.routes import login_required

settings_bp = Blueprint("settings", __name__, template_folder="templates")


@settings_bp.get("/settings")
@login_required
def settings_view():
    user = api_client.get_user_me()
    return render_template("settings/settings.html", user=user)


@settings_bp.post("/settings")
@login_required
def settings_save():
    timezone = request.form.get("timezone", "").strip()
    theme = request.form.get("theme", "light")
    data = {}
    if timezone:
        data["timezone"] = timezone
    data["preferences"] = {"theme": theme}
    try:
        user = api_client.update_user_me(data)
        # Update theme in session for immediate effect
        session["theme"] = theme
        flash("Settings saved.", "success")
    except APIError as e:
        flash(e.detail, "error")
    return redirect(url_for("settings.settings_view"))


@settings_bp.get("/settings/export")
@login_required
def export_data():
    with httpx.Client(base_url=_base_url()) as client:
        r = client.get("/api/v1/users/me/export", headers=_headers())
        r.raise_for_status()
    return Response(
        response=r.content,
        status=r.status_code,
        headers=dict(r.headers),
        content_type="application/json",
    )
