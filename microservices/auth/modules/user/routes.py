"""API routes for User module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.database import get_db
from modules.user.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    GoogleUserCreate,
    TokenResponse,
)
from modules.user.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


# ==================== User Routes ====================


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user."""
    service = UserService(db)
    try:
        return await service.create_user(user_data=user_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/google", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_google_user(
    google_data: GoogleUserCreate, db: AsyncSession = Depends(get_db)
):
    """Create or link a user via Google OAuth."""
    service = UserService(db)
    try:
        return await service.create_google_user(google_data=google_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[UserResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    """List all users."""
    service = UserService(db)
    return await service.list_users()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get user by ID."""
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str, user_data: UserUpdate, db: AsyncSession = Depends(get_db)
):
    """Update user."""
    service = UserService(db)
    try:
        user = await service.update_user(user_id, user_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a user."""
    service = UserService(db)
    success = await service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")


@router.get("/{user_id}/permissions", response_model=List[str])
async def get_user_permissions(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get all permissions for a user."""
    service = UserService(db)
    user = await service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await service.get_user_permissions(user_id)
