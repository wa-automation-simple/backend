"""
Payment Service Configuration
Dedicated database for payments and invoices
"""
import os
from pydantic import BaseSettings


class PaymentSettings(BaseSettings):
    SERVICE_NAME: str = "payment-service"
    SERVICE_PORT: int = 8006
    
    # Dedicated database for payment service
    DATABASE_URL: str = os.getenv("PAYMENT_DATABASE_URL", "postgresql://payment_user:payment_pass@postgres-payment:5432/payment_db")
    
    # Payment gateway settings
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "")
    PAYPAL_CLIENT_ID: str = os.getenv("PAYPAL_CLIENT_ID", "")
    
    # Currency
    DEFAULT_CURRENCY: str = "USD"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = PaymentSettings()
