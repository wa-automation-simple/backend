"""Configuration management for Blast service."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    SERVICE_NAME: str = "blast"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/blast_db"
    
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
