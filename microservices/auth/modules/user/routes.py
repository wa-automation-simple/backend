"""API routes for User module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from auth.core.database import get_db
from auth.modules.user.schemas import UserCreate, UserUpdate, UserResponse
from auth.modules.user.service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user."""
    service = UserService(db)
    return service.create_item(item_data=item_data)


@router.get("", response_model=List[UserResponse])
def list_items(db: Session = Depends(get_db)):
    """List all items."""
    service = UserService(db)
    return service.list_items()


@router.get("/{item_id}", response_model=UserResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    service = UserService(db)
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="User not found")
    return item


@router.put("/{item_id}", response_model=UserResponse)
def update_item(item_id: int, item_data: UserUpdate, db: Session = Depends(get_db)):
    """Update user."""
    service = UserService(db)
    item = service.update_item(item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="User not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a user."""
    service = UserService(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
