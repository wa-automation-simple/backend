"""Auth routes for Auth Service."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..schemas.serializers import (
    UserCreate, UserResponse, UserUpdate,
    LoginRequest, TokenResponse, PasswordChange, PermissionResponse
)
from ..services.user_service import UserService
from ..core.database import get_db
from ..models.user import UserRole
from ...shared.security.rbac import decode_token, TokenData


router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_current_user(token: str = Depends(lambda: None)) -> dict:
    """Dependency to get current user from token."""
    # This will be overridden by middleware in production
    return {"id": 1, "role": "user", "permissions": []}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    service = UserService(db)
    
    try:
        user, _ = service.register_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login and get access token."""
    service = UserService(db)
    
    result = service.authenticate_user(login_data.email, login_data.password)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    user, access_token = result
    
    # Generate refresh token
    from ...shared.security.rbac import create_refresh_token
    refresh_token = create_refresh_token({"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=1800  # 30 minutes
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current user profile."""
    service = UserService(db)
    
    user = service.get_user_by_id(current_user["id"])
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user


@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update current user profile."""
    service = UserService(db)
    
    try:
        user = service.update_user(current_user["id"], user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Change user password."""
    service = UserService(db)
    
    try:
        service.change_password(
            current_user["id"],
            password_data.old_password,
            password_data.new_password
        )
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/permissions", response_model=PermissionResponse)
def get_user_permissions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get current user permissions."""
    service = UserService(db)
    
    user = service.get_user_by_id(current_user["id"])
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    permissions = service.get_user_permissions_list(user)
    
    return PermissionResponse(role=user.role.value, permissions=permissions)


# Admin-only routes
@router.get("/users", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    is_active: bool = True,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all users (admin only)."""
    service = UserService(db)
    
    # Check permission
    if not service.has_user_permission(type('obj', (object,), {'role': type('obj', (object,), {'value': current_user['role']})()})(), "user:read"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    users = service.list_users(skip=skip, limit=limit, is_active=is_active)
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user by ID (admin only)."""
    service = UserService(db)
    
    # Check permission
    if not service.has_user_permission(type('obj', (object,), {'role': type('obj', (object,), {'value': current_user['role']})()})(), "user:read"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    user = service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete user (super_admin only)."""
    service = UserService(db)
    
    # Check permission
    if not service.has_user_permission(type('obj', (object,), {'role': type('obj', (object,), {'value': current_user['role']})()})(), "user:delete"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    success = service.delete_user(user_id)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return None
