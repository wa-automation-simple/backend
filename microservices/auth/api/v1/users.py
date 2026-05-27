"""Authentication routes for user registration, login, and token management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from auth.core.database import get_db
from auth.schemas.serializers import (
    UserCreate,
    UserResponse,
    UserUpdate,
    TokenRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordChange,
    UsersListResponse
)
from auth.services.user_service import UserService
from auth.api.deps import get_current_user, require_role
from auth.models.user import User, UserRole


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    service = UserService(db)
    
    try:
        user = service.register_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
def login(credentials: TokenRequest, db: Session = Depends(get_db)):
    """Login and receive access/refresh tokens."""
    service = UserService(db)
    
    token_response = service.authenticate_user(credentials.username, credentials.password)
    
    if token_response is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_response


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    service = UserService(db)
    
    token_response = service.refresh_tokens(request.refresh_token)
    
    if token_response is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    return token_response


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information."""
    service = UserService(db)
    
    try:
        updated_user = service.update_user(current_user.id, user_data)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/change-password")
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change current user password."""
    service = UserService(db)
    
    try:
        success = service.change_password(
            current_user.id,
            password_data.old_password,
            password_data.new_password
        )
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Admin-only routes
@router.get("/users", response_model=UsersListResponse)
def list_users(
    page: int = 1,
    page_size: int = 20,
    role: UserRole = None,
    is_active: bool = None,
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """List all users (admin only)."""
    service = UserService(db)
    
    users, total = service.list_users(page, page_size, role, is_active)
    total_pages = (total + page_size - 1) // page_size
    
    return UsersListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """Get user by ID (admin only)."""
    service = UserService(db)
    user = service.get_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(require_role(["super_admin"])),
    db: Session = Depends(get_db)
):
    """Delete user (super admin only)."""
    service = UserService(db)
    
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself"
        )
    
    success = service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deleted successfully"}


@router.post("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """Deactivate user account (admin only)."""
    service = UserService(db)
    user = service.deactivate_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User deactivated successfully"}


@router.post("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """Activate user account (admin only)."""
    service = UserService(db)
    user = service.activate_user(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User activated successfully"}
