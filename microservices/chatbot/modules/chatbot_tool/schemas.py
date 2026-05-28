"""Pydantic schemas for ChatbotTool module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ChatbotToolCreate(BaseModel):
    """Schema for creating a new chatbot_tool."""
    # Add fields as needed
    pass


class ChatbotToolUpdate(BaseModel):
    """Schema for updating a chatbot_tool."""
    # Add fields as needed
    pass


class ChatbotToolResponse(BaseModel):
    """Schema for chatbot_tool response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
