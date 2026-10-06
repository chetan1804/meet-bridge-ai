from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "MeetBridge AI"
    environment: str = "development"
    api_prefix: str = "/api"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    jwt_secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    database_url: str = "postgresql+psycopg2://meetbridge:meetbridge@localhost:5432/meetbridge"
    redis_url: str = "redis://localhost:6379/0"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    llm_provider: str = "mock"
    speech_to_text_provider: str = "mock"
    enable_audio_retention: bool = False
    audio_retention_days: int = 7

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env", case_sensitive=False, extra="ignore"
    )

    def validate_runtime_environment(self) -> bool:
        if self.environment.lower() != "production":
            return True

        if not self.jwt_secret_key or self.jwt_secret_key == "change-me-in-production":
            raise ValueError("JWT secret must be overridden in production.")
        if not self.database_url:
            raise ValueError("Database URL is required in production.")
        if not self.redis_url:
            raise ValueError("Redis URL is required in production.")
        if self.enable_audio_retention and self.audio_retention_days < 1:
            raise ValueError("Audio retention days must be at least 1 when retention is enabled.")
        return True


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_runtime_environment()
    return settings
