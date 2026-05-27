"""
AI Service Database Models
Dedicated database for tokens, transactions, and auto-reply configurations
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()


class TokenType(enum.Enum):
    PURCHASED = "purchased"
    BONUS = "bonus"
    REFUNDED = "refunded"


class TokenWallet(Base):
    """User token wallet for AI features."""
    __tablename__ = "token_wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, nullable=False, index=True)  # Reference to auth service user
    balance = Column(Float, default=0.0, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_transaction_at = Column(DateTime, nullable=True)
    
    # Relationships
    transactions = relationship("TokenTransaction", back_populates="wallet", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<TokenWallet(user_id={self.user_id}, balance={self.balance} {self.currency})>"


class TransactionType(enum.Enum):
    PURCHASE = "purchase"
    USAGE = "usage"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"


class TokenTransaction(Base):
    """Token transaction history."""
    __tablename__ = "token_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("token_wallets.id"), nullable=False)
    type = Column(SQLEnum(TransactionType), nullable=False)
    amount = Column(Float, nullable=False)  # Positive for credit, negative for debit
    balance_after = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    metadata = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationship
    wallet = relationship("TokenWallet", back_populates="transactions")
    
    def __repr__(self):
        return f"<TokenTransaction(id={self.id}, type='{self.type}', amount={self.amount})>"


class AutoReplyConfig(Base):
    """Auto-reply configuration with AI support."""
    __tablename__ = "auto_reply_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    account_id = Column(Integer, nullable=False)  # WhatsApp account ID
    trigger_keywords = Column(Text, nullable=False)  # JSON array of keywords
    response_template = Column(Text, nullable=True)  # Static response template
    use_ai = Column(Boolean, default=False, nullable=False)
    ai_personality = Column(Text, nullable=True)  # AI personality description
    ai_context = Column(Text, nullable=True)  # Additional context for AI
    is_active = Column(Boolean, default=True, nullable=False)
    priority = Column(Integer, default=1)  # For multiple configs, higher priority first
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_triggered_at = Column(DateTime, nullable=True)
    trigger_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<AutoReplyConfig(user_id={self.user_id}, use_ai={self.use_ai}, active={self.is_active})>"


class AIUsageLog(Base):
    """AI usage logging for tracking and billing."""
    __tablename__ = "ai_usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    account_id = Column(Integer, nullable=False)
    request_message = Column(Text, nullable=False)
    response_message = Column(Text, nullable=False)
    tokens_used = Column(Integer, nullable=False)
    cost = Column(Float, nullable=False)
    model_used = Column(String(50), nullable=False)
    processing_time_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<AIUsageLog(user_id={self.user_id}, tokens={self.tokens_used}, cost={self.cost})>"
