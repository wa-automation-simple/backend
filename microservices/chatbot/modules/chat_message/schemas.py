"""Pydantic schemas for ChatMessage module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ChatMessageCreate(BaseModel):
    """Schema for creating a new chat_message."""
    # Add fields as needed
    pass


class ChatMessageUpdate(BaseModel):
    """Schema for updating a chat_message."""
    # Add fields as needed
    pass


class ChatMessageResponse(BaseModel):
    """Schema for chat_message response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
