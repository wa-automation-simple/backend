"""
Shared SQLAlchemy models for all microservices
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from shared.utils.database import Base
from shared.models.rbac import Role

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    role = Column(SQLEnum(Role), default=Role.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    whatsapp_accounts = relationship("WhatsAppAccount", back_populates="user")
    tokens = relationship("TokenBalance", back_populates="user")
    blast_campaigns = relationship("BlastCampaign", back_populates="user")
    auto_replies = relationship("AutoReply", back_populates="user")
    followups = relationship("FollowUp", back_populates="user")
    payments = relationship("Payment", back_populates="user")


class WhatsAppAccount(Base):
    __tablename__ = "whatsapp_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    session_id = Column(String, unique=True)
    status = Column(String, default="disconnected")  # disconnected, connected, banned, warming
    is_warming = Column(Boolean, default=False)
    warmup_day = Column(Integer, default=0)
    warmup_started_at = Column(DateTime(timezone=True))
    auto_click_recovery = Column(Boolean, default=False)
    recovery_link = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="whatsapp_accounts")


class TokenBalance(Base):
    __tablename__ = "token_balances"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    balance = Column(Float, default=0.0)
    total_purchased = Column(Float, default=0.0)
    total_used = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="tokens")
    transactions = relationship("TokenTransaction", back_populates="token_balance")


class TokenTransaction(Base):
    __tablename__ = "token_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    token_balance_id = Column(Integer, ForeignKey("token_balances.id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String)  # purchase, usage, refund
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    token_balance = relationship("TokenBalance", back_populates="transactions")


class BlastCampaign(Base):
    __tablename__ = "blast_campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    media_url = Column(String, nullable=True)
    media_type = Column(String, nullable=True)  # image, video, document
    recipient_list = Column(JSON)  # List of phone numbers or contact IDs
    status = Column(String, default="draft")  # draft, scheduled, sending, completed, failed
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="blast_campaigns")


class AutoReply(Base):
    __tablename__ = "auto_replies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    whatsapp_account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"), nullable=True)
    trigger_keyword = Column(String, nullable=True)  # If null, matches all
    response_message = Column(Text, nullable=False)
    use_ai = Column(Boolean, default=False)
    ai_context = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="auto_replies")


class FollowUp(Base):
    __tablename__ = "followups"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    whatsapp_account_id = Column(Integer, ForeignKey("whatsapp_accounts.id"), nullable=False)
    contact_phone = Column(String, nullable=False)
    contact_name = Column(String, nullable=True)
    message = Column(Text, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String, default="pending")  # pending, sent, failed, skipped
    notes = Column(Text, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="followups")


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    payment_method = Column(String)  # stripe, paypal, crypto
    status = Column(String, default="pending")  # pending, completed, failed, refunded
    tokens_purchased = Column(Float, default=0.0)
    transaction_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="payments")


class WarmupSchedule(Base):
    __tablename__ = "warmup_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    day = Column(Integer, nullable=False)
    messages_min = Column(Integer, nullable=False)
    messages_max = Column(Integer, nullable=False)
    delay_min_seconds = Column(Integer, nullable=False)
    delay_max_seconds = Column(Integer, nullable=False)
    
    __table_args__ = (
        {'sqlite_autoincrement': True}
    )
