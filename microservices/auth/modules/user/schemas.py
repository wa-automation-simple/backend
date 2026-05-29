"""Pydantic schemas for User module."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
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


# ==================== User Schemas ====================

class UserBase(BaseModel):
    """Base schema for User."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8)
    google_account_connected: bool = False


class GoogleUserCreate(BaseModel):
    """Schema for creating a user via Google OAuth."""
    google_sub: str
    google_email: EmailStr
    google_name: Optional[str] = None
    google_picture: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    google_account_connected: Optional[bool] = None
    google_sub: Optional[str] = None
    google_name: Optional[str] = None
    google_picture: Optional[str] = None
    role_ids: Optional[List[str]] = None


class UserResponse(UserBase):
    """Schema for user response."""
    id: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    google_account_connected: bool
    google_email: Optional[str] = None
    google_name: Optional[str] = None
    roles: Optional[List[RoleResponse]] = []
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
