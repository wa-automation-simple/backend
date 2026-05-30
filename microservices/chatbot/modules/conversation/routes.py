"""API routes for Conversation module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from modules.conversation.schemas import ConversationCreate, ConversationUpdate, ConversationResponse
from modules.conversation.service import ConversationService

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_data: ConversationCreate, db: Session = Depends(get_db)):
    """Create a new conversation."""
    service = ConversationService(db)
    return service.create_item(item_data=item_data)


@router.get("", response_model=List[ConversationResponse])
def list_items(db: Session = Depends(get_db)):
    """List all items."""
    service = ConversationService(db)
    return service.list_items()


@router.get("/{item_id}", response_model=ConversationResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get conversation by ID."""
    service = ConversationService(db)
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return item


@router.put("/{item_id}", response_model=ConversationResponse)
def update_item(item_id: int, item_data: ConversationUpdate, db: Session = Depends(get_db)):
    """Update conversation."""
    service = ConversationService(db)
    item = service.update_item(item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a conversation."""
    service = ConversationService(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
