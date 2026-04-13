from flask import Blueprint, render_template, request, redirect, url_for, flash

from web.app import api_client
from web.app.api_client import APIError
from web.app.auth.routes import login_required

habits_bp = Blueprint("habits", __name__, template_folder="templates")


@habits_bp.get("/habits")
@login_required
def habit_board():
    habits = api_client.list_habits() or []
    return render_template("habits/habits.html", habits=habits)


@habits_bp.post("/habits")
@login_required
def create_habit():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Habit name required.", "error")
        return redirect(url_for("habits.habit_board"))
    try:
        api_client.create_habit({"name": name})
    except APIError as e:
        flash(e.detail, "error")
    return redirect(url_for("habits.habit_board"))


@habits_bp.post("/habits/<habit_id>/checkin")
@login_required
def checkin(habit_id: str):
    try:
        result = api_client.checkin_habit(habit_id)
    except APIError as e:
        return str(e.detail), e.status_code
    # Find the updated habit to re-render its row
    habits = api_client.list_habits() or []
    habit = next((h for h in habits if str(h.get("id")) == habit_id), None)
    if not habit:
        return "", 404
    habit["streak"] = result["streak"]
    return render_template("habits/_habit_row.html", habit=habit)


@habits_bp.post("/habits/<habit_id>/delete")
@login_required
def delete_habit(habit_id: str):
    try:
        api_client.delete_habit(habit_id)
    except APIError as e:
        flash(e.detail, "error")
    return redirect(url_for("habits.habit_board"))
