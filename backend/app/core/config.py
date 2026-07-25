"""Application settings loaded from environment variables or a local .env file."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "EduGenie Learning Assistant"
    app_version: str = "1.0.0"
    debug: bool = False

    host: str = "127.0.0.1"
    port: int = 8000

    database_url: str = f"sqlite:///{(PROJECT_ROOT / 'data' / 'edugenie.db').as_posix()}"

    gemini_api_key: str | None = None
    google_api_key: str | None = None
    gemini_model: str = "gemini-1.5-pro"
    lamini_model: str = "MBZUAI/LaMini-Flan-T5-783M"
    edugenie_use_local_model: bool = True

    @property
    def project_root(self) -> Path:
        return PROJECT_ROOT

    @property
    def templates_dir(self) -> Path:
        return PROJECT_ROOT / "frontend" / "templates"

    @property
    def static_dir(self) -> Path:
        return PROJECT_ROOT / "frontend" / "static"

    @property
    def ai_provider_configured(self) -> bool:
        return bool(self.gemini_api_key or self.google_api_key)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


def sync_environment(settings: Settings | None = None) -> None:
    """Publish resolved settings into ``os.environ``.

    The AI feature modules read their provider configuration with ``os.getenv``
    so they stay usable standalone. Values loaded from a ``.env`` file are only
    visible on the ``Settings`` object, so without this the modules would fall
    back to local output while ``/health`` reported the provider as configured.
    """

    settings = settings or get_settings()
    resolved = {
        "GEMINI_API_KEY": settings.gemini_api_key,
        "GOOGLE_API_KEY": settings.google_api_key,
        "GEMINI_MODEL": settings.gemini_model,
        "LAMINI_MODEL": settings.lamini_model,
        "EDUGENIE_USE_LOCAL_MODEL": "1" if settings.edugenie_use_local_model else "0",
    }
    for name, value in resolved.items():
        if value:
            os.environ[name] = str(value)
