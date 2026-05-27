"""Configuration for Auth Service."""
from pydantic_settings import BaseSettings
from typing import Optional


class AuthSettings(BaseSettings):
    """Auth service configuration."""
    
    # Service info
    SERVICE_NAME: str = "auth-service"
    SERVICE_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@auth-db:5432/auth_db"
    
    # JWT settings
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = AuthSettings()
