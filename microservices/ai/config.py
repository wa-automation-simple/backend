"""AI Service Configuration"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "ai"
    DATABASE_URL: str = "postgresql://postgres:postgres@ai-db:5432/ai_db"
    PORT: int = 8005
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI Provider Settings
    OPENAI_API_KEY: str = ""
    AI_MODEL: str = "gpt-3.5-turbo"
    
    class Config:
        env_file = ".env"


settings = Settings()
