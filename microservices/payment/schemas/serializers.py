"""Django-like Serializers for Payment Service"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PaymentStatusEnum(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class TokenPackageCreate(BaseModel):
    """Serializer for creating token package"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    tokens_included: int = Field(..., gt=0)
    base_price: float = Field(..., gt=0)  # $3 per token
    sell_price: float = Field(..., gt=0)  # Markup price
    discount_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    bonus_tokens: int = Field(default=0, ge=0)
    is_popular: bool = Field(default=False)


class TokenPackageResponse(BaseModel):
    """Serializer for token package response"""
    id: int
    name: str
    description: str
    tokens_included: int
    base_price: float
    sell_price: float
    discount_percentage: float
    bonus_tokens: int
    total_tokens: int
    is_active: bool
    is_popular: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TokenTopup(BaseModel):
    """Serializer for token top-up request"""
    package_id: Optional[int] = None
    custom_amount: Optional[int] = Field(None, gt=0)
    payment_method: str = Field(default="stripe", pattern="^(stripe|paypal|bank_transfer)$")

    @validator('custom_amount')
    def validate_custom_amount(cls, v, values):
        if v is None and values.get('package_id') is None:
            raise ValueError("Either package_id or custom_amount must be provided")
        return v


class TokenBalanceResponse(BaseModel):
    """Serializer for token balance response"""
    user_id: int
    balance: int
    reserved_tokens: int
    available_tokens: int
    price_per_token: float
    estimated_value_usd: float


class TokenTransactionResponse(BaseModel):
    """Serializer for token transaction response"""
    id: int
    user_id: int
    transaction_type: str
    tokens_amount: int
    unit_price: float
    total_amount: float
    payment_id: Optional[str]
    payment_method: Optional[str]
    package_name: Optional[str]
    bonus_tokens: int
    status: PaymentStatusEnum
    description: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    """Serializer for creating payment"""
    package_id: Optional[int] = None
    amount: Optional[float] = Field(None, gt=0)
    payment_method: str = Field(default="stripe", pattern="^(stripe|paypal|bank_transfer)$")
    description: Optional[str] = Field(None, max_length=500)


class PaymentResponse(BaseModel):
    """Serializer for payment response"""
    id: int
    user_id: int
    transaction_id: int
    amount: float
    payment_method: str
    status: PaymentStatusEnum
    payment_url: Optional[str]  # For redirect to payment gateway
    created_at: datetime

    class Config:
        from_attributes = True


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
