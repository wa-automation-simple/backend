"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None


# WhatsApp Account Schemas
class WhatsAppAccountBase(BaseModel):
    phone_number: str


class WhatsAppAccountCreate(WhatsAppAccountBase):
    pass


class WhatsAppAccountResponse(WhatsAppAccountBase):
    id: int
    user_id: int
    session_id: Optional[str]
    status: str
    is_warming: bool
    warming_level: int
    last_active: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Token Balance Schemas
class TokenBalanceResponse(BaseModel):
    id: int
    user_id: int
    balance: float
    tokens_used: float
    last_updated: datetime
    
    class Config:
        from_attributes = True


# Payment Schemas
class TopUpRequest(BaseModel):
    amount: float = Field(..., gt=0)
    payment_method: str


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    tokens_purchased: float
    payment_method: str
    status: str
    transaction_date: datetime
    
    class Config:
        from_attributes = True


# Blast Campaign Schemas
class BlastCampaignBase(BaseModel):
    name: str
    message_text: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    recipients: List[str]
    scheduled_at: Optional[datetime] = None


class BlastCampaignCreate(BlastCampaignBase):
    whatsapp_account_id: int


class BlastCampaignResponse(BlastCampaignBase):
    id: int
    user_id: int
    whatsapp_account_id: int
    status: str
    sent_count: int
    delivered_count: int
    failed_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# AI Auto-Reply Schemas
class AutoReplyBase(BaseModel):
    trigger_keyword: Optional[str] = None
    reply_message: Optional[str] = None
    use_ai: bool = False
    is_active: bool = True


class AutoReplyCreate(AutoReplyBase):
    whatsapp_account_id: Optional[int] = None


class AutoReplyResponse(AutoReplyBase):
    id: int
    user_id: int
    whatsapp_account_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AIRequest(BaseModel):
    message: str
    context: Optional[str] = None
    max_tokens: int = 100


class AIResponse(BaseModel):
    response: str
    tokens_used: int
    cost: float


# Follow-up Schemas
class FollowUpBase(BaseModel):
    contact_phone: str
    contact_name: Optional[str] = None
    notes: Optional[str] = None
    next_follow_up: Optional[datetime] = None


class FollowUpCreate(FollowUpBase):
    whatsapp_account_id: Optional[int] = None


class FollowUpResponse(FollowUpBase):
    id: int
    user_id: int
    whatsapp_account_id: Optional[int]
    last_interaction: Optional[datetime]
    follow_up_count: int
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Warming Schedule Schemas
class WarmingScheduleBase(BaseModel):
    day: int
    messages_per_day: int
    min_delay_seconds: int
    max_delay_seconds: int
    is_active: bool = True


class WarmingScheduleCreate(WarmingScheduleBase):
    whatsapp_account_id: int


class WarmingScheduleResponse(WarmingScheduleBase):
    id: int
    whatsapp_account_id: int
    
    class Config:
        from_attributes = True


# Message Schemas
class MessageSend(BaseModel):
    whatsapp_account_id: int
    recipient: str
    message: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None


class MessageResponse(BaseModel):
    success: bool
    message_id: Optional[str]
    status: str
