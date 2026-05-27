"""Pydantic schemas for request/response validation in Auth service."""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles for RBAC."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    TRIAL = "trial"


# ==================== User Schemas ====================

class UserBase(BaseModel):
    """Base user schema with common fields."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    role: UserRole = UserRole.USER


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response data."""
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== Auth Schemas ====================

class TokenRequest(BaseModel):
    """Schema for login request."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes in seconds


class RefreshTokenRequest(BaseModel):
    """Schema for refreshing access token."""
    refresh_token: str


class PasswordChange(BaseModel):
    """Schema for changing password."""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class PasswordResetRequest(BaseModel):
    """Schema for requesting password reset."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for confirming password reset."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


# ==================== Response Wrappers ====================

class UsersListResponse(BaseModel):
    """Schema for listing users with pagination."""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
