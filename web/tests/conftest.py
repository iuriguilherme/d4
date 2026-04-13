import pytest
from unittest.mock import MagicMock, patch

from web.app import create_app
from web.config import Config


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "test-secret"
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = "/tmp/flask_test_sessions"
    FASTAPI_BASE_URL = "http://fake-api"
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app():
    app = create_app(TestConfig)
    app.config["TESTING"] = True
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
