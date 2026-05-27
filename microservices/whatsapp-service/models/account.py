"""
WhatsApp Service Database Models
Dedicated database for WhatsApp accounts, warmup, and sessions
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class AccountStatus(enum.Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    BANNED = "banned"
    WARMING_UP = "warming_up"
    RECOVERY = "recovery"


class WhatsAppAccount(Base):
    """WhatsApp account model."""
    __tablename__ = "whatsapp_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Reference to auth service user
    phone_number = Column(String(20), unique=True, nullable=False)
    device_name = Column(String(100), nullable=True)
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.DISCONNECTED)
    is_primary = Column(Boolean, default=False)
    session_data = Column(Text, nullable=True)  # Encrypted session data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = Column(DateTime, nullable=True)
    banned_at = Column(DateTime, nullable=True)
    
    # Relationships
    warmup_sessions = relationship("WarmupSession", back_populates="account", cascade="all, delete-orphan")
    recovery_links = relationship("RecoveryLink", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WhatsAppAccount(id={self.id}, phone='{self.phone_number}', status='{self.status}')>"


class WarmupStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"


class WarmupSession(Base):
    """Warmup session model for gradual account warming."""
    __tablename__ = "warmup_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"), nullable=False)
    current_day = Column(Integer, default=1, nullable=False)
    total_days = Column(Integer, default=30, nullable=False)
    daily_limit = Column(Integer, default=10, nullable=False)
    messages_sent_today = Column(Integer, default=0, nullable=False)
    status = Column(SQLEnum(WarmupStatus), default=WarmupStatus.NOT_STARTED)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    account = relationship("WhatsAppAccount", back_populates="warmup_sessions")
    
    def __repr__(self):
        return f"<WarmupSession(account_id={self.account_id}, day={self.current_day}/{self.total_days})>"


class RecoveryLink(Base):
    """Recovery link for banned accounts with auto-click feature."""
    __tablename__ = "recovery_links"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"), nullable=False)
    recovery_url = Column(String(500), nullable=False)
    auto_click_enabled = Column(Boolean, default=True)
    click_delay_seconds = Column(Integer, default=3)
    retry_count = Column(Integer, default=3)
    clicks_attempted = Column(Integer, default=0)
    status = Column(String(20), default="active")  # active, clicked, expired
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    clicked_at = Column(DateTime, nullable=True)
    
    # Relationship
    account = relationship("WhatsAppAccount", back_populates="recovery_links")
    
    def __repr__(self):
        return f"<RecoveryLink(account_id={self.account_id}, status='{self.status}')>"
