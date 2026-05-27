"""
Pydantic schemas for request/response validation (like Django serializers)
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from shared.models.rbac import Role


# ============== USER SCHEMAS ==============

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: Role = Role.USER


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[Role] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== AUTH SCHEMAS ==============

class TokenRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


# ============== WHATSAPP ACCOUNT SCHEMAS ==============

class WhatsAppAccountBase(BaseModel):
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')


class WhatsAppAccountCreate(WhatsAppAccountBase):
    pass


class WhatsAppAccountUpdate(BaseModel):
    auto_click_recovery: Optional[bool] = None
    recovery_link: Optional[str] = None


class WhatsAppAccountResponse(WhatsAppAccountBase):
    id: int
    user_id: int
    status: str
    is_warming: bool
    warmup_day: int
    warmup_started_at: Optional[datetime]
    auto_click_recovery: bool
    recovery_link: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class WarmupStart(BaseModel):
    whatsapp_account_id: int


class WarmupStatus(BaseModel):
    whatsapp_account_id: int
    is_warming: bool
    current_day: int
    total_days: int
    messages_sent_today: int
    next_message_at: Optional[datetime]


# ============== BLAST CAMPAIGN SCHEMAS ==============

class BlastCampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1)
    recipient_list: List[str]


class BlastCampaignCreate(BlastCampaignBase):
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class BlastCampaignUpdate(BaseModel):
    name: Optional[str] = None
    message: Optional[str] = None
    recipient_list: Optional[List[str]] = None
    media_url: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class BlastCampaignResponse(BlastCampaignBase):
    id: int
    user_id: int
    media_url: Optional[str]
    media_type: Optional[str]
    status: str
    scheduled_at: Optional[datetime]
    sent_count: int
    delivered_count: int
    failed_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class MediaUpload(BaseModel):
    file_type: str  # image, video, document
    file_name: str
    file_size: int


class MediaUploadResponse(BaseModel):
    media_url: str
    media_type: str
    file_name: str
    file_size: int


# ============== AUTO REPLY SCHEMAS ==============

class AutoReplyBase(BaseModel):
    trigger_keyword: Optional[str] = None
    response_message: str = Field(..., min_length=1)
    use_ai: bool = False
    ai_context: Optional[str] = None
    priority: int = Field(default=0, ge=0, le=100)


class AutoReplyCreate(AutoReplyBase):
    whatsapp_account_id: Optional[int] = None


class AutoReplyUpdate(BaseModel):
    trigger_keyword: Optional[str] = None
    response_message: Optional[str] = None
    use_ai: Optional[bool] = None
    ai_context: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class AutoReplyResponse(AutoReplyBase):
    id: int
    user_id: int
    whatsapp_account_id: Optional[int]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== AI TOKEN SCHEMAS ==============

class TokenTopup(BaseModel):
    amount: float = Field(..., gt=0)
    payment_method: str


class TokenBalanceResponse(BaseModel):
    user_id: int
    balance: float
    total_purchased: float
    total_used: float
    base_price_per_token: float = 3.0
    sell_price_per_token: float = 10.0
    
    class Config:
        from_attributes = True


class TokenTransactionResponse(BaseModel):
    id: int
    amount: float
    transaction_type: str
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AIRequest(BaseModel):
    message: str
    context: Optional[str] = None
    conversation_history: Optional[List[Dict[str, str]]] = None


class AIResponse(BaseModel):
    response: str
    tokens_used: float
    cost: float


# ============== FOLLOW-UP SCHEMAS ==============

class FollowUpBase(BaseModel):
    contact_phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    contact_name: Optional[str] = None
    message: str = Field(..., min_length=1)
    scheduled_at: datetime
    notes: Optional[str] = None


class FollowUpCreate(FollowUpBase):
    whatsapp_account_id: int


class FollowUpUpdate(BaseModel):
    contact_name: Optional[str] = None
    message: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class FollowUpResponse(FollowUpBase):
    id: int
    user_id: int
    whatsapp_account_id: int
    status: str
    completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== PAYMENT SCHEMAS ==============

class PaymentCreate(BaseModel):
    amount: float = Field(..., gt=0)
    payment_method: str
    tokens_purchased: float


class PaymentResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    currency: str
    payment_method: str
    status: str
    tokens_purchased: float
    transaction_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== RECOVERY SCHEMAS ==============

class RecoveryLinkGenerate(BaseModel):
    whatsapp_account_id: int


class RecoveryLinkResponse(BaseModel):
    whatsapp_account_id: int
    recovery_link: str
    auto_click_enabled: bool
    expires_at: datetime


# ============== COMMON SCHEMAS ==============

class MessageResponse(BaseModel):
    message: str
    success: bool = True


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int
