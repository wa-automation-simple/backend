"""
SQLAlchemy models for the application
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    whatsapp_accounts = relationship("WhatsAppAccount", back_populates="user")
    token_balance = relationship("TokenBalance", back_populates="user", uselist=False)
    transactions = relationship("Transaction", back_populates="user")


class WhatsAppAccount(Base):
    """WhatsApp account model for multi-account support"""
    __tablename__ = "whatsapp_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    session_id = Column(String, unique=True)
    status = Column(String, default="disconnected")  # disconnected, connected, banned, warming
    is_warming = Column(Boolean, default=False)
    warming_level = Column(Integer, default=0)  # 1-10 scale
    last_active = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="whatsapp_accounts")
    campaigns = relationship("BlastCampaign", back_populates="whatsapp_account")


class TokenBalance(Base):
    """Token balance for AI usage"""
    __tablename__ = "token_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Float, default=0.0)  # Balance in dollars
    tokens_used = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="token_balance")


class Transaction(Base):
    """Payment transaction history"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    tokens_purchased = Column(Float, nullable=False)
    payment_method = Column(String)
    status = Column(String, default="pending")  # pending, completed, failed
    transaction_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="transactions")


class BlastCampaign(Base):
    """Bulk messaging campaign"""
    __tablename__ = "blast_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    whatsapp_account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"), nullable=False)
    name = Column(String, nullable=False)
    message_text = Column(Text, nullable=False)
    media_url = Column(String)  # Image/video URL
    media_type = Column(String)  # image, video, document
    recipients = Column(JSON)  # List of phone numbers
    scheduled_at = Column(DateTime(timezone=True))
    status = Column(String, default="draft")  # draft, scheduled, sending, completed, failed
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    whatsapp_account = relationship("WhatsAppAccount", back_populates="campaigns")


class AutoReply(Base):
    """Auto-reply configuration"""
    __tablename__ = "auto_replies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    whatsapp_account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"))
    trigger_keyword = Column(String)  # Keyword to trigger reply
    reply_message = Column(Text)
    use_ai = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FollowUp(Base):
    """Member follow-up tracking"""
    __tablename__ = "follow_ups"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    whatsapp_account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"))
    contact_phone = Column(String, nullable=False)
    contact_name = Column(String)
    last_interaction = Column(DateTime(timezone=True))
    next_follow_up = Column(DateTime(timezone=True))
    follow_up_count = Column(Integer, default=0)
    notes = Column(Text)
    status = Column(String, default="pending")  # pending, completed, skipped
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WarmingSchedule(Base):
    """WhatsApp warming schedule"""
    __tablename__ = "warming_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    whatsapp_account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"), nullable=False)
    day = Column(Integer)  # Day number (1-30)
    messages_per_day = Column(Integer)
    min_delay_seconds = Column(Integer)
    max_delay_seconds = Column(Integer)
    is_active = Column(Boolean, default=True)
