"""WhatsApp Account model for managing multiple WA accounts."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from whatsapp.core.database import Base


class AccountStatus(str, enum.Enum):
    """WhatsApp account status."""
    ACTIVE = "active"
    BANNED = "banned"
    DISCONNECTED = "disconnected"
    WARMING_UP = "warming_up"
    READY = "ready"


class WhatsAppAccount(Base):
    """WhatsApp Account table for multi-account support."""
    
    __tablename__ = "whatsapp_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Reference to auth service user
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    account_name = Column(String(100), nullable=True)
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.DISCONNECTED, nullable=False)
    session_data = Column(Text, nullable=True)  # Encrypted session data
    is_primary = Column(Boolean, default=False, nullable=False)
    last_active = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    warmup_schedule = relationship("WarmupSchedule", back_populates="account", uselist=False, cascade="all, delete-orphan")
    messages = relationship("MessageLog", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WhatsAppAccount(id={self.id}, phone='{self.phone_number}', status='{self.status}')>"


class WarmupSchedule(Base):
    """Warmup schedule for gradually increasing message limits."""
    
    __tablename__ = "warmup_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"), unique=True, nullable=False)
    day = Column(Integer, default=1, nullable=False)  # Day 1-30
    daily_limit = Column(Integer, default=10, nullable=False)  # Messages per day
    interval_min = Column(Integer, default=300, nullable=False)  # Min interval in seconds
    interval_max = Column(Integer, default=600, nullable=False)  # Max interval in seconds
    is_completed = Column(Boolean, default=False, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    account = relationship("WhatsAppAccount", back_populates="warmup_schedule")
    
    def __repr__(self):
        return f"<WarmupSchedule(account_id={self.account_id}, day={self.day}, limit={self.daily_limit})>"


class MessageLog(Base):
    """Log of all sent/received messages."""
    
    __tablename__ = "message_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"), nullable=False, index=True)
    recipient = Column(String(20), nullable=False, index=True)
    message_type = Column(String(20), default="text", nullable=False)  # text, image, video, etc.
    content = Column(Text, nullable=True)
    media_url = Column(String(500), nullable=True)
    status = Column(String(20), default="pending", nullable=False)  # pending, sent, delivered, read, failed
    error_message = Column(Text, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    account = relationship("WhatsAppAccount", back_populates="messages")
    
    def __repr__(self):
        return f"<MessageLog(id={self.id}, recipient='{self.recipient}', status='{self.status}')>"
