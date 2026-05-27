"""Configuration management for WhatsApp service."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Service Info
    SERVICE_NAME: str = "whatsapp"
    SERVICE_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/whatsapp_db"
    
    # WhatsApp API
    WA_API_URL: str = "http://localhost:3000"
    WA_WEBHOOK_SECRET: str = "whatsapp_webhook_secret_change_in_production"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
