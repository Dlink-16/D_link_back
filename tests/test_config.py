from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_settings_are_loaded_from_environment(monkeypatch, tmp_path):
    db_path = tmp_path / "configured.db"
    monkeypatch.setenv("ENV", "test")
    monkeypatch.setenv("API_HOST", "127.0.0.1")
    monkeypatch.setenv("API_PORT", "9000")
    monkeypatch.setenv("TOURAPI_DB_PATH", str(db_path))
    monkeypatch.setenv("CORS_ORIGINS", '["http://localhost:5173"]')

    settings = Settings(_env_file=None)

    assert settings.env == "test"
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 9000
    assert settings.tourapi_db_path == Path(db_path)
    assert settings.cors_origins == ["http://localhost:5173"]


def test_database_path_is_required(monkeypatch):
    monkeypatch.delenv("TOURAPI_DB_PATH", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
