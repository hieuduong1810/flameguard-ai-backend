"""Environment-driven settings; database credentials are never part of API responses."""

from functools import lru_cache
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore", hide_input_in_errors=True
    )

    app_name: str = "FlameGuard AI Backend"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    database_url: SecretStr = SecretStr(
        "postgresql+asyncpg://flameguard:local-development-only@localhost:5432/flameguard"
    )
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "https://flame-in-freewall-tourbillion.vercel.app",
        ]
    )
    db_connect_timeout_seconds: float = Field(default=3, gt=0, le=30)
    db_ready_timeout_seconds: float = Field(default=3, gt=0, le=30)
    catalog_collection_manifest: str | None = None
    scenario_test_providers: bool = False
    runtime_database_url: SecretStr | None = None
    chat_provider: Literal["unavailable", "mock"] = "unavailable"
    chat_timeout_seconds: float = Field(default=10, gt=0, le=30)
    prediction_provider: Literal["unavailable", "mock"] = "unavailable"
    prediction_timeout_seconds: float = Field(default=10, gt=0, le=30)

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: SecretStr) -> SecretStr:
        try:
            url = make_url(value.get_secret_value())
            valid = url.drivername == "postgresql+asyncpg" and bool(url.host and url.database)
        except ArgumentError:
            valid = False
        if not valid:
            raise ValueError("DATABASE_URL must use postgresql+asyncpg with host and database")
        return value

    @field_validator("api_v1_prefix")
    @classmethod
    def validate_prefix(cls, value: str) -> str:
        if not value.startswith("/") or value.endswith("/") or any(c in value for c in "?#{} "):
            raise ValueError("API_V1_PREFIX must be a path starting with /, without trailing /")
        return value

    @field_validator("cors_origins")
    @classmethod
    def validate_origins(cls, origins: list[str]) -> list[str]:
        for origin in origins:
            parsed = urlsplit(origin)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.hostname
                or "*" in origin
                or parsed.username is not None
                or parsed.password is not None
                or parsed.path
                or parsed.query
                or parsed.fragment
            ):
                raise ValueError("CORS_ORIGINS must contain explicit HTTP(S) origins without paths")
        return origins

    @model_validator(mode="after")
    def validate_production(self) -> "Settings":
        if self.app_env == "production" and self.debug:
            raise ValueError("DEBUG must be false in production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
