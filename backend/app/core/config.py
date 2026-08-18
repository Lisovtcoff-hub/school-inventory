from functools import lru_cache
from pathlib import Path

from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


_BACKEND_DIR = Path(__file__).resolve().parents[2]
_PROJECT_ROOT = _BACKEND_DIR.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "School Inventory API"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = "sqlite:///./school_inventory.db"

    SECRET_KEY: str = "development-only-secret-change-before-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    JWT_ALGORITHM: str = "HS256"

    BACKEND_CORS_ORIGINS: str = ""

    model_config = SettingsConfigDict(
        env_file=(
            _PROJECT_ROOT / ".env",
            _BACKEND_DIR / ".env",
        ),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @computed_field
    @property
    def cors_origins_list(self) -> list[str]:
        if not self.BACKEND_CORS_ORIGINS:
            return []
        return [
            origin.strip()
            for origin in self.BACKEND_CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.ENVIRONMENT.lower() not in {"production", "prod"}:
            return self

        weak_markers = {"change-this-secret-key-in-production", "development-only-secret-change-before-production"}
        if self.SECRET_KEY in weak_markers or len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be a strong value of at least 32 characters in production")

        if not self.DATABASE_URL.startswith("postgresql"):
            raise ValueError("Production DATABASE_URL must use PostgreSQL")

        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
