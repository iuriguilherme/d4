from datetime import date

from flask import Flask, session, g
from flask_session import Session

from web.config import Config


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config_class)

    Session(app)

    from web.app.auth.routes import auth_bp
    from web.app.log.routes import log_bp
    from web.app.journal.routes import journal_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(log_bp)
    app.register_blueprint(journal_bp)

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
