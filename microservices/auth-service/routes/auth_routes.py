"""
Auth Service Routes - Authentication and user management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta

from auth_service.config import settings
from auth_service.models.user import User
from auth_service.services.user_service import UserService
from auth_service.schemas.serializers import (
    UserCreate, UserResponse, UserUpdate,
    TokenRequest, TokenResponse, PasswordChange
)
from shared.security import create_access_token
from shared.middleware.auth import require_permission


router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


def get_db():
    """Database dependency - each service has its own DB."""
    # In production, this would connect to the auth-service dedicated database
    from sqlalchemy import create_engine
    from auth_service.models.user import Base
    
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    user_service = UserService(db)
    
    try:
        user = user_service.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            role=user_data.role
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: TokenRequest, db: Session = Depends(get_db)):
    """Login and get access token."""
    user_service = UserService(db)
    
    user = user_service.authenticate_user(credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value
        },
        expires_delta=timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            created_at=user.created_at,
            is_active=user.is_active
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission("user:read:self"))
):
    """Get current authenticated user."""
    user_service = UserService(db)
    user_id = int(request.state.user_id)
    
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission("user:update:self"))
):
    """Update current user profile."""
    user_service = UserService(db)
    user_id = int(request.state.user_id)
    
    user = user_service.update_user(user_id, **user_update.dict(exclude_unset=True))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(require_permission("user:update:self"))
):
    """Change user password."""
    user_service = UserService(db)
    user_id = int(request.state.user_id)
    
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify old password
    if not user_service.authenticate_user(user.username, password_data.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )
    
    # Update password
    user_service.update_user(user_id, password_hash=get_password_hash(password_data.new_password))
    
    return {"message": "Password changed successfully"}


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: str = None,
    is_active: bool = None,
    _: bool = Depends(require_permission("user:read")),
    db: Session = Depends(get_db)
):
    """List all users (admin only)."""
    user_service = UserService(db)
    users = user_service.list_users(skip=skip, limit=limit, role=role, is_active=is_active)
    return users
