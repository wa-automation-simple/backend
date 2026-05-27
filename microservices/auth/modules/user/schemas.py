"""Pydantic schemas for User module."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    # Add fields as needed
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    # Add fields as needed
    pass


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
