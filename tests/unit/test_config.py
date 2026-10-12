import pytest

from nyc_mobility.config import Settings

REQUIRED_ENV = {
    "POSTGRES_USER": "user",
    "POSTGRES_PASSWORD": "secret",
    "POSTGRES_DB": "nyc_mobility",
    "S3_ENDPOINT_URL": "http://object-store:9000",
    "S3_ACCESS_KEY": "key",
    "S3_SECRET_KEY": "secret-key",
    "S3_BUCKET": "bucket",
}
OPTIONAL_ENV = ["PIPELINE_ENV", "POSTGRES_HOST", "POSTGRES_PORT", "TLC_DATASET", "TLC_MONTH"]


@pytest.fixture
def required_env(monkeypatch):
    """Set every required variable and clear the optional ones, for one test only."""
    for name, value in REQUIRED_ENV.items():
        monkeypatch.setenv(name, value)
    for name in OPTIONAL_ENV:
        monkeypatch.delenv(name, raising=False)


def test_from_env_uses_defaults_for_optional_settings(required_env):
    settings = Settings.from_env()

    assert settings.pipeline_env == "local"
    assert settings.postgres_host == "localhost"
    assert settings.postgres_port == 5432
    assert settings.tlc_month == "2024-01"


def test_postgres_port_is_converted_to_int(required_env, monkeypatch):
    monkeypatch.setenv("POSTGRES_PORT", "5433")

    assert Settings.from_env().postgres_port == 5433


def test_postgres_dsn_is_built_from_parts(required_env, monkeypatch):
    monkeypatch.setenv("POSTGRES_HOST", "postgres")

    assert Settings.from_env().postgres_dsn == (
        "postgresql://user:secret@postgres:5432/nyc_mobility"
    )


def test_from_env_fails_fast_when_required_setting_missing(required_env, monkeypatch):
    monkeypatch.delenv("S3_BUCKET")                  # Arrange: remove one required variable

    with pytest.raises(KeyError, match="S3_BUCKET"):  # Assert: we expect a KeyError...
        Settings.from_env()                           # Act: ...when building settings