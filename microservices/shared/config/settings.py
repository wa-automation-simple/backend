import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    # General
    APP_NAME: str = "WhatsApp SaaS"
    DEBUG: bool = True
    VERSION: str = "1.0.0"
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Token Pricing (Markup)
    TOKEN_BASE_PRICE: float = 3.0  # Provider cost
    TOKEN_SELL_PRICE: float = 10.0  # User price (233% markup)
    
    class Config:
        env_file = ".env"


settings = Settings()
