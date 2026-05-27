"""WhatsApp Account model."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..core.database import Base


class AccountStatus(enum.Enum):
    """WhatsApp account status."""
    ACTIVE = "active"
    WARMING_UP = "warming_up"
    BANNED = "banned"
    RECOVERING = "recovering"
    DISCONNECTED = "disconnected"


class WhatsAppAccount(Base):
    """WhatsApp account table model."""
    
    __tablename__ = "whatsapp_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # Reference to auth-service user
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=True)
    profile_picture_url = Column(String(500), nullable=True)
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.DISCONNECTED, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    
    # Session info
    session_id = Column(String(255), unique=True, nullable=True)
    qr_code = Column(String(5000), nullable=True)  # Base64 encoded QR
    connected_at = Column(DateTime, nullable=True)
    last_active = Column(DateTime, nullable=True)
    
    # Stats
    total_messages_sent = Column(Integer, default=0, nullable=False)
    messages_today = Column(Integer, default=0, nullable=False)
    last_message_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    warmup_schedule = relationship("WarmupSchedule", back_populates="account", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<WhatsAppAccount(id={self.id}, phone={self.phone_number}, status={self.status})>"


class WarmupSchedule(Base):
    """Warmup schedule for gradual message increase."""
    
    __tablename__ = "warmup_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"), unique=True, nullable=False)
    
    # Schedule settings
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    total_days = Column(Integer, default=30, nullable=False)
    current_day = Column(Integer, default=0, nullable=False)
    
    # Daily limits
    day_1_limit = Column(Integer, default=5, nullable=False)
    daily_increment = Column(Integer, default=3, nullable=False)
    max_daily_limit = Column(Integer, default=100, nullable=False)
    
    # Current state
    today_limit = Column(Integer, default=5, nullable=False)
    messages_sent_today = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    account = relationship("WhatsAppAccount", back_populates="warmup_schedule")
    
    def __repr__(self):
        return f"<WarmupSchedule(account_id={self.account_id}, day={self.current_day})>"
