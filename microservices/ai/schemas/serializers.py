"""Django-like Serializers for AI Service"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
import re


class AIReplyCreate(BaseModel):
    """Serializer for creating AI auto-reply configuration"""
    whatsapp_account_id: int = Field(..., gt=0)
    trigger_type: str = Field(default="keyword", pattern="^(keyword|always|pattern)$")
    trigger_keywords: List[str] = Field(default_factory=list)
    trigger_pattern: Optional[str] = None
    system_prompt: str = Field(default="You are a helpful customer service assistant.", min_length=1, max_length=2000)
    max_tokens: int = Field(default=150, ge=50, le=4000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    enable_ai: bool = Field(default=True)
    fallback_message: str = Field(default="Terima kasih atas pesan Anda. Kami akan segera merespons.", max_length=500)

    @validator('trigger_keywords')
    def validate_keywords(cls, v):
        if len(v) > 50:
            raise ValueError("Maximum 50 keywords allowed")
        return v

    @validator('trigger_pattern')
    def validate_pattern(cls, v, values):
        if v and values.get('trigger_type') == 'pattern':
            try:
                re.compile(v)
            except re.error:
                raise ValueError("Invalid regex pattern")
        return v


class AIReplyUpdate(BaseModel):
    """Serializer for updating AI auto-reply configuration"""
    trigger_type: Optional[str] = Field(None, pattern="^(keyword|always|pattern)$")
    trigger_keywords: Optional[List[str]] = None
    trigger_pattern: Optional[str] = None
    system_prompt: Optional[str] = Field(None, min_length=1, max_length=2000)
    max_tokens: Optional[int] = Field(None, ge=50, le=4000)
    temperature: Optional[float] = Field(None, ge=0.0, le=2.0)
    enable_ai: Optional[bool] = None
    fallback_message: Optional[str] = Field(None, max_length=500)


class AIReplyResponse(BaseModel):
    """Serializer for AI auto-reply response"""
    id: int
    user_id: int
    whatsapp_account_id: int
    trigger_type: str
    trigger_keywords: List[str]
    trigger_pattern: Optional[str]
    system_prompt: str
    max_tokens: int
    temperature: float
    enable_ai: bool
    fallback_message: str
    tokens_used: int
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIRequest(BaseModel):
    """Serializer for AI generation request"""
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_history: List[dict] = Field(default_factory=list)
    max_tokens: int = Field(default=150, ge=50, le=4000)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)


class AIResponse(BaseModel):
    """Serializer for AI generation response"""
    response: str
    tokens_used: int
    model: str
    success: bool = True


class TokenUsageResponse(BaseModel):
    """Serializer for token usage statistics"""
    total_tokens_used: int
    tokens_remaining: int
    estimated_cost: float
    last_reset_date: Optional[datetime]
