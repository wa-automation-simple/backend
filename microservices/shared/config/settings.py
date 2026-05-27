"""
Shared configuration settings for all microservices
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/wa_saas"
    
    # JWT Settings
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # RabbitMQ / Message Broker
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    
    # AI Service
    AI_API_KEY: str = ""
    AI_BASE_URL: str = "https://api.openai.com/v1"
    AI_MODEL: str = "gpt-3.5-turbo"
    
    # Token Pricing (Markup)
    TOKEN_BASE_PRICE: float = 3.0  # Base cost from provider
    TOKEN_SELL_PRICE: float = 10.0  # Price to user (markup)
    
    # WhatsApp Settings
    WA_WARMUP_DAYS: int = 30
    WA_MAX_BLAST_PER_DAY: int = 1000
    
    # Service URLs
    AUTH_SERVICE_URL: str = "http://auth-service:8001"
    WHATSAPP_SERVICE_URL: str = "http://whatsapp-service:8003"
    BLAST_SERVICE_URL: str = "http://blast-service:8004"
    AI_SERVICE_URL: str = "http://ai-service:8005"
    PAYMENT_SERVICE_URL: str = "http://payment-service:8006"
    FOLLOWUP_SERVICE_URL: str = "http://followup-service:8007"
    SCHEDULER_SERVICE_URL: str = "http://scheduler-service:8008"
    
    class Config:
        env_file = ".env"

settings = Settings()
