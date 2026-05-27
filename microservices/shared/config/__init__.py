"""
Shared configuration for all microservices
"""
import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    # Service identification
    SERVICE_NAME: str = "unknown"
    SERVICE_PORT: int = 8000
    
    # Database (each service has its own)
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/db"
    
    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24  # 24 hours
    
    # Redis (shared for caching/sessions)
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # AI Provider
    OPENAI_API_KEY: str = ""
    AI_MODEL: str = "gpt-4"
    
    # Token Pricing
    TOKEN_BASE_PRICE: float = 3.0  # Cost from provider
    TOKEN_SELL_PRICE: float = 10.0  # Price to user (markup)
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
