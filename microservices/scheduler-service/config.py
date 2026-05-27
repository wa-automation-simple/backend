"""
Scheduler Service Configuration
Dedicated database for job scheduling and status tracking
"""
import os
from pydantic import BaseSettings


class SchedulerSettings(BaseSettings):
    SERVICE_NAME: str = "scheduler-service"
    SERVICE_PORT: int = 8008
    
    # Dedicated database for scheduler service
    DATABASE_URL: str = os.getenv("SCHEDULER_DATABASE_URL", "postgresql://scheduler_user:scheduler_pass@postgres-scheduler:5432/scheduler_db")
    
    # Redis for distributed task queue
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # Worker settings
    MAX_WORKERS: int = 10
    TASK_TIMEOUT_SECONDS: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = SchedulerSettings()
