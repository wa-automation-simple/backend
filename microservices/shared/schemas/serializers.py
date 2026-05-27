from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator, HttpUrl
from enum import Enum


# ==================== USER SCHEMAS ====================

class UserRoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    TRIAL = "trial"


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    role: Optional[UserRoleEnum] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    role: UserRoleEnum
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== AUTH SCHEMAS ====================

class TokenRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


# ==================== WHATSAPP ACCOUNT SCHEMAS ====================

class WhatsAppAccountBase(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=20)


class WhatsAppAccountCreate(WhatsAppAccountBase):
    pass


class WhatsAppAccountUpdate(BaseModel):
    auto_click_enabled: Optional[bool] = None


class WhatsAppAccountResponse(WhatsAppAccountBase):
    id: int
    user_id: int
    session_id: str
    status: str
    is_warming: bool
    warming_day: int
    warming_started_at: Optional[datetime]
    last_active: Optional[datetime]
    recovery_link: Optional[str]
    auto_click_enabled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class WarmupStart(BaseModel):
    whatsapp_account_id: int


class WarmupStatus(BaseModel):
    whatsapp_account_id: int
    day: int
    messages_sent_today: int
    messages_limit: int
    status: str


# ==================== BLAST SCHEMAS ====================

class BlastCampaignBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=255)
    message: str = Field(..., min_length=1)


class BlastCampaignCreate(BlastCampaignBase):
    recipients: List[str] = Field(..., min_items=1)  # List of phone numbers
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class BlastCampaignUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    message: Optional[str] = None
    status: Optional[str] = None


class BlastRecipientResponse(BaseModel):
    id: int
    phone_number: str
    contact_name: Optional[str]
    status: str
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


class BlastCampaignResponse(BlastCampaignBase):
    id: int
    user_id: int
    media_url: Optional[str]
    media_type: Optional[str]
    recipient_count: int
    sent_count: int
    delivered_count: int
    failed_count: int
    status: str
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    recipients: Optional[List[BlastRecipientResponse]] = []
    
    class Config:
        from_attributes = True


class MediaUploadResponse(BaseModel):
    media_url: str
    media_type: str
    file_size: int
    uploaded_at: datetime


# ==================== AUTO REPLY & AI SCHEMAS ====================

class AutoReplyBase(BaseModel):
    trigger_keyword: Optional[str] = Field(None, max_length=255)
    response_message: str = Field(..., min_length=1)
    use_ai: bool = False
    ai_model: Optional[str] = None
    priority: int = Field(default=0, ge=0, le=100)


class AutoReplyCreate(AutoReplyBase):
    whatsapp_account_id: Optional[int] = None


class AutoReplyUpdate(BaseModel):
    trigger_keyword: Optional[str] = Field(None, max_length=255)
    response_message: Optional[str] = None
    use_ai: Optional[bool] = None
    ai_model: Optional[str] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = Field(None, ge=0, le=100)


class AutoReplyResponse(AutoReplyBase):
    id: int
    user_id: int
    whatsapp_account_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AIRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    model: Optional[str] = "gpt-3.5-turbo"
    whatsapp_account_id: Optional[int] = None


class AIResponse(BaseModel):
    response: str
    tokens_consumed: float
    cost: float
    model_used: str


# ==================== TOKEN SCHEMAS ====================

class TokenBalanceResponse(BaseModel):
    user_id: int
    balance: float
    currency: str = "USD"
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TokenTopup(BaseModel):
    amount: float = Field(..., gt=0)  # Amount in USD to spend
    payment_method: str = Field(..., min_length=3)


class TokenTransactionResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    transaction_type: str
    description: Optional[str]
    reference_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenPackage(BaseModel):
    tokens: float
    price: float
    discount_percent: float
    effective_price_per_token: float


# ==================== FOLLOW-UP SCHEMAS ====================

class FollowUpBase(BaseModel):
    contact_phone: str = Field(..., min_length=10, max_length=20)
    contact_name: Optional[str] = Field(None, max_length=255)
    message: str = Field(..., min_length=1)
    notes: Optional[str] = None


class FollowUpCreate(FollowUpBase):
    whatsapp_account_id: int
    scheduled_at: datetime
    media_url: Optional[str] = None
    media_type: Optional[str] = None


class FollowUpUpdate(BaseModel):
    contact_name: Optional[str] = Field(None, max_length=255)
    message: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class FollowUpResponse(FollowUpBase):
    id: int
    user_id: int
    whatsapp_account_id: int
    media_url: Optional[str]
    media_type: Optional[str]
    status: str
    scheduled_at: datetime
    sent_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== PAYMENT SCHEMAS ====================

class PaymentBase(BaseModel):
    amount: float = Field(..., gt=0)
    currency: str = "USD"


class PaymentCreate(PaymentBase):
    tokens_purchased: float = Field(..., gt=0)
    payment_method: str


class PaymentUpdate(BaseModel):
    payment_status: Optional[str] = None
    transaction_id: Optional[str] = None


class PaymentResponse(PaymentBase):
    id: int
    user_id: int
    tokens_purchased: float
    payment_method: Optional[str]
    payment_status: str
    transaction_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ==================== RECOVERY SCHEMAS ====================

class RecoveryLinkResponse(BaseModel):
    whatsapp_account_id: int
    recovery_link: str
    auto_click_enabled: bool


class AutoClickRequest(BaseModel):
    whatsapp_account_id: int
    enabled: bool


# ==================== COMMON RESPONSE SCHEMAS ====================

class MessageResponse(BaseModel):
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    message: str
    error_code: str
    details: Optional[Dict[str, Any]] = None


class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
