"""Pydantic schemas for Chatbot module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ChatbotCreate(BaseModel):
    """Schema for creating a new chatbot."""
    # Add fields as needed
    pass


class ChatbotUpdate(BaseModel):
    """Schema for updating a chatbot."""
    # Add fields as needed
    pass


class ChatbotResponse(BaseModel):
    """Schema for chatbot response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
