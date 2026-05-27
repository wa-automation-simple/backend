"""Schemas/Serializers for WhatsApp Service."""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AccountStatus(str, Enum):
    """WhatsApp account status."""
    ACTIVE = "active"
    WARMING_UP = "warming_up"
    BANNED = "banned"
    RECOVERING = "recovering"
    DISCONNECTED = "disconnected"


class WhatsAppAccountCreate(BaseModel):
    """Schema for creating WhatsApp account."""
    
    phone_number: str = Field(..., min_length=10, max_length=20)
    display_name: Optional[str] = Field(None, max_length=100)
    is_primary: bool = False
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if not v.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValueError("Phone number must contain only digits")
        return v


class WhatsAppAccountResponse(BaseModel):
    """Schema for WhatsApp account response."""
    
    id: int
    user_id: int
    phone_number: str
    display_name: Optional[str]
    status: AccountStatus
    is_primary: bool
    connected_at: Optional[datetime]
    last_active: Optional[datetime]
    total_messages_sent: int
    messages_today: int
    
    class Config:
        from_attributes = True


class WarmupStart(BaseModel):
    """Schema for starting warmup."""
    
    total_days: int = Field(default=30, ge=7, le=90)
    day_1_limit: int = Field(default=5, ge=1, le=20)
    daily_increment: int = Field(default=3, ge=1, le=10)
    max_daily_limit: int = Field(default=100, ge=50, le=500)


class WarmupStatus(BaseModel):
    """Schema for warmup status response."""
    
    account_id: int
    current_day: int
    total_days: int
    today_limit: int
    messages_sent_today: int
    is_active: bool
    is_completed: bool
    start_date: datetime
    end_date: Optional[datetime]


class QRCodeResponse(BaseModel):
    """Schema for QR code response."""
    
    account_id: int
    qr_code: str  # Base64 encoded
    expires_in: int  # Seconds


class RecoveryLinkResponse(BaseModel):
    """Schema for recovery link response."""
    
    account_id: int
    recovery_link: str
    auto_click_enabled: bool
