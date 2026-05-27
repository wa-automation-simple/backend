"""Chatbot Service Configuration"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    SERVICE_NAME: str = "Chatbot Service"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/chatbot_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External Services
    AUTH_SERVICE_URL: str = "http://auth:8000"
    WHATSAPP_SERVICE_URL: str = "http://whatsapp:8000"
    
    # AI/LLM
    OPENAI_API_KEY: str = ""
    LANGCHAIN_API_KEY: str = ""
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()