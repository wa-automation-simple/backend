"""Subscription Model"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from datetime import datetime
from payment.core.database import Base


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
