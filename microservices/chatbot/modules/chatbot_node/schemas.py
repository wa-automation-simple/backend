"""Pydantic schemas for ChatbotNode module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ChatbotNodeCreate(BaseModel):
    """Schema for creating a new chatbot_node."""
    # Add fields as needed
    pass


class ChatbotNodeUpdate(BaseModel):
    """Schema for updating a chatbot_node."""
    # Add fields as needed
    pass


class ChatbotNodeResponse(BaseModel):
    """Schema for chatbot_node response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
