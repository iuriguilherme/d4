from flask import Flask
from flask_session import Session

from web.config import Config


def create_app(config_class=Config):
    app = Flask(__name__, template_folder="templates")
    app.config.from_object(config_class)

    Session(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
