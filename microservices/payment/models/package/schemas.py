"""Token Package Schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TokenPackageCreate(BaseModel):
    """Serializer for creating token package"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    tokens_included: int = Field(..., gt=0)
    base_price: float = Field(..., gt=0)
    sell_price: float = Field(..., gt=0)
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
