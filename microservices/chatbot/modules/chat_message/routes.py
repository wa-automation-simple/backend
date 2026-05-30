"""API routes for ChatMessage module."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from modules.chat_message.schemas import ChatMessageCreate, ChatMessageUpdate, ChatMessageResponse
from modules.chat_message.service import ChatMessageService

router = APIRouter(prefix="/chat_messages", tags=["ChatMessages"])


@router.post("", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
def create_item(item_data: ChatMessageCreate, db: Session = Depends(get_db)):
    """Create a new chat_message."""
    service = ChatMessageService(db)
    return service.create_item(item_data=item_data)


@router.get("", response_model=List[ChatMessageResponse])
def list_items(db: Session = Depends(get_db)):
    """List all items."""
    service = ChatMessageService(db)
    return service.list_items()


@router.get("/{item_id}", response_model=ChatMessageResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Get chat_message by ID."""
    service = ChatMessageService(db)
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="ChatMessage not found")
    return item


@router.put("/{item_id}", response_model=ChatMessageResponse)
def update_item(item_id: int, item_data: ChatMessageUpdate, db: Session = Depends(get_db)):
    """Update chat_message."""
    service = ChatMessageService(db)
    item = service.update_item(item_id, item_data)
    if not item:
        raise HTTPException(status_code=404, detail="ChatMessage not found")
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    """Delete a chat_message."""
    service = ChatMessageService(db)
    success = service.delete_item(item_id)
    if not success:
        raise HTTPException(status_code=404, detail="ChatMessage not found")
