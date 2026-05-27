"""Pydantic schemas for WhatsApp service request/response validation."""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AccountStatus(str, Enum):
    """WhatsApp account status."""
    ACTIVE = "active"
    BANNED = "banned"
    DISCONNECTED = "disconnected"
    WARMING_UP = "warming_up"
    READY = "ready"


# ==================== Account Schemas ====================

class WhatsAppAccountBase(BaseModel):
    """Base schema for WhatsApp account."""
    phone_number: str = Field(..., min_length=10, max_length=20)
    account_name: Optional[str] = Field(None, max_length=100)


class WhatsAppAccountCreate(WhatsAppAccountBase):
    """Schema for creating a new WhatsApp account."""
    user_id: int
    is_primary: bool = False


class WhatsAppAccountUpdate(BaseModel):
    """Schema for updating WhatsApp account."""
    account_name: Optional[str] = Field(None, max_length=100)
    is_primary: Optional[bool] = None
    status: Optional[AccountStatus] = None


class WhatsAppAccountResponse(WhatsAppAccountBase):
    """Schema for WhatsApp account response."""
    id: int
    user_id: int
    status: AccountStatus
    is_primary: bool
    last_active: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Warmup Schemas ====================

class WarmupScheduleBase(BaseModel):
    """Base schema for warmup schedule."""
    daily_limit: int = Field(..., ge=5, le=1000)
    interval_min: int = Field(..., ge=60, le=3600)
    interval_max: int = Field(..., ge=120, le=7200)


class WarmupStart(BaseModel):
    """Schema for starting warmup process."""
    account_id: int
    duration_days: int = Field(default=30, ge=7, le=30)


class WarmupScheduleResponse(WarmupScheduleBase):
    """Schema for warmup schedule response."""
    id: int
    account_id: int
    day: int
    is_completed: bool
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class WarmupStatusResponse(BaseModel):
    """Schema for warmup status."""
    account_id: int
    current_day: int
    total_days: int
    daily_limit: int
    messages_sent_today: int
    is_completed: bool
    progress_percentage: float


# ==================== Message Schemas ====================

class MessageSendBase(BaseModel):
    """Base schema for sending messages."""
    recipient: str = Field(..., min_length=10, max_length=20)
    content: str = Field(..., min_length=1, max_length=4096)


class MessageSendRequest(MessageSendBase):
    """Schema for sending a text message."""
    account_id: int


class MessageSendWithMedia(BaseModel):
    """Schema for sending message with media."""
    account_id: int
    recipient: str = Field(..., min_length=10, max_length=20)
    content: Optional[str] = Field(None, max_length=4096)
    media_url: HttpUrl
    media_type: str = Field(default="image", pattern="^(image|video|audio|document)$")


class MessageLogResponse(BaseModel):
    """Schema for message log response."""
    id: int
    account_id: int
    recipient: str
    message_type: str
    content: Optional[str] = None
    media_url: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== Response Wrappers ====================

class AccountsListResponse(BaseModel):
    """Schema for listing accounts with pagination."""
    accounts: List[WhatsAppAccountResponse]
    total: int
    page: int
    page_size: int


class MessagesListResponse(BaseModel):
    """Schema for listing messages with pagination."""
    messages: List[MessageLogResponse]
    total: int
    page: int
    page_size: int
