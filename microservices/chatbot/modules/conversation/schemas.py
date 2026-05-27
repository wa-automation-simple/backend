"""Pydantic schemas for Conversation module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ConversationCreate(BaseModel):
    """Schema for creating a new conversation."""
    # Add fields as needed
    pass


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation."""
    # Add fields as needed
    pass


class ConversationResponse(BaseModel):
    """Schema for conversation response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
