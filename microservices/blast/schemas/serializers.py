"""Pydantic schemas for Blast service."""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from enum import Enum


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"


class BlastCampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    account_id: int
    message_content: str = Field(..., min_length=1, max_length=4096)


class BlastCampaignCreate(BlastCampaignBase):
    recipients: List[str] = Field(..., min_items=1)
    media_url: Optional[HttpUrl] = None
    media_type: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class BlastCampaignResponse(BlastCampaignBase):
    id: int
    user_id: int
    total_recipients: int
    status: CampaignStatus
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    sent_count: int
    delivered_count: int
    failed_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MediaUploadResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    file_url: str
    file_type: str
    file_size: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CampaignsListResponse(BaseModel):
    campaigns: List[BlastCampaignResponse]
    total: int
    page: int
    page_size: int
