import uuid
from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g

from web.app import api_client
from web.app.api_client import APIError

auth_bp = Blueprint("auth", __name__, template_folder="templates")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("access_token"):
            flash("Please log in to continue.", "error")
            return redirect(url_for("auth.login_view"))
        return f(*args, **kwargs)
    return decorated


@auth_bp.get("/login")
def login_view():
    if session.get("access_token"):
        return redirect(url_for("log.daily_log"))
    return render_template("auth/login.html")


@auth_bp.post("/login")
def login_post():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    try:
        result = api_client.login(email, password)
        session["access_token"] = result["access_token"]
        session["session_id"] = str(uuid.uuid4())
        return redirect(url_for("log.daily_log"))
    except APIError:
        flash("Invalid email or password.", "error")
        return render_template("auth/login.html"), 400


@auth_bp.get("/logout")
def logout():
    try:
        api_client.logout()
    except Exception:
        session.clear()
    return redirect(url_for("auth.login_view"))


@auth_bp.get("/register")
def register_view():
    return render_template("auth/register.html")


@auth_bp.post("/register")
def register_post():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    try:
        api_client.register(email, password)
        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth.login_view"))
    except APIError as e:
        flash(e.detail, "error")
        return render_template("auth/register.html"), 400
