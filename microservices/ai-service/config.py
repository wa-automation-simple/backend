"""
AI Service Configuration
Dedicated database for AI tokens, transactions, and auto-reply configs
"""
import os
from pydantic import BaseSettings


class AISettings(BaseSettings):
    SERVICE_NAME: str = "ai-service"
    SERVICE_PORT: int = 8005
    
    # Dedicated database for ai service
    DATABASE_URL: str = os.getenv("AI_DATABASE_URL", "postgresql://ai_user:ai_pass@postgres-ai:5432/ai_db")
    
    # AI Provider settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    AI_MODEL: str = "gpt-4"
    MAX_TOKENS_PER_REQUEST: int = 2000
    
    # Token pricing (markup from base cost)
    TOKEN_BASE_PRICE: float = 3.0  # Cost from provider
    TOKEN_SELL_PRICE: float = 10.0  # Price to user (233% markup)
    
    # Bulk packages with discounts
    BULK_PACKAGES = {
        10: 0.05,    # 5% discount for 10+ tokens
        50: 0.10,    # 10% discount for 50+ tokens
        100: 0.15,   # 15% discount for 100+ tokens
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = AISettings()
