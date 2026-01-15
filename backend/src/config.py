"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "sqlite:///./taskflow_test.db"

    # JWT Authentication
    JWT_SECRET: str = "dev-secret-key-minimum-32-characters-for-development-only"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DAYS: int = 7

    # CORS (comma-separated string from .env)
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:3002,http://127.0.0.1:3002,http://localhost:3004,http://127.0.0.1:3004"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",")]  # FIXED: Both have same spelling now - 7 letters: O-R-I-G-I-N-S
        print(f"[DEBUG] CORS Origins Loaded: {origins}")  # Debug logging
        return origins

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # AI Service (Gemini API with OpenAI Agents SDK for Phase 3 Chatbot)
    GEMINI_API_KEY: str = ""
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai/"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
print(f"[DEBUG] Settings initialized with CORS: {settings.cors_origins_list}")