"""Pydantic schemas for ChatbotAgent module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ChatbotAgentCreate(BaseModel):
    """Schema for creating a new chatbot_agent."""
    # Add fields as needed
    pass


class ChatbotAgentUpdate(BaseModel):
    """Schema for updating a chatbot_agent."""
    # Add fields as needed
    pass


class ChatbotAgentResponse(BaseModel):
    """Schema for chatbot_agent response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
