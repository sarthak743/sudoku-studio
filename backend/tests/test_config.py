
import pytest
from pydantic import ValidationError

from app.core.config import Settings as AppSettings


def test_default_settings():
    config = AppSettings(_env_file=None)

    assert config.solver_deadline_ms == 10000
    assert config.max_stored_solutions == 15
    assert config.max_upload_mb == 5
    assert "http://localhost:5173" in config.allowed_origins


def test_custom_environment_settings(monkeypatch):
    monkeypatch.setenv("SOLVER_DEADLINE_MS", "5000")
    monkeypatch.setenv("MAX_STORED_SOLUTIONS", "10")
    monkeypatch.setenv("MAX_UPLOAD_MB", "8")
    monkeypatch.setenv(
        "ALLOWED_ORIGINS",
        '["http://localhost:3000"]',
    )

    config = AppSettings(_env_file=None)

    assert config.solver_deadline_ms == 5000
    assert config.max_stored_solutions == 10
    assert config.max_upload_mb == 8
    assert config.allowed_origins == ["http://localhost:3000"]


@pytest.mark.parametrize(
    "environment, value",
    [
        ("SOLVER_DEADLINE_MS", "0"),
        ("MAX_STORED_SOLUTIONS", "0"),
        ("MAX_STORED_SOLUTIONS", "16"),
        ("MAX_UPLOAD_MB", "-1"),
    ],
)
def test_invalid_environment_settings(monkeypatch, environment, value):
    monkeypatch.setenv(environment, value)

    with pytest.raises(ValidationError):
        AppSettings(_env_file=None)
