"""Subscription Schemas"""
from pydantic import BaseModel, Field
from datetime import datetime


class SubscriptionCreate(BaseModel):
    """Serializer for creating subscription"""
    plan_name: str = Field(..., min_length=3, max_length=100)
    tokens_per_month: int = Field(..., gt=0)
    monthly_price: float = Field(..., gt=0)


class SubscriptionResponse(BaseModel):
    """Serializer for subscription response"""
    id: int
    user_id: int
    plan_name: str
    tokens_per_month: int
    monthly_price: float
    billing_cycle_start: datetime
    next_billing_date: datetime
    is_active: bool
    cancel_at_period_end: bool
    created_at: datetime

    class Config:
        from_attributes = True
