"""Pydantic schemas for FollowUp module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class FollowUpCreate(BaseModel):
    """Schema for creating a new follow_up."""
    # Add fields as needed
    pass


class FollowUpUpdate(BaseModel):
    """Schema for updating a follow_up."""
    # Add fields as needed
    pass


class FollowUpResponse(BaseModel):
    """Schema for follow_up response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
