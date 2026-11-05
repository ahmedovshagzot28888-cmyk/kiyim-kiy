from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    tryon_provider: Literal["mock", "replicate", "gemini"] = "mock"
    frontend_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://127.0.0.1:3000"]
    )

    max_upload_bytes: int = 5 * 1024 * 1024
    min_image_dimension: int = 128
    max_image_dimension: int = 8000
    working_max_dimension: int = 1600
    jpeg_quality: int = 90

    rate_limit_requests: int = 5
    rate_limit_window_seconds: int = 3600
    trust_forwarded_for: bool = False
    trust_proxy_hops: int = 1

    job_ttl_seconds: int = 600
    job_reaper_interval_seconds: int = 30
    max_concurrent_jobs: int = 2

    provider_timeout_seconds: int = 120
    provider_max_retries: int = 2
    mock_delay_seconds: float = 0.6

    replicate_api_token: SecretStr | None = None
    replicate_model_version: str = "cuuupid/idm-vton:0513734a14f04a7ae3e5c81de8ff3c57"
    replicate_steps: int = 30

    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-nano-banana-2.1"

    environment: Literal["development", "production", "test"] = "development"
    log_level: str = "INFO"

    @field_validator("frontend_origins", mode="before")
    @classmethod
    def split_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    def validate_provider(self) -> None:
        if self.tryon_provider == "replicate" and not self.replicate_api_token:
            raise ValueError("REPLICATE_API_TOKEN is required when TRYON_PROVIDER=replicate")
        if self.tryon_provider == "gemini" and not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required when TRYON_PROVIDER=gemini")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_provider()
    return settings
