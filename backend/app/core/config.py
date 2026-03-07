"""
Configuration management for RAG Chatbot application.

Uses Pydantic Settings to load environment variables and provide
typed configuration throughout the application.
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost",
    ]

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Qdrant (Vector Database)
    QDRANT_URL: str
    QDRANT_API_KEY: str
    QDRANT_COLLECTION_NAME: str = "physical_ai_textbook"

    # PostgreSQL (Conversation History)
    DATABASE_URL: str

    # Authentication (JWT)
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DAYS: int = 7
    REMEMBER_ME_EXPIRATION_DAYS: int = 30

    # Application settings
    VECTOR_SEARCH_LIMIT: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    RESPONSE_TIMEOUT_SECONDS: int = 3

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = True


settings = Settings()
