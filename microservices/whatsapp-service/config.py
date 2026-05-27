"""Configuration for WhatsApp Service."""
from pydantic_settings import BaseSettings


class WhatsAppSettings(BaseSettings):
    """WhatsApp service configuration."""
    
    # Service info
    SERVICE_NAME: str = "whatsapp-service"
    SERVICE_VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@whatsapp-db:5432/whatsapp_db"
    
    # WhatsApp API settings
    WA_API_URL: str = "https://api.whatsapp.com"
    WA_WEBHOOK_SECRET: str = "whatsapp-webhook-secret"
    
    # Warmup settings
    WARMUP_DEFAULT_DAYS: int = 30
    WARMUP_MAX_MESSAGES_DAY1: int = 5
    WARMUP_INCREMENT_PER_DAY: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = WhatsAppSettings()
