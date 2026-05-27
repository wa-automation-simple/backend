"""Pydantic schemas for AIReply module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class AIReplyCreate(BaseModel):
    """Schema for creating a new ai_reply."""
    # Add fields as needed
    pass


class AIReplyUpdate(BaseModel):
    """Schema for updating a ai_reply."""
    # Add fields as needed
    pass


class AIReplyResponse(BaseModel):
    """Schema for ai_reply response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
