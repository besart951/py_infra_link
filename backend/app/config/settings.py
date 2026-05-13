from __future__ import annotations

from typing import cast

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")

    database_url: PostgresDsn = Field(
        default=cast(
            PostgresDsn,
            "postgresql+asyncpg://postgres:postgres@localhost:5432/py_infra_link",
        ),
        description="Async PostgreSQL connection URL.",
    )
    debug: bool = Field(default=False, description="Enable debug mode.")
    echo_sql: bool = Field(default=False, description="Echo all SQL statements.")

    jwt_secret_key: str = Field(
        default="change-me-in-production",
        description="Secret key used to sign and verify JWT tokens.",
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT signing algorithm.")
    jwt_expire_minutes: int = Field(
        default=60 * 24 * 7,
        description="JWT token lifetime in minutes (default: 7 days).",
    )


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
