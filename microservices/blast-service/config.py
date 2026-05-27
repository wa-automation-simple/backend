"""
Blast Service Configuration
Dedicated database for blast campaigns and media
"""
import os
from pydantic import BaseSettings


class BlastSettings(BaseSettings):
    SERVICE_NAME: str = "blast-service"
    SERVICE_PORT: int = 8004
    
    # Dedicated database for blast service
    DATABASE_URL: str = os.getenv("BLAST_DATABASE_URL", "postgresql://blast_user:blast_pass@postgres-blast:5432/blast_db")
    
    # Media storage
    MEDIA_STORAGE_PATH: str = "/app/media"
    MAX_MEDIA_SIZE_MB: int = 50
    
    # Rate limiting
    MESSAGES_PER_MINUTE: int = 60
    BATCH_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = BlastSettings()
