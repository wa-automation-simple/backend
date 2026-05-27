"""
Shared Schemas - Django-like Serializers for request/response validation
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, validator


# ============== AUTH SCHEMAS ==============

class UserCreate(BaseModel):
    """Serializer for user registration."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: str = Field(default="user")
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v
    
    @validator('role')
    def validate_role(cls, v):
        allowed_roles = ["super_admin", "admin", "manager", "user", "trial"]
        if v not in allowed_roles:
            raise ValueError(f"Role must be one of: {allowed_roles}")
        return v


class UserResponse(BaseModel):
    """Serializer for user response."""
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Serializer for updating user."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class TokenRequest(BaseModel):
    """Serializer for login request."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Serializer for token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class PasswordChange(BaseModel):
    """Serializer for password change."""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


# ============== WHATSAPP SCHEMAS ==============

class WhatsAppAccountCreate(BaseModel):
    """Serializer for creating WhatsApp account."""
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    device_name: Optional[str] = Field(None, max_length=100)
    user_id: Optional[int] = None  # For admin to assign to user


class WhatsAppAccountResponse(BaseModel):
    """Serializer for WhatsApp account response."""
    id: int
    user_id: int
    phone_number: str
    device_name: Optional[str]
    status: str  # connected, disconnected, banned, warming_up
    is_primary: bool
    created_at: datetime
    last_active: Optional[datetime]
    
    class Config:
        from_attributes = True


class WarmupStart(BaseModel):
    """Serializer for starting warmup process."""
    account_id: int
    duration_days: int = Field(default=30, ge=7, le=60)
    daily_increment: int = Field(default=5, ge=1, le=20)


class WarmupStatus(BaseModel):
    """Serializer for warmup status response."""
    account_id: int
    current_day: int
    total_days: int
    daily_limit: int
    messages_sent_today: int
    progress_percentage: float
    status: str
    started_at: datetime
    estimated_completion: datetime


# ============== BLAST SCHEMAS ==============

class BlastCampaignCreate(BaseModel):
    """Serializer for creating blast campaign."""
    name: str = Field(..., min_length=3, max_length=200)
    message: str = Field(..., min_length=1, max_length=4096)
    recipient_ids: List[int]
    schedule_at: Optional[datetime] = None
    send_immediately: bool = True


class BlastCampaignResponse(BaseModel):
    """Serializer for blast campaign response."""
    id: int
    name: str
    message: str
    total_recipients: int
    sent_count: int
    failed_count: int
    status: str  # pending, sending, completed, failed
    created_at: datetime
    scheduled_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MediaUploadResponse(BaseModel):
    """Serializer for media upload response."""
    media_id: str
    media_type: str  # image, video, document
    file_name: str
    file_size: int
    url: str
    uploaded_at: datetime


class BlastWithMedia(BaseModel):
    """Serializer for blast with media attachment."""
    campaign_id: int
    media_id: str
    caption: Optional[str] = Field(None, max_length=2048)


# ============== AI SCHEMAS ==============

class AutoReplyCreate(BaseModel):
    """Serializer for creating auto-reply configuration."""
    account_id: int
    trigger_keywords: List[str] = Field(..., min_items=1)
    response_template: str = Field(..., min_length=1, max_length=2048)
    use_ai: bool = False
    ai_personality: Optional[str] = Field(None, max_length=500)
    is_active: bool = True


class AutoReplyResponse(BaseModel):
    """Serializer for auto-reply response."""
    id: int
    account_id: int
    trigger_keywords: List[str]
    response_template: str
    use_ai: bool
    ai_personality: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AIRequest(BaseModel):
    """Serializer for AI message processing."""
    message: str = Field(..., min_length=1, max_length=4096)
    context: Optional[str] = Field(None, max_length=8192)
    personality: Optional[str] = None
    account_id: int


class AIResponse(BaseModel):
    """Serializer for AI response."""
    reply: str
    tokens_used: int
    cost: float
    processing_time_ms: int


class TokenBalanceResponse(BaseModel):
    """Serializer for token balance response."""
    user_id: int
    balance: float
    currency: str = "USD"
    last_updated: datetime


class TokenTopup(BaseModel):
    """Serializer for token topup request."""
    amount: float = Field(..., gt=0)
    package_id: Optional[int] = None  # Predefined package


class TokenTransactionResponse(BaseModel):
    """Serializer for token transaction response."""
    id: int
    user_id: int
    type: str  # purchase, usage, refund
    amount: float
    balance_after: float
    description: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============== PAYMENT SCHEMAS ==============

class PaymentCreate(BaseModel):
    """Serializer for creating payment."""
    user_id: int
    amount: float = Field(..., gt=0)
    payment_method: str  # credit_card, paypal, crypto, bank_transfer
    token_package_id: Optional[int] = None


class PaymentResponse(BaseModel):
    """Serializer for payment response."""
    id: int
    user_id: int
    amount: float
    currency: str
    status: str  # pending, completed, failed, refunded
    payment_method: str
    transaction_id: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class InvoiceResponse(BaseModel):
    """Serializer for invoice response."""
    id: int
    user_id: int
    amount: float
    items: List[dict]
    status: str
    due_date: datetime
    paid_at: Optional[datetime]
    created_at: datetime


# ============== FOLLOWUP SCHEMAS ==============

class FollowUpCreate(BaseModel):
    """Serializer for creating follow-up."""
    account_id: int
    contact_phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    contact_name: Optional[str] = Field(None, max_length=200)
    message: str = Field(..., min_length=1, max_length=4096)
    scheduled_at: datetime
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")
    notes: Optional[str] = Field(None, max_length=2048)


class FollowUpResponse(BaseModel):
    """Serializer for follow-up response."""
    id: int
    account_id: int
    contact_phone: str
    contact_name: Optional[str]
    message: str
    scheduled_at: datetime
    status: str  # pending, sent, failed, skipped
    priority: str
    notes: Optional[str]
    sent_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LeadResponse(BaseModel):
    """Serializer for lead response."""
    id: int
    phone_number: str
    name: Optional[str]
    source: str
    last_interaction: datetime
    follow_up_count: int
    conversion_status: str  # new, contacted, interested, converted, lost
    tags: List[str]
    
    class Config:
        from_attributes = True


# ============== RECOVERY SCHEMAS ==============

class RecoveryLinkResponse(BaseModel):
    """Serializer for recovery link response."""
    account_id: int
    recovery_url: str
    auto_click_enabled: bool
    expires_at: datetime
    status: str  # active, clicked, expired


class AutoClickConfig(BaseModel):
    """Serializer for auto-click configuration."""
    account_id: int
    enabled: bool
    click_delay_seconds: int = Field(default=3, ge=1, le=30)
    retry_count: int = Field(default=3, ge=0, le=10)
