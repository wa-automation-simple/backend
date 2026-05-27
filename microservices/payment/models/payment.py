"""Payment and Token Models"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from payment.core.database import Base


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class TokenType(enum.Enum):
    ONE_TIME = "one_time"
    SUBSCRIPTION = "subscription"
    BULK_PACKAGE = "bulk_package"


class TokenWallet(Base):
    __tablename__ = "token_wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, unique=True, index=True)
    
    # Balance tracking
    balance = Column(Integer, default=0)  # Number of tokens
    reserved_tokens = Column(Integer, default=0)  # Tokens reserved for pending operations
    
    # Pricing tier
    price_per_token = Column(Float, default=10.0)  # Markup price
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TokenWallet(user_id={self.user_id}, balance={self.balance})>"


class TokenTransaction(Base):
    __tablename__ = "token_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    wallet_id = Column(Integer, ForeignKey("token_wallets.id"), nullable=False)
    
    # Transaction details
    transaction_type = Column(String(50), nullable=False)  # purchase, usage, refund, transfer
    tokens_amount = Column(Integer, nullable=False)
    unit_price = Column(Float, default=10.0)
    total_amount = Column(Float, nullable=False)  # In USD
    
    # Payment reference
    payment_id = Column(String(255), nullable=True)  # External payment gateway ID
    payment_method = Column(String(50))  # stripe, paypal, bank_transfer
    
    # Token package info
    package_name = Column(String(100), nullable=True)  # e.g., "Starter Pack", "Pro Pack"
    bonus_tokens = Column(Integer, default=0)  # Bonus tokens from promotions
    
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    description = Column(Text, nullable=True)
    
    # AI usage tracking
    ai_reply_id = Column(Integer, nullable=True)  # Reference to AI reply that used tokens
    tokens_used_for_ai = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<TokenTransaction(id={self.id}, type={self.transaction_type}, amount={self.tokens_amount})>"


class TokenPackage(Base):
    __tablename__ = "token_packages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    
    # Package details
    tokens_included = Column(Integer, nullable=False)
    base_price = Column(Float, nullable=False)  # $3 per token base
    sell_price = Column(Float, nullable=False)  # Markup price (e.g., $10 per token)
    discount_percentage = Column(Float, default=0.0)  # Bulk discount
    
    # Bonus
    bonus_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, nullable=False)  # tokens_included + bonus_tokens
    
    is_active = Column(Boolean, default=True)
    is_popular = Column(Boolean, default=False)  # Mark as recommended
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<TokenPackage(name={self.name}, tokens={self.total_tokens})>"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    wallet_id = Column(Integer, ForeignKey("token_wallets.id"), nullable=False)
    
    # Subscription details
    plan_name = Column(String(100), nullable=False)
    tokens_per_month = Column(Integer, nullable=False)
    monthly_price = Column(Float, nullable=False)
    
    # Billing
    billing_cycle_start = Column(DateTime, nullable=False)
    next_billing_date = Column(DateTime, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    cancel_at_period_end = Column(Boolean, default=False)
    
    # Payment gateway subscription ID
    gateway_subscription_id = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Subscription(user_id={self.user_id}, plan={self.plan_name})>"
