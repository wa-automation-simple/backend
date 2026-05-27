"""Followup Service Configuration"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SERVICE_NAME: str = "followup"
    DATABASE_URL: str = "postgresql://postgres:postgres@followup-db:5432/followup_db"
    PORT: int = 8007
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
