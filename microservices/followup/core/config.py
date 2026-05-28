"""FollowUp Service Configuration"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    SERVICE_NAME: str = "FollowUp Service"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/followup_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External Services
    AUTH_SERVICE_URL: str = "http://auth:8000"
    WHATSAPP_SERVICE_URL: str = "http://whatsapp:8000"
    CHATBOT_SERVICE_URL: str = "http://chatbot:8000"
    SHARED_SERVICE_URL: str = "http://shared:8000"
    
    # FollowUp Settings
    DEFAULT_FOLLOWUP_INTERVAL_HOURS: int = 24
    MAX_FOLLOWUP_ATTEMPTS: int = 5
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
