"""API routes for FollowUp module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from followup.core.database import get_db
from followup.modules.follow_up.schemas import FollowUpCreate, FollowUpUpdate, FollowUpResponse
from followup.modules.follow_up.service import FollowUpService

router = APIRouter(prefix="/follow_ups", tags=["FollowUps"])


@router.post("", response_model=FollowUpResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_data: FollowUpCreate, db: Session = Depends(get_db)):
    """Create a new follow_up."""
    service = FollowUpService(db)
    return service.create_item(item_data=item_data)


@router.get("", response_model=List[FollowUpResponse])
def list_items(db: Session = Depends(get_db)):
    """List all items."""
    service = FollowUpService(db)
    return service.list_items()


@router.get("/{item_id}", response_model=FollowUpResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get follow_up by ID."""
    service = FollowUpService(db)
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="FollowUp not found")
    return item


@router.put("/{item_id}", response_model=FollowUpResponse)
def update_item(item_id: int, item_data: FollowUpUpdate, db: Session = Depends(get_db)):
    """Update follow_up."""
    service = FollowUpService(db)
    item = service.update_item(item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="FollowUp not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a follow_up."""
    service = FollowUpService(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="FollowUp not found")
