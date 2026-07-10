"""
Application settings loaded from environment variables via pydantic-settings.
All configuration lives here — no os.environ calls anywhere else in the codebase.
"""
from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- App ----
    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"

    # ---- Database ----
    database_url: str

    # ---- Redis / Celery ----
    redis_url: str = "redis://localhost:6379"

    # ---- Clerk Auth ----
    clerk_secret_key: str
    clerk_jwks_url: str

    # ---- Encryption ----
    encryption_key: str  # Fernet key — base64-url-safe 32-byte key

    # ---- CORS ----
    cors_origins: list[str] = ["http://localhost:3000"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            if not v.strip():
                return []
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # ---- LLM (Phase 3) ----
    llm_provider: Literal["groq", "openai", "anthropic"] = "groq"
    groq_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # ---- Email / Resend (Phase 4) ----
    resend_api_key: str = ""

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Return cached singleton settings instance."""
    return Settings()
