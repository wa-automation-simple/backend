"""Token Transaction Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from payment.modules.transaction.enums import PaymentStatus


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
    status: PaymentStatus
    description: Optional[str]
    created_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True


class TokenTopup(BaseModel):
    """Serializer for token top-up request"""
    package_id: Optional[int] = None
    custom_amount: Optional[int] = Field(None, gt=0)
    payment_method: str = Field(default="stripe", pattern="^(stripe|paypal|bank_transfer)$")


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
    status: PaymentStatus
    payment_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
