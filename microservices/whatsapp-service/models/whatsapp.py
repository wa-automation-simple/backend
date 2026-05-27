from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class WhatsAppAccount(Base):
    __tablename__ = "whatsapp_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)  # Denormalized from auth service
    phone_number = Column(String(20), nullable=False)
    session_id = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), default="disconnected")
    is_warming = Column(Boolean, default=False)
    warming_day = Column(Integer, default=0)
    warming_started_at = Column(DateTime, nullable=True)
    last_active = Column(DateTime, nullable=True)
    recovery_link = Column(String(500), nullable=True)
    auto_click_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WarmupLog(Base):
    __tablename__ = "warmup_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    whatsapp_account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"), nullable=False)
    day = Column(Integer, nullable=False)
    messages_sent = Column(Integer, default=0)
    messages_received = Column(Integer, default=0)
    status = Column(String(50), default="pending")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
