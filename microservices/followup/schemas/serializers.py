"""Django-like Serializers for Followup Service"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FollowUpStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class LeadCreate(BaseModel):
    """Serializer for creating a lead"""
    phone_number: str = Field(..., min_length=10, max_length=20)
    name: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    source: str = Field(default="manual", pattern="^(manual|blast|organic|campaign)$")
    campaign_id: Optional[int] = None
    priority: int = Field(default=1, ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=1000)
    next_followup_date: Optional[datetime] = None
    max_followups: int = Field(default=5, ge=1, le=20)


class LeadUpdate(BaseModel):
    """Serializer for updating a lead"""
    name: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    status: Optional[FollowUpStatusEnum] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = Field(None, max_length=1000)
    next_followup_date: Optional[datetime] = None
    max_followups: Optional[int] = Field(None, ge=1, le=20)


class LeadResponse(BaseModel):
    """Serializer for lead response"""
    id: int
    user_id: int
    whatsapp_account_id: int
    phone_number: str
    name: Optional[str]
    tags: Optional[List[str]]
    source: str
    campaign_id: Optional[int]
    status: FollowUpStatusEnum
    priority: int
    notes: Optional[str]
    last_interaction: Optional[datetime]
    next_followup_date: Optional[datetime]
    followup_count: int
    max_followups: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InteractionLogCreate(BaseModel):
    """Serializer for creating interaction log"""
    lead_id: int
    interaction_type: str = Field(..., pattern="^(message_sent|message_received|call|note|email)$")
    content: Optional[str] = Field(None, max_length=5000)
    media_url: Optional[str] = Field(None, max_length=500)
    is_outbound: bool = Field(default=True)
    followup_sequence_id: Optional[int] = None
    sequence_step: int = Field(default=0)


class InteractionLogResponse(BaseModel):
    """Serializer for interaction log response"""
    id: int
    lead_id: int
    user_id: int
    whatsapp_account_id: int
    interaction_type: str
    content: Optional[str]
    media_url: Optional[str]
    is_outbound: bool
    followup_sequence_id: Optional[int]
    sequence_step: int
    response_received: bool
    response_time_minutes: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class FollowUpSequenceCreate(BaseModel):
    """Serializer for creating follow-up sequence"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    interval_days: int = Field(default=3, ge=1, le=30)
    messages: List[str] = Field(..., min_items=1, max_items=20)


class FollowUpSequenceResponse(BaseModel):
    """Serializer for follow-up sequence response"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    total_steps: int
    interval_days: int
    messages: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
