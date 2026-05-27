from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()


class UserRole(enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    TRIAL = "trial"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.TRIAL, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    whatsapp_accounts = relationship("WhatsAppAccount", back_populates="user", cascade="all, delete-orphan")
    token_balance = relationship("TokenBalance", back_populates="user", uselist=False, cascade="all, delete-orphan")
    token_transactions = relationship("TokenTransaction", back_populates="user", cascade="all, delete-orphan")
    blast_campaigns = relationship("BlastCampaign", back_populates="user", cascade="all, delete-orphan")
    auto_replies = relationship("AutoReply", back_populates="user", cascade="all, delete-orphan")
    followups = relationship("FollowUp", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")


class WhatsAppAccount(Base):
    __tablename__ = "whatsapp_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    session_id = Column(String(255), unique=True, nullable=False)
    status = Column(String(50), default="disconnected")  # disconnected, connected, banned, warming
    is_warming = Column(Boolean, default=False)
    warming_day = Column(Integer, default=0)
    warming_started_at = Column(DateTime, nullable=True)
    last_active = Column(DateTime, nullable=True)
    recovery_link = Column(String(500), nullable=True)
    auto_click_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="whatsapp_accounts")
    warmup_logs = relationship("WarmupLog", back_populates="whatsapp_account", cascade="all, delete-orphan")


class WarmupLog(Base):
    __tablename__ = "warmup_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    whatsapp_account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"), nullable=False)
    day = Column(Integer, nullable=False)
    messages_sent = Column(Integer, default=0)
    messages_received = Column(Integer, default=0)
    status = Column(String(50), default="pending")  # pending, completed, failed
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    whatsapp_account = relationship("WhatsAppAccount", back_populates="warmup_logs")


class TokenBalance(Base):
    __tablename__ = "token_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="token_balance")


class TokenTransaction(Base):
    __tablename__ = "token_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)  # Can be positive (credit) or negative (debit)
    transaction_type = Column(String(50), nullable=False)  # purchase, usage, transfer, refund
    description = Column(Text, nullable=True)
    reference_id = Column(String(255), nullable=True)  # Reference to payment, AI usage, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="token_transactions")


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    tokens_purchased = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=True)  # stripe, paypal, crypto, etc.
    payment_status = Column(String(50), default="pending")  # pending, completed, failed, refunded
    transaction_id = Column(String(255), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="payments")


class BlastCampaign(Base):
    __tablename__ = "blast_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    media_url = Column(String(500), nullable=True)  # For image/video attachments
    media_type = Column(String(50), nullable=True)  # image, video, document
    recipient_count = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    status = Column(String(50), default="draft")  # draft, scheduled, sending, completed, cancelled
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="blast_campaigns")
    recipients = relationship("BlastRecipient", back_populates="campaign", cascade="all, delete-orphan")


class BlastRecipient(Base):
    __tablename__ = "blast_recipients"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("blast_campaigns.id"), nullable=False)
    phone_number = Column(String(20), nullable=False)
    contact_name = Column(String(255), nullable=True)
    status = Column(String(50), default="pending")  # pending, sent, delivered, failed
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = relationship("BlastCampaign", back_populates="recipients")


class AutoReply(Base):
    __tablename__ = "auto_replies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    whatsapp_account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"), nullable=True)
    trigger_keyword = Column(String(255), nullable=True)  # If null, matches all messages
    response_message = Column(Text, nullable=False)
    use_ai = Column(Boolean, default=False)
    ai_model = Column(String(100), nullable=True)  # e.g., "gpt-3.5-turbo", "gpt-4"
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher priority rules execute first
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="auto_replies")


class FollowUp(Base):
    __tablename__ = "followups"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    whatsapp_account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"), nullable=False)
    contact_phone = Column(String(20), nullable=False)
    contact_name = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    media_url = Column(String(500), nullable=True)
    media_type = Column(String(50), nullable=True)
    status = Column(String(50), default="pending")  # pending, sent, completed, cancelled
    scheduled_at = Column(DateTime, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="followups")


class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    whatsapp_account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"), nullable=True)
    input_message = Column(Text, nullable=False)
    output_message = Column(Text, nullable=False)
    model_used = Column(String(100), nullable=False)
    tokens_consumed = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
