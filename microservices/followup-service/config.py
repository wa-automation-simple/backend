"""
Follow-up Service Configuration
Dedicated database for leads and follow-up management
"""
import os
from pydantic import BaseSettings


class FollowUpSettings(BaseSettings):
    SERVICE_NAME: str = "followup-service"
    SERVICE_PORT: int = 8007
    
    # Dedicated database for followup service
    DATABASE_URL: str = os.getenv("FOLLOWUP_DATABASE_URL", "postgresql://followup_user:followup_pass@postgres-followup:5432/followup_db")
    
    # Follow-up settings
    DEFAULT_REMINDER_HOURS: int = 24
    MAX_FOLLOWUPS_PER_LEAD: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = FollowUpSettings()
