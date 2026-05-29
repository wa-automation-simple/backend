"""Pydantic schemas for Role module."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from auth.modules.permission.schemas import PermissionResponse


# ==================== Role Schemas ====================

class RoleBase(BaseModel):
    """Base schema for Role."""
    name: str = Field(..., description="Role name")
    description: Optional[str] = None
    is_system: bool = False


class RoleCreate(RoleBase):
    """Schema for creating a new role."""
    permission_ids: Optional[List[str]] = []


class RoleUpdate(BaseModel):
    """Schema for updating a role."""
    name: Optional[str] = None
    description: Optional[str] = None
    is_system: Optional[bool] = None
    permission_ids: Optional[List[str]] = None


class RoleResponse(RoleBase):
    """Schema for role response."""
    id: str
    created_at: datetime
    updated_at: datetime
    permissions: Optional[List[PermissionResponse]] = []
    
    class Config:
        from_attributes = True
