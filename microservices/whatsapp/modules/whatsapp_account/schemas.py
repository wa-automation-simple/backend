"""Pydantic schemas for WhatsAppAccount module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class WhatsAppAccountCreate(BaseModel):
    """Schema for creating a new whatsapp_account."""
    # Add fields as needed
    pass


class WhatsAppAccountUpdate(BaseModel):
    """Schema for updating a whatsapp_account."""
    # Add fields as needed
    pass


class WhatsAppAccountResponse(BaseModel):
    """Schema for whatsapp_account response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
