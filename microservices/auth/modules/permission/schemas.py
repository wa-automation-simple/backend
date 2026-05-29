"""Pydantic schemas for Permission module."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ==================== Permission Schemas ====================

class PermissionBase(BaseModel):
    """Base schema for Permission."""
    name: str = Field(..., description="Permission name, e.g., 'user:create'")
    description: Optional[str] = None
    resource: str = Field(..., description="Resource type, e.g., 'user', 'post'")
    action: str = Field(..., description="Action type, e.g., 'create', 'read'")


class PermissionCreate(PermissionBase):
    """Schema for creating a new permission."""
    pass


class PermissionUpdate(BaseModel):
    """Schema for updating a permission."""
    name: Optional[str] = None
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None


class PermissionResponse(PermissionBase):
    """Schema for permission response."""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
