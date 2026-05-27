"""Pydantic schemas for BlastCampaign module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class BlastCampaignCreate(BaseModel):
    """Schema for creating a new blast_campaign."""
    # Add fields as needed
    pass


class BlastCampaignUpdate(BaseModel):
    """Schema for updating a blast_campaign."""
    # Add fields as needed
    pass


class BlastCampaignResponse(BaseModel):
    """Schema for blast_campaign response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
