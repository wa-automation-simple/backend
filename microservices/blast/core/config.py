"""Blast Service Configuration"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    SERVICE_NAME: str = "Blast Service"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/blast_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External Services
    AUTH_SERVICE_URL: str = "http://auth:8000"
    WHATSAPP_SERVICE_URL: str = "http://whatsapp:8000"
    SHARED_SERVICE_URL: str = "http://shared:8000"
    
    # WhatsApp Automation (Playwright/Selenium)
    BROWSER_TYPE: str = "chromium"  # chromium, firefox, webkit
    HEADLESS_BROWSER: bool = True
    BROWSER_TIMEOUT: int = 30000  # milliseconds
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
