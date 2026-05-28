"""WhatsApp Service Configuration"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    SERVICE_NAME: str = "WhatsApp Service"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/whatsapp_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External Services
    AUTH_SERVICE_URL: str = "http://auth:8000"
    CHATBOT_SERVICE_URL: str = "http://chatbot:8000"
    
    # WhatsApp Web / Browser Automation
    BROWSER_TYPE: str = "chromium"  # chromium, firefox, webkit
    HEADLESS: bool = True
    BROWSER_TIMEOUT: int = 30000  # milliseconds
    SESSION_PATH: str = "./sessions"
    
    # WhatsApp Business API (optional)
    WHATSAPP_API_KEY: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = ""
    
    # Rate Limiting
    MAX_MESSAGES_PER_SECOND: int = 10
    MESSAGE_DELAY_MS: int = 100
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
