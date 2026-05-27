"""
WhatsApp Service Configuration
Dedicated database for WhatsApp account management
"""
import os
from pydantic import BaseSettings


class WhatsAppSettings(BaseSettings):
    SERVICE_NAME: str = "whatsapp-service"
    SERVICE_PORT: int = 8003
    
    # Dedicated database for whatsapp service
    DATABASE_URL: str = os.getenv("WHATSAPP_DATABASE_URL", "postgresql://wa_user:wa_pass@postgres-whatsapp:5432/whatsapp_db")
    
    # WhatsApp API settings
    WA_API_KEY: str = os.getenv("WA_API_KEY", "")
    WA_SESSION_TIMEOUT: int = 3600  # 1 hour
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = WhatsAppSettings()
