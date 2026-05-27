"""
Auth Service Configuration
Each service has its own database connection
"""
import os
from pydantic import BaseSettings


class AuthSettings(BaseSettings):
    SERVICE_NAME: str = "auth-service"
    SERVICE_PORT: int = 8001
    
    # Dedicated database for auth service
    DATABASE_URL: str = os.getenv("AUTH_DATABASE_URL", "postgresql://auth_user:auth_pass@postgres-auth:5432/auth_db")
    
    # JWT Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = AuthSettings()
