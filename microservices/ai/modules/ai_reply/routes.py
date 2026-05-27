"""API routes for AIReply module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ai.core.database import get_db
from ai.modules.ai_reply.schemas import AIReplyCreate, AIReplyUpdate, AIReplyResponse
from ai.modules.ai_reply.service import AIReplyService

router = APIRouter(prefix="/ai_replys", tags=["AIReplys"])


@router.post("", response_model=AIReplyResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_data: AIReplyCreate, db: Session = Depends(get_db)):
    """Create a new ai_reply."""
    service = AIReplyService(db)
    return service.create_item(item_data=item_data)


@router.get("", response_model=List[AIReplyResponse])
def list_items(db: Session = Depends(get_db)):
    """List all items."""
    service = AIReplyService(db)
    return service.list_items()


@router.get("/{item_id}", response_model=AIReplyResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get ai_reply by ID."""
    service = AIReplyService(db)
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="AIReply not found")
    return item


@router.put("/{item_id}", response_model=AIReplyResponse)
def update_item(item_id: int, item_data: AIReplyUpdate, db: Session = Depends(get_db)):
    """Update ai_reply."""
    service = AIReplyService(db)
    item = service.update_item(item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="AIReply not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a ai_reply."""
    service = AIReplyService(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="AIReply not found")
