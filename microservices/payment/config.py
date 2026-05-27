"""Payment Service Configuration"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "payment"
    DATABASE_URL: str = "postgresql://postgres:postgres@token-db:5432/token_db"
    PORT: int = 8006
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Payment Gateway Settings
    STRIPE_SECRET_KEY: str = ""
    PAYPAL_CLIENT_ID: str = ""
    
    # Token Pricing (Markup from $3 to $10)
    BASE_TOKEN_PRICE: float = 3.0  # Provider cost
    SELL_TOKEN_PRICE: float = 10.0  # User price with markup
    
    class Config:
        env_file = ".env"


settings = Settings()
