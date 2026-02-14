"""
Application configuration management.

Loads and validates environment variables for the FastAPI application.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables or .env file.
    """

    # Database Configuration
    DATABASE_URL: str

    # Authentication Configuration
    BETTER_AUTH_SECRET: str  # Shared secret with frontend Better Auth
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24

    # CORS Configuration
    CORS_ORIGINS: str = "http://localhost:3000"  # Comma-separated list

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_TITLE: str = "Todo App API"
    API_VERSION: str = "1.0.0"

    # Environment
    ENVIRONMENT: str = "development"

    # MCP Server Configuration
    MCP_SERVER_PORT: int = 8001

    # Google Gemini Configuration
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "models/gemini-2.0-flash"  # Gemini 2.0 Flash - fast and versatile
    GEMINI_MAX_TOKENS: int = 4000
    GEMINI_TEMPERATURE: float = 0.7
    
    # Groq Configuration (Free & Fast Alternative)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"  # Fast and capable
    GROQ_MAX_TOKENS: int = 4000
    GROQ_TEMPERATURE: float = 0.7

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields in .env without crashing

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
