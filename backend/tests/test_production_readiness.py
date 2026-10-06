import pytest

from app.core.config import Settings


def test_settings_validate_required_runtime_values_for_production() -> None:
    with pytest.raises(ValueError, match="JWT secret"):
        Settings(
            environment="production",
            jwt_secret_key="change-me-in-production",
            database_url="postgresql+psycopg2://meetbridge:meetbridge@localhost:5432/meetbridge",
        ).validate_runtime_environment()

    validated = Settings(
        environment="production",
        jwt_secret_key="strong-production-secret",
        database_url="postgresql+psycopg2://meetbridge:meetbridge@localhost:5432/meetbridge",
    )
    assert validated.validate_runtime_environment() is True
