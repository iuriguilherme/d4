from datetime import date
import os
import stat

from flask import Flask, session
from flask_session import Session

from web.config import Config


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config_class)

    # Resolve session directory: prefer explicit config, fall back to instance_path.
    _raw_dir = app.config.get("SESSION_FILE_DIR") or os.path.join(
        app.instance_path, "flask_sessions"
    )
    # Ensure instance_path exists (with restricted permissions) when used as fallback.
    if not app.config.get("SESSION_FILE_DIR"):
        _old_umask = os.umask(0o077)
        try:
            os.makedirs(app.instance_path, mode=0o700, exist_ok=True)
        finally:
            os.umask(_old_umask)
    # Canonicalize to resolve any parent-component symlinks.
    session_dir = os.path.realpath(_raw_dir)
    # Create with a restrictive umask to ensure atomic 0700 permissions.
    _old_umask = os.umask(0o077)
    try:
        os.makedirs(session_dir, mode=0o700, exist_ok=True)
    finally:
        os.umask(_old_umask)
    # Open with O_NOFOLLOW so the call fails if the path was replaced by a symlink.
    # fstat and fchmod operate on the fd, avoiding further symlink-following risks.
    try:
        _dir_fd = os.open(session_dir, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    except OSError as exc:
        raise RuntimeError(
            f"SESSION_FILE_DIR '{session_dir}' is a symlink or could not be opened: {exc}"
        ) from exc
    try:
        _st = os.fstat(_dir_fd)
        if not stat.S_ISDIR(_st.st_mode):
            raise RuntimeError(
                f"SESSION_FILE_DIR '{session_dir}' exists but is not a directory."
            )
        os.fchmod(_dir_fd, 0o700)
    finally:
        os.close(_dir_fd)
    app.config["SESSION_FILE_DIR"] = session_dir

    Session(app)

    from web.app.auth.routes import auth_bp
    from web.app.log.routes import log_bp
    from web.app.journal.routes import journal_bp
    from web.app.habits.routes import habits_bp
    from web.app.settings.routes import settings_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(log_bp)
    app.register_blueprint(journal_bp)
    app.register_blueprint(habits_bp)
    app.register_blueprint(settings_bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.context_processor
    def inject_globals():
        from web.app import api_client
        current_user = None
        if session.get("access_token"):
            try:
                current_user = api_client.get_current_user()
            except Exception:
                pass
        return {
            "current_user": current_user,
            "today": str(date.today()),
        }

    return app
