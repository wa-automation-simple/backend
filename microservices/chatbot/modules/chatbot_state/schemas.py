"""Pydantic schemas for ChatbotState module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ChatbotStateCreate(BaseModel):
    """Schema for creating a new chatbot_state."""
    # Add fields as needed
    pass


class ChatbotStateUpdate(BaseModel):
    """Schema for updating a chatbot_state."""
    # Add fields as needed
    pass


class ChatbotStateResponse(BaseModel):
    """Schema for chatbot_state response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
