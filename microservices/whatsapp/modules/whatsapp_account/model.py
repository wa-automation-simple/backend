"""WhatsAppAccount module - Auto-generated."""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from whatsapp.core.database import Base


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


