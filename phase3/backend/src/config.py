"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/dbname"

    # JWT Authentication
    JWT_SECRET: str = "dev-secret-key-minimum-32-characters-for-development-only"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DAYS: int = 7

    # CORS (comma-separated string from .env)
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:3002,http://127.0.0.1:3002"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        print(f"[DEBUG] CORS Origins Loaded: {origins}")  # Debug logging
        return origins

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
print(f"[DEBUG] Settings initialized with CORS: {settings.cors_origins_list}")
