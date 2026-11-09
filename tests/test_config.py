import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings


def test_environment_overrides_and_json_cors(monkeypatch) -> None:
    monkeypatch.setenv("APP_NAME", "Configured Backend")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost/db")
    monkeypatch.setenv("CORS_ORIGINS", '["https://research.example"]')
    settings = Settings(_env_file=None)
    assert settings.app_name == "Configured Backend"
    assert settings.cors_origins == ["https://research.example"]
    assert "password" not in repr(settings)
    assert "password" not in settings.model_dump_json()


def test_dotenv_loading(tmp_path) -> None:
    dotenv = tmp_path / "sample.env"
    dotenv.write_text(
        "APP_NAME=From dotenv\nPOSTGRES_DB=ignored-compose-setting\n", encoding="utf-8"
    )
    assert Settings(_env_file=dotenv).app_name == "From dotenv"


@pytest.mark.parametrize("prefix", ["api/v1", "/api/v1/", "/", "/api?x=1", "/{id}"])
def test_invalid_api_prefix(prefix: str) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, api_v1_prefix=prefix)


@pytest.mark.parametrize(
    "url",
    ["sqlite+aiosqlite:///test.db", "postgresql://host/db", "not-a-url", "postgresql+asyncpg://"],
)
def test_database_requires_async_postgres(url: str) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, database_url=url)


@pytest.mark.parametrize(
    "origin",
    ["*", "https://*.example", "https://example/path", "https://user:pass@example", "null"],
)
def test_cors_requires_explicit_origins(origin: str) -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, cors_origins=[origin])


def test_production_rejects_debug() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, app_env="production", debug=True)


def test_settings_cache_can_be_reset(monkeypatch) -> None:
    get_settings.cache_clear()
    try:
        monkeypatch.setenv("APP_NAME", "Cached")
        first = get_settings()
        monkeypatch.setenv("APP_NAME", "Changed")
        assert get_settings() is first
        get_settings.cache_clear()
        assert get_settings().app_name == "Changed"
    finally:
        get_settings.cache_clear()
