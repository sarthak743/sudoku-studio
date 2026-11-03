
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    solver_deadline_ms: int = Field(default=10000, gt=0)
    max_stored_solutions: int = Field(default=15, ge=1, le=15)
    max_upload_mb: int = Field(default=5, gt=0)

    allowed_origins: list[str] = Field(
        default=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )


settings = Settings()
