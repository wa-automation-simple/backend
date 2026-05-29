"""Pydantic schemas for User module."""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


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
    roles: Optional[List["RoleResponse"]] = []
    
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


# Import RoleResponse here to avoid circular imports
from auth.modules.role.schemas import RoleResponse

# Update forward references
UserResponse.update_forward_refs()
