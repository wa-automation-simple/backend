"""
Scheduler Service Database Models
Dedicated database for job scheduling and status tracking
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class JobStatus(enum.Enum):
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobType(enum.Enum):
    BLAST_SEND = "blast_send"
    FOLLOWUP_SEND = "followup_send"
    WARMUP_INCREMENT = "warmup_increment"
    RECOVERY_CLICK = "recovery_click"
    AI_PROCESS = "ai_process"
    CLEANUP = "cleanup"
    CUSTOM = "custom"


class ScheduledJob(Base):
    """Scheduled job model."""
    __tablename__ = "scheduled_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(SQLEnum(JobType), nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    priority = Column(Integer, default=5)  # 1=highest, 10=lowest
    payload = Column(Text, nullable=False)  # JSON string with job data
    scheduled_at = Column(DateTime, nullable=False, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<ScheduledJob(id={self.id}, type='{self.job_type}', status='{self.status}')>"


class JobExecutionLog(Base):
    """Job execution history log."""
    __tablename__ = "job_execution_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("scheduled_jobs.id"), nullable=False)
    execution_number = Column(Integer, nullable=False)  # Which attempt this is
    status = Column(SQLEnum(JobStatus), nullable=False)
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    metadata = Column(Text, nullable=True)  # JSON string for additional data
    
    def __repr__(self):
        return f"<JobExecutionLog(job_id={self.job_id}, attempt={self.execution_number}, status='{self.status}')>"


class CronSchedule(Base):
    """Recurring cron schedule definitions."""
    __tablename__ = "cron_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    job_type = Column(SQLEnum(JobType), nullable=False)
    cron_expression = Column(String(100), nullable=False)  # e.g., "0 * * * *" (every hour)
    payload_template = Column(Text, nullable=False)  # JSON template for job payload
    is_active = Column(Boolean, default=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CronSchedule(name='{self.name}', cron='{self.cron_expression}')>"


class RecoveryTask(Base):
    """Auto-click recovery task for banned WhatsApp accounts."""
    __tablename__ = "recovery_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, nullable=False)  # WhatsApp account ID
    recovery_url = Column(String(500), nullable=False)
    auto_click_enabled = Column(Boolean, default=True)
    click_delay_seconds = Column(Integer, default=3)
    retry_count = Column(Integer, default=3)
    attempts_made = Column(Integer, default=0)
    status = Column(String(20), default="pending")  # pending, clicking, success, failed, expired
    expires_at = Column(DateTime, nullable=False)
    last_attempt_at = Column(DateTime, nullable=True)
    success_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<RecoveryTask(account_id={self.account_id}, status='{self.status}')>"
