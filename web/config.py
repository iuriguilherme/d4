import os


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "change-me-in-production")
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = os.environ.get("FLASK_SESSION_FILE_DIR")
    SESSION_PERMANENT = False

    FASTAPI_BASE_URL = os.environ.get("FASTAPI_BASE_URL", "http://localhost:8000")
    ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
