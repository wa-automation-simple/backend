"""Payment Service Configuration"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    SERVICE_NAME: str = "Payment Service"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/payment_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External Services
    AUTH_SERVICE_URL: str = "http://auth:8000"
    
    # Xendit Payment Gateway
    XENDIT_SECRET_KEY: str = ""
    XENDIT_PUBLIC_KEY: str = ""
    XENDIT_BASE_URL: str = "https://api.xendit.co"
    XENDIT_WEBHOOK_TOKEN: str = ""
    
    # Callback URLs
    PAYMENT_CALLBACK_URL: str = "http://payment:8000/api/v1/payment/callback"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
